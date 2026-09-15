"""Create an isolated demo, really run its three tests, bind evidence and sync.

This demonstrates record plumbing on a toy program, not a client project's delivery.
No network, credentials, production operations or installation changes.
"""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('project_state', ROOT/'skills/ts-code/scripts/project_state.py')
ps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ps)


def put(root, name, text):
    p = root/name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path, help='New or empty demo directory only')
    args = parser.parse_args()
    root = args.root.resolve()
    if root.exists() and any(root.iterdir()):
        parser.error('Refusing to overwrite a nonempty project')
    root.mkdir(parents=True, exist_ok=True)
    put(root, 'app.py', 'def remaining(total, paid):\n    return total - paid\n')
    put(root, 'test_app.py', 'import unittest\nfrom app import remaining\nclass Tests(unittest.TestCase):\n    def test_partial(self): self.assertEqual(remaining(1000,200),800)\n    def test_full(self): self.assertEqual(remaining(10,10),0)\n    def test_empty(self): self.assertEqual(remaining(0,0),0)\n')
    put(root, 'docs/BASELINE.md', '# Toy arithmetic\nOnly integer subtraction, no payments or persistence.\n')
    put(root, 'docs/SLICES.md', '# 演示总览\n\n这里的客户说明不会被覆盖。\n\n'+ps.BEGIN+'\n'+ps.END+'\n')
    cfg = {'schema_version':1, 'overview':'docs/SLICES.md', 'records':['docs/slices/001.md'], 'baselines':['docs/BASELINE.md']}
    put(root, '.thinstack.json', json.dumps(cfg, indent=2))
    r = {'schema_version':1,'id':'S-001','title':'演示整数余额计算','type':'technical','module':'arithmetic',
         'stage':'verify','scope':'current','dependencies':[],'blocker':'','next':'检查演示结果',
         'approval':{'state':'approved','source':'Explicit local toy demo specification; not customer approval'},
         'acceptance':[{'id':'AC-1','text':'整数 total-paid 对部分/全部/零值成立','kinds':['runtime']}],
         'inputs':['app.py','test_app.py'], 'baseline_refs':{'docs/BASELINE.md':ps.digest((root/'docs/BASELINE.md').read_bytes())},
         'evidence':'reports/evidence.json','deployment':'未部署','customer_acceptance':'不适用：工具演示'}
    command = [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', '.', '-p', 'test_app.py', '-v']
    result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=30)
    log = result.stdout + result.stderr
    put(root, 'reports/tests.log', log)
    passed = result.returncode == 0 and 'Ran 3 tests' in log and 'OK' in log
    r['stage'] = 'verified' if passed else 'verify'
    e = {'schema_version':1,'scope':'S-001','slice_id':'S-001','contract_sha256':ps.contract_digest(r),
         'verdict':'GREEN' if passed else 'NOT_GREEN','required':['AC-1'],
         'snapshot':{p:ps.digest((root/p).read_bytes()) for p in r['inputs']+list(r['baseline_refs'])},
         'checks':[{'covers':['AC-1'],'status':'pass' if passed else 'fail','kind':'runtime',
                    'method':json.dumps(command),'observed_at':datetime.now(timezone.utc).isoformat(),
                    'environment':'isolated local toy demo; '+sys.version.split()[0], 'artifact':'reports/tests.log',
                    'sha256':ps.digest((root/'reports/tests.log').read_bytes())}], 'unresolved_high_risks':[]}
    put(root, r['evidence'], json.dumps(e, indent=2, ensure_ascii=False))
    put(root, 'docs/slices/001.md', '# 演示切片\n\n```thinstack-slice\n'+json.dumps(r,ensure_ascii=False,indent=2)+'\n```\n\n## 历史\n仅本地算术测试，不代表财务系统交付。\n')
    ps.Project(root).inspect().write()
    report=ps.Project(root).inspect(['S-001']).report()
    put(root, 'reports/doctor.json', json.dumps(report,indent=2,ensure_ascii=False))
    print(report['result'] + '; toy tests actually run; not client delivery')
    return 0 if passed and report['result']=='RECORDS_CONSISTENT' else 1


if __name__ == '__main__':
    raise SystemExit(main())
