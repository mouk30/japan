#!/usr/bin/env python3
"""V40: 20 subject-matched Commons photos + 2 genuine Tsushima-food photos.

Selections are editorially reviewed Commons filenames from v40-commons-research.json.
Fail closed before mutating files if *any* selected licence or image cannot be validated.
Maintain original article URLs/content except one representative image, social preview,
and a visible attribution under its photo. Never imply a visual example is a live venue.
"""
from __future__ import annotations
import html,io,json,re,time,urllib.request
from pathlib import Path
from PIL import Image,ImageOps

SITE=Path("site")
REPORT=Path("docs/v40-commons-research.json")
OUT=Path("docs/v40-deployed-photo-credits.json")
HOST="https://www.nipponferry.com"
MEDIA=SITE/"images/culture-verified"
FOODMEDIA=SITE/"images/food-verified"
# File name and Korean subject description are manually reviewed together.
CHOICES={
  "onsen-first-time": [
    "Takanoyu Onsen Rotenburo 086.jpg",
    "아키타현 다카노유 온천의 실제 노천탕",
    "처음 방문할 때 참고할 노천탕의 모습으로, 해당 시설의 현재 이용 규정이나 운영시간을 보장하지 않습니다."
  ],
  "nature-outdoor-checklist": [
    "Okuhamana Nature Trail (Mount Tonmaku).jpg",
    "시즈오카현 하마마쓰 오쿠하마나 산길의 실제 자연 탐방로",
    "야외 트레킹 길 사례이며 짐 꾸리기나 안전 장비를 촬영한 사진은 아닙니다."
  ],
  "shopping-city-night-guide": [
    "Dotombori Shopping Street at night 20190201-2.jpg",
    "오사카 도톤보리 쇼핑거리의 실제 야간 풍경",
    "오사카 대표 야경·쇼핑거리 사례이며 현재 매장 구성은 다를 수 있습니다."
  ],
  "port-to-experience-planner": [
    "Pacific Venus cruise ship docked at Yokohama International Passenger Terminal 2.jpg",
    "요코하마 국제여객터미널에 실제 정박한 크루즈선",
    "항구에서 관광을 시작하는 상황의 예시이며 모든 선박이 같은 터미널에 접안하는 것은 아닙니다."
  ],
  "japan-four-shopping-experiences": [
    "Shōtengai.jpg",
    "일본의 지붕 있는 전통 상점가 쇼텐가이 실제 풍경",
    "일본 쇼핑 경험 중 지역 상점가 한 유형을 보여주는 사진이며 네 가지 장소를 모두 촬영한 사진은 아닙니다."
  ],
  "japan-rail-pass-why-changes": [
    "JR Rail Pass 2023.jpg",
    "2023년에 실제 발행된 일본 JR 철도패스 표 실물",
    "2023년 발행 철도패스의 예시로 현재 판매 조건·디자인·가격을 뜻하지 않습니다."
  ],
  "japan-station-bento-vending": [
    "Dr.Yellow Bento 1.jpg",
    "신고베역에서 판매된 닥터옐로 신칸센 모양 에키벤 도시락",
    "역 도시락 문화를 보여주는 사례로 자동판매기 자체를 촬영한 사진은 아닙니다."
  ],
  "japan-shotengai-neon-signs": [
    "2018 Shinsaibashi Shopping Arcade, Shinsaibashi (43477561214).jpg",
    "오사카 신사이바시 상점가의 실제 간판과 아케이드 풍경",
    "2018년에 촬영한 상점가 간판 사례입니다."
  ],
  "japan-sakura-forecast-science": [
    "Flower viewing custom, Japan; April 2014 (02).jpg",
    "일본의 실제 벚꽃 개화 시기 풍경과 하나미",
    "벚꽃 개화 현상의 예시 사진이며 예보 측정이나 기상 모델 제작 장면은 아닙니다."
  ],
  "tanuki-japanese-shop-statues": [
    "Kyoto tanuki.jpg",
    "교토 음식점 앞에 세워진 도자기 너구리 타누키 장식 실사",
    "일본 가게 입구의 타누키 배치 사례입니다."
  ],
  "miso-japanese-fermented-soy": [
    "Miso 001.jpg",
    "일본 미소된장 페이스트를 촬영한 실제 음식 사진",
    "미소된장 제품의 예시이며 일본 각 지역의 모든 미소 종류를 비교한 사진은 아닙니다."
  ],
  "japanese-train-manners-quiet-car": [
    "Tokyo subway car interior in 2014.png",
    "2014년에 촬영한 도쿄 지하철 차량의 실제 실내",
    "조용한 열차 이용을 설명하기 위한 실내 사례이며 승객 예절을 입증하는 장면은 아닙니다."
  ],
  "japanese-queue-culture": [
    "電車を待つ行列 京急品川駅 2023-06-19.jpg",
    "도쿄 게이큐 시나가와역에서 전철을 기다리는 실제 승객 대기 줄",
    "2023년 시나가와역 줄서기 모습이며 일본 전체의 습관을 하나의 사진으로 일반화하지 않습니다."
  ],
  "shichi-go-san-japanese-children": [
    "Shichigosan Pilgrimage at Omiya Hachimangu Shrine in Suginami, Tokyo.jpg",
    "도쿄 오미야 하치만구 신사의 시치고산 기념 참배 행사 사진",
    "실제 시치고산 행사 사례이며 등장인물의 신원은 특정하지 않습니다."
  ],
  "obon-japanese-ancestors": [
    "Bon Odori, a style of dancing performed during Obon, Japan; August 2014 (01).jpg",
    "일본 오봉 기간의 실제 본오도리 전통 춤 행사",
    "오봉의 대표 행사인 본오도리 사례로 제사·추모 의식 전체를 촬영한 사진은 아닙니다."
  ],
  "yukimi-japanese-snow-viewing-tradition": [
    "Kenroku-en-winter-lantern.jpg",
    "가나자와 겐로쿠엔 정원의 겨울 석등 실사",
    "일본 겨울 정원 감상 사례로 촬영 당시 적설량은 계절마다 달라집니다."
  ],
  "kodo-japanese-incense-appreciation": [
    "香道 (1).JPG",
    "일본 전통 향도 의식에 쓰이는 향도구 실제 사진",
    "향 감상에 쓰이는 도구 사진으로 향을 맡는 행위나 현장 참여자를 보여주지는 않습니다."
  ],
  "japan-konbini-culture": [
    "愛情むすび (5137097559).jpg",
    "일본 편의점에서 판매하는 즉석 주먹밥과 음식 진열 실제 사진",
    "일본 편의점 식품의 예시로 현재 상품·가격과 동일하지 않을 수 있습니다."
  ],
  "ryokan-vs-hotel": [
    "My traditional accomodation at Toshiharu Ryokan (48885681992).jpg",
    "일본 전통 료칸의 다다미 객실 실제 사진",
    "료칸 객실의 사례이며 일반 호텔 객실과 두 시설을 한 화면에서 비교한 것은 아닙니다."
  ],
  "why-travel-japan-by-sea": [
    "Queen Olive Ryobiunyu.jpg",
    "일본 쇼도시마 도노쇼 앞바다를 항해하는 고속 여객선 실사",
    "일본 해상교통의 예시로 부산 출발 국제항로에 해당하는 선박은 아닙니다."
  ]
}
TSUSHIMA={}
assert len(CHOICES)==20 and len(TSUSHIMA)==0
report=json.loads(REPORT.read_text("utf-8"))

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
          "User-Agent":"Nipponferry-V40-editorial/1.0 (https://www.nipponferry.com/)",
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
        if f'/images/hub-thumbnails/{slug}.svg' not in piece:
            raise RuntimeError(f"Expected a graphic-only article, not a previously photographed card: {slug}")
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
            note=f'<p class="v40-image-credit" style="font-size:12px;line-height:1.7;padding:9px 15px;background:#f0f7fc;color:#345b71">{credit(obj)}</p>'
            art=art[:pos]+note+art[pos:]
        else:
            h1=re.search(r'</h1>',art)
            if not h1:raise RuntimeError("No insertion point for "+slug)
            art=art[:h1.end()]+(f'<figure class="v40-article-photo" style="margin:18px auto;max-width:950px">'
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
print("V40: 20/20 graphics replaced with matching Commons real photos, metadata and credits.")
