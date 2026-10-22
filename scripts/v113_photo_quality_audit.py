#!/usr/bin/env python3
"""V113: ten actual Commons photos, source credits, binary fingerprints and frozen SEO."""
from pathlib import Path
import json,re,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def scan(root=ROOT):
    root=Path(root)
    planned=json.loads((root/"audit-reports/v113/photo-import-plan.json").read_text("utf8"))["items"]
    baseline={x["slug"]:x for x in json.loads((root/"audit-reports/v113/seo-baselines.json").read_text("utf8"))["articles"]}
    imported=json.loads((root/"audit-reports/v113/import-result.json").read_text("utf8"))
    latest={x["slug"]:x for x in imported["items"]}
    errs=[];checked=0
    if len(planned)!=10 or len(latest)!=10 or imported["photo_replacements"]!=10:
        errs.append("V113 expected ten distinct real photographs and pages")
    patterns={"title":r"<title>([^<]*)</title>",
      "description":r'<meta name="description" content="([^"]*)"',
      "canonical":r'<link rel="canonical" href="([^"]*)"',
      "h1":r"<h1[^>]*>([\s\S]*?)</h1>",
      "jsonld":r'<script type="application/ld\+json">([\s\S]*?)</script>'}
    for item in planned:
        slug=item["slug"]
        try:
            data=latest[slug]
            page=root/"site/things-to-do"/(slug+"-cruise-port-day-trip")/"index.html"
            html=page.read_text("utf8")
            for field,pattern in patterns.items():
                m=re.search(pattern,html,re.S)
                if not m or m.group(1)!=baseline[slug][field]:
                    errs.append(slug+" original SEO drift "+field)
            og=re.search(r'<meta property="og:image" content="([^"]+)"',html)
            expected="https://www.nipponferry.com"+item["output"]
            if not og or og.group(1)!=expected:errs.append(slug+" photo OG doesn't match")
            real=re.findall(r'<img\b[^>]*src="'+re.escape(item["output"])+r'"[^>]*>',html)
            if len(real)!=1:errs.append(slug+" absent or repeated real hero")
            else:
                img=real[0]
                if "onerror=" in img or "AI 생성" in img:errs.append(slug+" misleading AI photo fallback")
                if f'width="{data["width"]}"' not in img or f'height="{data["height"]}"' not in img:
                    errs.append(slug+" incorrect intrinsic image dimensions")
                if not any(term in img for term in ("실사", "실제")) or "크루즈" not in img or "촬영일" not in img:
                    errs.append(slug+" photo alt not location/time verified")
            if re.search(r'<img\b[^>]*src="'+re.escape(baseline[slug]["previous_image"])+r'"',html):
                errs.append(slug+" staged AI hero still displayed")
            credit=re.findall(r'<figcaption class="v113-photo-credit"[^>]*>([\s\S]*?)</figcaption>',html)
            if len(credit)!=1:errs.append(slug+" source credit not exactly once")
            else:
                for keyword in [data["source"],data["author"],data["license"],data["taken"],
                                item["license_url"],"WebP로 축소·형식 변환"]:
                    if keyword not in credit[0]:errs.append(slug+" missing photo attribution "+str(keyword))
                if "현행 크루즈 접안부두" not in credit[0]:
                    errs.append(slug+" might falsely claim tourist image is active berth")
            photo=root/"site"/item["output"].lstrip("/")
            binary=photo.read_bytes()
            if hashlib.sha256(binary).hexdigest()!=data["sha256"]:
                errs.append(slug+" WebP SHA-256 differs from verified original")
            with Image.open(photo) as im:
                if im.format!="WEBP" or im.size!=(data["width"],data["height"]):
                    errs.append(slug+" WebP corrupt/wrong declared dimensions")
            checked+=1
        except Exception as exc:errs.append(slug+": "+str(exc))
    if latest["shiraoi"]["source"].find("14.jpg")==-1:errs.append("Indoor Ainu hearth not corrected to traditional village")
    return {"passed":not errs,"checked":checked,"expected":10,"webp_images":10,"ai_hero_images_replaced":10,
            "metadata_preserved":10,"errors":errs}
if __name__=="__main__":
    value=scan();print(json.dumps(value,ensure_ascii=False,indent=2))
    raise SystemExit(0 if value["passed"] and value["checked"]==10 else 1)
