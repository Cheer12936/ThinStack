"""Bridge an existing stdin-prompt/stdout-JSON agent command into the file protocol.

This is NOT a model or a tool-executing agent. The configured command must provide
its own coding tools, permissions, model choice and metering. No shell is used.
"""
import json
from pathlib import Path
import subprocess
import sys


def main():
    if len(sys.argv) < 5 or sys.argv[3] != '--':
        raise SystemExit('Usage: stdio_adapter.py REQUEST RESPONSE -- AGENT_EXECUTABLE [ARG ...]')
    request = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    response_path = Path(sys.argv[2])
    prompt = request['prompt'] + '\n\n工作目录：' + request['workspace']
    prompt += '\n已有用户回答：\n' + json.dumps(request['answers'], ensure_ascii=False)
    prompt += '\n此前交互：\n' + json.dumps(request['history'], ensure_ascii=False)
    result = subprocess.run(sys.argv[4:], input=prompt, text=True, encoding='utf-8',
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=request['workspace'], timeout=110)
    response_path.with_suffix('.stdout.txt').write_text(result.stdout, encoding='utf-8')
    response_path.with_suffix('.stderr.txt').write_text(result.stderr, encoding='utf-8')
    if result.returncode:
        raise SystemExit(result.returncode)
    text = result.stdout.strip()
    if text.startswith('```json') and text.endswith('```'):
        text = text[7:-3].strip()
    data = json.loads(text)  # Fail visibly on vendor streaming envelopes; never fabricate a reply.
    response_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')


if __name__ == '__main__':
    main()
