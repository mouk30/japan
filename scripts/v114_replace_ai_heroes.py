#!/usr/bin/env python3
"""V114: all-or-none documented Commons photo imports for ten existing cruise pages.
Preserve title, meta description, canonical, H1, JSON-LD and itinerary body.
"""
from __future__ import annotations
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request,urlopen
from PIL import Image,ImageOps
from html import escape
import hashlib,io,json,re,time

ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/"audit-reports/v114/photo-plan.json"
BASE=ROOT/"audit-reports/v114/seo-baselines.json"
REPORT=ROOT/"audit-reports/v114/import-result.json"
PATTERNS={
 "title":r"<title>([^<]*)</title>",
 "description":r'<meta name="description" content="([^"]*)"',
 "canonical":r'<link rel="canonical" href="([^"]*)"',
 "h1":r"<h1[^>]*>([\s\S]*?)</h1>",
 "jsonld":r'<script type="application/ld\+json">([\s\S]*?)</script>',
}
def find(data,pattern,kind):
    m=re.search(pattern,data,re.S)
    if not m:raise ValueError("Missing "+kind)
    return m.group(1)
def download(filename):
    url="https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(filename,safe="")+"?width=1400"
    failures=[]
    for i in range(4):
        try:
            req=Request(url,headers={
             "User-Agent":"NipponFerryEditorialAudit/1.0 (https://www.nipponferry.com/contact/)",
             "Accept":"image/jpeg,image/png,image/webp,*/*"})
            with urlopen(req,timeout=65) as response:
                if response.status!=200:raise ValueError("HTTP "+str(response.status))
                if "text/html" in response.headers.get("Content-Type",""):
                    raise ValueError("HTML response, not original photo")
                raw=response.read(16000001)
                if not 10000<len(raw)<=16000000:raise ValueError("Invalid downloaded size "+str(len(raw)))
                return raw,response.url
        except Exception as err:
            failures.append(type(err).__name__+": "+str(err)[:100])
            if i<3:time.sleep(2*(i+1))
    raise RuntimeError("Source not available "+filename+" "+("; ".join(failures)))
def run():
    specs=json.loads(PLAN.read_text("utf8"))["selected"]
    original=json.loads(BASE.read_text("utf8"))["pages"]
    frozen={v["slug"]:v for v in original}
    if len(specs)!=10 or len(frozen)!=10:raise ValueError("V114 requires exactly 10 originals")
    if len({x["slug"] for x in specs})!=10:raise ValueError("Duplicate selection")
    staged=[]
    for spec in specs:
        slug=spec["slug"]
        before=frozen[slug]
        path=ROOT/"site/things-to-do"/(slug+"-cruise-port-day-trip")/"index.html"
        html=path.read_text("utf8")
        for kind,pattern in PATTERNS.items():
            if find(html,pattern,kind)!=before[kind]:
                raise ValueError(slug+" existing SEO mismatch "+kind)
        old_image=before["hero"]
        if not old_image.startswith("/images/editorial/"):
            raise ValueError("Not AI original "+slug)
        target=re.search(r'<img\b[^>]*src="'+re.escape(old_image)+r'"[^>]*>',html)
        if not target:raise ValueError(slug+": old AI image element not found")
        after_img=html[target.end():]
        caption=re.match(r'\s*<(figcaption|p)\b[^>]*>[\s\S]*?</\1>',after_img)
        if not caption:raise ValueError(slug+": original image caption not adjacent")
        old_og=find(html,r'<meta property="og:image" content="([^"]+)"',"og:image")
        if old_og!=before["og"]:raise ValueError(slug+": original OG mismatch")
        original_bytes,actual_url=download(spec["filename"])
        with Image.open(io.BytesIO(original_bytes)) as raw:
            photo=ImageOps.exif_transpose(raw).convert("RGB")
            if photo.width<600 or photo.height<400:
                raise ValueError(slug+" insufficient photo resolution")
            photo.thumbnail((1400,1000),Image.Resampling.LANCZOS)
            buffer=io.BytesIO()
            photo.save(buffer,"WEBP",quality=84,method=6)
            webp=buffer.getvalue()
            w,h=photo.size
        if webp[:4]!=b"RIFF" or webp[8:12]!=b"WEBP" or len(webp)<8000:
            raise ValueError(slug+": invalid converted WebP")
        # Replace ONLY hero image and its directly adjacent disclosure.
        alt=f'{spec["region"]} 여행 관광지 실사: {spec["subject"]}. 촬영일 {spec["taken"]}. 현재 크루즈 접안부두나 승객 하선 게이트의 사진이 아닙니다.'
        new_img=(f'<img class="cover" src="{spec["output"]}" '
                 f'alt="{escape(alt,quote=True)}" width="{w}" height="{h}" '
                 f'decoding="async" fetchpriority="high">')
        rights=(f'<figcaption class="v114-photo-credit" data-taken="{spec["taken"]}" '
                f'style="font-size:12px;line-height:1.85;color:#516a80">'
                f'실제 촬영 장소: {escape(spec["subject"])}. 촬영일 {spec["taken"]}. '
                f'관광지의 촬영 당시 모습으로 현재 승객 하선 선석·셔틀·예약·영업정보를 증명하지 않습니다. '
                f'촬영자: {escape(spec["author"])} · '
                f'<a href="{spec["source"]}" target="_blank" rel="noopener noreferrer">사진 원본·출처</a> · '
                f'<a href="{spec["license_url"]}" target="_blank" rel="noopener noreferrer">{escape(spec["license"])}</a> · '
                f'원본 사진에서 WebP로 축소·형식 변환. 원본 저작권과 재이용 조건을 확인하세요.</figcaption>')
        # Use indices instead of global caption replacement to prevent unrelated edits
        combined=html[:target.start()]+new_img+after_img.replace(caption.group(),rights,1)
        combined=combined.replace(f'<meta property="og:image" content="{old_og}">',
                    f'<meta property="og:image" content="https://www.nipponferry.com{spec["output"]}">',1)
        for name in ("twitter:image",):
            for attr in ("name","property"):
                combined=combined.replace(f'<meta {attr}="{name}" content="{old_og}">',
                             f'<meta {attr}="{name}" content="https://www.nipponferry.com{spec["output"]}">')
        for kind,pattern in PATTERNS.items():
            if find(combined,pattern,kind)!=before[kind]:
                raise ValueError(slug+": protected SEO changed "+kind)
        if re.search(r'<img\b[^>]*src="'+re.escape(old_image)+r'"',combined):
            raise ValueError(slug+" old AI illustration retained elsewhere")
        staged.append({
          "slug":slug,"page":path,"html":combined,"file":ROOT/"site"/spec["output"].lstrip("/"),
          "raw":webp,"pixel_width":w,"pixel_height":h,
          "webp_sha256":hashlib.sha256(webp).hexdigest(),
          "original_sha256":hashlib.sha256(original_bytes).hexdigest(),
          "origin_download_url":actual_url,"source":spec["source"],"license":spec["license"],
          "photographer":spec["author"],"taken":spec["taken"],
          "replaced_old_image":old_image,"new_image":spec["output"],
          "size_bytes":len(webp)})
        print("READY",slug,str(w)+"x"+str(h),len(webp),flush=True)
    # Commit to working tree only after all ten sources and SEO checks pass.
    for record in staged:
        record["file"].parent.mkdir(parents=True,exist_ok=True)
        record["file"].write_bytes(record["raw"])
        record["page"].write_text(record["html"],encoding="utf8")
    output={ "version":"V114","review_date":"2026-10-22","status":"10/10 converted",
       "updated_pages":10,"replaced_ai_heroes":10,"original_seo_preserved":10,
       "images":[{k:v for k,v in e.items() if k not in ("file","raw","page","html")} for e in staged]}
    REPORT.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"passed":True,"images":10,"articles":10,"seo_protected":10},ensure_ascii=False))
if __name__=="__main__":run()
