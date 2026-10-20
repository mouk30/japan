#!/usr/bin/env python3
"""Normalize NIPPONFERRY cruise favicon links across the deployed static site.

Usage:
  python3 scripts/standardize_cruise_favicon.py --check
  python3 scripts/standardize_cruise_favicon.py --fix
Does not change canonical, titles, JSON-LD, content, or page routes.
"""
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "site"
ICONS = '<link rel="icon" type="image/svg+xml" href="/favicon.svg"><link rel="alternate icon" href="/favicon.ico">'
LINK = re.compile(r'<link\b(?=[^>]*\brel\s*=\s*["\'](?:shortcut icon|icon|alternate icon)["\'])[^>]*>', re.I)

def normalize(text):
    head_end = re.search(r"</head\s*>", text, re.I)
    if not head_end:
        return text, False
    head, tail = text[:head_end.start()], text[head_end.start():]
    clean = LINK.sub('', head)
    clean += ICONS
    return clean + tail, clean + tail != text

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--fix', action='store_true')
    args = ap.parse_args()
    if args.check == args.fix:
        ap.error('Choose exactly one of --check or --fix')
    if not (ROOT / 'favicon.svg').is_file():
        raise SystemExit('site/favicon.svg missing')
    pages = list(ROOT.rglob('*.html'))
    modified = []
    for f in pages:
        raw = f.read_text(encoding='utf-8')
        new, changed = normalize(raw)
        if changed:
            modified.append(f.relative_to(ROOT).as_posix())
            if args.fix:
                f.write_text(new, encoding='utf-8')
    print(f'Pages scanned: {len(pages)}; favicon mismatches: {len(modified)}')
    for name in modified[:30]:
        print('  ', name)
    if args.check and modified:
        raise SystemExit(1)
if __name__ == '__main__':
    main()
