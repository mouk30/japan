#!/usr/bin/env python3
"""V38: 20 subject-matched Commons photos + 2 genuine Tsushima-food photos.

Selections are editorially reviewed Commons filenames from v38-commons-research.json.
Fail closed before mutating files if *any* selected licence or image cannot be validated.
Maintain original article URLs/content except one representative image, social preview,
and a visible attribution under its photo. Never imply a visual example is a live venue.
"""
from __future__ import annotations
import html,io,json,re,time,urllib.request
from pathlib import Path
from PIL import Image,ImageOps

SITE=Path("site")
REPORT=Path("docs/v38-commons-research.json")
OUT=Path("docs/v38-deployed-photo-credits.json")
HOST="https://www.nipponferry.com"
MEDIA=SITE/"images/culture-verified"
FOODMEDIA=SITE/"images/food-verified"
# File name and Korean subject description are manually reviewed together.
CHOICES={
  "japan-castle-moats": [
    "Matsumoto Castle Moat Bridge (26828913331).jpg",
    "마쓰모토성 해자와 붉은 다리가 함께 보이는 실제 사진",
    "해자 위 다리를 촬영한 사례입니다. 모든 성의 해자 구조가 동일하지는 않습니다."
  ],
  "japanese-pagoda-five-stories": [
    "Tō-ji.jpg",
    "교토 도지 사찰의 실제 오층탑",
    "교토 도지의 오층탑을 촬영한 사진으로, 모든 오층탑의 세부 구조를 대표하지는 않습니다."
  ],
  "japan-samurai-armor": [
    "Display of samurai armor and weapons in Japan (104).jpg",
    "일본에서 전시된 사무라이 갑옷과 무구 실물",
    "실제 역사 유물·복원 전시를 보여주며 전투 장면은 아닙니다."
  ],
  "japanese-katana-curvature": [
    "Katana, sword (AM 1934.316-1).jpg",
    "곡선 형태가 보이는 박물관 소장 일본도(카타나) 실물",
    "박물관 소장품으로 실제 검날의 곡률을 설명하는 사진입니다."
  ],
  "japanese-sword-guards-tsuba": [
    "Sword Guard (Tsuba) MET 36.120.79 001may2014.jpg",
    "미국 메트로폴리탄 미술관의 일본도 쓰바 검장 실물 유물",
    "일본도 손잡이와 칼날 사이의 손 보호용 쓰바 유물입니다."
  ],
  "japan-traditional-roof-tiles": [
    "Seiman-ji onigawara ac (9).jpg",
    "아이치현 세이만지의 1815년 제작 오니가와라 장식 기와",
    "아이치현 사찰의 실제 오니가와라 유물입니다."
  ],
  "japanese-engawa-veranda": [
    "Engawa.jpg",
    "일본 전통 건물 구 반도 가옥의 엔가와 마루 실제 사진",
    "전통 주택 엔가와의 공간 구성 사례입니다."
  ],
  "japanese-local-train-one-man": [
    "Takayama Honsen -One man operation.jpg",
    "일본 다카야마 본선의 차장 없이 운행하는 원맨 디젤열차",
    "다카야마 본선의 실제 원맨운전 차량입니다."
  ],
  "japanese-ferries-islands-life": [
    "Shodoshima-exp-ferry Tonosho.jpg",
    "쇼도시마 도노쇼항을 출항하는 지역 연락 페리 실사",
    "쇼도시마 도노쇼항의 페리 운항 사례입니다."
  ],
  "japanese-ropeways-mountain-access": [
    "Hakone Ropeway Gondola 20050105.jpg",
    "2005년 하코네 로프웨이의 옛 모델 곤돌라 차량",
    "2005년에 촬영된 구형 차량이며 현재 운행 모델이나 운영상태를 뜻하지 않습니다."
  ],
  "japan-tram-streetcars-history": [
    "HIROSHIMA STREETCAR AT HIROSHIMA STATION JAPAN JUNE 2012 (7428018070).jpg",
    "2012년 히로시마역 앞 실제 노면전차 운행 사진",
    "2012년 촬영한 역사적 운행 장면으로 현재 편성·노선 정보는 별도 확인해야 합니다."
  ],
  "japan-railway-station-stamps": [
    "Tokyo station eki stamp.jpg",
    "2024년 도쿄역의 실제 에키 스탬프 날인물 사진",
    "도쿄역의 역 스탬프를 촬영한 사례로 현재 도장 디자인·비치 위치는 달라질 수 있습니다."
  ],
  "japan-geothermal-steam-hells": [
    "Umi Jigoku (Sea Hell) in Beppu.jpg",
    "벳푸 우미지고쿠의 고온 온천 연못 실사",
    "관광용 고온 연못이므로 일반 목욕탕과 다릅니다."
  ],
  "japan-terraced-rice-fields": [
    "Wajima Shiroyone Senmaida Rice Terraces.jpg",
    "2018년 이시카와현 와지마 시로요네 센마이다 계단식 논 실사",
    "2018년 촬영 자료로 최근 지진 이후 현장의 현재 상태와 동일하지 않을 수 있습니다."
  ],
  "japan-yakushima-ancient-cedars": [
    "Jomon Sugi 01.jpg",
    "가고시마현 야쿠시마의 오래된 조몬스기 삼나무 실사",
    "야쿠시마에서 촬영한 조몬스기 나무 사진입니다."
  ],
  "japan-snow-country-architecture": [
    "Suganuma Gassho village - Flickr - tsuda.jpg",
    "일본 설국 지역 고카야마 스가누마의 갓쇼즈쿠리 지붕 건축 실사",
    "설국에 발달한 급경사 초가지붕 구조의 예시이며 사진 속 계절은 별도로 판단해야 합니다."
  ],
  "japan-ajisai-hydrangea-season": [
    "Hydrangeas of Hase-dera Temple - panoramio.jpg",
    "가마쿠라 하세데라 사찰의 수국이 핀 풍경 실제 사진",
    "가마쿠라 하세데라의 2012년 수국 사진이며 최신 개화 상황은 아닙니다."
  ],
  "japan-stone-lanterns": [
    "Japanese garden, Sanzen-in 03.jpg",
    "교토 산젠인 사찰 정원의 돌 석등 실사",
    "교토 산젠인 정원의 석등 장식 사례입니다."
  ],
  "japanese-wind-chimes-furin": [
    "Fūrin windchimes at Togo Shrine, Harajuku, Tokyo.jpg",
    "도쿄 하라주쿠 도고신사에 설치된 일본식 후린 풍경",
    "하라주쿠 도고신사의 풍경 전시 실사입니다."
  ],
  "japan-kagawa-udon-pilgrimage": [
    "Kama-age sanuki udon by sekido in Takamatsu, Kagawa.jpg",
    "가가와현 다카마쓰 식당에서 촬영한 가마아게 사누키 우동",
    "가가와현의 실제 사누키 우동 음식 예시로 현재 영업 상황과 관계 없습니다."
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
          "User-Agent":"Nipponferry-V38-editorial/1.0 (https://www.nipponferry.com/)",
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
        tag=re.search(r'<figure class="v36-photo"><img[^>]*>',piece)
        if not tag:raise RuntimeError("card photo missing "+slug)
        oldtag=tag.group()
        newtag=re.sub(r'src="[^"]+"',f'src="{obj["local"]}"',oldtag,count=1)
        newtag=re.sub(r'alt="[^"]+"',f'alt="{html.escape(obj["subject"],quote=True)}"',newtag,count=1)
        piece=piece.replace(oldtag,newtag,1)
        piece=piece.replace("<em>주제 참고 이미지</em>","<em>주제 실사 · 출처 본문</em>",1)
        hub=hub[:a]+piece+hub[b:]
        path=SITE/f"things-to-do/{slug}/index.html"
        art=path.read_text("utf-8")
        photo_pat=r'<img\b(?![^>]*mascot\.png)[^>]*>'
        matches=list(re.finditer(photo_pat,art))
        if matches:
            art,pos=change_img(art,obj,photo_pat)
            note=f'<p class="v38-image-credit" style="font-size:12px;line-height:1.7;padding:9px 15px;background:#f0f7fc;color:#345b71">{credit(obj)}</p>'
            art=art[:pos]+note+art[pos:]
        else:
            h1=re.search(r'</h1>',art)
            if not h1:raise RuntimeError("No insertion point for "+slug)
            art=art[:h1.end()]+(f'<figure class="v38-article-photo" style="margin:18px auto;max-width:950px">'
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
print("V38 complete 20/20 subject-photo article+card+OG updates and 2/2 Tsushima actual food photos.")
