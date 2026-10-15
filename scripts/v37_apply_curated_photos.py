#!/usr/bin/env python3
"""V37: 20 subject-matched Commons photos + 2 genuine Tsushima-food photos.

Selections are editorially reviewed Commons filenames from v37-commons-research.json.
Fail closed before mutating files if *any* selected licence or image cannot be validated.
Maintain original article URLs/content except one representative image, social preview,
and a visible attribution under its photo. Never imply a visual example is a live venue.
"""
from __future__ import annotations
import html,io,json,re,time,urllib.request
from pathlib import Path
from PIL import Image,ImageOps

SITE=Path("site")
REPORT=Path("docs/v37-commons-research.json")
OUT=Path("docs/v37-deployed-photo-credits.json")
HOST="https://www.nipponferry.com"
MEDIA=SITE/"images/culture-verified"
FOODMEDIA=SITE/"images/food-verified"
# File name and Korean subject description are manually reviewed together.
CHOICES={
"local-food-market-guide":("Nishiki market - Dec 31 2021 various 18 22 06 321000.jpeg","교토 니시키시장 안쪽의 실제 식품 판매 공간","교토 시장을 예로 든 사진이며 모든 일본 시장을 대표하지는 않습니다."),
"japan-castle-stone-walls":("Himeji castle April 04.jpg","효고현 히메지성 내해자 옆 돌담(이시가키) 실제 사진","히메지성 내해자와 돌담"),
"japan-castle-tenshu-towers":("Himeji Castle The Keep Towers.jpg","히메지성의 천수각 건물 실제 사진","천수각의 실물 구조"),
"japan-temple-bells":("RyoanJi-Kane.jpg","교토 료안지 사찰의 범종 실제 촬영 사진","료안지 범종, 모든 사찰의 종은 아님"),
"japan-night-train-travel":("Jr 285 Sunrise Izumo 20130413.jpg","JR 선라이즈 이즈모 침대열차 실물 차량","일본 침대열차 실제 차량"),
"japan-volcanic-onsen-geology":("Beppu Umi-jigoku04n4272.jpg","벳푸 우미지고쿠에서 솟는 온천수와 수증기 실제 사진","벳푸의 온천 현상 사례. 지질 단면 사진은 아님"),
"japan-izakaya-yokocho-alleys":("Shinjuku-West Omoide-Yokocho.jpg","도쿄 신주쿠 오모이데요코초의 실제 골목 촬영","신주쿠 요코초 골목 풍경"),
"japan-public-parks-hanami":("Hanami Matsuri picknick in Ueno park, Tokyo Japan.jpg","도쿄 우에노공원의 실제 벚꽃놀이 피크닉","공원의 봄 풍경 사례. 사계절 전체가 찍힌 사진은 아님"),
"japan-kanazawa-gold-leaf":("Kanazawa Gold Factory.jpg","가나자와 금박 공방의 금박 가공 작업 실제 사진","가나자와 금박 공정"),
"japan-niigata-rice-snow":("Rice terraces, Yamakoshi, Niigata.jpg","니가타현 나가오카 야마코시의 계단식 논 실제 풍경","니가타 쌀농사 풍경. 설경 사진은 아님"),
"japan-nagasaki-lantern-festival":("Lanterns in Nagasaki.jpg","나가사키 랜턴 페스티벌 행사 현장에 걸린 등불","나가사키 실제 행사 사진"),
"washi-japanese-handmade-paper":("Japanese paper making 02.jpg","후쿠이현 에치젠시 전통 수제 종이 뜨기 시연 실제 사진","에치젠 전통 화지 제작 공정"),
"sushi-edo-japanese-food-history":("Tuna nigiri sushi - Sushiko (2648979899).jpg","참치 니기리초밥 실제 음식 사진","니기리초밥 음식 예시. 에도시대 역사 현장 사진은 아님"),
"tempura-japanese-fried-food":("Tempura 001.jpg","일본 덴푸라 튀김을 담은 실제 정식 음식 사진","덴푸라 음식의 예시"),
"regional-soba-japanese-buckwheat":("Ten zaru soba by akira yamada in Yokohama.jpg","일본 요코하마 식당의 자루소바와 튀김 실제 사진","자루소바의 실제 조리 예시. 각 지역 소바의 차이를 모두 보여주지는 않음"),
"okonomiyaki-osaka-hiroshima":("Okonomiyaki by zezebono in Osaka.jpg","오사카 도톤보리 식당에서 촬영한 오코노미야키","오사카식 예시. 히로시마식과의 비교 사진은 아님"),
"takoyaki-osaka-street-food":("Takoyaki by hirotomo in Osaka.jpg","오사카 도톤보리에서 촬영한 타코야키 실제 음식","오사카 타코야키 실사"),
"depachika-japanese-department-food":("銀座 天一 2010 (4673838729).jpg","이세탄 백화점 지하 데파치카에서 판매 중인 튀김 실제 사진","백화점 식품관의 실제 판매 사례"),
"hanabi-japanese-fireworks-summer":("Sumidagawa Fireworks Festival2012.jpg","도쿄 스미다가와 불꽃놀이 축제 실제 사진","스미다가와 불꽃축제의 실제 불꽃"),
"hatsumode-japanese-first-shrine-visit":("Meiji shrine saisenbako (New Year).jpg","1월 1일 메이지신궁 새해 참배 시기의 새전함 실사","하쓰모데 기간의 메이지신궁 사진")
}
TSUSHIMA={
"tsushima-food":("tsushima-taiyaki","Sakanotaiyaki.jpg","대마도 사가 지역의 둥근 붕어빵, 2020년 이전 판매 제품","역사적인 대마도 지역 간식입니다. 2020년 해당 가게가 폐업했으며 현재 구매 가능하다는 의미는 아닙니다."),
"tsushima-dessert":("tsushima-kasumaki","かすまき.png","대마도의 전통 팥소 과자 카스마키 실물 사진","대마도 카스마키의 실제 사진이며 특정 판매점 상품을 보증하지 않습니다."),
}
assert len(CHOICES)==20 and len(TSUSHIMA)==2
report=json.loads(REPORT.read_text("utf-8"))
def get(slug,filename):
    options=report[slug]["options"]
    item=next((x for x in options if x["filename"]==filename),None)
    if item is None:raise RuntimeError(f"Verified image metadata missing: {slug}: {filename}")
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
            note=f'<p class="v37-image-credit" style="font-size:12px;line-height:1.7;padding:9px 15px;background:#f0f7fc;color:#345b71">{credit(obj)}</p>'
            art=art[:pos]+note+art[pos:]
        else:
            h1=re.search(r'</h1>',art)
            if not h1:raise RuntimeError("No insertion point for "+slug)
            art=art[:h1.end()]+(f'<figure class="v37-article-photo" style="margin:18px auto;max-width:950px">'
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
print("V37 complete 20/20 subject-photo article+card+OG updates and 2/2 Tsushima actual food photos.")
