#!/usr/bin/env python3
"""V128: atomically import ten sourced Commons tourist photographs, preserving SEO."""
from __future__ import annotations
import hashlib, io, json, re, time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from html import escape
from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/"audit-reports/v128/photo-plan.json"
BASE=ROOT/"audit-reports/v128/seo-and-ai-candidate-baselines.json"
RESULT=ROOT/"audit-reports/v128/import-result.json"
FIELDS={
 "title":r"<title>([^<]*)</title>",
 "description":r'<meta name="description" content="([^"]*)"',
 "canonical":r'<link rel="canonical" href="([^"]*)"',
 "h1":r"<h1[^>]*>([\s\S]*?)</h1>",
 "jsonld":r'<script type="application/ld\+json">([\s\S]*?)</script>'
}
def only(h,pattern,name):
    m=re.search(pattern,h,re.S)
    if not m: raise ValueError("Missing "+name)
    return m.group(1)

def get_original(filename):
    url="https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(filename,safe="")+"?width=1400"
    errors=[]
    for n in range(4):
        try:
            req=Request(url,headers={
              "User-Agent":"NipponFerryPhotoVerification/1.0 (https://www.nipponferry.com/contact/)",
              "Accept":"image/jpeg,image/png,image/webp,*/*"})
            with urlopen(req,timeout=65) as resp:
                if resp.status!=200: raise ValueError("HTTP "+str(resp.status))
                if "image/" not in resp.headers.get("Content-Type",""):
                    raise ValueError("Not an image source")
                data=resp.read(16000001)
                if not 10000<len(data)<=16000000:raise ValueError("Bad image size "+str(len(data)))
                if "wikimedia.org" not in resp.url:raise ValueError("Unexpected redirect "+resp.url)
                return data,resp.url
        except Exception as e:
            errors.append(str(e)[:120])
            if n<3:time.sleep(3*(n+1))
    raise RuntimeError(filename+": "+"; ".join(errors))

def run():
    plan=json.loads(PLAN.read_text("utf8"))["selected"]
    baselines=json.loads(BASE.read_text("utf8"))["pages"]
    original={x["slug"]:x for x in baselines}
    if len(plan)!=len(original) or len(plan)!=10 or len({x["slug"] for x in plan})!=10:
        raise ValueError("Must use exactly ten distinct original article baselines")
    staged=[]
    for spec in plan:
        slug=spec["slug"]
        base=original[slug]
        path=ROOT/"site"/base["page"].lstrip("/")/"index.html"
        before=path.read_text("utf8")
        for name,regex in FIELDS.items():
            if only(before,regex,name)!=base[name]:
                raise ValueError(slug+" protected original SEO drift "+name)
        old=base["current_hero"]
        if not old.startswith("/images/editorial/"):
            raise ValueError(slug+" not an original AI illustration")
        tag=re.search(r'<img\b[^>]*class="cover"[^>]*src="'+re.escape(old)+r'"[^>]*>',before)
        if not tag:raise ValueError(slug+" old cover tag missing")
        rest=before[tag.end():]
        cap=re.match(r'\s*<(figcaption|p)\b[^>]*>[\s\S]*?</\1>',rest)
        if not cap:raise ValueError(slug+" original hero caption missing")
        og=only(before,r'<meta property="og:image" content="([^"]*)"', "OG image")
        if og!=base["og_image"]:raise ValueError(slug+" unexpected OG original")

        raw,realurl=get_original(spec["filename"])
        with Image.open(io.BytesIO(raw)) as im:
            im=ImageOps.exif_transpose(im).convert("RGB")
            if im.width<800 or im.height<400:raise ValueError(slug+" insufficient photo pixels")
            im.thumbnail((1400,1100),Image.Resampling.LANCZOS)
            width,height=im.size
            f=io.BytesIO()
            im.save(f,format="WEBP",quality=85,method=6)
            webp=f.getvalue()
        if len(webp)<7000 or not (webp[:4]==b"RIFF" and webp[8:12]==b"WEBP"):
            raise ValueError(slug+" invalid WebP export")
        is_sharealike="BY-SA" in spec["license"]
        ext="동일 CC BY-SA 라이선스 조건을 적용합니다. " if is_sharealike else ""
        date=spec["taken"]
        label=spec["subject"]
        alt=f'{spec["region"]} 실제 관광지 촬영 사진: {label}. 촬영일 {date}. 현재 크루즈 접안 부두나 승객 게이트 사진은 아닙니다.'
        newtag=(f'<img class="cover" src="{spec["output"]}" width="{width}" height="{height}" '
                f'alt="{escape(alt,quote=True)}" decoding="async" fetchpriority="high">')
        credit=(f'<figcaption class="v128-photo-credit" style="font-size:12px;line-height:1.8;color:#516a80">'
                f'실제 촬영 관광지: {escape(label)}. 촬영일 {date}. 촬영자: {escape(spec["author"])} · '
                f'<a href="{spec["source"]}" rel="noopener noreferrer" target="_blank">원본·출처</a> · '
                f'<a href="{spec["license_url"]}" rel="noopener noreferrer" target="_blank">{escape(spec["license"])}</a> · '
                f'원본을 축소하여 WebP로 형식 변환했습니다. {ext}{escape(spec.get("extra_credit",""))} '
                f'이 사진은 촬영 당시의 관광명소 기록이며 현재 부두·하선게이트·셔틀·영업·공연 일정을 증명하지 않습니다.</figcaption>')
        replaced=before[:tag.start()]+newtag+rest[:cap.start()]+credit+rest[cap.end():]
        newog="https://www.nipponferry.com"+spec["output"]
        replaced=replaced.replace(f'<meta property="og:image" content="{og}">',
                                  f'<meta property="og:image" content="{newog}">',1)
        for attr in ("name","property"):
            replaced=replaced.replace(f'<meta {attr}="twitter:image" content="{og}">',
                                      f'<meta {attr}="twitter:image" content="{newog}">')
        for name,regex in FIELDS.items():
            if only(replaced,regex,name)!=base[name]:
                raise ValueError(slug+" original SEO modified "+name)
        if re.search(r'<img\b[^>]*src="'+re.escape(old)+r'"',replaced):
            raise ValueError(slug+" old AI image still displayed")
        if replaced.count('class="v128-photo-credit"')!=1:
            raise ValueError(slug+" credit missing/duplicated")
        staged.append({
          "slug":slug,"path":path,"html":replaced,"output":ROOT/"site"/spec["output"].lstrip("/"),
          "bytes":webp,"source":spec["source"],"actual_download":realurl,
          "original_sha256":hashlib.sha256(raw).hexdigest(),
          "webp_sha256":hashlib.sha256(webp).hexdigest(),"size_bytes":len(webp),
          "pixel_width":width,"pixel_height":height,"date":date,"author":spec["author"],
          "license":spec["license"],"old_hero":old,"new_hero":spec["output"]
        })
        print("READY",slug,width,height,len(webp),flush=True)
    if len(staged)!=10:raise ValueError("Partial batch rejected")
    for row in staged:
        row["output"].parent.mkdir(parents=True,exist_ok=True)
        row["output"].write_bytes(row["bytes"])
        row["path"].write_text(row["html"],encoding="utf8")
    details=[{k:v for k,v in r.items() if k not in ("path","html","output","bytes")} for r in staged]
    RESULT.write_text(json.dumps({
      "version":"V128","status":"converted and local article edits staged","images":details,
      "updated_pages":10,"original_seo_preserved":10
    },ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"converted_photos":10,"updated_existing_articles":10,"seo_preserved":10}))
if __name__=="__main__":run()
