#!/usr/bin/env python3
"""One-off V85: import a provenance-verified Dotonbori photograph for route banners."""
import hashlib, io, json
from pathlib import Path
import requests
from PIL import Image, ImageOps

SOURCE="https://upload.wikimedia.org/wikipedia/commons/f/f3/D%C5%8Dtonbori_at_night%2C_Osaka_%2819551420339%29.jpg"
SOURCE_PAGE="https://commons.wikimedia.org/wiki/File:D%C5%8Dtonbori_at_night%2C_Osaka_%2819551420339%29.jpg"
LICENSE="https://creativecommons.org/licenses/by/2.0/"
TARGET=Path("site/images/venues/nf-v85-osaka-dotonbori-licensed.webp")
headers={"User-Agent":"NIPPONFERRY-Editorial-SourceAudit/1.0 (license attribution and visual QA, educational travel guide)"}
response=requests.get(SOURCE,headers=headers,timeout=60)
response.raise_for_status()
assert len(response.content)>300000,"Downloaded photo too small"
im=Image.open(io.BytesIO(response.content))
assert im.width>1800 and im.height>1200,"Unexpected photo dimensions"
im=ImageOps.exif_transpose(im).convert("RGB")
im.thumbnail((1800,1200),Image.Resampling.LANCZOS)
TARGET.parent.mkdir(parents=True,exist_ok=True)
im.save(TARGET,format="WEBP",quality=85,method=6)
assert TARGET.stat().st_size>70000
info={
 "asset":str(TARGET),
 "depicts":"Dotonbori canal, Namba district, Osaka; NOT a ferry berth",
 "original":SOURCE_PAGE,
 "photographer":"Kristoffer Trolle",
 "taken":"2015-06-30",
 "license":"CC BY 2.0",
 "license_url":LICENSE,
 "modification":"WebP resize to max 1800x1200 from original JPEG; photo used as city reference, not departure image.",
 "source_sha256":hashlib.sha256(response.content).hexdigest(),
 "output_sha256":hashlib.sha256(TARGET.read_bytes()).hexdigest(),
 "width":im.width,"height":im.height
}
Path("site/images/venues/nf-v85-osaka-dotonbori-licensed.source.json").write_text(json.dumps(info,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
print(json.dumps(info,indent=2))
