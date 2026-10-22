#!/usr/bin/env python3
"""V114 regression: all 10 real-place photos, hash, attribution, old AI removal and SEO."""
import re,json,hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
PLAN="audit-reports/v114/photo-plan.json"
IMPORT="audit-reports/v114/import-result.json"
SEO="audit-reports/v114/seo-baselines.json"
FIELDS={
 "title":r"<title>([^<]*)</title>",
 "description":r'<meta name="description" content="([^"]*)"',
 "canonical":r'<link rel="canonical" href="([^"]*)"',
 "h1":r"<h1[^>]*>([\s\S]*?)</h1>",
 "jsonld":r'<script type="application/ld\+json">([\s\S]*?)</script>'
}
def one(text,regex,field):
    match=re.search(regex,text,re.S)
    if match is None:raise ValueError("Missing "+field)
    return match.group(1)
def audit(root=ROOT):
    root=Path(root)
    plan=json.loads((root/PLAN).read_text("utf8"))["selected"]
    imp=json.loads((root/IMPORT).read_text("utf8"))["images"]
    bases=json.loads((root/SEO).read_text("utf8"))["pages"]
    frozen={x["slug"]:x for x in bases}
    images={x["slug"]:x for x in imp}
    errs=[];done=0
    if len(plan)!=len(frozen) or len(plan)!=len(images) or len(plan)!=10:
        errs.append("V114 requires 10 original pages + 10 converted photos")
    for spec in plan:
        slug=spec["slug"]
        try:
            d=images[slug]
            html=(root/"site/things-to-do"/(slug+"-cruise-port-day-trip")/"index.html").read_text("utf8")
            old=frozen[slug]
            for field,regex in FIELDS.items():
                if one(html,regex,field)!=old[field]:
                    errs.append(slug+" original SEO drift: "+field)
            if one(html,r'<meta property="og:image" content="([^"]+)"',"OG")!="https://www.nipponferry.com"+spec["output"]:
                errs.append(slug+" OG mismatch with new WebP")
            found=re.findall(r'<img\b[^>]*src="'+re.escape(spec["output"])+r'"[^>]*>',html)
            if len(found)!=1:errs.append(slug+" exactly one real-place hero is required")
            else:
                img=found[0]
                if "class=\"cover\"" not in img:errs.append(slug+" cover image class missing")
                if "onerror=" in img:errs.append(slug+" generic ferry fallback still active")
                for val in [f'width="{d["pixel_width"]}"',f'height="{d["pixel_height"]}"',"실사","촬영일","크루즈 접안부두"]:
                    if val not in img:errs.append(slug+" missing image descriptor: "+val)
            if re.search(r'<img\b[^>]*src="'+re.escape(old["hero"])+r'"',html):
                errs.append(slug+" old AI hero still displayed")
            credits=re.findall(r'<figcaption class="v114-photo-credit"[^>]*>([\s\S]*?)</figcaption>',html)
            if len(credits)!=1:errs.append(slug+" visible rights credit missing/duplicate")
            else:
                for val in [d["source"],spec["license_url"],spec["taken"],spec["author"],spec["license"],"원본 사진에서 WebP"]:
                    if val not in credits[0]:errs.append(slug+" missing original author/license/date "+val)
            raw=(root/"site"/spec["output"].lstrip("/")).read_bytes()
            if hashlib.sha256(raw).hexdigest()!=d["webp_sha256"]:
                errs.append(slug+" WebP changed from verified export")
            if len(raw)!=d["size_bytes"]:errs.append(slug+" WebP byte length changed")
            with Image.open(root/"site"/spec["output"].lstrip("/")) as photo:
                if photo.format!="WEBP" or photo.size!=(d["pixel_width"],d["pixel_height"]):
                    errs.append(slug+" image corrupt / dimensions mismatch")
            done+=1
        except Exception as e:errs.append(slug+" "+str(e))
    return {"passed":not errs,"checked":done,"expected":10,"converted_photos":10,"original_seo_preserved":10,"errors":errs}
if __name__=="__main__":
    r=audit();print(json.dumps(r,ensure_ascii=False,indent=2))
    raise SystemExit(0 if r["passed"] and r["checked"]==10 else 1)
