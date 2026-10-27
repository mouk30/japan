#!/usr/bin/env python3
"""V251: full-built-site image existence + priority hub thumbnail coverage.

Read-only: does not create HTML pages, change SEO tags, or fetch unlicensed photos.
The large card coverage inventory distinguishes intentionally text-only information
cards from required photographic visual cards. Report missing external images
separately because the local build cannot guarantee third-party availability.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import posixpath
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
OUT=ROOT/'audit-reports'/'v251'
OUT.mkdir(parents=True,exist_ok=True)
ALLOWED_HOSTS={'www.nipponferry.com','nipponferry.com'}
REQUIRED={
 '/japan/tokyo/':('tky-card',220),
 '/japan-cruise/':('jc-card',12),
 '/okinawa/':('oc',12),
 '/japan/osaka/':('os-card',9),
 '/japan/fukuoka/':('fk-card',9),
 '/japan/':('dircard',23),
 '/things-to-do/':('v36-photo-card',152),
}
FATAL=[]
WARN=[]
counts=Counter()
missing_by_route=defaultdict(list)
classes=defaultdict(lambda:Counter())
external_images=set()
def route_for(p):
 rel=p.relative_to(DIST).as_posix()
 return '/' + (rel[:-len('index.html')] if rel.endswith('index.html') else rel)
def local_path(route,url):
 url=(url or '').strip()
 if not url or url.startswith(('data:','blob:','javascript:','mailto:','tel:')):return None
 if url.startswith('//'): url='https:'+url
 parsed=urlsplit(url)
 if parsed.scheme and parsed.scheme not in ('http','https'):return None
 if parsed.netloc and (parsed.hostname or '').lower() not in ALLOWED_HOSTS:
  external_images.add(parsed.hostname or '')
  return None
 raw=unquote(parsed.path)
 if not raw:return None
 if not raw.startswith('/'):raw=posixpath.join(posixpath.dirname(route),raw)
 clean=posixpath.normpath(raw).lstrip('/')
 if not clean or clean.startswith('../'):return None
 return DIST/clean
class Scan(HTMLParser):
 def __init__(self,route):
  super().__init__(convert_charrefs=True)
  self.route=route
  self.stack=[]
  self.card_records=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs);cl=set((a.get('class') or '').split())
  if tag in ('a','article') and ('card' in ' '.join(cl) or cl & {'oc','dircard'}):
   wanted=next((c for c in ('tky-card','jc-card','oc','os-card','fk-card','dircard','v36-photo-card') if c in cl),None)
   if wanted:
    item={'class':wanted,'href':a.get('href',''),'imgs':0,'alt_missing':0}
    self.card_records.append(item)
   else:item=None
  else:item=None
  self.stack.append((tag,item))
  if tag=='img':
   counts['img_tags']+=1
   if 'alt' not in a:counts['img_missing_alt_attr']+=1
   elif a['alt']=='':counts['img_decorative_alt']+=1
   for _,card in self.stack:
    if card:
     card['imgs']+=1
     if 'alt' not in a:card['alt_missing']+=1
   for key in ('src','data-src'):
    if a.get(key):self.verify(a[key],kind=key)
   for key in ('srcset','data-srcset'):
    if a.get(key):
     for part in a[key].split(','):
      item=part.strip().split()[0] if part.strip() else ''
      if item:self.verify(item,kind=key)
  if tag in ('video','source') and a.get('poster'):
   self.verify(a['poster'],kind='poster')
 def handle_startendtag(self,tag,attrs):
  self.handle_starttag(tag,attrs)
  self.handle_endtag(tag)
 def handle_endtag(self,tag):
  for i in range(len(self.stack)-1,-1,-1):
   if self.stack[i][0]==tag:
    del self.stack[i:]
    break
 def verify(self,src,kind):
  p=local_path(self.route,src)
  if p is None:return
  counts['local_image_refs']+=1
  if not p.is_file():
   if len(missing_by_route[self.route])<20:missing_by_route[self.route].append({'type':kind,'src':src})
   counts['missing_local_image_refs']+=1

def verify_bytes():
 # Structure check only; actual decode is checked by the browser QA.
 bad=[]
 for f in DIST.rglob('*'):
  if not f.is_file():continue
  ext=f.suffix.lower()
  if ext not in ('.jpg','.jpeg','.png','.webp','.svg','.gif','.avif'):continue
  counts['image_files']+=1
  try:
   b=f.open('rb').read(24)
   valid=({'.jpg':b.startswith(bytes([255,216,255])),'.jpeg':b.startswith(bytes([255,216,255])),
           '.png':b.startswith(bytes([137,80,78,71,13,10,26,10])),
           '.webp':b.startswith(b'RIFF') and b[8:12]==b'WEBP',
           '.gif':b.startswith((b'GIF87a',b'GIF89a')),
           '.avif':b'ftypavif' in b or b'ftypavis' in b,
           '.svg':b'<?xml' in b or b'<svg' in b})
   if not valid[ext]:bad.append(str(f.relative_to(DIST)))
  except OSError:bad.append(str(f.relative_to(DIST)))
 return bad

priority={}
for f in sorted(DIST.rglob('*.html')):
 route=route_for(f);counts['pages']+=1
 doc=Scan(route)
 try:doc.feed(f.read_text('utf-8'))
 except Exception as e:FATAL.append('parse '+route+': '+str(e));continue
 counts['card_nodes']+=len(doc.card_records)
 for card in doc.card_records:
  classes[card['class']]['total']+=1
  if card['imgs']>0:classes[card['class']]['with_img']+=1
  else:
   classes[card['class']]['without_img']+=1
   if len(missing_by_route[route])<20:missing_by_route[route].append({'type':'card_without_img','class':card['class'],'href':card['href']})
  if card['alt_missing']:classes[card['class']]['alt_missing']+=card['alt_missing']
 if route in REQUIRED:
  cls,expected=REQUIRED[route]
  cards=[c for c in doc.card_records if c['class']==cls]
  actual=len(cards)
  pictured=sum(c['imgs']>0 for c in cards)
  entry=dict(class_name=cls,expected=expected,found=actual,with_image=pictured)
  priority[route]=entry
  if actual!=expected or pictured!=expected:FATAL.append(f'{route}: {cls} {pictured}/{actual}, expected {expected}')
# Sources such as CSS background images and JavaScript-created nodes require
# browser coverage; explicit <img> image paths are checked here.
if counts['missing_local_image_refs']:
 FATAL.append('missing_local_image_refs='+str(counts['missing_local_image_refs']))
bad_assets=verify_bytes()
if bad_assets:FATAL.append('image files with unrecognized format signatures: '+str(bad_assets[:12]))
counts['bad_asset_signatures']=len(bad_assets)
# Any text-only informational cards outside the required cohorts are merely
# inventoried; they are not invented missing images.
report=dict(version='V251',generated_at_utc=datetime.now(timezone.utc).isoformat(),
 source_commit=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True).stdout.strip(),
 passed=not FATAL,counts=dict(counts),priority=priority,
 grouped_card_coverage={k:dict(v) for k,v in classes.items()},
 missing_examples=dict(missing_by_route),external_image_hosts=sorted(external_images),
 errors=FATAL,warnings=WARN,format_signature_failure_paths=bad_assets)
(OUT/'thumbnail-sitewide.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
lines=['# V251 sitewide thumbnails and image paths','',
 f'- Pages: {counts["pages"]}',
 f'- HTML <img> tags: {counts["img_tags"]}',
 f'- Local image references checked: {counts["local_image_refs"]}',
 f'- Missing local image files: {counts["missing_local_image_refs"]}',
 f'- Unrecognized image file headers: {len(bad_assets)}','','## Priority hubs']
for path,entry in priority.items():
 lines.append(f'- {path}: {entry["class_name"]} {entry["with_image"]}/{entry["found"]} (expected {entry["expected"]})')
lines+=['','## Other card group inventory (not automatic failures)']
for cl,d in sorted(classes.items()):
 lines.append(f'- {cl}: {d["with_img"]}/{d["total"]} with inline images, {d["without_img"]} without')
if FATAL:lines+=['','## Failures']+['- '+x for x in FATAL]
lines+=['','External image URLs and CSS background image rendering are not verified by this file-system audit.']
(OUT/'thumbnail-sitewide-summary.md').write_text('\n'.join(lines)+'\n','utf-8')
print('V251_THUMBNAIL_SUMMARY',json.dumps({k:report[k] for k in ('passed','source_commit','counts','priority','grouped_card_coverage','errors')},ensure_ascii=False))
if FATAL:raise SystemExit(1)
