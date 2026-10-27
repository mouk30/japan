#!/usr/bin/env python3
"""V251: read-only inventory of legacy SEO-field exceptions and pre-V246 changes.

Uses the exact built HTML under dist/. It does not change pages, URLs, or robots.
A metadata omission is blocking only when its URL is listed in the sitemap.
Historical field differences are reported for human interpretation, not assumed regressions.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE, DIST = ROOT / 'site', ROOT / 'dist'
OUT = ROOT / 'audit-reports' / 'v251'
OUT.mkdir(parents=True, exist_ok=True)
BASE = '524b9c4809f50d9e7f567d3a43b63d682fb86b41'
FIELDS = ('title', 'description', 'canonical', 'robots', 'h1_count', 'jsonld')
class Seo(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ''
        self.description = []
        self.canonical = []
        self.robots = []
        self.h1 = []
        self._title = False
        self._h1 = False
        self._h1text = ''
        self._ld = False
        self._ldtext = ''
        self.jsonld = []
        self.meta_refresh = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'title': self._title = True
        if tag == 'h1': self._h1, self._h1text = True, ''
        if tag == 'meta':
            name = (a.get('name') or '').lower()
            if name == 'description': self.description.append(a.get('content') or '')
            if name == 'robots': self.robots.append(a.get('content') or '')
            if (a.get('http-equiv') or '').lower() == 'refresh': self.meta_refresh = True
        if tag == 'link' and 'canonical' in (a.get('rel') or '').lower().split():
            self.canonical.append(a.get('href') or '')
        if tag == 'script' and (a.get('type') or '').lower() == 'application/ld+json':
            self._ld, self._ldtext = True, ''
    def handle_data(self, data):
        if self._title: self.title += data
        if self._h1: self._h1text += data
        if self._ld: self._ldtext += data
    def handle_endtag(self, tag):
        if tag == 'title': self._title = False
        if tag == 'h1': self.h1.append(self._h1text.strip()); self._h1 = False
        if tag == 'script' and self._ld:
            self.jsonld.append(self._ldtext.strip()); self._ld = False
    def fields(self):
        return dict(title=self.title.strip(),
                    description=tuple(self.description), canonical=tuple(self.canonical),
                    robots=tuple(self.robots), h1_count=len(self.h1), jsonld=tuple(self.jsonld))
def read(file):
    p = Seo()
    p.feed(file.read_text('utf-8'))
    return p
def route(file, root):
    rel = file.relative_to(root).as_posix()
    return '/' + (rel[:-10] if rel.endswith('index.html') else rel)
def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout
def canonical_paths():
    root = ET.parse(SITE/'sitemap.xml').getroot()
    paths = []
    for e in root.iter():
        if e.tag.endswith('}loc') and e.text:
            parsed = urlsplit(e.text.strip())
            paths.append(parsed.path or '/')
    return set(paths)
sitemap = canonical_paths()
pages = sorted(DIST.rglob('*.html'))
exceptions, blocking, changes = [], [], []
for f in pages:
    p = read(f)
    route_path = route(f, DIST)
    missing = []
    if not p.description or not p.description[0].strip(): missing.append('description')
    if not p.canonical or not p.canonical[0].strip(): missing.append('canonical')
    if not p.h1: missing.append('h1')
    noindex = any('noindex' in x.lower() for x in p.robots)
    if missing or noindex:
        record = dict(route=route_path, missing=missing, noindex=noindex,
                      in_sitemap=route_path in sitemap, refresh_redirect=p.meta_refresh,
                      title=p.title, canonical=p.canonical, robots=p.robots)
        exceptions.append(record)
        if missing and route_path in sitemap and not noindex and not p.meta_refresh:
            blocking.append(record)
# Compare the original (pre-V246) source HTML metadata only where the URL already existed.
oldpaths = {x.removeprefix('site/') for x in git('ls-tree','-r','--name-only',BASE,'site').splitlines()
            if x.endswith('.html')}
current_files = sorted(SITE.rglob('*.html'))
for f in current_files:
    rel = f.relative_to(SITE).as_posix()
    if rel not in oldpaths: continue
    old_html = git('show',BASE+':site/'+rel)
    old = Seo(); old.feed(old_html)
    new = read(f)
    of, nf = old.fields(), new.fields()
    diff = {k: dict(before=of[k], after=nf[k]) for k in FIELDS if of[k] != nf[k]}
    if diff:
        changes.append(dict(route=route(f,SITE), changes=diff))
# Changes of title, description, canonical or robots are surfaced for assessment,
# rather than treated as evidence that search traffic changed.
change_counts = Counter(k for row in changes for k in row['changes'])
report = dict(version='V251', checked_at_utc=datetime.now(timezone.utc).isoformat(),
              source_commit=git('rev-parse','HEAD').strip(),
              baseline_commit=BASE, page_count=len(pages),
              sitemap_url_count=len(sitemap), exceptions=exceptions, blocking=blocking,
              pre_v246_metadata_changes=changes, change_counts=dict(change_counts),
              passed=(not blocking))
(OUT/'seo-exception-inventory.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2, default=list)+'\n', 'utf-8')
lines = ['# V251 · SEO exception and pre-V246 change inventory','',
 f"- Built HTML: {len(pages)}",
 f"- Sitemap URLs: {len(sitemap)}",
 f"- Metadata exception pages: {len(exceptions)}",
 f"- Sitemap-listed pages with missing required fields: {len(blocking)}",
 f"- Previously existing pages with source SEO-field changes: {len(changes)}",
 f"- Field change counts: {dict(change_counts)}", '',
 '## Every exception']
for e in exceptions:
    lines.append(f"- `{e['route']}`: missing={e['missing']}; noindex={e['noindex']}; sitemap={e['in_sitemap']}; redirect={e['refresh_redirect']}")
lines += ['', '## Pre-V246 SEO field changes by route']
for e in changes:
    lines.append(f"- `{e['route']}`: {', '.join(e['changes'].keys())}")
lines += ['', 'Search Console data is required to determine actual clicks, indexing or traffic impact.']
(OUT/'seo-exception-summary.md').write_text('\n'.join(lines)+'\n', 'utf-8')
print('V251_REPORT', json.dumps({k:report[k] for k in ('passed','source_commit','page_count','sitemap_url_count','exceptions','blocking','change_counts')}, ensure_ascii=False, default=list))
if blocking: raise SystemExit(1)
