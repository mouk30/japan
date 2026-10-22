#!/usr/bin/env python3
"""V128 strict regression for ten real-venue WebPs and protected old article SEO."""
import hashlib,json,re
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/"audit-reports/v128/photo-plan.json"
BASE=ROOT/"audit-reports/v128/seo-and-ai-candidate-baselines.json"
REPORT=ROOT/"audit-reports/v128/import-result.json"
PATTERNS={
 "title":r"<title>([^<]*)</title>",
 "description":r'<meta name="description" content="([^"]*)"',
 "canonical":r'<link rel="canonical" href="([^"]*)"',
 "h1":r"<h1[^>]*>([\s\S]*?)</h1>",
 "jsonld":r'<script type="application/ld\+json">([\s\S]*?)</script>'
}
def get(html,pat):
    m=re.search(pat,html,re.S)
    if not m:raise ValueError("Missing pattern "+pat[:60])
    return m.group(1)
def check():
    selection=json.loads(PLAN.read_text("utf8"))["selected"]
    previous={x["slug"]:x for x in json.loads(BASE.read_text("utf8"))["pages"]}
    record=json.loads(REPORT.read_text("utf8"))
    exported={x["slug"]:x for x in record["images"]}
    failures=[];passed=0
    if len(selection)!=len(previous)!=len(exported):failures.append("Mismatched batch counts")
    if len(selection)!=10 or len(previous)!=10 or len(exported)!=10:failures.append("Must audit exactly 10 pages")
    for s in selection:
        slug=s["slug"]
        try:
            p=previous[slug];e=exported[slug]
            h=(ROOT/"site"/p["page"].lstrip("/")/"index.html").read_text("utf8")
            for name,regex in PATTERNS.items():
                if get(h,regex)!=p[name]:failures.append(slug+" protected SEO drift "+name)
            target="https://www.nipponferry.com"+s["output"]
            if get(h,r'<meta property="og:image" content="([^"]+)"')!=target:
                failures.append(slug+" OG not linked to new photograph")
            img=re.findall(r'<img\b[^>]*class="cover"[^>]*src="'+re.escape(s["output"])+r'"[^>]*>',h)
            if len(img)!=1:failures.append(slug+" missing/duplicate real hero")
            else:
                if "onerror=" in img[0]:failures.append(slug+" old fallback present")
                if f'width="{e["pixel_width"]}"' not in img[0] or f'height="{e["pixel_height"]}"' not in img[0]:
                    failures.append(slug+" pixel dimensions mismatch")
                for phrase in (s["subject"],s["taken"],"현재 크루즈 접안"):
                    if phrase not in img[0]:failures.append(slug+" alt disclosure missing "+phrase)
            credits=re.findall(r'<figcaption class="v128-photo-credit"[^>]*>([\s\S]*?)</figcaption>',h)
            if len(credits)!=1:failures.append(slug+" source caption missing")
            else:
                for term in (s["author"],s["taken"],s["license"],s["license_url"],s["source"],"WebP","현재 부두"):
                    if term not in credits[0]:failures.append(slug+" source rights missing "+term)
                if s.get("extra_credit") and s["extra_credit"] not in credits[0]:
                    failures.append(slug+" source-required attribution missing")
                if "BY-SA" in s["license"] and "동일 CC BY-SA 라이선스" not in credits[0]:
                    failures.append(slug+" share-alike disclosure missing")
            if re.search(r'<img\b[^>]*src="'+re.escape(p["current_hero"])+r'"',h):
                failures.append(slug+" previous AI hero still in visible document")
            binary=(ROOT/"site"/s["output"].lstrip("/")).read_bytes()
            if len(binary)!=e["size_bytes"] or hashlib.sha256(binary).hexdigest()!=e["webp_sha256"]:
                failures.append(slug+" changed WebP hash or byte length")
            with Image.open(ROOT/"site"/s["output"].lstrip("/")) as photo:
                if photo.format!="WEBP" or photo.size!=(e["pixel_width"],e["pixel_height"]):
                    failures.append(slug+" image unreadable or pixel mismatch")
            passed+=1
        except Exception as ex:failures.append(slug+" "+str(ex))
    return {"passed":not failures and passed==10,"checked":passed,"expected":10,"errors":failures}
if __name__=="__main__":
    r=check();print(json.dumps(r,ensure_ascii=False,indent=2))
    raise SystemExit(0 if r["passed"] else 1)
