#!/usr/bin/env python3
"""V253 Tokyo photo provenance, consistency, and actionable unresolved work.
Read only. Distinguishes technical completeness from exact-subject photography.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from html.parser import HTMLParser
import json,re,subprocess

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
OUT=ROOT/'audit-reports/v253'
OUT.mkdir(parents=True,exist_ok=True)
source=(SITE/'tokyo-card-photos.js').read_text('utf-8')
mapping=json.loads(source.split('const map=',1)[1].split(';document.querySelectorAll',1)[0])
hub=(SITE/'japan/tokyo/index.html').read_text('utf-8')
class Cards(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True)
  self.cards=[];self.current=None;self.credit=False
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='a' and 'tky-card' in (a.get('class') or '').split():
   self.current={'href':a.get('href',''),'src':None,'alt':None,'caption':''}
   self.cards.append(self.current)
  if self.current and tag=='img':
   self.current['src']=a.get('src','')
   self.current['alt']=a.get('alt','')
  if self.current and tag=='span' and 'tky-photo-label' in (a.get('class') or '').split():
   self.credit=True
 def handle_data(self,data):
  if self.current and self.credit:self.current['caption']+=data
 def handle_endtag(self,tag):
  if tag=='span' and self.credit:self.credit=False
  if tag=='a' and self.current:self.current=None
p=Cards();p.feed(hub)
errors=[];duplicates=defaultdict(list);generic=[];without_source=[];licensing=[];article_mismatches=[];article_credit_gaps=[]
for card in p.cards:
 slug=card['href'].strip('/').split('/')[-1];m=mapping.get(slug)
 if not m:
  errors.append(slug+': no map entry');continue
 for field in ['src','alt']:
  if card[field]!=m.get(field):
   errors.append(slug+': hub/'+field+' differs from licensed mapping')
 if card['caption']!=m.get('caption'):
  errors.append(slug+': hub image credit differs from licensed mapping')
 src=m.get('src','')
 duplicates[src].append(slug)
 if not (SITE/src.lstrip('/')).is_file():errors.append(slug+': image file absent')
 if not src.endswith(('.jpg','.jpeg','.png','.webp')):
  errors.append(slug+': not a raster photographic asset')
 lic=m.get('license','')
 if not lic or not re.search(r'CC(?:0| BY)|public.domain',lic,re.I):
  licensing.append({'slug':slug,'license':lic})
 if not m.get('source','').startswith('https://commons.wikimedia.org/wiki/File:'):
  without_source.append(slug)
 if re.search(r'아닙니다|아님|참고 사진|관련 역 사진|관련 장소|정보형|실사진 아님',m.get('alt','')+' '+m.get('caption','')):
  generic.append({'slug':slug,'alt':m.get('alt',''),'source':src})
 page=SITE/'japan/tokyo'/slug/'index.html'
 if not page.is_file():
  errors.append(slug+': article absent');continue
 doc=page.read_text('utf-8')
 figure=re.search(r'<figure class="tokyo-article-photo-v1">([\s\S]*?)</figure>',doc)
 if not figure:
  errors.append(slug+': article has no lead image');continue
 photo=re.search(r'<img\b[^>]*src="([^"]+)"',figure[1])
 if not photo or photo[1]!=src:article_mismatches.append(slug)
 if m.get('source','') and m['source'] not in figure[1]:
  article_credit_gaps.append(slug)
unique=len(duplicates)
repeated=[{'src':src,'count':len(names),'slugs':names} for src,names in duplicates.items() if len(names)>1]
report={
 'version':'V253','generated_at':datetime.now(timezone.utc).isoformat(),
 'commit':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,text=True,capture_output=True).stdout.strip(),
 'passed_structural':not errors and len(p.cards)==220 and len(mapping)==220 and not licensing and not without_source,
 'cards':len(p.cards),'map_records':len(mapping),'distinct_photos':unique,
 'duplicate_photo_groups':repeated,'generic_photo_disclosures':generic,
 'not_licensed':licensing,'missing_provenance':without_source,'article_photo_mismatch':article_mismatches,'article_source_link_missing':article_credit_gaps,'errors':errors,
 'editorial_complete':not generic and not repeated and not article_mismatches and not article_credit_gaps,
 'limitations':['Image labels identify related but not necessarily exact subjects.','Creative Commons licensing does not verify the depicted subject without editorial visual review.']
}
(OUT/'tokyo-editorial-photo-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# V253 Tokyo photograph accuracy review','',
 f"- Hub cards: {len(p.cards)} / 220",
 f"- Unique photos: {unique}",
 f"- Repeated-photo groups: {len(repeated)}",
 f"- Generic/non-exact subject disclosures: {len(generic)}",
 f"- Structural failures: {len(errors)}",
 f"- Provenance/license issues: {len(licensing)+len(without_source)}",
 f"- Article photo differences to review: {len(article_mismatches)}",
 f"- Article source link gaps to review: {len(article_credit_gaps)}",
 f"- Structurally passed: {report['passed_structural']}",
 f"- Editorial exact-match complete: {report['editorial_complete']}",'',
 '## Duplicated photograph groups']
for row in repeated:lines.append('- '+row['src']+': '+', '.join(row['slugs']))
lines+=['','## Photos explicitly disclosed as generic or inexact']
for row in generic:lines.append('- '+row['slug']+': '+row['alt'])
lines+=['','## Article photo differences']+['- '+x for x in article_mismatches]
lines+=['','## Article photographer source link gaps']+['- '+x for x in article_credit_gaps]
lines+=['','## Structural failures']
for error in errors:lines.append('- '+error)
lines+=['','No new URLs/pages; this is editorial review, not live ticket/availability validation.']
(OUT/'tokyo-editorial-photo-qa.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('V253_EDITORIAL_QA',json.dumps({k:report[k] for k in ('passed_structural','editorial_complete','cards','distinct_photos','duplicate_photo_groups','errors','missing_provenance','not_licensed')},ensure_ascii=False))
if not report['passed_structural']:raise SystemExit(1)
