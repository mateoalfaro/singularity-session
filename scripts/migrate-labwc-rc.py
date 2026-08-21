#!/usr/bin/env python3
import argparse
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET

BIND_RE = re.compile(
    r'[ \t]*<(?P<tag>keybind|mousebind)\b[^>]*?'
    r'(?:/>|>.*?</(?P=tag)>)[ \t]*\n',
    re.DOTALL)
KEY_RE = re.compile(r'\bkey="([^"]+)"')


def binds(text, tag):
    for match in BIND_RE.finditer(text):
        if match.group('tag') != tag:
            continue
        key = KEY_RE.search(match.group(0))
        if key:
            yield key.group(1), match.group(0)


def load_state(path):
    if not path or not os.path.exists(path):
        return set()
    with open(path, encoding='utf-8') as handle:
        return {line.strip() for line in handle if line.strip()}


def save_state(path, keys):
    if not path:
        return
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as handle:
        handle.write('\n'.join(sorted(keys)) + '\n')


def insert(text, blocks):
    anchor = text.rfind('</keyboard>')
    if anchor < 0:
        return None
    line_start = text.rfind('\n', 0, anchor) + 1
    return text[:line_start] + ''.join(blocks) + text[line_start:]


def main():
    parser = argparse.ArgumentParser(
        description='Add keybinds shipped with the session to a user rc.xml '
                    'without touching anything the user already changed.')
    parser.add_argument('shipped')
    parser.add_argument('user')
    parser.add_argument('--state')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    if not os.path.exists(args.shipped):
        print(f'no shipped config at {args.shipped}', file=sys.stderr)
        return 1

    with open(args.shipped, encoding='utf-8') as handle:
        shipped_text = handle.read()
    shipped = dict(binds(shipped_text, 'keybind'))

    if not os.path.exists(args.user):
        if not args.dry_run:
            os.makedirs(os.path.dirname(args.user), exist_ok=True)
            shutil.copyfile(args.shipped, args.user)
            save_state(args.state, set(shipped))
        print(f'seeded {args.user}')
        return 0

    with open(args.user, encoding='utf-8') as handle:
        user_text = handle.read()
    present = {key for key, _ in binds(user_text, 'keybind')}
    seen = load_state(args.state)

    missing = [(key, block) for key, block in shipped.items()
               if key not in present and key not in seen]
    if not missing:
        if not args.dry_run:
            save_state(args.state, seen | present)
        print('labwc keybinds already up to date')
        return 0

    merged = insert(user_text, [block for _, block in missing])
    if merged is None:
        print('no <keyboard> section in the user config, nothing merged',
              file=sys.stderr)
        return 1
    try:
        ET.fromstring(merged)
    except ET.ParseError as error:
        print(f'merged config is not valid XML, keeping the original: {error}',
              file=sys.stderr)
        return 1

    added = ', '.join(key for key, _ in missing)
    if args.dry_run:
        print(f'would add: {added}')
        return 0

    shutil.copyfile(args.user, args.user + '.bak')
    with open(args.user, 'w', encoding='utf-8') as handle:
        handle.write(merged)
    save_state(args.state, seen | present | set(shipped))
    print(f'added keybinds: {added}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
