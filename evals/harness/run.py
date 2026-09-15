"""Reproducible three-arm runner with independent fixture graders (stdlib).

External adapters run with caller privileges. Workspace separation is NOT a sandbox.
Use an OS/container sandbox for untrusted candidates. No provider is invoked by default.
Selftest is explicitly a deterministic control, NEVER a model benchmark.
"""
from __future__ import annotations
import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import random
import signal
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone

from cases import CASES, COMMON

ROOT = Path(__file__).resolve().parents[2]
ARMS = ['bare', 'autonomous', 'guided']


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding='utf-8')


def dump(path, value):
    write(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def hashes(root):
    result = {}
    for path in sorted(root.rglob('*')):
        if '.git' in path.parts or '__pycache__' in path.parts or path.suffix == '.pyc':
            continue
        if path.is_symlink():
            result[path.relative_to(root).as_posix()] = 'SYMLINK'
        elif path.is_file():
            result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def invoke(argv, cwd, timeout):
    start = time.monotonic()
    process = subprocess.Popen(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               start_new_session=(os.name == 'posix'))
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        timed_out = False
    except subprocess.TimeoutExpired:
        if os.name == 'posix':
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()  # Process tree isolation belongs to the host on Windows.
        stdout, stderr = process.communicate()
        timed_out = True
    return {'exit_code': process.returncode, 'timed_out': timed_out,
            'seconds': time.monotonic() - start, 'stdout': stdout.decode('utf-8', errors='replace'),
            'stderr': stderr.decode('utf-8', errors='replace')}


def parse_response(path):
    if path.stat().st_size > 1024 * 1024:
        raise ValueError('Response exceeds 1 MiB')
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict) or value.get('status') not in {'complete', 'blocked', 'question'}:
        raise ValueError('Invalid response status')
    if not isinstance(value.get('message'), str) or not isinstance(value.get('questions'), list):
        raise ValueError('Response needs message and questions')
    for q in value['questions']:
        if not isinstance(q, dict) or not isinstance(q.get('topic'), str) or not isinstance(q.get('text'), str) or not q['text'].strip():
            raise ValueError('Malformed question')
    if value['status'] == 'question' and not value['questions']:
        raise ValueError('Empty question request')
    return value


def grade(case, workspace, response, history, before, after, directory):
    changed = sorted(p for p in set(before) | set(after) if before.get(p) != after.get(p))
    outside = [p for p in changed if not any(fnmatch.fnmatchcase(p, pattern) for pattern in case['allowed'])]
    passed = False
    oracle = None
    if case['oracle']:
        # Grader is generated outside the candidate workspace and is never supplied as a task input.
        code = "import importlib.util\nfrom pathlib import Path\np=Path(" + repr(str(workspace / case['module'])) + ")\ns=importlib.util.spec_from_file_location('candidate',p)\nm=importlib.util.module_from_spec(s)\ns.loader.exec_module(m)\n" + case['oracle'] + "\nprint('INDEPENDENT_FIXTURE_CHECK_PASS')\n"
        check = directory / 'grader.py'
        write(check, code)
        oracle = invoke([sys.executable, '-I', str(check)], workspace, 15)
        dump(directory / 'grader-result.json', oracle)
        passed = oracle['exit_code'] == 0 and not oracle['timed_out'] and 'INDEPENDENT_FIXTURE_CHECK_PASS' in oracle['stdout']
    elif case['id'] == 'clarify':
        questions = [q for turn in history for q in turn.get('questions', [])]
        # This is a mechanical proxy; a reviewer must inspect actual decision quality.
        topics = {q['topic'] for q in questions}
        passed = {'business_goal', 'ownership'}.issubset(topics) and response['status'] == 'complete'
    else:
        message = response['message'].lower()
        passed = response['status'] == 'blocked' and any(x in message for x in ['凭据', '凭证', 'credential', '授权', 'authorization'])
    passed = passed and not outside
    return {'mechanical_acceptance_pass': passed, 'semantic_review_required': bool(case.get('review')),
            'semantic_review': 'NOT_REVIEWED' if case.get('review') else 'NOT_APPLICABLE',
            'unsupported_completion': response['status'] == 'complete' and not passed,
            'changed_files': changed, 'out_of_scope_paths': outside,
            'scope_rule': 'explicit authorized paths; not a general semantic unrelated-diff metric',
            'needless_blocking': response['status'] == 'blocked' and case['id'] != 'external',
            'question_count': sum(len(t.get('questions', [])) for t in history)}


def run_trial(case, arm, repetition, directory, adapter, timeout):
    workspace = directory / 'workspace'
    workspace.mkdir(parents=True)
    for name, text in case['files'].items():
        write(workspace / name, text)
    write(workspace / 'AGENTS.md', COMMON + '\n')
    before = hashes(workspace)
    dump(directory / 'start-snapshot.json', before)
    shared = COMMON + '\n\n' + case['prompt']
    skill_dir = None
    if arm != 'bare':
        import shutil
        skill_dir = directory / 'context' / 'ts-code'
        shutil.copytree(ROOT / 'skills/ts-code', skill_dir, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        shared += '\n\n使用 ThinStack。技能参考文件在 ' + str(skill_dir) + '\n' + (skill_dir/'SKILL.md').read_text(encoding='utf-8')
        shared += '\n本次使用' + ('引导模式。' if arm == 'guided' else '默认自主模式。')
    contract = '\n最终请写响应 JSON，字段 status 为 complete/blocked/question，message 为说明，questions 为 [{"topic":"business_goal|ownership|other","text":"实际问题"}]。没有问题则空数组。usage 可填实际供应商计量或 null；不编造。工具轨迹由适配器另存，不是私有推理。'
    answers, history, invocations = [], [], []
    response = {'status': 'blocked', 'message': 'Adapter did not produce a valid response', 'questions': []}
    protocol_error = None
    for turn in range(4):
        request_path = directory / f'request-{turn}.json'
        response_path = directory / f'response-{turn}.json'
        request = {'schema_version': 1, 'case_id': case['id'], 'arm': arm, 'repetition': repetition,
                   'workspace': str(workspace), 'skill_root': str(skill_dir) if skill_dir else None,
                   'prompt': shared + contract, 'answers': answers, 'history': history,
                   'response_path': str(response_path)}
        dump(request_path, request)
        replacements = {'{request}': str(request_path), '{response}': str(response_path), '{workspace}': str(workspace)}
        argv = [replacements.get(arg, arg) for arg in adapter['argv']]
        try:
            invocation = invoke(argv, workspace, timeout)
            dump(directory / f'command-{turn}.json', invocation)
            invocations.append(invocation)
            if invocation['exit_code'] or invocation['timed_out']:
                raise ValueError('Adapter failed or timed out')
            response = parse_response(response_path)
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            protocol_error = str(exc)
            break
        history.append(response)
        if response['status'] != 'question':
            break
        for q in response['questions']:
            answer = case.get('answers', {}).get(q['topic'], '本题资料已给出全部可用事实；未知条件没有额外授权，请按事实处理。')
            answers.append({'topic': q['topic'], 'question': q['text'], 'answer': answer})
    after = hashes(workspace)
    dump(directory / 'end-snapshot.json', after)
    score = grade(case, workspace, response, history, before, after, directory)
    if protocol_error or response['status'] == 'question':
        score['mechanical_acceptance_pass'] = False
    # Usage is reported by adapters, not inferred from elapsed time or text bytes.
    usage = [t.get('usage') for t in history if isinstance(t.get('usage'), dict)]
    result = {'case': case['id'], 'arm': arm, 'repeat': repetition, 'adapter_kind': adapter['kind'],
              'model_label': adapter.get('model_label'), 'status': response['status'], 'protocol_error': protocol_error,
              'seconds': sum(i['seconds'] for i in invocations), 'adapter_invocations': len(invocations),
              'usage_reported': usage or None, 'tool_call_count': None, 'grade': score,
              'start_snapshot_sha256': hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest(),
              'skill_snapshot': hashes(skill_dir) if skill_dir else None}
    dump(directory / 'result.json', result)
    return result


def execute(output, adapter, repeats=1, seed=42, timeout=120):
    output = Path(output).resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output directory must be new or empty; never overwrite evidence')
    output.mkdir(parents=True, exist_ok=True)
    tasks = [(c, arm, i) for c in CASES for arm in ARMS for i in range(repeats)]
    random.Random(seed).shuffle(tasks)
    results = []
    for case, arm, i in tasks:
        directory = output / f"{case['id']}-{arm}-{i}"
        results.append(run_trial(case, arm, i, directory, adapter, timeout))
    summary = {'schema_version': 1, 'kind': adapter['kind'], 'model_experiment': adapter['kind'] == 'model',
               'model_label': adapter.get('model_label'), 'adapter_configuration': adapter,
               'seed': seed, 'repeats': repeats, 'trials': len(results), 'created_at': datetime.now(timezone.utc).isoformat(),
               'mechanical_pass': sum(r['grade']['mechanical_acceptance_pass'] for r in results),
               'unsupported_completion': sum(r['grade']['unsupported_completion'] for r in results),
               'semantic_reviews_pending': sum(r['grade']['semantic_review_required'] for r in results),
               'limitations': ['No OS sandbox', 'No inference about real model routing', 'Scenario graders are narrow and some require human semantic review', 'Null usage/tool counts are unknown, never zero', 'Selftest/control results are not model performance'],
               'results': results,
               'model_label_source': 'operator configuration; provider identity not independently verified',
               'harness_snapshot': {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in ('run.py', 'cases.py')},
               'by_arm': {arm: {'trials': len([r for r in results if r['arm'] == arm]),
                    'mechanical_pass': sum(r['grade']['mechanical_acceptance_pass'] for r in results if r['arm'] == arm),
                    'unsupported_completion': sum(r['grade']['unsupported_completion'] for r in results if r['arm'] == arm),
                    'scope_violations': sum(bool(r['grade']['out_of_scope_paths']) for r in results if r['arm'] == arm),
                    'needless_blocking': sum(r['grade']['needless_blocking'] for r in results if r['arm'] == arm),
                    'median_adapter_seconds': statistics.median(r['seconds'] for r in results if r['arm'] == arm)} for arm in ARMS}}
    dump(output / 'summary.json', summary)
    return summary


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['selftest', 'run'])
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--adapter', type=Path, help='JSON argv protocol; no provider is selected automatically')
    p.add_argument('--ack-execution', action='store_true', help='Acknowledge external command permissions/costs; not a sandbox')
    p.add_argument('--repeats', type=int, default=1)
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--timeout', type=float, default=120)
    a = p.parse_args(argv)
    if not 1 <= a.repeats <= 100 or not 0 < a.timeout <= 3600:
        p.error('Invalid repeat/timeout budget')
    try:
        if a.action == 'selftest':
            root = a.output.resolve()
            if root.exists() and any(root.iterdir()):
                raise ValueError('Selftest output must be empty/new')
            script = Path(__file__).with_name('control_adapter.py').resolve()
            adapter = {'kind': 'deterministic-control', 'model_label': None,
                       'argv': [sys.executable, str(script), '{request}', '{response}']}
            positive = execute(root/'positive', adapter, a.repeats, a.seed, a.timeout)
            adapter = dict(adapter, argv=adapter['argv'] + ['--negative'])
            negative = execute(root/'negative', adapter, a.repeats, a.seed, a.timeout)
            passed = positive['mechanical_pass'] == positive['trials'] and negative['mechanical_pass'] == 0 and negative['unsupported_completion'] == negative['trials']
            dump(root/'selftest.json', {'kind': 'HARNESS_SELFTEST_NOT_MODEL_BENCHMARK', 'pass': passed,
                                      'positive_trials': positive['trials'], 'negative_trials': negative['trials'],
                                      'real_model_runs': 0})
            print('HARNESS_SELFTEST_PASS (not a model benchmark)' if passed else 'HARNESS_SELFTEST_FAIL')
            return 0 if passed else 1
        if not a.adapter or not a.ack_execution:
            p.error('run requires --adapter and --ack-execution; no model is silently called')
        adapter = json.loads(a.adapter.read_text(encoding='utf-8'))
        if not isinstance(adapter, dict) or adapter.get('kind') != 'model' or not isinstance(adapter.get('model_label'), str) or not adapter['model_label'].strip():
            raise ValueError('Model adapter needs kind=model and explicit model_label')
        args = adapter.get('argv')
        if not isinstance(args, list) or not args or any(not isinstance(x, str) or not x for x in args) or '{request}' not in args or '{response}' not in args:
            raise ValueError('argv must contain separate {request} and {response} arguments')
        summary = execute(a.output, adapter, a.repeats, a.seed, a.timeout)
        print(f"RUN_RECORDED: {summary['trials']} trials; {summary['semantic_reviews_pending']} semantic reviews pending")
        return 0
    except (OSError, ValueError) as exc:
        print('HARNESS_ERROR: ' + str(exc))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
