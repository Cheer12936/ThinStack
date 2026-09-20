"""Project data consistency tests; not a model evaluation or execution attestation."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/ts-code/scripts/project_state.py'
spec = importlib.util.spec_from_file_location('project_state', SCRIPT)
ps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ps)


def put(root, path, content):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding='utf-8')


def fixture(root):
    put(root, 'app.py', 'VALUE = 1\n')
    put(root, 'test_app.py', 'assert True\n')
    put(root, 'docs/BASELINE.md', '# Rules\n\nData belongs to the current tenant.\n')
    put(root, 'docs/SLICES.md', '# Demo\n\nCustomer text: preserve me.\n\n' + ps.BEGIN + '\n' + ps.END + '\n\nFooter stays.\n')
    cfg = {'schema_version': 1, 'overview': 'docs/SLICES.md', 'records': ['docs/slices/001.md'], 'baselines': ['docs/BASELINE.md']}
    put(root, '.thinstack.json', json.dumps(cfg))
    r = {'schema_version': 1, 'id': 'S-001', 'title': 'Create item', 'type': 'business',
         'module': 'inventory', 'stage': 'planned', 'scope': 'current', 'dependencies': [],
         'blocker': '', 'next': 'Implement and verify', 'approval': {'state': 'approved', 'source': 'fixture approval; not a real customer'},
         'acceptance': [{'id': 'AC-1', 'text': 'Value equals 1', 'kinds': ['runtime']}],
         'inputs': ['app.py', 'test_app.py'], 'baseline_refs': {'docs/BASELINE.md': ps.digest((root/'docs/BASELINE.md').read_bytes())},
         'evidence': '', 'deployment': '未部署', 'customer_acceptance': '未验收'}
    save_record(root, r)
    return r


def save_record(root, record):
    put(root, 'docs/slices/001.md', '# Slice\n\n```thinstack-slice\n' + json.dumps(record, ensure_ascii=False, indent=2) + '\n```\n\n## Notes\nPersistent history.\n')


def evidence(root, record):
    # Deliberately synthetic integrity fixture; these tests do not claim genuine execution.
    put(root, 'reports/test.log', 'SYNTHETIC CONTROL: PASS AC-1\n')
    record['evidence'] = 'reports/evidence.json'
    record['stage'] = 'verified'
    payload = {'schema_version': 1, 'scope': 'S-001', 'slice_id': 'S-001', 'contract_sha256': ps.contract_digest(record),
               'verdict': 'GREEN', 'required': ['AC-1'],
               'snapshot': {p: ps.digest((root/p).read_bytes()) for p in record['inputs'] + list(record['baseline_refs'])},
               'checks': [{'covers': ['AC-1'], 'status': 'pass', 'kind': 'runtime', 'method': 'synthetic fixture',
                           'observed_at': '2026-09-15T00:00:00Z', 'environment': 'unit fixture',
                           'artifact': 'reports/test.log', 'sha256': ps.digest((root/'reports/test.log').read_bytes())}],
               'unresolved_high_risks': []}
    save_record(root, record)
    put(root, record['evidence'], json.dumps(payload))
    return payload


class ProjectTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.r = fixture(self.root)

    def project(self, required=()):
        return ps.Project(self.root).inspect(required)

    def codes(self, p=None):
        return {x['code'] for x in (p or self.project()).issues}

    def save_ev(self, e):
        put(self.root, self.r['evidence'], json.dumps(e))

    def test_doctor_is_read_only_and_reports_staleness(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertIn('overview_stale', self.codes())
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_sync_idempotent_and_preserves_user_text(self):
        p = self.project()
        self.assertTrue(p.write())
        p = self.project()
        self.assertFalse(p.stale)
        self.assertFalse(p.write())
        self.assertIn('Customer text: preserve me.', p.overview)
        self.assertIn('Footer stays.', p.overview)

    def test_valid_bound_evidence(self):
        evidence(self.root, self.r)
        self.project().write()
        p = self.project(['S-001'])
        self.assertEqual(p.rows[0]['verification'], '证据匹配')
        self.assertFalse(p.issues)

    def test_progress_update_does_not_invalidate_contract(self):
        evidence(self.root, self.r)
        self.r['next'] = 'Show the demo'
        save_record(self.root, self.r)
        self.assertEqual(self.project().rows[0]['verification'], '证据匹配')

    def test_manual_green_rejected(self):
        self.r['stage'] = 'verified'
        save_record(self.root, self.r)
        self.assertIn('unsupported_completion', self.codes())

    def test_formal_criterion_cannot_be_omitted_by_report(self):
        evidence(self.root, self.r)
        self.r['acceptance'].append({'id': 'AC-2', 'text': 'No unauthorized access', 'kinds': ['runtime']})
        save_record(self.root, self.r)
        self.assertIn('evidence_invalid', self.codes())

    def test_changed_acceptance_text_same_id_invalidates(self):
        evidence(self.root, self.r)
        self.r['acceptance'][0]['text'] = 'Value equals 2'
        save_record(self.root, self.r)
        self.assertIn('evidence_invalid', self.codes())

    def test_wrong_slice_rejected(self):
        e = evidence(self.root, self.r)
        e['slice_id'] = 'S-002'
        self.save_ev(e)
        self.assertIn('evidence_invalid', self.codes())

    def test_mock_cannot_stand_for_runtime(self):
        e = evidence(self.root, self.r)
        e['checks'][0]['kind'] = 'mock'
        self.save_ev(e)
        self.assertIn('evidence_invalid', self.codes())

    def test_source_change(self):
        evidence(self.root, self.r)
        put(self.root, 'app.py', 'VALUE = 2\n')
        self.assertIn('evidence_invalid', self.codes())

    def test_test_change(self):
        evidence(self.root, self.r)
        put(self.root, 'test_app.py', 'assert False\n')
        self.assertIn('evidence_invalid', self.codes())

    def test_baseline_change(self):
        evidence(self.root, self.r)
        put(self.root, 'docs/BASELINE.md', '# Different rules\n')
        self.assertIn('baseline_changed', self.codes())
        self.assertIn('evidence_invalid', self.codes())

    def test_omitted_declared_input(self):
        e = evidence(self.root, self.r)
        del e['snapshot']['test_app.py']
        self.save_ev(e)
        self.assertIn('evidence_invalid', self.codes())

    def test_failed_skipped_and_missing_checks(self):
        for status in ['fail', 'skipped']:
            e = evidence(self.root, self.r)
            e['checks'][0]['status'] = status
            self.save_ev(e)
            with self.subTest(status=status):
                self.assertIn('evidence_invalid', self.codes())

    def test_honest_not_green_is_valid_but_not_verified(self):
        e = evidence(self.root, self.r)
        e['verdict'] = 'NOT_GREEN'
        e['checks'][0]['status'] = 'fail'
        self.r['stage'] = 'verify'
        save_record(self.root, self.r)
        self.save_ev(e)
        p = self.project(['S-001'])
        self.assertEqual(p.rows[0]['verification'], '失败')
        self.assertIn('required_slice_unverified', self.codes(p))

    def test_duplicate_ids(self):
        path = self.root/'docs/slices/001.md'
        path.write_bytes(path.read_bytes() * 2)
        p = self.project()
        self.assertTrue(p.fatal)
        with self.assertRaises(ValueError):
            p.write()

    def test_missing_dependency(self):
        self.r['dependencies'] = ['S-999']
        save_record(self.root, self.r)
        self.assertIn('dependency_missing', self.codes())

    def test_cycle(self):
        self.r['dependencies'] = ['S-001']
        save_record(self.root, self.r)
        self.assertIn('dependency_cycle', self.codes())

    def test_missing_local_link(self):
        path = self.root/'docs/slices/001.md'
        path.write_text(path.read_text(encoding='utf-8') + '\n[bad](missing.md)\n', encoding='utf-8')
        self.assertIn('dead_link', self.codes())

    def test_explicit_anchor(self):
        put(self.root, 'docs/BASELINE.md', '<a id="rules"></a>\n# Rules\n')
        path = self.root/'docs/slices/001.md'
        path.write_text(path.read_text(encoding='utf-8') + '\n[good](../BASELINE.md#rules)\n', encoding='utf-8')
        self.assertNotIn('dead_link', self.codes())
        self.assertNotIn('anchor_unresolved', self.codes())

    def test_legacy_record_is_not_silently_parsed(self):
        put(self.root, 'docs/slices/001.md', '# Old SPEC\nDone!\n')
        self.assertIn('unstructured_record', self.codes())

    def test_unconfigured_is_error(self):
        (self.root/'.thinstack.json').unlink()
        with self.assertRaises(ValueError):
            self.project()

    def test_duplicate_json_keys(self):
        put(self.root, 'docs/slices/001.md', '```thinstack-slice\n{"id":"A", "id":"B"}\n```\n')
        self.assertIn('record_invalid', self.codes())

    def test_non_finite_numbers(self):
        with self.assertRaises(ValueError):
            ps.load_json('{"cost": NaN}')

    def test_unknown_field_typo(self):
        self.r['stgae'] = 'verified'
        save_record(self.root, self.r)
        self.assertIn('record_invalid', self.codes())

    def test_no_overview_markers(self):
        put(self.root, 'docs/SLICES.md', '# Handwritten overview\n')
        with self.assertRaises(ValueError):
            self.project()

    def test_concurrent_record_change(self):
        p = self.project()
        self.r['next'] = 'Another writer changed this'
        save_record(self.root, self.r)
        with self.assertRaises(ValueError):
            p.write()
        self.assertFalse((self.root/'.thinstack-sync.lock').exists())

    def test_wrong_snapshot(self):
        with self.assertRaises(ValueError):
            self.project().write('0'*64)

    def test_symlink_and_escape(self):
        with self.assertRaises(ValueError):
            ps.local(self.root, '../outside.md')
        with self.assertRaises(ValueError):
            ps.local(self.root, '/tmp/absolute.md')
        try:
            (self.root/'alias.py').symlink_to(self.root/'app.py')
        except OSError:
            self.skipTest('Symlinks unavailable')
        with self.assertRaises(ValueError):
            ps.local(self.root, 'alias.py')

    def test_table_injection_escaped(self):
        self.r['title'] = 'bad|row\n[click](javascript:x)<script>'
        save_record(self.root, self.r)
        g = self.project().generated
        self.assertNotIn('<script>', g)
        self.assertNotIn('[click]', g)
        self.assertIn('&#124;', g)

    def test_cancelled_record_retained_and_excluded(self):
        self.r['stage'] = 'cancelled'
        save_record(self.root, self.r)
        g = self.project().generated
        self.assertIn('本期 0 片', g)
        self.assertIn('取消 1 片', g)
        self.assertIn('S-001', g)

    def test_invalid_evidence_can_render_honest_status(self):
        evidence(self.root, self.r)
        put(self.root, 'app.py', 'VALUE = 9\n')
        self.project().write()
        self.assertIn('需重验', (self.root/'docs/SLICES.md').read_text(encoding='utf-8'))

    def test_crlf_records(self):
        p = self.root/'docs/slices/001.md'
        p.write_bytes(p.read_bytes().replace(b'\r\n', b'\n').replace(b'\n', b'\r\n'))
        self.assertNotIn('unstructured_record', self.codes())

    def test_normalized_config_paths_are_idempotent(self):
        p = self.root/'.thinstack.json'
        cfg = json.loads(p.read_text())
        cfg['overview'] = './docs/SLICES.md'
        p.write_text(json.dumps(cfg))
        self.project().write()
        self.assertFalse(self.project().stale)

    def test_cli_check_then_sync(self):
        args = [sys.executable, '-B', str(SCRIPT)]
        p = subprocess.run(args + ['doctor', '--root', str(self.root), '--json'], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(p.returncode, 1)
        self.assertEqual(json.loads(p.stdout)['result'], 'PROJECT_INVALID')
        p = subprocess.run(args + ['sync', '--root', str(self.root), '--write'], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(p.returncode, 0, p.stdout+p.stderr)


class SliceRegistrationTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)

    def test_first_add_initializes_fixed_project_structure(self):
        result = ps.register_slice(
            self.root, title='登记回款', goal='财务人员可以登记客户回款',
            module='receivables', acceptance=['登记后未收金额减少'],
            evidence_kinds=['runtime'])
        self.assertEqual(result['id'], 'S-001')
        self.assertEqual(result['path'], 'docs/slices/S-001.md')
        self.assertTrue((self.root/'docs/SLICES.md').is_file())
        self.assertTrue((self.root/'docs/architecture/BASELINE.md').is_file())
        cfg = json.loads((self.root/'.thinstack.json').read_text(encoding='utf-8'))
        self.assertEqual(cfg['records'], ['docs/slices/S-001.md'])
        self.assertIn('## 目标\n\n财务人员可以登记客户回款', (self.root/'docs/slices/S-001.md').read_text(encoding='utf-8'))
        project = ps.Project(self.root).inspect()
        self.assertEqual(project.rows[0]['record']['acceptance'][0]['text'], '登记后未收金额减少')
        self.assertFalse(project.stale)

    def test_add_uses_next_stable_id_and_preserves_existing_record(self):
        fixture(self.root)
        before = (self.root/'docs/slices/001.md').read_bytes()
        result = ps.register_slice(
            self.root, title='查询未收款', goal='财务人员可以查询未收款',
            module='receivables', dependencies=['S-001'])
        self.assertEqual(result['id'], 'S-002')
        self.assertEqual((self.root/'docs/slices/001.md').read_bytes(), before)
        self.assertTrue((self.root/'docs/slices/S-002.md').is_file())
        project = ps.Project(self.root).inspect()
        self.assertEqual([row['record']['id'] for row in project.rows], ['S-001', 'S-002'])

    def test_add_rejects_unknown_dependency_without_writes(self):
        with self.assertRaises(ValueError):
            ps.register_slice(self.root, title='导出', goal='导出对账单',
                              module='reporting', dependencies=['S-999'])
        self.assertFalse((self.root/'.thinstack.json').exists())

    def test_approved_add_requires_source(self):
        with self.assertRaises(ValueError):
            ps.register_slice(self.root, title='导出', goal='导出对账单',
                              module='reporting', approval_state='approved')

    def test_cli_add_registers_slice(self):
        args = [sys.executable, '-B', str(SCRIPT), 'add', '--root', str(self.root),
                '--title', '客户对账单', '--goal', '财务人员导出未收款明细',
                '--module', 'reporting', '--json']
        result = subprocess.run(args, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['id'], 'S-001')


if __name__ == '__main__':
    unittest.main()
