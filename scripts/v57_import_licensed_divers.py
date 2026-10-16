#!/usr/bin/env python3
"""Import CC BY 2.0 actual scuba divers in Japan from Wikimedia Commons.
Original by Vincent Lou, 2014 Yonaguni. WebP resizing documented as a derivative.
"""
from pathlib import Path
from io import BytesIO
from PIL import Image
import urllib.request
import json, hashlib

ROOT=Path(__file__).resolve().parents[1]
source="https://upload.wikimedia.org/wikipedia/commons/7/7a/Yonaguni_Monument_DSC02807_%2812737575034%29.jpg"
out=ROOT/"site/images/nature-verified/okinawa-yonaguni-scuba-divers.webp"
req=urllib.request.Request(source, headers={"User-Agent":"Mozilla/5.0 (compatible; JapanTravelGuideImageCredit/1.0)", "Referer":"https://commons.wikimedia.org/wiki/File:Yonaguni_Monument_DSC02807_(12737575034).jpg", "Accept":"image/webp,image/jpeg,image/*;q=0.8"})
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
 "author":"Vincent Lou / Wikimedia Commons",
 "license":"CC BY 2.0",
 "license_url":"https://creativecommons.org/licenses/by/2.0/",
 "photographed":"Two divers at Yonaguni Monument, Okinawa, photographed 2014",
 "processing":"Converted to WebP and resized for site performance",
 "sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
 "file_size":out.stat().st_size
}
doc=ROOT/"docs/v57-yonaguni-diver-photo-source.json"
doc.parent.mkdir(parents=True,exist_ok=True)
doc.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(f"V57: imported {out} - {record['file_size']} bytes, source: {source}")
