#!/usr/bin/env python3
"""V286 static cruise/ferry image inventory. Flags candidates; never claims visual or rights verification."""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
import json,re
ROOT=Path('site')
PAT=re.compile(r"""(?:url\(\s*['"]?|(?:src|poster)=['"])(/images/[^)'"]+)""")
class P(HTMLParser):
 def __init__(self): super().__init__();self.img=[]
 def handle_starttag(self,tag,attrs):
  if tag=='img': self.img.append(dict(attrs))
rows=[];missing=[];old=[];baked=[];clip=[]
for f in ROOT.rglob('*.html'):
 s=f.read_text(encoding='utf-8',errors='replace')
 urls=PAT.findall(s)
 if not urls:continue
 a=P();a.feed(s)
 for u in urls:
  if not (ROOT/u.lstrip('/').split('?')[0]).is_file():missing.append({'page':str(f),'asset':u})
 if '/images/ferry.jpg' in urls:old.append(str(f))
 if '/images/nipponferry-cruise-hero-visual.webp' in urls:baked.append(str(f))
 if any(x in str(f) for x in ('/cruise/','/ferry/','/booking/')) and ('background-size:cover' in s or 'center/cover' in s):clip.append(str(f))
 if any(x in str(f) for x in ('/cruise/','/ferry/','/booking/')):rows.append({'page':str(f),'images':len(urls),'unique':len(set(urls)),'candidate_blurry': '/images/ferry.jpg' in urls,'candidate_baked_text':'/images/nipponferry-cruise-hero-visual.webp' in urls})
report={'scope':'all HTML static image refs; cruise/ferry/booking candidate subset','all_pages_with_images':len(list(ROOT.rglob('*.html'))),'cruise_ferry_booking_candidates':rows,'missing_image_references':missing,'legacy_ferry_image_pages':old,'baked_text_hero_pages':baked,'potential_cover_crop_pages':clip,'not_verified':['photo geographic accuracy','license','resolution','browser rendering']}
out=Path('audit-output/v286');out.mkdir(parents=True,exist_ok=True)
(out/'cruise-image-inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('V286 image inventory:',len(rows),'cruise/ferry/booking pages,',len(old),'legacy ferry images,',len(baked),'baked-text images,',len(missing),'missing refs,',len(clip),'cover-crop candidates')
assert not any(p in baked for p in ['site/japan-cruise/index.html','site/booking/japan-cruise/index.html'])
assert not any(p in old for p in ['site/booking/index.html','site/booking/japan-cruise/index.html','site/booking/fukuoka/index.html','site/booking/osaka/index.html','site/booking/shimonoseki/index.html','site/booking/tsushima/index.html'])


# V288: prioritize inspection of legacy photo use, rather than blindly replacing 108 images.
def legacy_priority(path):
 if path.startswith('site/japan-cruise/') or path.startswith('site/booking/'):return (1,path)
 if path.startswith('site/ferry/') or path.startswith('site/guide/'):return (2,path)
 if '/cruise-' in path or '/ferry-' in path or '/cruise/' in path:return (3,path)
 return (4,path)
ranked=sorted(old,key=legacy_priority)
tier_counts={str(n):sum(legacy_priority(x)[0]==n for x in ranked) for n in range(1,5)}
v288=Path('audit-output/v288');v288.mkdir(parents=True,exist_ok=True)
(v288/'legacy-ferry-priority.json').write_text(json.dumps(
 {'total_legacy_pages':len(ranked),'priority_tiers':tier_counts,
  'first_50_candidates':[{'priority':legacy_priority(p)[0],'page':p} for p in ranked[:50]],
  'cover_crop_candidates':sorted(clip),
  'review_note':'These are automated inspection candidates. Image identity, age, rights and real crop require manual verification.'},
 ensure_ascii=False,indent=2),encoding='utf-8')
print('V288 legacy priority tiers',tier_counts)
for page in ranked[:28]:
 print('V288 REVIEW',legacy_priority(page)[0],page)
