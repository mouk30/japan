#!/usr/bin/env python3
"""V113 visual polish: use an exterior Ainu cise instead of an interior hearth;
remove Korean alt/caption grammatical errors on all ten existing cruise guides.
Preserve SEO title, description, H1, canonical, JSON-LD, and screenshot metadata.
"""
import hashlib, io, json, re, time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request,urlopen
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/"audit-reports/v113/photo-import-plan.json"
RESULT=ROOT/"audit-reports/v113/import-result.json"
SEO=ROOT/"audit-reports/v113/seo-baselines.json"
NEW="Shiraoi-upopoy 14.jpg"
NEW_SUBJECT="시라오이 우포포이 전통 아이누 가옥(치세) 외관"
def readphoto(filename):
    url="https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(filename,safe="")+"?width=1400"
    for i in range(4):
        try:
            with urlopen(Request(url,headers={"User-Agent":"NipponFerryEditorialAudit/1.0 (https://www.nipponferry.com/contact/)"}),timeout=60) as response:
                data=response.read(16_000_001)
                if len(data)<10000 or len(data)>16000000:raise ValueError("Invalid content size")
                return data
        except Exception:
            if i==3:raise
            time.sleep((i+1)*3)
source=readphoto(NEW)
with Image.open(io.BytesIO(source)) as im:
    im=ImageOps.exif_transpose(im).convert("RGB")
    im.thumbnail((1400,1000),Image.Resampling.LANCZOS)
    out=io.BytesIO()
    im.save(out,format="WEBP",quality=84,method=6)
    data=out.getvalue()
    w,h=im.size
if data[0:4]!=b"RIFF" or data[8:12]!=b"WEBP":raise ValueError("Image invalid")
planned=json.loads(PLAN.read_text("utf8"))["items"]
result=json.loads(RESULT.read_text("utf8"))
frozen={x["slug"]:x for x in json.loads(SEO.read_text("utf8"))["articles"]}
imported={x["slug"]:x for x in result["items"]}
updated={}
for x in planned:
    slug=x["slug"]
    p=ROOT/"site/things-to-do"/(slug+"-cruise-port-day-trip")/"index.html"
    html=p.read_text("utf8")
    before=frozen[slug]
    patterns={"title":r"<title>([^<]*)</title>","description":r'<meta name="description" content="([^"]*)"',
              "canonical":r'<link rel="canonical" href="([^"]*)"',
              "h1":r"<h1[^>]*>([\s\S]*?)</h1>",
              "jsonld":r'<script type="application/ld\+json">([\s\S]*?)</script>'}
    source_url=x["commons_url"];subject=x["subject"]
    if slug=="shiraoi":
        subject=NEW_SUBJECT
        source_url="https://commons.wikimedia.org/wiki/File:"+quote(NEW,safe="")
        photo=ROOT/"site/images/venues/nf-v113-shiraoi-real.webp"
        photo.write_bytes(data)
        imported[slug].update({"original_jpeg_url":"https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(NEW,safe=""),
                               "orig_jpeg_sha256":hashlib.sha256(source).hexdigest(),"sha256":hashlib.sha256(data).hexdigest(),
                               "width":w,"height":h,"source":source_url,"taken":x["taken"]})
    article=imported[slug]
    hero=re.search(r'<img class="cover" src="'+re.escape(x["output"])+r'"[^>]*>',html)
    if not hero:raise ValueError("Missing reviewed cover on "+slug)
    updated_alt=f'{x["city"]} 관광지 실사: {subject}. 촬영일 {x["taken"]}. 현재 크루즈 접안부두 또는 승객 하선 게이트 모습이 아닙니다.'
    cover=hero.group().replace(re.search(r'alt="[^"]+"',hero.group()).group(),f'alt="{updated_alt}"')
    if slug=="shiraoi":
        cover=re.sub(r'width="\d+"',f'width="{w}"',cover)
        cover=re.sub(r'height="\d+"',f'height="{h}"',cover)
    html=html.replace(hero.group(),cover,1)
    cap=re.search(r'<figcaption class="v113-photo-credit"[^>]*>[\s\S]*?</figcaption>',html)
    if cap is None:raise ValueError("Missing photo credit "+slug)
    credit=(f'<figcaption class="v113-photo-credit" data-taken="{x["taken"]}" '
            f'style="font-size:12px;line-height:1.85;color:#536e81">'
            f'실제 촬영 장소: {subject}. 촬영일: {x["taken"]}. 이 사진은 관광지의 촬영 당시 모습입니다. '
            f'현행 크루즈 접안부두·승객 게이트·셔틀·시설 운영 여부는 사진으로 확인할 수 없습니다. '
            f'사진: {x["author"]} · <a href="{source_url}" target="_blank" rel="noopener noreferrer">원본 촬영 정보</a> · '
            f'<a href="{x["license_url"]}" target="_blank" rel="noopener noreferrer">{x["license"]}</a> · '
            f'원본을 WebP로 축소·형식 변환.</figcaption>')
    html=html.replace(cap.group(),credit,1)
    for key,pattern in patterns.items():
        f=re.search(pattern,html,re.S)
        if not f or f.group(1)!=before[key]:raise ValueError("SEO drift: "+slug+" "+key)
    updated[slug]=html
for slug,html in updated.items():
    (ROOT/"site/things-to-do"/(slug+"-cruise-port-day-trip")/"index.html").write_text(html,"utf8")
result["items"]=[imported[x["slug"]] for x in planned]
result["visual_polish"]="Photo 06 interior hearth corrected to Photo 14 exterior traditional Ainu cise. Ten Korean alt descriptions and visible source captions polished."
RESULT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n","utf8")
(ROOT/"audit-reports/v113/visual-corrections.json").write_text(json.dumps({
 "visual_review_date":"2026-10-22",
 "corrected_slug":"shiraoi","old_file":"Shiraoi-upopoy 06.jpg","old_photo_content":"indoor Ainu hearth",
 "new_file":NEW,"new_photo_subject":NEW_SUBJECT,
 "new_source":"https://commons.wikimedia.org/wiki/File:"+quote(NEW,safe=""),
 "photographer":"Higa4","license":"CC0 1.0","taken":"2020-11-15",
 "new_webp_sha256":hashlib.sha256(data).hexdigest(),"photo_pixel_size":[w,h],
 "alt_and_credit_language_polished":len(updated),"original_seo_preserved":True,
 "no_new_articles_created":True},ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps({"status":"success","replaced_shiraoi_photo":True,"korean_alt_polished":len(updated),"width":w,"height":h},ensure_ascii=False))
