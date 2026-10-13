#!/usr/bin/env python3
"""V10 rights-reviewed photo conversion. Outputs review artifacts; does not deploy images automatically."""
from pathlib import Path
from urllib.request import urlopen, Request
import io,json
from PIL import Image, ImageOps
registry=[
 {"id":"osaka-kaiyukan","url":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Kaiy%C5%ABkan.jpg","page":"https://commons.wikimedia.org/wiki/File:Kaiy%C5%ABkan.jpg","author":"Sakai Yayoi","license":"CC0 1.0","date":"2026-05-07","subject":"오사카 가이유칸 실제 건물 항공 사진"}
]
out=Path("photo-review");out.mkdir(exist_ok=True)
reports=[]
for item in registry:
 try:
  req=Request(item["url"],headers={"User-Agent":"NipponFerryEditorialPhotoReview/1.0 (photo-license-checked)"})
  with urlopen(req,timeout=30) as response:
   data=response.read(12000000)
  im=Image.open(io.BytesIO(data)); im=ImageOps.exif_transpose(im).convert("RGB")
  im.thumbnail((1200,1200),Image.Resampling.LANCZOS)
  target=out/(item["id"]+".webp")
  im.save(target,format="WEBP",quality=83,method=6)
  reports.append({**item,"review_status":"converted_pending_editor_review","file":str(target),"dimensions":list(im.size),"bytes":target.stat().st_size})
 except Exception as e:reports.append({**item,"review_status":"download_failed","error":str(e)})
(out/"manifest.json").write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(reports,ensure_ascii=False,indent=2))
