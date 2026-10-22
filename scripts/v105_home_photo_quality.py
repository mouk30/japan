#!/usr/bin/env python3
"""V105 static maintenance regression for 18 region/theme photo cards.

Checks real source files and the actual HOME HTML. Image/region semantics and
copyright are NOT machine-verified: only a human may approve a new photograph.
This does not change any indexed page automatically.
"""
import argparse
import ast
import copy
import datetime as dt
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image, ImageStat, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "scripts/v105_home_photo_manifest.json"
GROUPS = {
    "popular": {"grid":'class="v65-grid"', "photo_class":"v65-photo", "heading":"인기 여행지", "ratio":"16/10"},
    "daytrips": {"grid":'class="d61-home-grid"', "photo_class":"d61-home-photo", "heading":"도착해서 뭐 하지? 지역별 즐길거리", "ratio":"4/3"},
    "themes": {"grid":'class="v63-grid"', "photo_class":"v63-visual", "heading":"추천 테마 여행", "ratio":"16/10"},
}
STAGED_CLASS = {"popular":"v104-photo-origin","daytrips":"v104-photo-origin","themes":"v63-photo-disclosure"}
KNOWN_KIND = {"illustrative","licensed_photo","reference"}
MISMATCHED_ASSERTIONS = ("실제 장소 촬영 · 2023년","실제 장소 촬영 · 2017년",
                         "도쿄 이미지는 실제 야경 사진입니다")

class PhotoLinkParser(HTMLParser):
    def __init__(self, class_name):
        super().__init__(convert_charrefs=True)
        self.class_name=class_name
        self.entries=[]
        self.current=None

    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        classes=set((attrs.get("class") or "").split())
        if tag=="a" and self.class_name in classes:
            if self.current is not None:
                raise ValueError("Nested photo anchors are invalid")
            self.current={"href":attrs.get("href"),"images":[],"labels":[]}
        elif self.current is not None and tag=="img":
            self.current["images"].append({"src":attrs.get("src"),"alt":attrs.get("alt"),
                "loading":attrs.get("loading"),"width":attrs.get("width"),
                "height":attrs.get("height")})
        elif self.current is not None and tag in ("span","em"):
            if classes & {"v104-photo-origin","v63-photo-disclosure","d61-home-type","v65-type","v63-visual-label"}:
                self.current["labels"].extend(classes)

    def handle_endtag(self,tag):
        if tag=="a" and self.current is not None:
            self.entries.append(self.current)
            self.current=None

def extract_cards(html):
    parsed={}
    for name,g in GROUPS.items():
        start=html.find(g["grid"])
        if start<0:raise ValueError("Missing section grid "+name)
        end=html.find("</section>",start)
        if end<0:raise ValueError("Section does not close "+name)
        block=html[start:end]
        parser=PhotoLinkParser(g["photo_class"])
        parser.feed(block)
        parsed[name]=parser.entries
    return parsed

def audit_markup(html, manifest):
    errors=[]
    try:
        cards=extract_cards(html)
    except ValueError as e:
        return [str(e)],{}
    all_sources=[]
    for group,spec in GROUPS.items():
        expected=manifest["sections"].get(group,[])
        actual=cards.get(group,[])
        if len(actual)!=len(expected):
            errors.append(f"{group}: card count changed: {len(actual)} != {len(expected)}")
        for pos,(card,ref) in enumerate(zip(actual,expected),1):
            prefix=f"{group}[{pos}] {ref['label']}"
            if card["href"]!=ref["href"]:
                errors.append(prefix+": target URL changed: "+str(card["href"]))
            if len(card["images"])!=1:
                errors.append(prefix+": exactly one source image required")
                continue
            img=card["images"][0]
            if img["src"]!=ref["src"]:
                errors.append(prefix+": expected "+ref["src"]+", found "+str(img["src"]))
            all_sources.append(img["src"])
            alt=img["alt"] or ""
            if len(alt)<12 or ref["alt_keyword"] not in alt:
                errors.append(prefix+": alt description missing or no longer matches locale/subject")
            if img["loading"]!="lazy":
                errors.append(prefix+": preserve lazy loading")
            if not img["width"] or not img["height"]:
                errors.append(prefix+": missing explicit width/height attributes")
            label=STAGED_CLASS[group] in card["labels"]
            if ref["kind"]=="illustrative" and not label:
                errors.append(prefix+": staged artwork disclosure disappeared")
            if ref["kind"]!="illustrative" and label:
                errors.append(prefix+": non-staged image incorrectly marked as illustrative")
            if ref["kind"]=="illustrative" and not ("표현한" in alt or "분위기" in alt):
                errors.append(prefix+": creative depiction must not be phrased as verified field photography")
        style_pattern=r"\."+re.escape(spec["photo_class"])+r"\s*\{[^}]*aspect-ratio:\s*"+re.escape(spec["ratio"])+r"\b"
        if not re.search(style_pattern,html):
            errors.append(group+": original image aspect ratio is missing or modified")
    if len(all_sources)!=len(set(all_sources)):
        errors.append("The 18 cards must use distinct, approved thumbnail assets")
    if '<link rel="canonical" href="https://www.nipponferry.com/">' not in html:
        errors.append("Homepage canonical SEO URL missing or changed")
    if not ('<link rel="stylesheet" href="/nf-v104-home-thumbnails.css' in html):
        errors.append("Homepage artwork disclosure stylesheet missing")
    for phrase in MISMATCHED_ASSERTIONS:
        if phrase in html:errors.append("Obsolete photo-origin statement returned: "+phrase)
    for need in ("모지코는 시모노세키와", "여행 분위기 연출 이미지"):
        if need not in html:errors.append("Critical regional disclosure missing: "+need)
    for credit in manifest.get("licensed_credits",[]):
        for field in ("creator","license","url"):
            if str(credit[field]).replace("&","&amp;") not in html and str(credit[field]) not in html:
                errors.append("Licensed photographer attribution missing: "+field+" "+credit["src"])
    return errors,cards

def audit_assets(root,manifest):
    errors=[]
    images=[]
    rules=manifest["image_format_rules"]
    for name,entries in manifest["sections"].items():
        for entry in entries:
            src=entry["src"]
            local=root/"site"/src.lstrip("/")
            prefix=name+" "+entry["label"]
            if entry["kind"] not in KNOWN_KIND:
                errors.append(prefix+": unknown license/photo type")
                continue
            if not src.startswith("/images/") or ".." in src or not local.is_file():
                errors.append(prefix+": source image not in repository "+src)
                continue
            if local.stat().st_size>rules["maximum_bytes"]:
                errors.append(prefix+": asset exceeded expected download size budget")
            try:
                with Image.open(local) as img:
                    img.verify()
                with Image.open(local) as img:
                    width,height=img.size
                    encoding=img.format
                    expected_format="JPEG" if src.lower().endswith(".jpg") else "WEBP"
                    if encoding!=expected_format:
                        errors.append(prefix+": file extension does not match encoded image")
                    if width<rules["minimum_width"] or height<rules["minimum_height"]:
                        errors.append(prefix+": image unexpectedly small or likely blurry")
                    # Flat placeholder detection is only a coarse technical test.
                    thumb=img.convert("L").resize((32,32))
                    contrast=ImageStat.Stat(thumb).stddev[0]
                    if contrast<8:
                        errors.append(prefix+": image is near-uniform / likely placeholder")
                    images.append({"area":name,"label":entry["label"],"url":src,
                                   "width":width,"height":height,"bytes":local.stat().st_size,
                                   "format":encoding,"contrast":round(contrast,2),"kind":entry["kind"]})
            except (OSError,ValueError,UnidentifiedImageError) as e:
                errors.append(prefix+": file cannot be decoded: "+type(e).__name__)
    for credit in manifest["licensed_credits"]:
        if credit.get("manifest"):
            path=root/credit["manifest"]
            if not path.exists():
                errors.append("Licensed source manifest missing: "+credit["manifest"])
                continue
            data=json.loads(path.read_text("utf8"))
            local=root/"site"/credit["src"].lstrip("/")
            if local.is_file():
                actual=hashlib.sha256(local.read_bytes()).hexdigest()
                if data.get("output_sha256")!=actual:
                    errors.append("Licensed photo changed without corresponding author/source review: "+credit["src"])
            for match_key,manifest_key in (("creator","photographer"),("license","license"),("url","original")):
                if credit[match_key]!=data.get(manifest_key):
                    errors.append("Photo source manifest attribution mismatch: "+credit["src"])
    return errors,images

def audit_v104_reference(root,manifest):
    """Detect independent V104 browser-test list falling out of sync."""
    script=(root/"scripts/v104_home_thumbnail_browser_qa.py").read_text("utf8")
    module=ast.parse(script)
    cards_node=next((n.value for n in module.body if isinstance(n,ast.Assign) and
                      any(isinstance(t,ast.Name) and t.id=="CARDS" for t in n.targets)),None)
    if cards_node is None:return ["V104 browser QA manifest missing"]
    cards=ast.literal_eval(cards_node)
    errors=[]
    for group,expected in manifest["sections"].items():
        current=cards.get(group,{}).get("sources",[])
        assets=[x["src"] for x in expected]
        if current!=assets:
            errors.append("V104 browser checks are not synchronized with curated V105 photo manifest: "+group)
    return errors

def run(root=ROOT):
    root=Path(root)
    manifest=json.loads((root/"scripts/v105_home_photo_manifest.json").read_text("utf8"))
    html=(root/"site/index.html").read_text("utf8")
    html_errors,cards=audit_markup(html,manifest)
    file_errors,images=audit_assets(root,manifest)
    reference_errors=audit_v104_reference(root,manifest)
    errs=html_errors+file_errors+reference_errors
    return {
        "stage":"V105",
        "checked_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "status":"source_clean" if not errs else "review_required",
        "card_counts":{k:len(v) for k,v in cards.items()},
        "images_inspected":len(images),"illustrations":sum(x["kind"]=="illustrative" for x in images),
        "licensed_or_reference":sum(x["kind"]!="illustrative" for x in images),
        "assets":images,"errors":errs,
        "limits":[
            "Image recognition or geography is not automatically verified; any new photo requires human editorial review.",
            "Existence or license link metadata alone is not proof of copyright compliance.",
            "Live browser rendering and image responses are tested separately in V104's Playwright QA.",
            "No automatic edits to indexed pages, prices, route URLs or booking links."
        ]
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="audit-output/v105-home-photo-audit")
    args=p.parse_args()
    report=run()
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    (out/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
    lines=["# V105 — homepage editorial image quality and origin", "",
           f"Status: **{report['status']}**","",
           f"Images decoded/inspected: **{report['images_inspected']}/18**",
           f"Staged-image disclosures expected: **{report['illustrations']}/12**",
           f"Licensed photo / subject reference assets: **{report['licensed_or_reference']}/6**",
           f"Observed source problems: **{len(report['errors'])}**",""]
    for error in report["errors"]:lines.append("- "+error)
    lines.extend(["","**Scope:** editorial source, MIME/format, resolution, file corruption, license manifest, 8+4+6 card destination mapping and existing V104 browser QA list.",
      "**Not proven:** photographic location, third-party license rights, or real booking success."])
    (out/"summary.md").write_text("\n".join(lines)+"\n","utf8")
    print(json.dumps({"status":report["status"],"images":report["images_inspected"],
                     "problems":len(report["errors"]),"counts":report["card_counts"],
                     "problem_samples":report["errors"][:12]},ensure_ascii=False))
    return 1 if report["errors"] else 0

if __name__=="__main__":sys.exit(main())
