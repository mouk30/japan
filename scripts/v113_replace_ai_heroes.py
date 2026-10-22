#!/usr/bin/env python3
"""V113 - replacement of ten AI title images only after full Commons source retrieval.
Runs inside GitHub Actions. All-or-nothing: no HTML is changed until all ten valid
licensed originals are downloaded and converted. Article SEO remains byte-identical.
"""
from __future__ import annotations
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote, urlencode
from urllib.error import HTTPError
from PIL import Image, ImageOps, UnidentifiedImageError
import io, hashlib, json, re, time, sys

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"audit-reports/v113/photo-import-plan.json"
SEO=ROOT/"audit-reports/v113/seo-baselines.json"
REPORT=ROOT/"audit-reports/v113/import-result.json"
HEADERS={"User-Agent":"NipponFerryEditorialAudit/1.0 (https://www.nipponferry.com/contact/; verifying attributed Commons photos)","Accept":"image/avif,image/webp,image/jpeg,image/png,*/*"}
SEO_PATTERNS={
"title":r"<title>([^<]*)</title>",
"description":r'<meta name="description" content="([^"]*)"',
"canonical":r'<link rel="canonical" href="([^"]*)"',
"h1":r"<h1[^>]*>([\s\S]*?)</h1>",
"jsonld":r'<script type="application/ld\+json">([\s\S]*?)</script>'}
def group(data,pattern,name):
    match=re.search(pattern,data,re.S)
    if not match:raise ValueError("Missing "+name)
    return match.group(1)
def download(file):
    url="https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(file,safe="")+"?width=1400"
    errors=[]
    for i in range(4):
        try:
            with urlopen(Request(url,headers=HEADERS),timeout=60) as r:
                data=r.read(16_000_001)
                if len(data)>16_000_000 or len(data)<12_000:
                    raise ValueError("Invalid photo source byte count "+str(len(data)))
                content_type=r.headers.get("Content-Type","")
                if "text/html" in content_type:
                    raise ValueError("Photo source returned HTML rather than image")
                return data, r.url
        except Exception as e:
            errors.append(type(e).__name__+": "+str(e)[:110])
            if i<3:time.sleep(3*(i+1))
    raise RuntimeError("Commons download failed for "+file+": "+"; ".join(errors))
def run():
    entries=json.loads(P.read_text("utf8"))["items"]
    prior={x["slug"]:x for x in json.loads(SEO.read_text("utf8"))["articles"]}
    if len(entries)!=10 or len(prior)!=10:raise ValueError("Expected exactly ten photos and frozen articles")
    edits=[]
    for x in entries:
        slug=x["slug"]
        page=ROOT/"site/things-to-do"/(slug+"-cruise-port-day-trip")/"index.html"
        html=page.read_text("utf8")
        frozen=prior[slug]
        for k,pattern in SEO_PATTERNS.items():
            if group(html,pattern,k)!=frozen[k]:raise ValueError(slug+": SEO already drifted "+k)
        old_src=frozen["previous_image"]
        if not old_src.startswith("/images/editorial/"):raise ValueError("Only edit confirmed AI hero: "+slug)
        tag_match=re.search(r'<img\b[^>]*src="'+re.escape(old_src)+r'"[^>]*>',html)
        if tag_match is None:raise ValueError(slug+": original AI img missing")
        tag=tag_match.group()
        where=tag_match.end()
        cap=re.match(r'\s*<(figcaption|p)\b[^>]*>[\s\S]*?</\1>',html[where:])
        if cap is None:raise ValueError(slug+": immediate AI caption missing")
        old_og=group(html,r'<meta property="og:image" content="([^"]*)"', "OG image")
        if old_og!=frozen["previous_og"]:raise ValueError(slug+": prior OG changed")
        photo, origin=download(x["file"])
        with Image.open(io.BytesIO(photo)) as opened:
            im=ImageOps.exif_transpose(opened).convert("RGB")
            if im.width<550 or im.height<390:raise ValueError(slug+": picture too small")
            im.thumbnail((1400,1000),Image.Resampling.LANCZOS)
            binary=io.BytesIO()
            im.save(binary,format="WEBP",quality=84,method=6)
            contents=binary.getvalue()
            width,height=im.size
        if not contents.startswith(b"RIFF") or contents[8:12]!=b"WEBP" or len(contents)<8000:
            raise ValueError(slug+": invalid converted WebP")
        caption=(f'<figcaption class="v113-photo-credit" data-taken="{x["taken"]}" style="font-size:12px;line-height:1.85;color:#536e81">'
                 f'{x["subject"]} 실제 장소의 {x["taken"]} 촬영 자료입니다. 관광시설의 과거 모습이며 '
                 f'현행 크루즈 접안부두·승객 게이트·셔틀·시설 운영 여부를 증명하지 않습니다. '
                 f'사진: {x["author"]} · <a href="{x["commons_url"]}" rel="noopener noreferrer" target="_blank">원본 사진</a> · '
                 f'<a href="{x["license_url"]}" rel="noopener noreferrer" target="_blank">{x["license"]}</a> · '
                 f'원본에서 WebP로 축소·형식 변환. 저작자 및 이용 조건은 원본 링크 참조.</figcaption>')
        caption_start=where
        # Preserve whitespace and replace only the original adjacent AI caption.
        html=html[:caption_start]+html[caption_start:].replace(cap.group(),caption,1)
        alt=(f'{x["city"]}의 {x["subject"]}을 보여주는 {x["taken"]} 실제 촬영 사진. '
             f'크루즈 접안부두나 현행 하선 게이트의 사진이 아닙니다.')
        newtag=(f'<img class="cover" src="{x["output"]}" alt="{alt}" width="{width}" '
                f'height="{height}" decoding="async" fetchpriority="high">')
        if html.count(tag)!=1:raise ValueError(slug+": AI tag ambiguous")
        html=html.replace(tag,newtag,1)
        html=html.replace(f'<meta property="og:image" content="{old_og}">',
                          f'<meta property="og:image" content="https://www.nipponferry.com{x["output"]}">',1)
        # Change twitter card image only if it matched precisely the old AI image.
        html=html.replace(f'<meta name="twitter:image" content="{old_og}">',
                          f'<meta name="twitter:image" content="https://www.nipponferry.com{x["output"]}">')
        html=html.replace(f'<meta property="twitter:image" content="{old_og}">',
                          f'<meta property="twitter:image" content="https://www.nipponferry.com{x["output"]}">')
        for k,pattern in SEO_PATTERNS.items():
            if group(html,pattern,k)!=frozen[k]:raise ValueError(slug+": modified protected "+k)
        if old_src in html and '<img' in html:
            # Existing secondary uses can legitimately remain, but no AI hero remains
            if re.search(r'<img\b[^>]*src="'+re.escape(old_src)+r'"',html):
                raise ValueError(slug+": stale AI illustration image remains")
        edits.append({"slug":slug,"page":page,"content":html,"bytes":contents,"dst":ROOT/"site"/x["output"].lstrip("/"),
                      "original_jpeg_url":origin,"orig_jpeg_sha256":hashlib.sha256(photo).hexdigest(),
                      "sha256":hashlib.sha256(contents).hexdigest(),"width":width,"height":height,
                      "source":x["commons_url"],"author":x["author"],"license":x["license"],
                      "previous_ai_image":old_src,"replaced":x["output"],"taken":x["taken"]})
        print(f"PREPARED {slug}: {width}x{height}, {len(contents)} bytes",flush=True)
    # All 10 verified; now publish bytes and markup atomically in a single git commit.
    for entry in edits:
        entry["dst"].parent.mkdir(parents=True,exist_ok=True)
        entry["dst"].write_bytes(entry["bytes"])
        entry["page"].write_text(entry["content"],encoding="utf8")
    report={"version":"V113","status":"all_10_source_photos_ready","date":"2026-10-22",
            "photo_replacements":len(edits),"seo_preserved":len(edits),"items":[
            {k:v for k,v in e.items() if k not in ("page","content","bytes","dst")}
            for e in edits]}
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
    print(json.dumps({"passed":True,"replaced":len(edits),"pages":len(edits),"result":str(REPORT)},ensure_ascii=False))
if __name__=="__main__":
    run()
