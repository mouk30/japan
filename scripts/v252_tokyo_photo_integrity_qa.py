#!/usr/bin/env python3
"""V252: all 220 Tokyo cards AND corresponding article hero images, not a sample.

Fail when SVG editorial placeholders return, image files disappear, alt text is
missing, photo credits vanish, card URLs change, or Tokyo travel pages no longer
have individual photographic heroes. Track distinct images and reuse for review.
This test intentionally does not claim every photo depicts the exact attraction.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import json, re, subprocess, datetime, hashlib

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
HUB=DIST/'japan/tokyo/index.html'
OUT=ROOT/'audit-reports/v252'
OUT.mkdir(parents=True,exist_ok=True)
ISSUES=[]
class Tags(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True)
  self.cards=[];self.in_card=False;self.depth=0;self.photo=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='a' and 'tky-card' in (a.get('class') or '').split():
   if self.in_card: ISSUES.append('nested_tky_card')
   self.in_card=True
   self.depth=1
   self.cards.append({'href':a.get('href',''), 'images':[], 'labels':[]})
   return
  if self.in_card:
   if tag=='a':self.depth+=1
   if tag=='img':self.cards[-1]['images'].append(a)
   if tag=='span' and 'tky-photo-label' in (a.get('class') or '').split():
    self.photo='';self.cards[-1]['labels'].append('')
 def handle_data(self,data):
  if self.photo is not None and self.in_card and self.cards[-1]['labels']:
   self.cards[-1]['labels'][-1]+=data
 def handle_endtag(self,tag):
  if tag=='a' and self.in_card:
   self.depth-=1
   if not self.depth:self.in_card=False;self.photo=None
  if tag=='span' and self.photo is not None:self.photo=None
html=HUB.read_text('utf-8')
p=Tags();p.feed(html)
if len(p.cards)!=220:ISSUES.append(f'card_count:{len(p.cards)}!=220')
if '/tokyo-card-photos.js' in html:ISSUES.append('JS_only_photo_loader_still_enabled')
if '/images/tokyo-editorial/' in html:ISSUES.append('SVG_editorial_assets_referenced_in_hub')
if 'https://www.nipponferry.com/japan/tokyo/' not in html:ISSUES.append('canonical_missing')
seen={}
images={}
for card in p.cards:
 href=card['href']
 slug=href.rstrip('/').rsplit('/',1)[-1]
 if slug in seen: ISSUES.append('duplicate_card_slug:'+slug)
 seen[slug]=href
 if not href.startswith('/japan/tokyo/') or not href.endswith('/'):
  ISSUES.append('card_url_invalid:'+href)
 if len(card['images'])!=1:ISSUES.append('card_img_count:'+slug+':'+str(len(card['images'])));continue
 img=card['images'][0]
 src=img.get('src','')
 images[slug]=src
 if not src.startswith('/images/') or not src.endswith(('.webp','.jpg','.jpeg','.png')):
  ISSUES.append('card_not_photo:'+slug+':'+src)
 elif not (DIST/src.lstrip('/')).is_file():ISSUES.append('missing_asset:'+slug+':'+src)
 if not img.get('alt','').strip():ISSUES.append('missing_alt:'+slug)
 if not card['labels'] or not card['labels'][0].strip():
  ISSUES.append('missing_photo_credit:'+slug)
 article=DIST/href.lstrip('/')/'index.html'
 if not article.is_file():ISSUES.append('article_missing:'+slug);continue
 page=article.read_text('utf-8')
 figure=re.search(r'<figure class="tokyo-article-photo-v1">([\s\S]*?)</figure>',page)
 if not figure:ISSUES.append('article_no_lead_photo:'+slug);continue
 a=re.search(r'<img\b[^>]*src="([^"]+)"[^>]*>',figure.group(1))
 if not a:ISSUES.append('article_no_image:'+slug);continue
 hero_src=a.group(1)
 if not hero_src.startswith('/images/') or not hero_src.endswith(('.webp','.jpg','.jpeg','.png')):
  ISSUES.append('article_non_photo:'+slug+':'+hero_src)
 elif not (DIST/hero_src.lstrip('/')).is_file():ISSUES.append('article_missing_asset:'+slug)
 if not re.search(r'\balt="[^"]{2,}"',a.group(0)):ISSUES.append('article_missing_alt:'+slug)
 if 'tokyo-editorial/' in page:ISSUES.append('article_editorial_image_left:'+slug)
# Count image re-use. Related topic images may be legitimately repeated, but
# inappropriate repeat photographs must be reviewed separately by an editor.
from collections import Counter
used=Counter(images.values())
reused={img:n for img,n in used.items() if n>1}
src_has_svg=any('.svg' in s for s in images.values())
if src_has_svg:ISSUES.append('SVG_photographs_remaining')
report={
 'version':'V252','generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'source_commit':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,text=True,capture_output=True).stdout.strip(),
 'passed':not ISSUES,'tokyo_hub_cards':len(p.cards),'tokyo_article_pages_checked':len(seen),
 'image_assets_distinct':len(used),'reused_photos':reused,'issues':ISSUES,
 'limitations':['Photographic validity and precise subject matching require photo-by-photo visual/editorial review.',
 'A generic related photo is not proof of an exact attraction, store, ticket or current operating condition.']
}
(OUT/'tokyo-all-220-photo-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
(OUT/'tokyo-all-220-photo-audit.md').write_text(
 '# V252 Tokyo 220 image integrity\n\n'
 +f'- All cards: {len(p.cards)}\n- Article hero checks: {len(seen)}\n- Distinct images: {len(used)}\n'
 +f'- Photo files reused: {len(reused)}\n- Blocking errors: {len(ISSUES)}\n'
 + '\n## Photo reuse to review\n'+''.join(f'- `{img}`: {n}\n' for img,n in reused.items())
 + '\n## Blocking errors\n'+''.join(f'- {msg}\n' for msg in ISSUES), 'utf-8')
print('V252_TOKYO_AUDIT',json.dumps({k:report[k] for k in ('passed','source_commit','tokyo_hub_cards','tokyo_article_pages_checked','image_assets_distinct','reused_photos','issues')},ensure_ascii=False))
if ISSUES:raise SystemExit(1)
