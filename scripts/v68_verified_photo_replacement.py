#!/usr/bin/env python3
"""V68 evidence-backed photos. Never relabel AI art as a location photograph."""
import io, json, re, urllib.parse, urllib.request, urllib.error, hashlib, time
from pathlib import Path
from PIL import Image, ImageOps
ROOT=Path(__file__).resolve().parents[1];SITE=ROOT/"site"
DATA=[
{"slug":"hiroshima-miyajima-ferry-crossing","file":"Miyajima-Ferry-STA JR-Gate.jpg","author":"MaedaAkihiko","license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/","description":"미야지마섬 측 미야지마 부두 JR서일본 페리 개찰구·매표소 사진 (미야지마구치 출발측 아님)"},
{"slug":"shodoshima-ferry-island-access","file":"Shodo-shima ferry port in Tonosho (6453360287).jpg","author":"Maarten Heerlien","license":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/","description":"쇼도시마 도노쇼항의 페리 항구 모습 (2010년 촬영)"},
{"slug":"okinawa-shuri-castle","file":"Shuri Castle Reconstruction.jpg","author":"おにく","license":"CC0 1.0","license_url":"https://creativecommons.org/publicdomain/zero/1.0/","description":"오키나와 슈리성 정전 복원 공사 현장 (2025년 2월 촬영, 현재 현장 상태와 다를 수 있음)"},
{"slug":"yokohama-red-brick-warehouse","file":"20250101 Yokohama Red Brick Warehouse 115522.jpg","author":"Matthide127","license":"CC0 1.0","license_url":"https://creativecommons.org/publicdomain/zero/1.0/","description":"요코하마 아카렌가 창고 외관 (2025년 1월 촬영, 크루즈 터미널 사진 아님)"}
]
def fetch(item):
    name=item["file"].replace(" ","_")
    digest=hashlib.md5(name.encode("utf-8")).hexdigest()
    encoded=urllib.parse.quote(name,safe="()")
    base=f"https://upload.wikimedia.org/wikipedia/commons/{digest[0]}/{digest[:2]}/{encoded}"
    candidates=[
        f"https://upload.wikimedia.org/wikipedia/commons/thumb/{digest[0]}/{digest[:2]}/{encoded}/1280px-{encoded}",
        base,
        "https://commons.wikimedia.org/wiki/Special:Redirect/file/"+encoded,
    ]
    last=None
    for url in candidates:
        for attempt in range(2):
            try:
                req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; NIPPONFERRY ImageQA/1.0)","Accept":"image/avif,image/webp,image/apng,image/*,*/*;q=0.8"})
                with urllib.request.urlopen(req,timeout=25) as resp:raw=resp.read(14000000)
                im=Image.open(io.BytesIO(raw));im.verify()
                im=Image.open(io.BytesIO(raw)).convert("RGB")
                im.thumbnail((1800,1350),Image.Resampling.LANCZOS)
                out=SITE/"images"/"v68-verified"/(item["slug"]+".webp")
                out.parent.mkdir(parents=True,exist_ok=True)
                im.save(out,"WEBP",quality=84,method=6)
                if out.stat().st_size < 15000:raise ValueError("Image too small "+str(out))
                item["source"]="https://commons.wikimedia.org/wiki/File:"+encoded
                item["webp"]="/images/v68-verified/"+item["slug"]+".webp"
                item["size_bytes"]=out.stat().st_size
                return out
            except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,OSError,ValueError) as exc:
                last=str(exc);print("SOURCE RETRY",item["slug"],url,last,flush=True)
                time.sleep(3*(attempt+1))
    raise RuntimeError("No retrievable original for "+item["slug"]+": "+str(last))
def apply(item):
    p=SITE/"things-to-do"/item["slug"]/"index.html"
    html=p.read_text(encoding="utf-8")
    if "nf-v68-photo-attribution" in html: return
    tag=re.search(r'<img\b[^>]*src="/images/editorial/[^"]+\.webp"[^>]*>',html)
    if tag is None:raise RuntimeError("Original editorial hero not found: "+item["slug"])
    old=tag.group()
    new=re.sub(r'src="[^"]+"','src="'+item["webp"]+'"',old,count=1)
    new=re.sub(r'alt="[^"]*"','alt="'+item["description"]+'"',new,count=1)
    html=html.replace(old,new,1)
    attribution='<p id="nf-v68-photo-attribution" style="font-size:13px;padding:12px 16px;border-left:3px solid #1e7da6;background:#f1f8fc"><strong>실제 장소 사진:</strong> '+item["description"]+' · 촬영/제공: '+item["author"]+' · <a href="'+item["source"]+'" target="_blank" rel="noopener noreferrer">원본 사진</a> · <a href="'+item["license_url"]+'" target="_blank" rel="noopener noreferrer">'+item["license"]+'</a> · JPG 원본을 WebP로 변환·축소했습니다. 사진은 촬영 당시 모습을 보여주며 최신 시설 상태를 보증하지 않습니다.</p>'
    # Place immediately after hero image, preserving the rest of the article structure.
    html=html.replace(new,new+attribution,1)
    # Other AI disclosure remains if it refers to the same hero; remove only contradictory caption text.
    html=html.replace('AI 생성 여행 참고 이미지로 실제 장소의 세부 모습과 다를 수 있습니다.','대표 사진은 실제 장소 촬영 이미지입니다. 촬영 연도와 출처를 위에서 확인하세요.',1)
    html=html.replace('AI 생성 참고 이미지로 실제 장소와 차이가 있을 수 있습니다.','대표 사진은 실제 장소 촬영 이미지입니다. 촬영 연도와 출처를 위에서 확인하세요.',1)
    p.write_text(html,encoding="utf-8")
def main():
    for item in DATA:
        print("DOWNLOAD",item["slug"],flush=True)
        fetch(item)
    for item in DATA:
        print("PATCH",item["slug"],flush=True)
        apply(item)
    out=ROOT/"audit-reports"/"v68";out.mkdir(parents=True,exist_ok=True)
    (out/"verified-photo-sources.json").write_text(json.dumps(DATA,ensure_ascii=False,indent=2),encoding="utf-8")
    print("V68 COMPLETE",len(DATA))
if __name__=="__main__":main()
