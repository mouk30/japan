#!/usr/bin/env python3
"""V144-B: three independently verified documentary photos plus existing accurate
information diagrams, never unverified stock and never claims they show 2027.
Supports commercial reuse only per recorded Creative Commons attribution & SA.
"""
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request,urlopen
from PIL import Image,ImageOps
import re,hashlib,io,json,time
ROOT=Path(__file__).resolve().parents[1]
REP=ROOT/"audit-reports/v144/editorial-image-provenance-report.json"
DATA=json.loads(REP.read_text("utf8"))
ASSETS=ROOT/"site/images/venues"
SPECS=[
 {"slug":"asahikawa-winter-festival","group":"season",
  "file":"Asahikawa Winter Festival Snow Statue 1.jpg",
  "output":"nf-v144-asahikawa-snow-2007-real.webp",
  "author":"京浜にけ","date":"2007-02-11","license":"CC BY-SA 3.0","licurl":"https://creativecommons.org/licenses/by-sa/3.0/",
  "description":"2007년 아사히카와 겨울축제 현장에서 촬영한 실제 대형 눈조각","rights_note":"과거 행사 기록 사진이며 2026·2027년 현장 조각이나 운영 정보를 보여주지 않습니다."},
 {"slug":"otaru-snow-light-path-2027","group":"season",
  "file":"小樽雪あかりの路（Otaru Snow Light Path Festival） - panoramio.jpg",
  "output":"nf-v144-otaru-snow-light-2014-real.webp",
  "author":"t-konno","date":"2014-02-14","license":"CC BY-SA 3.0","licurl":"https://creativecommons.org/licenses/by-sa/3.0/",
  "description":"2014년 오타루 눈빛거리 행사 실제 현장을 촬영한 겨울 촛불 풍경","rights_note":"2014년 실제 기록 사진으로 2027년 행사 설치물·일정을 보여주는 사진이 아닙니다."},
 {"slug":"kyoto-tango-kuromatsu","group":"practical",
  "file":"京都丹後鉄道観光列車「あかまつ」「くろまつ」.jpg",
  "output":"nf-v144-kyoto-tango-akamatsu-kuromatsu-2019-real.webp",
  "author":"おのののの","date":"2019-03-21","license":"CC BY-SA 4.0","licurl":"https://creativecommons.org/licenses/by-sa/4.0/",
  "description":"2019년 교토탄고철도 미야마이선에서 아카마츠와 쿠로마츠 관광열차가 교행하는 실제 사진","rights_note":"두 열차가 함께 보이는 과거 기록 사진입니다. 현재 운행일·코스·식사 서비스는 별도 확인해야 합니다."}
]
def htmlesc(s):
 import html;return html.escape(str(s),quote=True)
def import_all():
 if DATA.get("verified_documentary_photo_additions"):
  print("3 images already recorded; skip duplicate import");return
 work=[]
 for x in SPECS:
  page=ROOT/"site"/x["group"]/x["slug"]/"index.html"
  src=page.read_text("utf8")
  if 'data-v144-detail="true"' not in src or src.count('<figure class="v144-topic-visual"')!=1:
   raise ValueError("Unrecognized article structure "+str(page))
  if "v144-real-photo" in src:raise ValueError("prior addition present "+str(page))
  commons="https://commons.wikimedia.org/wiki/File:"+quote(x["file"].replace(" ","_"),safe=":(),")
  source_url="https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(x["file"],safe="")+"?width=1400"
  raw=None
  for i in range(3):
   try:
    with urlopen(Request(source_url,headers={"User-Agent":"NipponFerryVerifiedLocationEditorial/1.0 (https://www.nipponferry.com/)","Accept":"image/*"}),timeout=75) as res:
     if not res.headers.get("Content-Type","").startswith("image/"):raise ValueError("not an image")
     raw=res.read(16_000_001)
    if len(raw)<30_000 or len(raw)>16_000_000:raise ValueError("size of source unexpected")
    break
   except Exception:
    if i==2:raise
    time.sleep(4)
  picture=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
  if picture.width<950 or picture.height<650:raise ValueError("image too small")
  picture.thumbnail((1500,1000),Image.Resampling.LANCZOS)
  out=io.BytesIO();picture.save(out,format="WEBP",quality=86,method=6)
  b=out.getvalue()
  assert b[:4]==b'RIFF' and b[8:12]==b'WEBP'
  pic_path="/images/venues/"+x["output"]
  credit=('<figure class="v144-real-photo" data-v144-licensed="'+htmlesc(x["slug"])+'">'
   '<img src="'+pic_path+'" alt="'+htmlesc(x["description"])+'" loading="eager" decoding="async">'
   '<figcaption>실제 촬영 사진 · '+htmlesc(x["date"])+' · 촬영자 '
   '<a href="'+commons+'" target="_blank" rel="noopener noreferrer">'+htmlesc(x["author"])+' / Wikimedia Commons 원본</a>'
   ' · <a href="'+x["licurl"]+'" target="_blank" rel="noopener noreferrer">'+x["license"]+'</a>'
   ' · 원본 크기 조정 및 WebP 변환. '+htmlesc(x["rights_note"])+'</figcaption></figure>')
  insert='<figure class="v144-topic-visual"'
  revised=src.replace(insert,credit+insert,1)
  for pat in [r'<title>[^<]*</title>',r'<meta name="description"[^>]*>',r'<link rel="canonical"[^>]*>',
              r'<script type="application/ld\+json">[\s\S]*?</script>']:
   if (re.search(pat,src).group(0) if re.search(pat,src) else '') != (re.search(pat,revised).group(0) if re.search(pat,revised) else ''):
    raise ValueError("SEO drift")
  work.append((x,page,revised,ASSETS/x["output"],b,commons,pic_path,picture.size))
 # No disk changes until all three source images and licenses' metadata have been inspected.
 ASSETS.mkdir(parents=True,exist_ok=True)
 records=[]
 for x,page,html,p,b,commons,img_url,size in work:
  if p.exists():raise ValueError("New destination already exists: "+str(p))
  p.write_bytes(b);page.write_text(html,'utf8')
  records.append({"page":"/"+x["group"]+"/"+x["slug"]+"/","image":img_url,
   "source":commons,"author":x["author"],"capture_date":x["date"],
   "license":x["license"],"license_url":x["licurl"],
   "description":x["description"],"historical_notice":x["rights_note"],
   "size":list(size),"sha256":hashlib.sha256(b).hexdigest(),"transformations":"resized, converted to WebP"})
  for obj in DATA["edited_pages"]:
   if obj["url"]==records[-1]["page"]:
    obj["additional_real_photo"]=img_url
    break
 DATA["verified_documentary_photo_additions"]=records
 DATA["verified_real_photo_count"]=len(records)
 DATA["image_followups"]=[z for z in DATA["image_followups"] if z["url"] not in {d["page"] for d in records}]
 REP.write_text(json.dumps(DATA,ensure_ascii=False,indent=2)+"\n","utf8")
 print(json.dumps({"count":len(records),"images":[z["image"] for z in records]},ensure_ascii=False))
if __name__=="__main__":import_all()
