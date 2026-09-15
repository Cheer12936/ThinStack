"""Report static skill context sizes. Optional tokenizer is explicitly named, never guessed."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'skills/ts-code'


def report(root=ROOT, encoding=None):
    root = Path(root)
    groups = {'core': [root/'SKILL.md'], 'references': sorted((root/'references').glob('*.md')),
              'templates': sorted((root/'assets').glob('*.md')), 'tool_documentation': sorted((root/'scripts').glob('*.md'))}
    encoder = None
    if encoding:
        import tiktoken
        encoder = tiktoken.get_encoding(encoding)
    records = {}
    for group, paths in groups.items():
        records[group] = []
        for p in paths:
            text = p.read_text(encoding='utf-8')
            records[group].append({'path': p.relative_to(root).as_posix(), 'bytes': len(text.encode('utf-8')),
                                   'characters': len(text), 'tokens': len(encoder.encode(text)) if encoder else None})
    flat = [r for group in records.values() for r in group]
    return {'groups': records, 'encoding': encoding, 'total_bytes': sum(r['bytes'] for r in flat),
            'total_characters': sum(r['characters'] for r in flat),
            'total_tokens': sum(r['tokens'] for r in flat) if encoder else None,
            'meaning': 'Each static text loaded once; excludes tool output, code, project docs and repeated reads. Not a session worst-case or exact provider billing.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--encoding', help='Optional installed tiktoken encoding, not a model-name guess')
    a = p.parse_args()
    try:
        print(json.dumps(report(encoding=a.encoding), indent=2, ensure_ascii=False))
    except (OSError, ImportError, ValueError) as exc:
        p.exit(2, str(exc)+'\n')
