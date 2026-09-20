"""Run one harness request through an installed Codex CLI in an isolated workspace."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


def usage_from_events(text):
    usage = None
    for line in text.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict) and isinstance(event.get('usage'), dict):
            usage = event['usage']
        payload = event.get('turn') if isinstance(event, dict) else None
        if isinstance(payload, dict) and isinstance(payload.get('usage'), dict):
            usage = payload['usage']
    return usage


def command(model, thinking, output, schema):
    return ['codex', 'exec', '--ignore-user-config', '--ignore-rules',
            '--enable', 'skip_host_skill_discovery', '--ephemeral',
            '--skip-git-repo-check', '--approve-for-me',
            '--output-schema', str(schema), '--output-last-message', str(output),
            '--color', 'never', '--json', '-m', model,
            '-c', f'model_reasoning_effort="{thinking}"', '-']


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('request', type=Path)
    parser.add_argument('response', type=Path)
    parser.add_argument('--model', required=True)
    parser.add_argument('--thinking', default='medium', choices=['low', 'medium', 'high', 'xhigh', 'max', 'ultra'])
    parser.add_argument('--timeout', type=float, default=900)
    args = parser.parse_args(argv)
    request = json.loads(args.request.read_text(encoding='utf-8'))
    workspace = Path(request['workspace']).resolve()
    if not workspace.is_dir():
        parser.error('Request workspace does not exist')
    prompt = request['prompt'] + '\n\n已有用户回答：\n' + json.dumps(request['answers'], ensure_ascii=False)
    prompt += '\n此前交互：\n' + json.dumps(request['history'], ensure_ascii=False)
    prompt += '\n只在给定工作区内工作；最终严格返回请求规定的 JSON 对象。'
    raw = args.response.with_suffix('.codex.jsonl')
    last = args.response.with_suffix('.codex-final.json')
    schema = Path(__file__).with_name('response-schema.json').resolve()
    result = subprocess.run(command(args.model, args.thinking, last, schema), input=prompt,
                            text=True, encoding='utf-8', stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, cwd=workspace, timeout=args.timeout)
    raw.write_text(result.stdout, encoding='utf-8')
    args.response.with_suffix('.codex.stderr.txt').write_text(result.stderr, encoding='utf-8')
    if result.returncode:
        raise SystemExit(result.returncode)
    response = json.loads(last.read_text(encoding='utf-8'))
    response['usage'] = usage_from_events(result.stdout)
    args.response.write_text(json.dumps(response, ensure_ascii=False), encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
