#!/usr/bin/env python3
"""V140 final Okinawa replacement after reviewing real public screenshots.
Uses Commons photo showing actual Kouri Bridge and sea, not beach foreground.
All old SEO & mobile CSS preserved, photo credit/link corrected.
"""
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen,Request
from PIL import Image,ImageOps
from io import BytesIO
from hashlib import sha256
import json,re
ROOT=Path(__file__).resolve().parents[1]
HOME=ROOT/"site/index.html"
REPORT=ROOT/"audit-reports/v140/import-report.json"
data=json.loads(REPORT.read_text("utf8"))
old=HOME.read_text("utf8")
rec=next(x for x in data["source_photos"] if x["key"]=="okinawa")
old_dest=rec["dest"];old_source=rec["source"];old_author=rec["author"];old_date=rec["date"];old_license=rec["license"];old_license_url=rec["licurl"]
fn="Kouri Bridge (15130568259).jpg"
source="https://commons.wikimedia.org/wiki/File:Kouri_Bridge_(15130568259).jpg"
author="Takuya ASADA"
date="2014-09-21"
license="CC BY 2.0"
license_url="https://creativecommons.org/licenses/by/2.0/"
dest="/images/venues/nf-v140-okinawa-kouri-bridge-view-2014-real.webp"
alt="2014년 9월 고우리 오션타워에서 촬영한 오키나와 고우리대교와 에메랄드빛 바다의 실제 전경"
assert old.count('src="'+old_dest+'"')==1
assert old.count('href="'+old_source+'"')==1
assert old.count("v140-credit")==1
url="https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(fn,safe="")+"?width=1400"
with urlopen(Request(url,headers={"User-Agent":"NipponFerryCommonsQA/1.0 (https://www.nipponferry.com/)"}),timeout=75) as response:
  if "image/" not in response.headers.get("Content-Type",""):raise RuntimeError("not an image")
  raw=response.read(14000001)
photo=ImageOps.exif_transpose(Image.open(BytesIO(raw))).convert("RGB")
assert photo.width>=950 and photo.height>=630
photo.thumbnail((1400,1000),Image.Resampling.LANCZOS)
out=BytesIO()
photo.save(out,format="WEBP",quality=86,method=6)
blob=out.getvalue()
assert blob[:4]==b"RIFF" and blob[8:12]==b"WEBP" and len(blob)>20000
m=re.search(r'<img src="'+re.escape(old_dest)+r'" alt="[^"]+"',old)
assert m
new='<img src="'+dest+'" alt="'+alt+'"'
s=old[:m.start()]+new+old[m.end():]
old_credit='<a href="'+old_source+'" target="_blank" rel="noopener noreferrer">okinawa · '+old_author+' · '+old_date+' · '+old_license+' (원본 WebP 변환·축소)</a> (<a href="'+old_license_url+'" target="_blank" rel="noopener noreferrer">라이선스</a>)'
new_credit='<a href="'+source+'" target="_blank" rel="noopener noreferrer">오키나와 · '+author+' · '+date+' · '+license+' (원본 크기 조정·WebP 변환)</a> (<a href="'+license_url+'" target="_blank" rel="noopener noreferrer">라이선스</a>)'
assert s.count(old_credit)==1,"Original V140 caption unexpected"
s=s.replace(old_credit,new_credit,1)
for rx in [r'<title>[^<]*</title>',r'<meta name="description"[^>]*>',r'<link rel="canonical"[^>]*>',r'<script type="application/ld\+json">.*?</script>']:
  assert re.search(rx,old).group()==re.search(rx,s).group(),"SEO regression "+rx
assert 'nf-v137-mobile-readability.css' in s and 'nf-v138-mobile-polish.css' in s
path=ROOT/"site"/dest.lstrip("/")
path.parent.mkdir(parents=True,exist_ok=True)
path.write_bytes(blob)
HOME.write_text(s,"utf8")
data["visual_correction"]="V140 public screenshot review: first Okinawa photo showed beach foreground, Kouri Bridge not recognizable; replaced with bridge-focused original."
data["superseded_okinawa_photo"]={"path":old_dest,"source":old_source,"author":old_author,"license":old_license,"file_retained_in_repo":True}
rec.update({"file":fn,"dest":dest,"alt":alt,"author":author,"date":date,"license":license,"licurl":license_url,"size":[photo.width,photo.height],"sha256":sha256(blob).hexdigest(),"source":source})
REPORT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps({"new_hero":dest,"dimensions":[photo.width,photo.height],"bytes":len(blob),"sha256":rec["sha256"],"source":source},ensure_ascii=False))
