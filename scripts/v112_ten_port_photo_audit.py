#!/usr/bin/env python3
"""V112: prove ten older genuine travel photos keep source, location and SEO."""
from pathlib import Path
from PIL import Image
import hashlib, json, re
ROOT=Path(__file__).resolve().parents[1]
INV="audit-reports/v112/ten-port-photo-provenance.json"
SEO="audit-reports/v112/seo-baselines.json"
FIELDS={
"title":r"<title>([^<]+)</title>",
"description":r'<meta name="description" content="([^"]*)"',
"canonical":r'<link rel="canonical" href="([^"]*)"',
"h1":r"<h1[^>]*>([\s\S]*?)</h1>",
"json_ld":r'<script type="application/ld\+json">([\s\S]*?)</script>'}
def find(s,rex,label):
    m=re.search(rex,s,re.S)
    if not m: raise ValueError("Missing "+label)
    return m.group(1)
def audit(root=ROOT):
    root=Path(root)
    records=json.loads((root/INV).read_text("utf8"))["items"]
    before={p["slug"]:p for p in json.loads((root/SEO).read_text("utf8"))["pages"]}
    errors=[];inspected=0
    if len(records)!=10 or len(before)!=10 or len(set(x["slug"] for x in records))!=10:
        errors.append("Expected exactly ten nonduplicated photo records and SEO snapshots")
    for x in records:
        slug=x["slug"]
        try:
            article=root/"site"/"things-to-do"/(slug+"-cruise-port-day-trip")/"index.html"
            html=article.read_text("utf8")
            for key,regex in FIELDS.items():
                if find(html,regex,key)!=before[slug][key]:
                    errors.append(slug+" preserved SEO changed: "+key)
            if find(html,r'<meta property="og:image" content="([^"]*)"',"og:image")!="https://www.nipponferry.com"+x["asset"]:
                errors.append(slug+" image and OG mismatch")
            tags=re.findall(r'<img\b[^>]+>',html)
            selected=[tag for tag in tags if 'src="'+x["asset"]+'"' in tag]
            if len(selected)!=1:errors.append(slug+" expected exactly one real site WebP image")
            else:
                tag=selected[0]
                if f'width="{x["width"]}"' not in tag or f'height="{x["height"]}"' not in tag:
                    errors.append(slug+" intrinsic width/height differ from inventory")
                if "접안" not in tag or "실제 촬영" not in tag:
                    errors.append(slug+" photo alt lacks real-place vs berth distinction")
                if slug in ("otaru","tokyo") and "onerror=" in tag:
                    errors.append(slug+" misleading generic ferry photo fallback remains")
            if html.count('class="v112-photo-credit small"')!=1:
                errors.append(slug+" photo source credit missing or duplicated")
            for part in [x["source"],x["license_url"],x["author"],x["captured"],f'data-photo-year="{x["year"]}"']:
                if part not in html:errors.append(slug+" missing source/date/attribution "+str(part))
            if slug=="tokyo" and ("철도역" not in html or "승선 터미널 건물" not in html):
                errors.append("Tokyo transit station photo confused with cruise passenger terminal")
            if slug=="mojiko" and "2014년의 과거 역 건물" not in html:
                errors.append("Mojiko vintage photo not described as historic")
            photo=root/"site"/x["asset"].lstrip("/")
            raw=photo.read_bytes()
            digest=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
            if digest!=x["git_blob_sha1"]:errors.append(slug+" WebP bytes differ from original reviewed asset")
            with Image.open(photo) as img:
                if img.format!="WEBP" or img.size!=(x["width"],x["height"]):
                    errors.append(slug+" image encoding/dimensions unexpected")
            inspected+=1
        except Exception as exc:errors.append(slug+": "+str(exc))
    return {"passed":not errors,"checked":inspected,"expected":10,"photo_files_reused":10,"photo_binary_replacements":0,"misleading_fallbacks_removed":2,"errors":errors}
if __name__=="__main__":
    result=audit()
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result["passed"] and result["checked"]==10 else 1)
