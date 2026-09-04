"""Standalone SRT timing demo, adapted from a generic caption-offset operation."""
import argparse
import re
from pathlib import Path

STAMP = r'\d{2,}:\d{2}:\d{2},\d{3}'
TIMELINE = re.compile(rf'^({STAMP}) --> ({STAMP})$')


def milliseconds(stamp):
    h, m, rest = stamp.split(':')
    s, ms = rest.split(',')
    if int(m) >= 60 or int(s) >= 60:
        raise ValueError('invalid minutes or seconds')
    return ((int(h) * 60 + int(m)) * 60 + int(s)) * 1000 + int(ms)


def format_stamp(value):
    h, value = divmod(value, 3600000)
    m, value = divmod(value, 60000)
    s, ms = divmod(value, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'


def parse_srt(text):
    cues = []
    last_start = -1
    text = text.lstrip('\ufeff').replace('\r\n', '\n').strip()
    if not text:
        raise ValueError('SRT is empty')
    for index, block in enumerate(re.split(r'\n\s*\n', text), 1):
        lines = block.splitlines()
        if len(lines) < 3 or not lines[0].isdigit():
            raise ValueError(f'cue {index}: expected number, timestamps and text')
        match = TIMELINE.fullmatch(lines[1])
        if not match:
            raise ValueError(f'cue {index}: invalid timeline')
        start, end = map(milliseconds, match.groups())
        if end <= start or start < last_start:
            raise ValueError(f'cue {index}: invalid time ordering')
        last_start = start
        cues.append({'id': lines[0], 'start': start, 'end': end, 'text': '\n'.join(lines[2:])})
    return cues


def shift_srt(text, offset):
    shift = round(offset * 1000)
    blocks = []
    for cue in parse_srt(text):
        start, end = cue['start'] + shift, cue['end'] + shift
        if start < 0:
            raise ValueError(f"cue {cue['id']}: offset produces a negative timestamp")
        blocks.append(f"{cue['id']}\n{format_stamp(start)} --> {format_stamp(end)}\n{cue['text']}")
    return '\n\n'.join(blocks) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--offset', required=True, type=float)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error('use a distinct output path')
    result = shift_srt(args.input.read_text(encoding='utf-8-sig'), args.offset)
    args.output.write_text(result, encoding='utf-8')
    print(f"Wrote {len(parse_srt(result))} cue(s)")


if __name__ == '__main__':
    main()
