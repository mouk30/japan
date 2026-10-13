#!/usr/bin/env python3
"""V10: convert rights-reviewed Wikimedia photos to site-local WebP and rewrite their URLs.
Requires Pillow and network access in GitHub Actions. Fail closed on download problems.
"""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote
from PIL import Image, ImageOps
import io,json
root=Path("site")
items=[
 ("DMM_Kariyushi_Aquarium_202106_14.jpg","naha-dmm-kariyushi-aquarium","Kugel~commonswiki","CC BY-SA 4.0"),
 ("Shurei-mon.jpeg","naha-shureimon","nnh","public domain"),
 ("Shigira_Bayside_Suite_ALLAMANDA09s3s4592.jpg","miyakojima-shigira-allamanda","663highland","CC BY-SA 3.0")
]
paths=list((root/"things-to-do").glob("*-cruise-*-guide/index.html"))
image_dir=root/"images"/"venues";image_dir.mkdir(parents=True,exist_ok=True)
report=[]
for filename,slug,author,license in items:
 url="https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(filename)+"?width=1280"
 try:
  req=Request(url,headers={"User-Agent":"NIPPONFERRY content quality audit/1.0 (https://www.nipponferry.com/)"})
  with urlopen(req,timeout=35) as req_stream:
   data=req_stream.read(16*1024*1024)
  im=Image.open(io.BytesIO(data));im=ImageOps.exif_transpose(im).convert("RGB")
  im.thumbnail((1200,900),Image.Resampling.LANCZOS)
  dest=image_dir/(slug+".webp");im.save(dest,"WEBP",quality=82,method=6)
  assert dest.stat().st_size>3000
  updated=[]
  for page in paths:
   html=page.read_text(encoding="utf-8")
   original=html
   from_url="https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(filename)+"?width=640"
   from_url_alt="https://commons.wikimedia.org/wiki/Special:FilePath/"+filename+"?width=640"
   html=html.replace(from_url,'/images/venues/'+slug+'.webp').replace(from_url_alt,'/images/venues/'+slug+'.webp')
   # Fix legacy wrong captions where sources were changed
   if html!=original:page.write_text(html,encoding="utf-8");updated.append(str(page))
  report.append({"image":slug,"status":"success","bytes":dest.stat().st_size,"dimensions":im.size,"author":author,"license":license,"updated_pages":updated})
 except Exception as exc:report.append({"image":slug,"status":"failed","error":str(exc)})
Path("site/images/venues/manifest.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps(report,indent=2,ensure_ascii=False))
if any(x["status"]=="failed" for x in report):raise SystemExit(1)
