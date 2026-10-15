#!/usr/bin/env python3
"""V42: 20 subject-matched Commons photos + 2 genuine Tsushima-food photos.

Selections are editorially reviewed Commons filenames from v42-commons-candidates.json.
Fail closed before mutating files if *any* selected licence or image cannot be validated.
Maintain original article URLs/content except one representative image, social preview,
and a visible attribution under its photo. Never imply a visual example is a live venue.
"""
from __future__ import annotations
import html,io,json,re,time,urllib.request
from pathlib import Path
from PIL import Image,ImageOps

SITE=Path("site")
REPORT=Path("docs/v42-commons-candidates.json")
OUT=Path("docs/v42-deployed-photo-credits.json")
HOST="https://www.nipponferry.com"
MEDIA=SITE/"images/culture-verified"
FOODMEDIA=SITE/"images/food-verified"
# File name and Korean subject description are manually reviewed together.
CHOICES={
  "shotengai-japanese-shopping-arcades": [
    "Tanukikoji 01.jpg",
    "홋카이도 삿포로 다누키코지의 지붕 있는 쇼텐가이 상점가 실제 사진",
    "지붕 있는 상점가의 실제 예시이며 기존 오키나와 야외 쇼핑거리와는 다릅니다."
  ],
  "japanese-shrine-vs-buddhist-temple": [
    "Double torii path at Fushimi Inari Taisha Shrine, Kyoto, Japan.jpg",
    "교토 후시미이나리타이샤 신사의 실제 도리이 통로 사진",
    "신사의 도리이 모습만 촬영한 사진이며 신사와 불교 사찰을 동시에 비교한 장면은 아닙니다."
  ],
  "japanese-matsuri-festival-culture": [
    "Kyoto Gion Matsuri J09 049.jpg",
    "2009년 교토 기온마쓰리의 실제 야마호코 수레 행렬 사진",
    "교토 기온마쓰리 현장 사례이며 모든 지역 마쓰리 행사의 모습이나 현재 일정을 뜻하지 않습니다."
  ],
  "japanese-daruma-doll-wishes": [
    "Daruma Dolls Osaka.JPG",
    "오사카 가쓰오지 사찰에 놓인 실제 다루마 인형 사진",
    "가쓰오지에서 촬영한 다루마 인형 사례이며 소원 성취를 증명하는 사진은 아닙니다."
  ],
  "japanese-maneki-neko-lucky-cat": [
    "Maneki-neko (Japanese Lucky Cat) Statues at Gotokuji Temple, Tokyo.jpg",
    "도쿄 고토쿠지 사찰에 모인 실제 마네키네코 고양이 인형 사진",
    "고토쿠지의 마네키네코 공양 인형 사례로 모든 가게 인형의 모습을 대표하지는 않습니다."
  ],
  "japanese-noren-curtain-shop-culture": [
    "Noren of a restaurant by tomooka in Kyoto.jpg",
    "교토 식당 입구에 걸린 일본 전통 노렌 천가리개 실제 사진",
    "일본 식당 노렌의 실제 사례이며 해당 식당의 현재 영업 상태는 별도 확인해야 합니다."
  ],
  "japanese-ekiben-railway-bento-culture": [
    "Bento Meals (2908879539).jpg",
    "신칸센으로 도쿄에 가는 여행자가 구입한 일본 철도 도시락의 실제 사진",
    "열차 여행 중 먹는 에키벤 사례이며 특정 역의 현재 판매 메뉴는 아닙니다."
  ],
  "japanese-kintsugi-gold-repair-culture": [
    "Hand Pinted Kintsugi Pottery Bowl.jpg",
    "금빛 접합부로 깨진 부분을 수선한 긴쓰기 도자기 실제 사진",
    "긴쓰기 수리 결과물의 예시로 전통 우루시 재료와 제작 과정을 모두 검증한 것은 아닙니다."
  ],
  "japanese-omiyage-souvenir-gift-culture": [
    "Japanese Omiyage.jpg",
    "나고야역에서 촬영한 일본 여행 기념 선물·오미야게 실제 사진",
    "나고야역 오미야게 상품 사례로 현재 상품 및 가격을 뜻하지 않습니다."
  ],
  "japanese-garden-stone-water-moss": [
    "Kenroku-en - Kenrokuen644.jpg",
    "이시카와현 가나자와 겐로쿠엔의 연못과 석등, 일본 정원 실제 사진",
    "돌과 물이 어우러진 정원 사례이며 이끼의 종류나 세부 재료를 모두 촬영한 사진은 아닙니다."
  ],
  "japanese-tea-ceremony-culture": [
    "Spouses learn traditional art of ancient Japanese tea ceremonies 130926-M-DV087-081.jpg",
    "오키나와 나고의 문화교류 행사에서 진행된 실제 일본 다도 시연 사진",
    "실제 일본 다도 시연 장면이며 해당 체험의 현재 예약 조건을 보증하지 않습니다."
  ]
}
TSUSHIMA={}
assert len(CHOICES)==11 and len(TSUSHIMA)==0
report=json.loads(REPORT.read_text("utf-8"))
broad=json.loads(Path("docs/v42-commons-supplement.json").read_text("utf-8"))
for slug,r in broad.items():
    if slug not in report: report[slug]=r
    else:
        oldfiles={x["filename"] for x in report[slug]["options"]}
        report[slug]["options"].extend(x for x in r["options"] if x["filename"] not in oldfiles)

def get(slug,filename):
    options=report[slug]["options"]
    item=next((x for x in options if x["filename"]==filename),None)
    if item is None:
        # Exact additional named Wikimedia Commons file found by editorial review.
        # Verify its copyright metadata through Commons API, never inventing a licence.
        import urllib.parse
        api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({
          "action":"query","titles":"File:"+filename,
          "prop":"imageinfo","iiprop":"url|mime|size|extmetadata",
          "iiurlwidth":"1200","format":"json","formatversion":2})
        req=urllib.request.Request(api,headers={
          "User-Agent":"Nipponferry-V42-editorial/1.0 (https://www.nipponferry.com/)",
          "Accept":"application/json"})
        with urllib.request.urlopen(req,timeout=60) as response:
            data=json.load(response)
        page=next(iter(data.get("query",{}).get("pages",[])),{})
        infos=page.get("imageinfo") or []
        if not infos:raise RuntimeError(f"Commons file missing: {slug}: {filename}")
        img=infos[0]
        if img.get("mime") not in ("image/jpeg","image/png","image/webp"):
            raise RuntimeError(f"Unacceptable MIME: {filename}")
        if img.get("width",0)<500 or img.get("height",0)<370:
            raise RuntimeError(f"Image too small for hero: {filename}")
        meta=img.get("extmetadata",{})
        def val(key):
            raw=meta.get(key,{}).get("value","")
            return html.unescape(re.sub("<[^>]*>"," ",raw)).strip()
        item={"filename":filename,"author":val("Artist"),"licence":val("LicenseShortName"),
              "licence_url":val("LicenseUrl"),
              "source_page":"https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(filename.replace(" ","_")),
              "remote":img.get("thumburl",img.get("url")),
              "description":val("ImageDescription")[:850],
              "width":img.get("width"),"height":img.get("height")}
    license=item["licence"]
    if not (license.startswith("CC BY") or license.startswith("CC0") or license=="Public domain"):
        raise RuntimeError(f"Unacceptable license: {slug} {license}")
    assert item["source_page"].startswith("https://commons.wikimedia.org/wiki/File:")
    return item
items=[{"slug":slug,"type":"things","subject":subject,"note":note,"data":get(slug,file),
        "local":f"/images/culture-verified/{slug}.webp"} for slug,(file,subject,note) in CHOICES.items()]
for slug,(lookup,file,subject,note) in TSUSHIMA.items():
    items.append({"slug":slug,"type":"tsushima","subject":subject,"note":note,"data":get(lookup,file),
                  "local":f"/images/food-verified/{slug}.webp"})
def credit(obj):
    c=obj["data"]
    author=html.escape((c["author"] or "Wikimedia Commons 사용자").strip())
    source=html.escape(c["source_page"],quote=True)
    lic=html.escape(c["licence"])
    licurl=html.escape(c["licence_url"] if c["licence_url"] and c["licence_url"].startswith("https://") else c["source_page"],quote=True)
    note=html.escape(obj["note"])
    return (f'사진: <a href="{source}" target="_blank" rel="noopener noreferrer">{author} / Wikimedia Commons</a>'
            f' · <a href="{licurl}" target="_blank" rel="noopener noreferrer">{lic}</a> · {note} '
            '· 원본 사진을 축소하여 WebP로 변환했습니다.')
def download(obj):
    src=obj["data"]["remote"]
    for attempt in range(5):
        try:
            req=urllib.request.Request(src,headers={"User-Agent":"Nipponferry-photography-preservation/1.0 (https://www.nipponferry.com/)", "Accept":"image/jpeg,image/png,image/webp,image/*;q=0.8"})
            with urllib.request.urlopen(req,timeout=70) as r:
                raw=r.read()
                mt=r.headers.get("Content-Type","")
            if not mt.lower().startswith("image/") or len(raw)<5000:
                raise RuntimeError(f"Not an image: {mt} {len(raw)} bytes")
            with Image.open(io.BytesIO(raw)) as img:
                img.load()
                img=ImageOps.exif_transpose(img).convert("RGB")
                img.thumbnail((1440,1440),Image.Resampling.LANCZOS)
                b=io.BytesIO()
                img.save(b,"WEBP",quality=82,method=5)
            result=b.getvalue()
            with Image.open(io.BytesIO(result)) as im: im.verify()
            return result
        except Exception as ex:
            print(obj["slug"],"retry",attempt+1,str(ex)[:180],flush=True)
            time.sleep(2*(attempt+1))
    raise RuntimeError(f"Image could not be downloaded: {obj['slug']}")
def change_img(h,obj,pattern):
    # Update only the first on-page editorial/hero image, excluding brand mascot;
    # do not tamper with additional menu illustrations or other images.
    match=re.search(pattern,h)
    if not match:raise RuntimeError("Article photo tag not found for "+obj["slug"])
    old=match.group()
    alt=html.escape(obj["subject"],quote=True)
    new=re.sub(r'\bsrc="[^"]+"',lambda _:f'src="{obj["local"]}"',old,count=1)
    if re.search(r'\balt="[^"]*"',new):new=re.sub(r'\balt="[^"]*"',lambda _:f'alt="{alt}"',new,count=1)
    else:new=new[:-1]+f' alt="{alt}">'
    new=re.sub(r'\s+onerror="[^"]*"', "",new)
    return h[:match.start()]+new+h[match.end():],match.start()+len(new)
def social(h,obj):
    url=HOST+obj["local"]
    if 'property="og:image"' in h:
        h=re.sub(r'<meta property="og:image" content="[^"]*">',f'<meta property="og:image" content="{url}">',h,count=1)
    else:h=h.replace("</head>",f'<meta property="og:image" content="{url}"></head>',1)
    if 'name="twitter:image"' in h:
        h=re.sub(r'<meta name="twitter:image" content="[^"]*">',f'<meta name="twitter:image" content="{url}">',h,count=1)
    else:h=h.replace("</head>",f'<meta name="twitter:image" content="{url}"></head>',1)
    return h

# All images first; all page transformations in memory; then write.
for idx,obj in enumerate(items):
    obj["_webp"]=download(obj)
    print(f"Retrieved {idx+1}/{len(items)}: {obj['slug']} {len(obj['_webp'])} bytes",flush=True)
    time.sleep(0.6)
hub=(SITE/"things-to-do/index.html").read_text("utf-8")
food=(SITE/"food/index.html").read_text("utf-8")
changed={}
for obj in items:
    if obj["type"]=="things":
        slug=obj["slug"]
        ref=f'<a class="v28-panel v36-photo-card" href="/things-to-do/{slug}/"'
        a=hub.find(ref)
        if a<0:raise RuntimeError("hub missing "+slug)
        b=hub.find("</a>",a)
        if b<0:raise RuntimeError("hub incomplete "+slug)
        b+=4
        piece=hub[a:b]
        if obj['type']=='things' and 'src="'+obj['local']+'"' in piece:
            raise RuntimeError(f"Already source verified, refusing double replacement: {slug}")
        tag=re.search(r'<figure class="v36-photo"><img[^>]*>',piece)
        if not tag:raise RuntimeError("card photo missing "+slug)
        oldtag=tag.group()
        newtag=re.sub(r'src="[^"]+"',f'src="{obj["local"]}"',oldtag,count=1)
        newtag=re.sub(r'alt="[^"]+"',f'alt="{html.escape(obj["subject"],quote=True)}"',newtag,count=1)
        piece=piece.replace(oldtag,newtag,1)
        piece=piece.replace("<em>주제 참고 이미지</em>","<em>주제 실사 · 출처 본문</em>",1)
        piece=piece.replace("<em>주제 안내 그래픽</em>","<em>주제 실사 · 출처 본문</em>",1)
        hub=hub[:a]+piece+hub[b:]
        path=SITE/f"things-to-do/{slug}/index.html"
        art=path.read_text("utf-8")
        photo_pat=r'<img\b(?![^>]*mascot\.png)[^>]*>'
        matches=list(re.finditer(photo_pat,art))
        if matches:
            art,pos=change_img(art,obj,photo_pat)
            note=f'<p class="v42-image-credit" style="font-size:12px;line-height:1.7;padding:9px 15px;background:#f0f7fc;color:#345b71">{credit(obj)}</p>'
            art=art[:pos]+note+art[pos:]
        else:
            h1=re.search(r'</h1>',art)
            if not h1:raise RuntimeError("No insertion point for "+slug)
            art=art[:h1.end()]+(f'<figure class="v42-article-photo" style="margin:18px auto;max-width:950px">'
                   f'<img src="{obj["local"]}" alt="{html.escape(obj["subject"],quote=True)}" '
                   'style="width:100%;max-height:570px;object-fit:cover;border-radius:12px">'
                   f'<figcaption style="font-size:12px;line-height:1.7">{credit(obj)}</figcaption></figure>')+art[h1.end():]
        art=social(art,obj)
        changed[path]=art
    else:
        slug=obj["slug"]
        ref=f'<a class="dircard" href="/japan/{slug}/"'
        a=food.find(ref)
        if a<0:raise RuntimeError("food hub missing "+slug)
        b=food.find("</a>",a)
        if b<0:raise RuntimeError("food card markup missing "+slug)
        b+=4
        piece=food[a:b]
        tag=re.search(r'<img[^>]*>',piece)
        if not tag:raise RuntimeError("food img tag missing "+slug)
        nt=re.sub(r'src="[^"]+"',f'src="{obj["local"]}"',tag.group(),count=1)
        nt=re.sub(r'alt="[^"]+"',f'alt="{html.escape(obj["subject"],quote=True)}"',nt,count=1)
        piece=piece.replace(tag.group(),nt,1)
        piece=piece.replace("주제 참고 이미지","실제 지역 음식 사진",1)
        food=food[:a]+piece+food[b:]
        path=SITE/f"japan/{slug}/index.html"
        art=path.read_text("utf-8")
        art,pos=change_img(art,obj,r'<img\b[^>]*\bclass="(?:article-cover|d-img|s17-img)"[^>]*>')
        # Earlier V36 has credit paragraph; replace it cleanly rather than duplicating.
        nxt=art[pos:]
        old=re.match(r'<p class="v36-food-credit"[^>]*>[\s\S]*?</p>',nxt)
        if old:art=art[:pos]+art[pos+old.end():]
        note=f'<p class="v36-food-credit" style="font-size:12px;line-height:1.7;color:#486b7f">{credit(obj)}</p>'
        art=art[:pos]+note+art[pos:]
        art=social(art,obj)
        changed[path]=art

# Validation before any files written.
for obj in items:
    if obj["type"]=="things":
        assert f'src="{obj["local"]}"' in hub
    else:assert f'src="{obj["local"]}"' in food
for path,content in changed.items():
    slug=path.parent.name
    match=next(x for x in items if x["slug"]==slug)
    assert f'src="{match["local"]}"' in content
    assert f'content="{HOST}{match["local"]}"' in content
    assert "Wikimedia Commons" in content

MEDIA.mkdir(parents=True,exist_ok=True)
FOODMEDIA.mkdir(parents=True,exist_ok=True)
for obj in items:
    (SITE/obj["local"].lstrip("/")).write_bytes(obj["_webp"])
for path,content in changed.items():path.write_text(content,encoding="utf-8")
(SITE/"things-to-do/index.html").write_text(hub,encoding="utf-8")
(SITE/"food/index.html").write_text(food,encoding="utf-8")
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps([{
    "slug":a["slug"],"section":a["type"],"source_file":a["data"]["filename"],
    "photographer":a["data"]["author"],"licence":a["data"]["licence"],
    "license_url":a["data"]["licence_url"],"source_page":a["data"]["source_page"],
    "subject":a["subject"],"note":a["note"],"asset":a["local"],"webp_bytes":len(a["_webp"])}
    for a in items],ensure_ascii=False,indent=2),encoding="utf-8")
print("V42: 11 topic-related editorial references replaced with verified original photos, source credit and metadata.")
