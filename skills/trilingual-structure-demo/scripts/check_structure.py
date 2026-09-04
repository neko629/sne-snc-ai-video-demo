"""Generic three-line block validator, adapted from a production structure check."""
import argparse
import json
import re
import sys
from pathlib import Path


def check(text):
    text = text.lstrip('\ufeff').replace('\r\n', '\n').strip()
    blocks = re.split(r'\n\s*\n', text) if text else []
    errors = []
    if not blocks:
        errors.append({'block': 0, 'reason': 'empty input'})
    for index, block in enumerate(blocks, 1):
        lines = block.splitlines()
        if len(lines) != 3 or any(not line.strip() for line in lines):
            errors.append({'block': index, 'reason': 'expected three nonempty lines'})
            continue
        chinese = re.sub(r'^[^:：]{1,30}[:：]', '', lines[0]).strip()
        expected = sum('\u4e00' <= c <= '\u9fff' for c in chinese)
        expected += len(re.findall(r'[A-Za-z]+', chinese))
        actual = len(lines[1].split())
        if expected == 0 or expected != actual:
            errors.append({'block': index, 'reason': 'token count mismatch',
                           'expected': expected, 'actual': actual})
    return {'blocks': len(blocks), 'valid': not errors, 'errors': errors}


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    args = parser.parse_args()
    report = check(args.input.read_text(encoding='utf-8-sig'))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['valid'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
