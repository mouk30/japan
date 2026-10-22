#!/usr/bin/env python3
"""V110 audit for 10 existing cruise-port pages: images, source credit and SEO."""
import hashlib,json,re
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]

def capture(text,pattern,label):
    x=re.search(pattern,text,re.S)
    if x is None: raise AssertionError("Missing "+label)
    return x.group(1)

def audit(root=ROOT):
    root=Path(root)
    inventory=json.loads((root/"audit-reports/v110/ten-port-photo-sources.json").read_text("utf8"))
    baselines=json.loads((root/"audit-reports/v110/seo-baselines.json").read_text("utf8"))
    seo={p["slug"]:p for p in baselines["pages"]}
    failures=[]; checked=0
    if len(inventory["items"])!=10 or len(seo)!=10:
        failures.append("Not exactly ten source records and SEO snapshots")
    sources=set()
    for spec in inventory["items"]:
        slug=spec["slug"]; path=root/"site"/"things-to-do"/(slug+"-cruise-port-day-trip")/"index.html"
        try:
            html=path.read_text("utf8")
            baseline=seo[slug]
            fields={
                "title":r"<title>([^<]*)</title>",
                "description":r'<meta name="description" content="([^"]*)"',
                "canonical":r'<link rel="canonical" href="([^"]*)"',
                "h1":r"<h1[^>]*>([\s\S]*?)</h1>",
                "json_ld":r'<script type="application/ld\+json">([\s\S]*?)</script>'
            }
            for key,regex in fields.items():
                if capture(html,regex,key)!=baseline[key]:
                    failures.append(slug+": SEO "+key+" changed")
            if capture(html,r'<meta property="og:image" content="([^"]*)"', "OG image") != "https://www.nipponferry.com"+spec["asset"]:
                failures.append(slug+": wrong OG photo")
            covers=re.findall(r'<img class="cover"[^>]*>',html)
            if len(covers)!=1:
                failures.append(slug+": missing/duplicate cover photo")
            else:
                img=covers[0]
                if 'src="'+spec["asset"]+'"' not in img:
                    failures.append(slug+": wrong cover src")
                if 'width="'+str(spec["width"])+'"' not in img or 'height="'+str(spec["height"])+'"' not in img:
                    failures.append(slug+": incorrect dimensions")
                if "실제" not in img or "접안" not in img:
                    failures.append(slug+": alt must distinguish tourism photo from berth")
            if html.count('class="v110-photo-credit"')!=1:
                failures.append(slug+": one visible credit required")
            for need in (spec["source"],spec["author"],spec["license"],"WebP 크기·형식 변환"):
                if need not in html:failures.append(slug+": origin/credit missing "+need)
            file=root/"site"/spec["asset"].lstrip("/")
            raw=file.read_bytes()
            sha=hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()
            if sha!=spec["sha"]:failures.append(slug+": image bytes differ from reviewed Git blob")
            with Image.open(file) as im:
                if im.format!="WEBP" or list(im.size)!=[spec["width"],spec["height"]]:
                    failures.append(slug+": invalid WebP or intrinsic size")
            if spec["asset"] in sources:failures.append(slug+": repeated photo across ten pages")
            sources.add(spec["asset"])
            checked+=1
        except Exception as e:
            failures.append(slug+": "+str(e))
    return {"pages":checked,"passed":not failures,"visible_images_replaced":sum(x["changed"] for x in inventory["items"]),"og_aligned":len(inventory["items"]),"errors":failures}

if __name__=="__main__":
    result=audit()
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result["passed"] and result["pages"]==10 else 1)
