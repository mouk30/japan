#!/usr/bin/env python3
"""V36.2: Replace cross-region food cover mismatches with verified Commons photography.

Curated original file names, photographers and Creative Commons licences were
checked against each original Commons file page. Non-local dessert examples are
visibly labelled as examples; items lacking suitable real photos retain a
clearly labelled non-photographic cover, never a fake regional photograph.
"""
from __future__ import annotations
import hashlib
import html
import io
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"
FOOD=SITE/"food"/"index.html"
OUTPUT=SITE/"images"/"food-verified"
OUTPUT.mkdir(parents=True,exist_ok=True)
DOC=ROOT/"docs"/"v36-food-photo-provenance.json"
LICENSES={
 "CC BY-SA 4.0":"https://creativecommons.org/licenses/by-sa/4.0/",
 "CC BY-SA 3.0":"https://creativecommons.org/licenses/by-sa/3.0/",
 "CC BY-SA 2.0":"https://creativecommons.org/licenses/by-sa/2.0/",
 "CC BY 2.0":"https://creativecommons.org/licenses/by/2.0/",
}
PHOTOS=[
 ("fukuoka","food","Hakata ramen bowl closeup.jpg","Ominae","CC BY-SA 4.0","후쿠오카 야타이의 하카타 라멘"),
 ("fukuoka","market","Yanagibashi Rengo Ichiba by LWY in Fukuoka.jpg","LWY","CC BY 2.0","후쿠오카 야나기바시 연합시장"),
 ("fukuoka","local-food","Fukuoka-style hot pot (3637375629).jpg","pelican","CC BY-SA 2.0","후쿠오카 스타일 모츠나베 요리"),
 ("osaka","food","Takoyaki in Osaka.jpg","ZhengZhou","CC BY-SA 4.0","오사카에서 촬영한 타코야키"),
 ("osaka","market","Osaka market.jpg","SungMinSeung","CC BY-SA 4.0","오사카 구로몬시장 실제 거리"),
 ("osaka","local-food","Okonomiyaki osaka.jpg","Retinafunk","CC BY-SA 3.0","오사카식 오코노미야키 요리"),
 ("shimonoseki","food","Fugo-sashimi.jpg","Hajime NAKANO","CC BY 2.0","일본 복어회 테사 요리, 시모노세키 촬영 사진은 아님"),
 ("shimonoseki","market","Karato market, Shimonoseki.jpg","Maria-Yamaguchi","CC BY-SA 4.0","시모노세키 가라토시장에서 판매 중인 초밥"),
 ("shimonoseki","local-food","Kawara soba by woinary in Moji, Fukuoka.jpg","woinary","CC BY-SA 2.0","야마구치 향토음식 가와라소바, 모지의 식당 촬영"),
]
ALIASES={
 ("fukuoka","dessert"):("/images/editorial/wagashi-japanese-seasonal-sweets.webp","일본 전통 화과자 참고 이미지 · 후쿠오카 현장 사진 아님"),
 ("osaka","dessert"):("/images/editorial/wagashi-japanese-seasonal-sweets.webp","일본 전통 화과자 참고 이미지 · 오사카 현장 사진 아님"),
 ("tsushima","food"):("/images/hub-thumbnails/food-tsushima-food.svg","대마도 식도락 주제 그래픽 · 실제 음식 사진 아님"),
 ("tsushima","market"):("/images/hub-thumbnails/food-tsushima-market.svg","대마도 시장 주제 그래픽 · 실제 시장 사진 아님"),
 ("tsushima","dessert"):("/images/editorial/wagashi-japanese-seasonal-sweets.webp","일본 화과자 참고 이미지 · 대마도 지역 상품 사진 아님"),
 ("tsushima","local-food"):("/images/hub-thumbnails/food-tsushima-local-food.svg","대마도 향토 식문화 그래픽 · 실제 요리 사진 아님"),
 ("shimonoseki","dessert"):("/images/editorial/wagashi-japanese-seasonal-sweets.webp","일본 전통 화과자 참고 이미지 · 시모노세키 현장 사진 아님"),
}

def commons_url(filename: str) -> str:
    n=filename.replace(" ","_")
    digest=hashlib.md5(n.encode("utf-8")).hexdigest()
    return ("https://upload.wikimedia.org/wikipedia/commons/"
            f"{digest[0]}/{digest[:2]}/{urllib.parse.quote(n,safe='()')}")

def commons_page(filename: str) -> str:
    return "https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(filename.replace(" ","_"),safe="()")

def download(photo) -> bytes:
    filename=photo[2]
    uri=commons_url(filename)
    for i in range(5):
        try:
            req=urllib.request.Request(uri,headers={
                "User-Agent":"NIPPONFERRY-v36-verified-cuisine/1.0 (https://www.nipponferry.com/)",
                "Accept":"image/jpeg,image/png,image/*;q=0.7",
            })
            with urllib.request.urlopen(req,timeout=70) as res:
                data=res.read()
                ct=res.headers.get("Content-Type","")
            if not ct.lower().startswith("image/") or len(data)<10000:
                raise RuntimeError(f"Non-image upstream ({ct}, {len(data)} bytes): {uri}")
            with Image.open(io.BytesIO(data)) as pic:
                pic.load()
                pic=ImageOps.exif_transpose(pic).convert("RGB")
                pic.thumbnail((1440,1200),Image.Resampling.LANCZOS)
                output=io.BytesIO()
                pic.save(output,format="WEBP",quality=84,method=6)
            webp=output.getvalue()
            with Image.open(io.BytesIO(webp)) as check:
                check.verify()
            return webp
        except Exception as e:
            print(f"download {filename} attempt {i+1}: {e}",flush=True)
            time.sleep(3*(i+1))
    raise RuntimeError("Failed verified photo: "+filename)

photo_data=[]
for photo in PHOTOS:
    city,typ,filename,author,license,subject=photo
    webp=download(photo)
    path=f"/images/food-verified/{city}-{typ}.webp"
    photo_data.append({
      "city":city,"type":typ,"image":path,"author":author,
      "license":license,"license_url":LICENSES[license],"source":commons_page(filename),
      "subject":subject,"bytes":len(webp),"data":webp
    })
    print(city,typ,len(webp),flush=True)
    time.sleep(0.7)

assign={(x["city"],x["type"]):x for x in photo_data}
for (city,typ),(path,note) in ALIASES.items():
    if not (SITE/path.lstrip("/")).exists():
        raise RuntimeError(f"Reference image missing: {path}")
    assign[(city,typ)]={"city":city,"type":typ,"image":path,"subject":note,"license":None,"author":None}

assert len(assign)==16
hub=FOOD.read_text("utf-8")
if 'id="v36-food-source-index"' in hub:raise RuntimeError("Already corrected food hub")
changed=[]
for (city,typ),entry in assign.items():
    path=entry["image"]
    article=SITE/"japan"/f"{city}-{typ}"/"index.html"
    if not article.exists():raise RuntimeError(f"Missing article {article}")
    # Find the exact link and first image inside that link.
    pat=(r'(<a class="dircard" href="/japan/'+city+'-'+typ+r'/"><img\s+)([^>]*)(>)')
    def swap(m):
        attributes=m.group(2)
        attributes,count=re.subn(r'src="[^"]+"',lambda x:f'src="{path}"',attributes,count=1)
        if count!=1:raise RuntimeError(f"Missing img src: {city} {typ}")
        attributes=re.sub(r'alt="[^"]+"',lambda x:f'alt="{html.escape(entry["subject"],quote=True)}"',attributes)
        return m.group(1)+attributes+m.group(3)
    hub,n=re.subn(pat,swap,hub,count=1)
    if n!=1:raise RuntimeError(f"Food card not found: {city} {typ}")
    old=article.read_text("utf-8")
    # Migrate only primary cover (not lower content images).
    match=re.compile(r'(<img\b[^>]*\bclass="(?:article-cover|d-img|s17-img)"[^>]*\bsrc=")[^"]+(")')
    new,n=match.subn(lambda m:m.group(1)+path+m.group(2),old,count=1)
    if n!=1:raise RuntimeError(f"No primary cover on {article}")
    new=re.sub(r'<meta property="og:image" content="[^"]+">',
               lambda m:f'<meta property="og:image" content="https://www.nipponferry.com{path}">',new,count=1)
    if 'name="twitter:image"' in new:
        new=re.sub(r'<meta name="twitter:image" content="[^"]+">',
                   lambda m:f'<meta name="twitter:image" content="https://www.nipponferry.com{path}">',new,count=1)
    else:
        new=new.replace("</head>",f'<meta name="twitter:image" content="https://www.nipponferry.com{path}"></head>',1)
    label=html.escape(entry["subject"])
    if entry.get("license"):
        source=html.escape(entry["source"],quote=True)
        licurl=entry["license_url"]
        name=html.escape(entry["author"])
        credit=f'<a href="{source}" target="_blank" rel="noopener noreferrer">{name} / Wikimedia Commons</a> · <a href="{licurl}" target="_blank" rel="noopener noreferrer">{entry["license"]}</a> · {label} · 원본에서 WebP 변환·크기 조정'
    else: credit=label
    # Accessible credit immediately after actual primary cover for users to verify.
    marker=re.compile(r'(<img\b[^>]*\bclass="(?:article-cover|d-img|s17-img)"[^>]*>)')
    new,count=marker.subn(lambda m:m.group(1)+f'<p class="v36-photo-credit" style="font-size:12px;color:#517486;line-height:1.75;margin:6px 0 20px">사진 안내: {credit}</p>',new,count=1)
    if count!=1:raise RuntimeError("Credit insertion failed")
    changed.append((article,new))

# Add index of photography below grid, outside the 16 cards to avoid invalid nested links.
credit_cards=[]
for entry in photo_data:
    source=html.escape(entry["source"],quote=True)
    credit_cards.append(
        f'<li>{html.escape(entry["subject"])} — <a href="{source}" target="_blank" rel="noopener noreferrer">{html.escape(entry["author"])} / Wikimedia Commons</a> · '
        f'<a href="{entry["license_url"]}" target="_blank" rel="noopener noreferrer">{entry["license"]}</a></li>'
    )
index='<aside id="v36-food-source-index" class="wrap" style="margin:24px auto 45px;padding:18px;border:1px solid #dae6f0;border-radius:15px;background:#f8fbff"><h2 style="font-size:18px;margin:0 0 9px;color:#184764">식도락 실제 사진 출처</h2><p style="font-size:13px;color:#527081">실제 지역 촬영·요리 예시를 구분합니다. 원본 사진은 사이트용 WebP로 변환했습니다.</p><ul style="font-size:12px;line-height:1.9;padding-left:22px">'+''.join(credit_cards)+'</ul></aside>'
# Footer appears after nested mains in source. Source index between content and footer.
if '<footer' in hub: hub=hub.replace('<footer',index+'<footer',1)
else:hub=hub.replace('</body>',index+'</body>',1)

for entry in photo_data:
    (SITE/entry["image"].lstrip("/")).write_bytes(entry["data"])
FOOD.write_text(hub,encoding="utf-8")
for article,new in changed:article.write_text(new,encoding="utf-8")
metadata=[{k:v for k,v in obj.items() if k!="data"} for obj in photo_data]
metadata.extend({k:v for k,v in obj.items() if k!="data"} for obj in assign.values() if not obj.get("license"))
DOC.write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding="utf-8")

assert hub.count('class="dircard"')==16
assert len(metadata)==16
print("V36.2: corrected 16 existing food cards + 16 food article covers; 9 licensed real photographs, 4 explicit topic references, 3 honest graphic placeholders.")
