#!/usr/bin/env python3
"""V140: import three independently documented Commons photographs into homepage cards.
Stops without changing HTML if any download/verification fails.
Preserves all titles, meta descriptions, canonical URLs and mobile styling.
"""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote
from PIL import Image,ImageOps
import io,json,re,hashlib,time
root=Path(__file__).resolve().parents[1]
spec=[
dict(key='okinawa',file='JP 沖繩 Okinawa Nago Kouri Road Bridge n Beach January 2026 N13P 01.jpg',old='/images/editorial/okinawa-kouri-bridge.webp',dest='/images/venues/nf-v140-okinawa-kouri-bridge-2026-real.webp',alt='2026년 1월 실제 촬영한 오키나와 고우리대교와 해변 풍경',author='NORTLAUKAU 26088 JP',date='2026-01-30',license='CC0 1.0',licurl='https://creativecommons.org/publicdomain/zero/1.0/'),
dict(key='fukuoka',file='Hakata Port from Fukuoka Tower.jpg',old='/images/editorial/hakata-cruise-port-day-trip.webp',dest='/images/venues/nf-v140-fukuoka-hakata-port-2017-real.webp',alt='2017년 6월 후쿠오카타워에서 실제 촬영한 하카타항 방향 전망',author='そらみみ',date='2017-06-18',license='CC BY-SA 4.0',licurl='https://creativecommons.org/licenses/by-sa/4.0/'),
dict(key='kobe',file='Kobe Port Tower in November 2025 at night 06.jpg',old='/images/editorial/kobe-cruise-port-day-trip.webp',dest='/images/venues/nf-v140-kobe-port-tower-2025-real.webp',alt='2025년 11월 실제 촬영한 고베 포트타워 야경',author='ノボホショコロトソ',date='2025-11-02',license='CC BY 4.0',licurl='https://creativecommons.org/licenses/by/4.0/')
]
htmlfile=root/'site/index.html'
old=htmlfile.read_text(encoding='utf-8')
assert old.count('V140 실사 출처:')==1
files=[]
for x in spec:
  assert old.count('src="'+x['old']+'"')>=1, x['key']
  url='https://commons.wikimedia.org/wiki/Special:FilePath/'+quote(x['file'],safe='')+'?width=1300'
  for attempt in range(3):
    try:
      with urlopen(Request(url,headers={'User-Agent':'NipponFerry-ImageVerification/1.0 (https://www.nipponferry.com)','Accept':'image/*'}),timeout=75) as res:
        if not res.headers.get('Content-Type','').startswith('image/'): raise RuntimeError('not image')
        raw=res.read(14000001)
      if len(raw)>14000000 or len(raw)<20000: raise RuntimeError('unexpected size')
      photo=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert('RGB')
      if photo.width<750 or photo.height<600:raise RuntimeError('too small')
      photo.thumbnail((1400,1000),Image.Resampling.LANCZOS)
      out=io.BytesIO();photo.save(out,format='WEBP',quality=85,method=6)
      data=out.getvalue()
      assert data[0:4]==b'RIFF' and data[8:12]==b'WEBP'
      x['blob']=data
      x['size']=[photo.width,photo.height]
      x['sha256']=hashlib.sha256(data).hexdigest()
      x['source']='https://commons.wikimedia.org/wiki/File:'+quote(x['file'].replace(' ','_'),safe=':(),')
      files.append(x)
      break
    except Exception as e:
      if attempt==2:raise
      time.sleep(4)
s=old
for x in files:
  before='<img src="'+x['old']+'"'
  assert s.count(before)==1
  start=s.index(before)
  end=s.index('>',start)
  tag=s[start:end+1]
  newtag=re.sub(r'src="[^"]+"','src="'+x['dest']+'"',tag)
  newtag=re.sub(r'alt="[^"]+"','alt="'+x['alt']+'"',newtag)
  s=s[:start]+newtag+s[end+1:]
  idx=s.index('src="'+x['dest']+'"')
  a=s.rfind('<article class="v65-card"',0,idx)
  b=s.find('</article>',idx)
  section=s[a:b]
  label='<span class="v104-photo-origin">여행 분위기 연출 이미지</span>'
  assert section.count(label)==1
  section=section.replace(label,'',1)
  s=s[:a]+section+s[b:]
credit=', '.join('<a href="'+x['source']+'" target="_blank" rel="noopener noreferrer">'+x['key']+' · '+x['author']+' · '+x['date']+' · '+x['license']+' (원본 WebP 변환·축소)</a> (<a href="'+x['licurl']+'" target="_blank" rel="noopener noreferrer">라이선스</a>)' for x in files)
s=s.replace('V140 실사 출처: ','V140 실사 출처: '+credit+', ',1)
for rx in [r'<title>[^<]+</title>',r'<meta name="description"[^>]+>',r'<link rel="canonical"[^>]+>',r'<script type="application/ld\+json">.*?</script>']:
  assert re.search(rx,old).group()==re.search(rx,s).group(), 'protected SEO changed'
for x in files:
  dest=root/'site'/x['dest'].lstrip('/')
  dest.parent.mkdir(parents=True,exist_ok=True)
  dest.write_bytes(x['blob'])
htmlfile.write_text(s,encoding='utf-8')
report={'version':'V140','date':'2026-10-23','new_verified_photo_imports':3,'prior_site_images_reused':2,'total_home_cards_changed':5,'source_photos':[ {k:v for k,v in x.items() if k!='blob'} for x in files ],'seo_preserved':True}
(root/'audit-reports/v140').mkdir(parents=True,exist_ok=True)
(root/'audit-reports/v140/import-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'imported':3,'total_cards':5,'source_files':[x['dest'] for x in files]},ensure_ascii=False))
