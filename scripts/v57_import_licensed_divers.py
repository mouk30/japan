#!/usr/bin/env python3
"""Import CC BY 4.0 actual scuba photo from the Okinawa Institute of Science and Technology.
Photographer Shawn Miller / OIST. Do not alter photo content; WebP is a lossy encoding.
"""
from pathlib import Path
from io import BytesIO
from PIL import Image
import urllib.request
import json, hashlib

ROOT=Path(__file__).resolve().parents[1]
source="https://www.oist.jp/sites/default/files/2024-05/51147572901_d2045e6c1c_k.jpg"
out=ROOT/"site/images/nature-verified/okinawa-scuba-divers-oist.webp"
req=urllib.request.Request(source, headers={"User-Agent":"Mozilla/5.0 (compatible; JapanTravelGuideImageCredit/1.0)", "Referer":"https://www.oist.jp/image/coi-next-stream3-coral-reefjpg", "Accept":"image/webp,image/jpeg,image/*;q=0.8"})
with urllib.request.urlopen(req,timeout=25) as r:
    data=r.read(15_000_000)
assert 10000<len(data)<15_000_000, "Unexpected image byte count"
with Image.open(BytesIO(data)) as im:
    assert im.width>=700 and im.height>=450 and im.format in {"JPEG","PNG","WEBP"}
    im=im.convert("RGB")
    im.thumbnail((1400,1000))
    out.parent.mkdir(parents=True,exist_ok=True)
    im.save(out,"WEBP",quality=84,method=5)
with Image.open(out) as im:
    assert im.format=="WEBP" and im.width>=700 and im.height>=450
record={
 "asset":"/images/nature-verified/okinawa-scuba-divers-oist.webp",
 "source_url":"https://www.oist.jp/image/coi-next-stream3-coral-reefjpg",
 "original_photo_url":source,
 "author":"Shawn Miller/OIST",
 "license":"CC BY 4.0",
 "license_url":"https://creativecommons.org/licenses/by/4.0/",
 "photographed":"Okinawa coral reef divers, 2024",
 "processing":"Converted to WebP and resized for site performance",
 "sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
 "file_size":out.stat().st_size
}
doc=ROOT/"docs/v57-okinawa-diver-photo-source.json"
doc.parent.mkdir(parents=True,exist_ok=True)
doc.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(f"V57: imported {out} - {record['file_size']} bytes, source: {source}")
