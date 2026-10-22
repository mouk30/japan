#!/usr/bin/env python3
"""V124 check 3 licensed scenic WebPs, their exact homepage card mapping,
visible on-page attribution, preserved homepage SEO, and prior assets not deleted."""
from pathlib import Path
import json,hashlib,re
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];SITE=ROOT/"site"
p=json.loads((ROOT/"audit-reports/v124/photo-plan.json").read_text("utf8"))["photos"]
a=json.loads((ROOT/"audit-reports/v124/import-result.json").read_text("utf8"))
h=(SITE/"index.html").read_text("utf8")
assert a["card_updates"]==3 and a["home_seo_preserved"]
assert len(p)==len(a["images"])==3
for x in p:
 row=next(y for y in a["images"] if y["slug"]==x["slug"])
 file=SITE/x["output"].lstrip("/")
 assert file.exists(),str(file)
 data=file.read_bytes()
 assert data[:4]==b"RIFF" and data[8:12]==b"WEBP"
 assert hashlib.sha256(data).hexdigest()==row["sha256"]
 with Image.open(file) as im:assert im.format=="WEBP" and im.size==(1200,800)
 pattern=(r'<article class="d61-home-card"><a class="d61-home-photo" href="'
     +re.escape(x["href"])+r'"[\s\S]*?<img[^>]*src="'+re.escape(x["output"])+r'"[^>]*>')
 assert len(re.findall(pattern,h))==1,x["slug"]+" wrong card mapping"
 assert h.count(x["source"])==1 and x["author"] in h and x["taken"] in h and x["license"] in h
 assert (SITE/x["old"].lstrip("/")).exists(),"Do not remove original photo; other pages may reuse it."
 assert x["old"] not in re.search(r'<article class="d61-home-card"><a class="d61-home-photo" href="'+re.escape(x["href"])+r'"[\s\S]*?</article>',h).group(0)
assert "<title>일본크루즈 여행 | 가격·일정·기항지 | 일본페리</title>" in h
assert '<link rel="canonical" href="https://www.nipponferry.com/">' in h
assert h.count('class="d61-home-card"')==4
print(json.dumps({"version":"V124","cards":3,"webps_valid":3,"attribution_links":3,"source_seo_kept":True,"status":"passed"},ensure_ascii=False))
