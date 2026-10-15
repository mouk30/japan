#!/usr/bin/env python3
"""V41: 20 subject-matched Commons photos + 2 genuine Tsushima-food photos.

Selections are editorially reviewed Commons filenames from v41-commons-research.json.
Fail closed before mutating files if *any* selected licence or image cannot be validated.
Maintain original article URLs/content except one representative image, social preview,
and a visible attribution under its photo. Never imply a visual example is a live venue.
"""
from __future__ import annotations
import html,io,json,re,time,urllib.request
from pathlib import Path
from PIL import Image,ImageOps

SITE=Path("site")
REPORT=Path("docs/v41-commons-research.json")
OUT=Path("docs/v41-deployed-photo-credits.json")
HOST="https://www.nipponferry.com"
MEDIA=SITE/"images/culture-verified"
FOODMEDIA=SITE/"images/food-verified"
# File name and Korean subject description are manually reviewed together.
CHOICES={
  "traditional-experience-booking": [
    "Tea ceremony performing 2.jpg",
    "기모노를 입고 차를 준비하는 일본 다도 시연 실사",
    "다도 체험의 실제 시연 장면이며 예약 가능 여부를 뜻하지 않습니다."
  ],
  "japan-railway-platform-melodies": [
    "Tobu-railway-TS43-Kameidosuijin-station-platform-20190914-105007.jpg",
    "도쿄 도부 가메이도스이진역 승강장 실제 사진",
    "음악을 촬영한 사진은 아니며 일본 승강장의 한 사례입니다."
  ],
  "japan-sea-of-japan-coast": [
    "Tojinbo (8706974709).jpg",
    "후쿠이현 도진보의 동해 연안 해안 절벽 실사",
    "실제 도진보 해안이며 사진 촬영 시기가 반드시 겨울인 것은 아닙니다."
  ],
  "kabuki-japanese-theater": [
    "Japan Kabuki actress makeup 1202.jpg",
    "실제 가부키 배우의 얼굴 분장 사진",
    "가부키 분장 사례로 모든 구마도리 양식을 보여주는 것은 아닙니다."
  ],
  "rakugo-japanese-storytelling": [
    "Rakugo-sanmafestival.jpg",
    "도쿄 메구로 산마축제에서 진행된 라쿠고 이야기 공연 사진",
    "실제 라쿠고 공연 장면으로 현재 공연 일정이나 예약 가능 여부와는 무관합니다."
  ],
  "aizome-japanese-indigo-dye": [
    "Indigobad från Japan.jpg",
    "아이치현 오카자키 천연 염색 공방의 쪽염색 염색조 실제 사진",
    "남색 염색조의 실물이며 완성된 직물이나 체험 중인 사람을 보여주는 사진은 아닙니다."
  ],
  "kutani-japanese-porcelain": [
    "Kutani-Ware Plate, late 17th century, Japan, porcelain with enamel - Art Institute of Chicago - DSC00224.JPG",
    "시카고 미술관 소장 17세기 후반 일본 구타니야키 채색 접시 실물",
    "구타니야키 역사적 유물로 오늘날 일본 공방의 작업 장면은 아닙니다."
  ],
  "dashi-japanese-umami-stock": [
    "JapaneseKatsuobushi.jpg",
    "일본 다시 육수의 재료인 가쓰오부시와 전용 대패 실제 사진",
    "가쓰오부시 재료 사진으로 완성된 육수나 모든 다시 재료를 보여주지는 않습니다."
  ],
  "japan-trash-bin-shortage": [
    "See thru recycle bins JR東海 2010 (4624233234).jpg",
    "2010년 나고야역 신칸센 승강장의 투명 분리수거함 실제 사진",
    "일본 분리수거함 사례이며 모든 거리에서 쓰레기통이 부족하다는 주장 자체를 증명하지는 않습니다."
  ],
  "japanese-sento-public-bath-manners": [
    "The view from BANDAI in Japanese SENTO 番台からの眺め 01.jpg",
    "도쿄 에도도쿄 야외건축박물관에 보존된 고다카라유 목욕탕 내부 실사",
    "보존된 역사적 센토 공간이며 현재 운영 중인 시설이나 목욕 예절 시연 사진은 아닙니다."
  ],
  "kissaten-japanese-retro-coffee": [
    "名曲喫茶ヴィオロン.jpg",
    "도쿄 아사가야 클래식 음악 킷사텐 비올롱의 실제 사진",
    "실제 음악 감상 카페의 사례이며 현재 운영시간·메뉴는 별도 확인해야 합니다."
  ],
  "toji-yuzu-bath-japan": [
    "Citron hot water of the winter solstice,yuzuyu,katori-city,japan.JPG",
    "지바현 가토리시 동짓날 유자탕 물에 띄운 유자 실사",
    "유자탕의 실제 사진으로 특정 온천 시설의 겨울 행사 사진은 아닙니다."
  ],
  "japan-forest-bathing-shinrin-yoku": [
    "Kugurisugi Cedar (31536833473).jpg",
    "야쿠시마 시라타니운스이쿄 숲의 이끼 낀 삼나무와 산책길 실사",
    "삼림욕 장소의 실제 예시이며 건강 효과를 입증하는 사진은 아닙니다."
  ],
  "japan-diving-first-time": [
    "Big Turtle Rock 大亀石 near the Yonaguni Monument.jpg",
    "오키나와 요나구니 해역의 바닷속 거북바위 실제 수중 사진",
    "일본 다이빙 지역의 수중 풍경으로 초보 교육과정이나 강습 장면은 아닙니다."
  ],
  "why-japanese-onsen-special": [
    "Tsurunoyu onsen rotenburo2.JPG",
    "아키타현 쓰루노유 온천의 실제 야외 노천탕 사진",
    "전통 온천의 한 사례이며 현재 수질·요금·운영 상태를 보장하지 않습니다."
  ],
  "family-with-kids": [
    "Water tank of the goldfish,Aqua-marine-Fukushima,Iwaki-city,Japan.jpg",
    "후쿠시마현 아쿠아마린 수족관의 금붕어 수조 전시 실사",
    "가족 여행지 수족관 전시의 실제 사례로 운영시간·전시 구성은 달라질 수 있습니다."
  ],
  "solo-cultural-day": [
    "Dry-sand Zen garden made of beige stripes a sunny day at Higashiyama Jisho-ji Buddhist temple Ginkaku-ji Kyoto Japan.jpg",
    "교토 긴카쿠지 경내의 전통 모래 선(禪) 정원 실제 사진",
    "혼자 감상할 수 있는 실제 문화공간 예시로 현장 혼잡도는 나타내지 않습니다."
  ],
  "japan-free-low-budget": [
    "Lascar Ueno-koen Park (1298835399).jpg",
    "도쿄 우에노공원 산책 공간의 실제 사진",
    "무료 공원 산책 예시이며 공원 안 모든 박물관과 유료 시설이 무료인 것은 아닙니다."
  ],
  "accessible-slow-travel": [
    "Accessible slope in Chion-in.jpg",
    "교토 지온인 사찰에 설치된 실제 휠체어 경사로 실사",
    "무장애 편의시설의 예시이며 사찰 전체 동선 접근성을 보증하지는 않습니다."
  ],
  "experience-booking-checklist": [
    "Japan tea ceremony 1165.jpg",
    "일본 전통 다도 시연의 실제 사진",
    "체험 준비를 설명하는 다도 예시이며 상품 예약·취소 규정은 사진과 무관합니다."
  ]
}
TSUSHIMA={}
assert len(CHOICES)==20 and len(TSUSHIMA)==0
report=json.loads(REPORT.read_text("utf-8"))
broad=json.loads(Path("docs/v41-broad-commons-research.json").read_text("utf-8"))
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
          "User-Agent":"Nipponferry-V41-editorial/1.0 (https://www.nipponferry.com/)",
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
            note=f'<p class="v41-image-credit" style="font-size:12px;line-height:1.7;padding:9px 15px;background:#f0f7fc;color:#345b71">{credit(obj)}</p>'
            art=art[:pos]+note+art[pos:]
        else:
            h1=re.search(r'</h1>',art)
            if not h1:raise RuntimeError("No insertion point for "+slug)
            art=art[:h1.end()]+(f'<figure class="v41-article-photo" style="margin:18px auto;max-width:950px">'
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
print("V41: all final 20 graphics replaced with sourced real photographs, credits and metadata.")
