#!/usr/bin/env python3
"""V298: approved PanStar hero and route-correct imagery; preserves original SEO/CTA."""
from pathlib import Path
from html.parser import HTMLParser
import json
ROOT=Path('site')
asset='/images/panstar-cruise-clean-2048.webp'
expect={
 'japan-cruise/':(asset,2048,682),
 'booking/':(asset,2048,682),
 'booking/japan-cruise/':(asset,2048,682),
 'booking/osaka/':(asset,2048,682),
 'booking/fukuoka/':('/images/venues/nf-v134-new-camellia-busan-2026-real.webp',1400,934),
 'booking/shimonoseki/':('/images/venues/nf-v135-shimonoseki-international-terminal-2021-real.webp',1333,1000),
 'booking/tsushima/':('/images/venues/nf-v124-tsushima-harbor-real.webp',720,450),
}
class Parse(HTMLParser):
 def __init__(self):
  super().__init__();self.img=[];self.a=[];self.canonical=[];self.h1=0
 def handle_starttag(self,tag,attrs):
  v=dict(attrs)
  if tag=='img':self.img.append(v)
  if tag=='a':self.a.append(v.get('href',''))
  if tag=='h1':self.h1+=1
  if tag=='link' and v.get('rel')=='canonical':self.canonical.append(v.get('href',''))
results=[]
for slug,(file,w,h) in expect.items():
 path=ROOT/slug/'index.html'
 s=path.read_text(encoding='utf-8');a=Parse();a.feed(s)
 pics=[x for x in a.img if x.get('class')=='nf298-banner-img']
 assert len(pics)==1,(slug,'missing or duplicate hero image')
 photo=pics[0]
 assert photo.get('src')==file,(slug,'wrong operator/photo')
 assert photo.get('width')==str(w) and photo.get('height')==str(h),(slug,'wrong dimensions')
 assert photo.get('alt') and len(photo['alt'])>=24,(slug,'missing accurate alt')
 assert photo.get('fetchpriority')=='high',(slug,'hero loading priority')
 assert (ROOT/file.lstrip('/')).is_file(),(slug,'missing local photo')
 assert '<figure class="nf298-banner">' in s and '<figcaption class="nf298-caption">' in s,(slug,'missing separate caption')
 assert 'object-fit:contain' in s and 'max-height:640px' in s,(slug,'cropping risk')
 assert 'content:none!important' in s or slug=='japan-cruise/',(slug,'old hero overlay still present')
 assert len(a.canonical)==1 and a.canonical[0]=='https://www.nipponferry.com/'+slug,(slug,'canonical changed')
 assert a.h1==1,(slug,'H1 count altered')
 assert all(v in a.a for v in ['/ferry/#recommended-ferry-routes','/stay/']) if slug=='booking/' else True
 if file==asset:
  assert 'AI 제작 연출 이미지' in s,(slug,'illustration disclosure missing')
 else:
  assert 'AI 제작 연출 이미지' not in s.split('<figcaption class="nf298-caption">')[1].split('</figcaption>')[0],(slug,'wrong photo label')
 if slug=='booking/':
  assert 'willer-travel.com/ko/ferry/' not in s,(slug,'domestic-only booking URL remains')
  assert a.a.count('/ferry/#recommended-ferry-routes')==3,(slug,'route CTAs missing')
 results.append({'page':slug,'hero_image':file,'caption_checked':True,'seo_checked':True})
 print('PASS',slug,file)
assert (ROOT/'ferry/index.html').read_text(encoding='utf-8').count('id="recommended-ferry-routes"')==1
assert (ROOT/'images/panstar-cruise-clean-2048.webp').stat().st_size>200000,'approved image size mismatch'
out=Path('audit-output/v298');out.mkdir(parents=True,exist_ok=True)
(out/'operator-image-cta-qa.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print('V298 PASS: 7 / 7 pages; exact PanStar image, route photos, canonical and booking links')
