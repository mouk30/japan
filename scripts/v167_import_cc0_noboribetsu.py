#!/usr/bin/env python3
"""Fetch and self-host ONE explicitly CC0 Hokkaido real photo.
Source: https://commons.wikimedia.org/wiki/File:Noboribetsu_Onsen_hot_spring.jpg
Photographer: Lawsonstu; captured 2015-04-07; CC0 1.0.
PanStar brand image is NOT copied: remains credited official external source.
"""
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageOps
import urllib.request, time, json

sources=[
"https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Noboribetsu_Onsen_hot_spring.jpg/1280px-Noboribetsu_Onsen_hot_spring.jpg",
"https://commons.wikimedia.org/wiki/Special:Redirect/file/Noboribetsu_Onsen_hot_spring.jpg?width=1280",
"https://upload.wikimedia.org/wikipedia/commons/6/68/Noboribetsu_Onsen_hot_spring.jpg",
]
srcfile=None;photo=None;error=""
for source in sources:
 try:
  request=urllib.request.Request(source,headers={"User-Agent":"NIPPONFERRY-Editorial-PhotoVerification/1.0 (+https://www.nipponferry.com; Wikimedia CC0 editorial reuse)","Accept":"image/avif,image/webp,image/jpeg,image/*"})
  with urllib.request.urlopen(request,timeout=20) as response:
   payload=response.read(8_000_000)
  im=Image.open(BytesIO(payload));im.load()
  if im.width<1200 or im.height<700:raise RuntimeError(f"Too small: {im.size}")
  photo=im;srcfile=source;break
 except Exception as e:
  error=str(e);print("RETRY",source,error,flush=True);time.sleep(2)
if photo is None:raise SystemExit("No verified photographic bytes fetched: "+error)
# do not upscale; high quality sRGB and keep full image, CSS owns 4:3 crop.
im=ImageOps.exif_transpose(photo).convert("RGB")
im.thumbnail((1800,1350),Image.Resampling.LANCZOS)
out=Path("site/images/v167");out.mkdir(parents=True,exist_ok=True)
dest=out/"noboribetsu-onsen-lawsonstu-cc0-2015.webp"
im.save(dest,"WEBP",quality=88,method=6)
if dest.stat().st_size<30_000:raise SystemExit("Suspicious image size")
meta={
 "original_file":"Noboribetsu Onsen hot spring.jpg",
 "source_page":"https://commons.wikimedia.org/wiki/File:Noboribetsu_Onsen_hot_spring.jpg",
 "photographer":"Lawsonstu",
 "captured":"2015-04-07",
 "license":"CC0-1.0",
 "license_uri":"https://creativecommons.org/publicdomain/zero/1.0/",
 "verified_original_pixels":[photo.width,photo.height],
 "saved_pixels":[im.width,im.height],
 "retrieval_url":srcfile,
 "purpose":"NIPPONFERRY /japan/hokkaido/ actual Noboribetsu hot spring"
}
(out/"noboribetsu-onsen-lawsonstu-cc0-2015.source.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("SUCCESS",dest,im.size,dest.stat().st_size,flush=True)
