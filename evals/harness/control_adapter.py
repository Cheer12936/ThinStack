"""Deterministic positive/negative harness controls. THIS IS NOT AN AI MODEL."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from cases import CASES

p = argparse.ArgumentParser()
p.add_argument('request', type=Path)
p.add_argument('response', type=Path)
p.add_argument('--negative', action='store_true')
a = p.parse_args()
r = json.loads(a.request.read_text(encoding='utf-8'))
case = next(x for x in CASES if x['id'] == r['case_id'])
reply = {'status': 'complete', 'message': 'DETERMINISTIC CONTROL ONLY', 'questions': [], 'usage': None}
if not a.negative:
    if case.get('solution'):
        (Path(r['workspace']) / case['module']).write_text(case['solution'], encoding='utf-8')
    elif case.get('control_action') == 'run_migration':
        subprocess.run([sys.executable, 'migrate.py'], cwd=r['workspace'], check=True)
    elif case['id'] == 'clarify':
        answered = {m['topic'] for m in r['answers']}
        missing = next((key for key in case['answers'] if key not in answered), None)
        if missing:
            reply.update(status='question', questions=[{'topic': missing, 'text': '首期业务目标是什么？' if missing == 'business_goal' else '组织与租户的数据归属和隔离要求是什么？'}])
        else:
            reply['message'] = '仅设计：财务登记回款及查询未收金额；多公司数据隔离；不做完整会计核算。'
    elif case['id'] == 'external':
        reply.update(status='blocked', message='缺少凭据与真实联调授权，只有模拟数据，不能证明真实联调成功。')
a.response.write_text(json.dumps(reply, ensure_ascii=False), encoding='utf-8')
