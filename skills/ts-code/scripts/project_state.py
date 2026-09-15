"""Read-only project doctor and opt-in overview renderer. Python 3.10+, stdlib only.

Checks explicit records, not arbitrary business semantics. Never runs record commands,
certifies report truth, edits slice history, or grants deployment permission.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import quote, unquote, urlsplit

BEGIN = '<!-- thinstack:progress:start -->'
END = '<!-- thinstack:progress:end -->'
BLOCK = re.compile(r'^```thinstack-slice[ \t]*\n(.*?)\n```[ \t]*$', re.M | re.S)
STAGES = {'clarify': '待澄清', 'approval': '待确认', 'planned': '已计划',
          'doing': '开发中', 'verify': '待验证', 'verified': '已验证', 'cancelled': '已取消'}
KINDS = {'mock', 'replay', 'runtime', 'live', 'manual'}
MAX_FILE_BYTES = 16 * 1024 * 1024


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def load_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('Non-finite JSON value: ' + value)
    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid)


def local(root: Path, name: str, *, exists=True) -> Path:
    if not isinstance(name, str) or not name or '\\' in name or ':' in name:
        raise ValueError('Expected portable project-relative path')
    path = Path(name)
    if path.is_absolute():
        raise ValueError('Absolute path not allowed')
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError('Symlink not allowed: ' + name)
    resolved = current.resolve()
    if not resolved.is_relative_to(root) or (exists and not resolved.is_file()):
        raise ValueError('Missing file or path outside project: ' + name)
    return resolved


def text_cell(value) -> str:
    # Never let record contents inject table rows, HTML or Markdown links.
    return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '&#124;').replace('\n', ' ').replace('\r', ' ').replace('[', '&#91;').replace(']', '&#93;').replace('`', '&#96;')


def contract_digest(record) -> str:
    """Status, timestamps, prose notes and evidence pointers do not self-invalidate."""
    keys = ('id', 'acceptance', 'approval', 'inputs', 'baseline_refs')
    return digest(canonical({k: record.get(k) for k in keys}))


def required_schema(record):
    if not isinstance(record, dict):
        raise ValueError('Slice block must contain an object')
    allowed = {'schema_version', 'id', 'title', 'type', 'module', 'stage', 'scope',
               'dependencies', 'blocker', 'next', 'approval', 'acceptance',
               'inputs', 'baseline_refs', 'evidence', 'deployment', 'customer_acceptance'}
    if set(record) - allowed:
        raise ValueError('Unknown slice fields: ' + ', '.join(sorted(set(record) - allowed)))
    if type(record.get('schema_version')) is not int or record['schema_version'] != 1:
        raise ValueError('Slice schema_version must be 1')
    for key in ('id', 'title', 'module'):
        if not isinstance(record.get(key), str) or not record[key].strip():
            raise ValueError('Missing text field: ' + key)
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}', record['id']):
        raise ValueError('id must be stable ASCII identifier (1..80 characters)')
    if record.get('stage') not in STAGES or record.get('type') not in {'business', 'technical', 'foundation'}:
        raise ValueError('Invalid stage/type')
    if record.get('scope') not in {'current', 'deferred'}:
        raise ValueError('scope must be current/deferred; cancellation uses stage')
    for key in ('dependencies', 'inputs'):
        values = record.get(key)
        if not isinstance(values, list) or any(not isinstance(x, str) or not x for x in values) or len(set(values)) != len(values):
            raise ValueError(key + ' must contain unique nonempty strings')
    for key in ('blocker', 'next', 'evidence', 'deployment', 'customer_acceptance'):
        if key in record and not isinstance(record[key], str):
            raise ValueError(key + ' must be text')
    approval = record.get('approval')
    if not isinstance(approval, dict) or set(approval) != {'state', 'source'} or approval['state'] not in {'proposed', 'approved'} or not isinstance(approval['source'], str):
        raise ValueError('approval needs state and source')
    if approval['state'] == 'approved' and not approval['source'].strip():
        raise ValueError('Approved scope needs an explicit source (not proof of its authenticity)')
    refs = record.get('baseline_refs')
    if not isinstance(refs, dict) or any(not isinstance(k, str) or not isinstance(v, str) or not re.fullmatch(r'[0-9a-f]{64}', v) for k, v in refs.items()):
        raise ValueError('baseline_refs must map paths to SHA256')
    criteria = record.get('acceptance')
    if not isinstance(criteria, list):
        raise ValueError('acceptance must be a list')
    ids = set()
    for ac in criteria:
        if not isinstance(ac, dict) or set(ac) != {'id', 'text', 'kinds'}:
            raise ValueError('Acceptance needs id, text, kinds')
        if not isinstance(ac['id'], str) or not ac['id'].strip() or ac['id'] in ids:
            raise ValueError('Invalid/duplicate acceptance ID')
        ids.add(ac['id'])
        if not isinstance(ac['text'], str) or not ac['text'].strip():
            raise ValueError('Acceptance text is required')
        if not isinstance(ac['kinds'], list) or not ac['kinds'] or any(not isinstance(k, str) or k not in KINDS for k in ac['kinds']):
            raise ValueError('Acceptance kinds must explicitly allow evidence types')


class Project:
    def __init__(self, root, config='.thinstack.json'):
        self.root = Path(root).resolve()
        if not self.root.is_dir():
            raise ValueError('Project root does not exist')
        self.files = {}
        self.issues = []
        self.rows = []
        self.documents = []
        self.fatal = False
        self.config_name = config
        self.config = load_json(self.read(config).decode('utf-8-sig'))
        cfg = self.config
        if not isinstance(cfg, dict) or set(cfg) != {'schema_version', 'overview', 'records', 'baselines'} or type(cfg['schema_version']) is not int or cfg['schema_version'] != 1:
            raise ValueError('Config needs schema_version=1, overview, records, baselines')
        for key in ('records', 'baselines'):
            if not isinstance(cfg[key], list) or any(not isinstance(x, str) or not x for x in cfg[key]) or len(set(cfg[key])) != len(cfg[key]):
                raise ValueError(key + ' must be a unique path list')
        if not cfg['records']:
            raise ValueError('No records configured; cannot certify an empty inventory')
        if not isinstance(cfg['overview'], str):
            raise ValueError('overview must be a path')
        paths = [cfg['overview']] + cfg['records'] + cfg['baselines']
        normalized = [local(self.root, x).relative_to(self.root).as_posix() for x in paths]
        if len(normalized) != len(set(normalized)):
            raise ValueError('Overview, record and baseline paths must be distinct; legacy combined files need an explicit adaptation')
        cfg['overview'] = normalized[0]
        n = len(cfg['records'])
        cfg['records'] = normalized[1:1+n]
        cfg['baselines'] = normalized[1+n:]
        self.overview = self.read(cfg['overview']).decode('utf-8')
        if self.overview.count(BEGIN) != 1 or self.overview.count(END) != 1 or self.overview.index(BEGIN) >= self.overview.index(END):
            raise ValueError('Overview needs exactly one ordered pair of progress markers')

    def read(self, name):
        path = local(self.root, name)
        data = path.read_bytes()
        if len(data) > MAX_FILE_BYTES:
            raise ValueError('File exceeds 16 MiB inspection limit: ' + name)
        key = path.relative_to(self.root).as_posix()
        if key in self.files and data != self.files[key]:
            raise ValueError('Source changed during inspection: ' + key)
        self.files[key] = data
        return data

    def issue(self, code, path, message, *, fatal=False, warning=False):
        self.issues.append({'code': code, 'path': path, 'message': message,
                            'severity': 'warning' if warning else 'error'})
        self.fatal = self.fatal or fatal

    def links(self, name, body):
        body = re.sub(r'^```.*?^```[^\n]*$', '', body, flags=re.S | re.M)
        for target in re.findall(r'\]\(([^\s)]+)(?:\s+"[^"\n]*")?\)', body):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue  # No network, credentials or remote-link claims.
            try:
                part = unquote(parsed.path)
                dest = (Path(name).parent / part).as_posix() if part else name
                raw = self.read(dest)
                if parsed.fragment:
                    text = raw.decode('utf-8')
                    explicit = set(re.findall(r'(?:id|name)=["\']([^"\']+)', text))
                    headings = re.findall(r'^#{1,6}\s+(.+?)\s*#*$', text, re.M)
                    # Explicit anchors are preferred; common Markdown headings are recognized.
                    seen, anchors = {}, set(explicit)
                    for heading in headings:
                        slug = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
                        count = seen.get(slug, 0)
                        anchors.add(slug + (f'-{count}' if count else ''))
                        seen[slug] = count + 1
                    if unquote(parsed.fragment) not in anchors:
                        self.issue('anchor_unresolved', name, target + ' (common Markdown/explicit anchors only)', warning=True)
            except (OSError, ValueError, UnicodeError) as exc:
                self.issue('dead_link', name, str(exc))

    def evidence(self, row):
        r, name = row['record'], row['path']
        row['verification'] = '未验证'
        row['detail'] = ''
        baselines = {local(self.root, p).relative_to(self.root).as_posix() for p in self.config['baselines']}
        changed_baseline = False
        for path, expected in r['baseline_refs'].items():
            try:
                if local(self.root, path).relative_to(self.root).as_posix() not in baselines:
                    raise ValueError('Baseline is not in project config: ' + path)
                if digest(self.read(path)) != expected:
                    changed_baseline = True
                    self.issue('baseline_changed', name, path + ': 规则版本变化，相关证据需核对', warning=True)
            except (OSError, ValueError) as exc:
                self.issue('baseline_reference', name, str(exc))
                changed_baseline = True
        ev = r.get('evidence', '')
        if not ev:
            if changed_baseline:
                row['verification'] = '需重验'
            return
        try:
            e = load_json(self.read(ev).decode('utf-8'))
            if not isinstance(e, dict):
                raise ValueError('Evidence must be an object')
            spec = importlib.util.spec_from_file_location('ts_evidence', Path(__file__).with_name('check_evidence.py'))
            validator = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(validator)
            errors = validator.check_record(e, self.root)
            # Include all checked inputs and artifacts in the consistency snapshot.
            for p in e.get('snapshot', {}) if isinstance(e.get('snapshot'), dict) else []:
                try:
                    self.read(p)
                except (OSError, ValueError) as exc:
                    errors.append(str(exc))
            for check in e.get('checks', []) if isinstance(e.get('checks'), list) else []:
                if isinstance(check, dict) and isinstance(check.get('artifact'), str):
                    try:
                        self.read(check['artifact'])
                    except (OSError, ValueError) as exc:
                        errors.append(str(exc))
            if e.get('slice_id') != r['id'] or e.get('contract_sha256') != contract_digest(r):
                errors.append('Evidence is not bound to current slice/acceptance contract')
            required = [ac['id'] for ac in r['acceptance']]
            if not isinstance(e.get('required'), list) or sorted(e['required']) != sorted(required):
                errors.append('Evidence required IDs differ from approved slice criteria')
            inputs = set(r['inputs']) | set(r['baseline_refs'])
            if not inputs or not isinstance(e.get('snapshot'), dict) or not inputs.issubset(e['snapshot']):
                errors.append('Evidence must cover every declared code/test/config/baseline input')
            # Check declared inputs even when maliciously omitted from evidence snapshot.
            for p in inputs:
                if local(self.root, p) in {local(self.root, name), local(self.root, self.config['overview']), local(self.root, ev)}:
                    errors.append('Progress/evidence files cannot be their own tested inputs')
                self.read(p)
            if changed_baseline:
                errors.append('Referenced baseline revision changed')
            if e.get('verdict') == 'GREEN':
                checks = e.get('checks', [])
                for ac in r['acceptance']:
                    if not any(isinstance(c, dict) and c.get('status') == 'pass' and isinstance(c.get('covers'), list) and ac['id'] in c['covers'] and c.get('kind') in ac['kinds'] for c in checks):
                        errors.append('Wrong/missing evidence kind for ' + ac['id'])
                if r['approval']['state'] != 'approved' or not required:
                    errors.append('No approved, nonempty acceptance contract')
                if r.get('blocker'):
                    errors.append('Unresolved blocker prevents completion')
            if errors:
                row['verification'] = '需重验'
                row['detail'] = '; '.join(errors)
                self.issue('evidence_invalid', name, row['detail'])
            elif e['verdict'] == 'GREEN':
                row['verification'] = '证据匹配'
            else:
                row['verification'] = '失败' if any(c['status'] == 'fail' for c in e['checks']) else '未验证'
        except (ValueError, OSError, UnicodeError, TypeError) as exc:
            row['verification'] = '需重验'
            row['detail'] = str(exc)
            self.issue('evidence_invalid', name, str(exc))

    def inspect(self, require_verified=()):
        for name in self.config['baselines']:
            self.documents.append((name, self.read(name).decode('utf-8')))
        seen = {}
        for name in self.config['records']:
            body = self.read(name).decode('utf-8').replace('\r\n', '\n')
            self.documents.append((name, body))
            matches = list(BLOCK.finditer(body))
            if not matches:
                self.issue('unstructured_record', name, '未适配旧文档：需要 thinstack-slice JSON 块；不会猜测状态', fatal=True)
            for match in matches:
                try:
                    record = load_json(match.group(1))
                    required_schema(record)
                    if record['id'] in seen:
                        raise ValueError('Duplicate slice id: ' + record['id'])
                    row = {'record': record, 'path': name}
                    seen[record['id']] = row
                    self.rows.append(row)
                except (ValueError, TypeError) as exc:
                    self.issue('record_invalid', name, str(exc), fatal=True)
        for row in self.rows:
            r = row['record']
            for dep in r['dependencies']:
                if dep not in seen:
                    self.issue('dependency_missing', row['path'], dep, fatal=True)
                elif seen[dep]['record']['stage'] == 'cancelled' and r['stage'] != 'cancelled':
                    self.issue('dependency_cancelled', row['path'], dep)
            self.evidence(row)
            if r['stage'] == 'verified' and row['verification'] != '证据匹配':
                self.issue('unsupported_completion', row['path'], '档案声称已验证，但当前证据不支持')
        visiting, done = set(), set()
        def visit(sid):
            if sid in visiting:
                self.issue('dependency_cycle', seen[sid]['path'], sid, fatal=True)
                return
            if sid in done:
                return
            visiting.add(sid)
            for dep in seen[sid]['record']['dependencies']:
                if dep in seen:
                    visit(dep)
            visiting.remove(sid)
            done.add(sid)
        for sid in seen:
            visit(sid)
        for sid in require_verified:
            row = seen.get(sid)
            if row is None or row['verification'] != '证据匹配' or row['record']['stage'] == 'cancelled':
                self.issue('required_slice_unverified', sid, '指定交付范围缺少匹配证据')
        for name, body in self.documents:
            self.links(name, body)
        # Generated section is recomputed; inspect user-maintained links separately.
        prefix, tail = self.overview.split(BEGIN)
        _, suffix = tail.split(END)
        self.links(self.config['overview'], prefix + suffix)
        self.generated = self.render()
        self.expected_overview = prefix + BEGIN + '\n' + self.generated + END + suffix
        self.stale = self.overview != self.expected_overview
        if self.stale:
            self.issue('overview_stale', self.config['overview'], '总览生成区与当前来源不一致')
        return self

    def render(self):
        source_hashes = {p: digest(b) for p, b in self.files.items() if p != self.config['overview']}
        stamp = digest(canonical(source_hashes))
        rows = ['> 自动汇总；来源摘要：`' + stamp + '`。仅记录/证据关联检查，不认证业务正确或生产可用。', '',
                '| 切片 | 结果/模块 | 阶段 | 当前证据 | 阻塞/下一步 | 依赖 | 部署/客户验收（记录值） |',
                '|---|---|---|---|---|---|---|']
        for row in self.rows:
            r = row['record']
            rel = os.path.relpath(local(self.root, row['path']), local(self.root, self.config['overview']).parent).replace(os.sep, '/')
            title = '[' + text_cell(r['id']) + '](' + quote(rel, safe='/.-_') + ')'
            phase = STAGES[r['stage']]
            if r['stage'] == 'verified' and row['verification'] != '证据匹配':
                phase = '档案称已验证，待核对'
            values = [title, text_cell(r['title'] + ' / ' + r['module']), phase,
                      row['verification'], text_cell(r.get('blocker') or r.get('next', '')),
                      text_cell(', '.join(r['dependencies'])), text_cell(r.get('deployment', '未知') + ' / ' + r.get('customer_acceptance', '未知'))]
            rows.append('| ' + ' | '.join(values) + ' |')
        active = [x for x in self.rows if x['record']['scope'] == 'current' and x['record']['stage'] != 'cancelled']
        verified = sum(x['verification'] == '证据匹配' for x in active)
        cancelled = sum(x['record']['stage'] == 'cancelled' for x in self.rows)
        deferred = sum(x['record']['scope'] == 'deferred' and x['record']['stage'] != 'cancelled' for x in self.rows)
        rows += ['', f'本期 {len(active)} 片，{verified} 片证据匹配；取消 {cancelled} 片，延后 {deferred} 片。数量不是工期完成率。',
                 '仅包含配置登记的档案；未登记任务、远程链接及业务语义未被检查。', '']
        return '\n'.join(rows)

    @property
    def snapshot(self):
        return digest(canonical({p: digest(b) for p, b in sorted(self.files.items())}))

    def write(self, expected_snapshot=None):
        if self.fatal:
            raise ValueError('Malformed/ambiguous records: refusing to publish a partial overview')
        if expected_snapshot is not None and expected_snapshot != self.snapshot:
            raise ValueError('Expected snapshot mismatch; inspect again')
        if not self.stale:
            return False
        lock = self.root / '.thinstack-sync.lock'
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        temp = None
        try:
            # Cooperative writers are locked; arbitrary concurrent writers are detected best-effort.
            for p, original in self.files.items():
                if local(self.root, p).read_bytes() != original:
                    raise ValueError('Concurrent source change: ' + p)
            destination = local(self.root, self.config['overview'])
            fd, temp = tempfile.mkstemp(prefix='.thinstack-', dir=destination.parent)
            with os.fdopen(fd, 'wb') as output:
                output.write(self.expected_overview.encode('utf-8'))
                output.flush()
                os.fsync(output.fileno())
            os.chmod(temp, destination.stat().st_mode & 0o777)
            for p, original in self.files.items():
                if local(self.root, p).read_bytes() != original:
                    raise ValueError('Concurrent source change: ' + p)
            os.replace(temp, destination)
            temp = None
            return True
        finally:
            if temp is not None:
                Path(temp).unlink(missing_ok=True)
            lock.unlink(missing_ok=True)

    def report(self):
        return {'schema_version': 1, 'result': 'PROJECT_INVALID' if any(x['severity'] == 'error' for x in self.issues) else 'RECORDS_CONSISTENT',
                'meaning': '结构与显式来源一致性；不是产品 GREEN、真实执行认证或独立安全边界',
                'snapshot_sha256': self.snapshot, 'overview_stale': self.stale, 'issues': self.issues,
                'slices': [{'id': r['record']['id'], 'stage': r['record']['stage'], 'verification': r['verification'],
                            'contract_sha256': contract_digest(r['record']), 'path': r['path']} for r in self.rows]}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['doctor', 'sync'])
    p.add_argument('--root', required=True, type=Path)
    p.add_argument('--config', default='.thinstack.json')
    p.add_argument('--write', action='store_true', help='Only sync may replace its marked generated region')
    p.add_argument('--expect', help='Optional expected snapshot_sha256 from doctor')
    p.add_argument('--require-verified', action='append', default=[], metavar='SLICE_ID')
    p.add_argument('--json', action='store_true')
    args = p.parse_args(argv)
    if args.action != 'sync' and (args.write or args.expect):
        p.error('--write/--expect require sync')
    try:
        project = Project(args.root, args.config).inspect(args.require_verified)
        if args.action == 'sync':
            if args.write:
                project.write(args.expect)
                project = Project(args.root, args.config).inspect(args.require_verified)
            elif not args.json:
                print(''.join(difflib.unified_diff(project.overview.splitlines(True), project.expected_overview.splitlines(True), fromfile='current', tofile='proposed')), end='')
        report = project.report()
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(report['result'] + ': ' + report['meaning'])
            for issue in report['issues']:
                print(f"{issue['severity'].upper()} {issue['code']} {issue['path']}: {issue['message']}")
        return 1 if any(i['severity'] == 'error' for i in project.issues) else 0
    except (OSError, ValueError, UnicodeError, RecursionError) as exc:
        result = {'result': 'PROJECT_ERROR', 'message': str(exc)}
        print(json.dumps(result, ensure_ascii=False) if args.json else 'PROJECT_ERROR: ' + str(exc))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
