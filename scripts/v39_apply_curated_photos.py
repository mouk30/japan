#!/usr/bin/env python3
"""V39: 20 subject-matched Commons photos + 2 genuine Tsushima-food photos.

Selections are editorially reviewed Commons filenames from v39-commons-research.json.
Fail closed before mutating files if *any* selected licence or image cannot be validated.
Maintain original article URLs/content except one representative image, social preview,
and a visible attribution under its photo. Never imply a visual example is a live venue.
"""
from __future__ import annotations
import html,io,json,re,time,urllib.request
from pathlib import Path
from PIL import Image,ImageOps

SITE=Path("site")
REPORT=Path("docs/v39-commons-research.json")
OUT=Path("docs/v39-deployed-photo-credits.json")
HOST="https://www.nipponferry.com"
MEDIA=SITE/"images/culture-verified"
FOODMEDIA=SITE/"images/food-verified"
# File name and Korean subject description are manually reviewed together.
CHOICES={
  "japanese-machiya-townhouses": [
    "Streets of Gion, Kyoto - Gion7712.jpg",
    "교토 기온의 좁은 골목에 늘어선 전통 마치야 가옥 실제 사진",
    "교토 기온의 마치야 외관 사례이며 주택 내부를 촬영한 사진은 아닙니다."
  ],
  "japan-ainu-embroidery": [
    "Robe, 'Retara Kapara Amip' LACMA M.71.87.1.jpg",
    "홋카이도 아이누 민족의 19세기 자수와 덧댐 장식이 있는 의복 유물",
    "로스앤젤레스 카운티 미술관 소장 역사 의복이며 현재 공방에서 제작하는 장면은 아닙니다."
  ],
  "japan-amami-oshima-tsumugi": [
    "Mud Dyeing Kanai Workshop.jpg",
    "아마미 오시마쓰무기 전통 염색과 연관된 가나이 공방의 진흙 염색 작업 장소",
    "염색 공방의 진흙 염색 공간으로 완성된 직물 제품 사진은 아닙니다."
  ],
  "noh-japanese-mask-theater": [
    "Noh mask in Berlin museum 2.jpg",
    "베를린 박물관에 전시된 일본 전통 노(能) 공연 가면 실물",
    "박물관 소장 가면 유물로 실제 무대 공연 중인 배우의 사진은 아닙니다."
  ],
  "bunraku-japanese-puppet-theater": [
    "Bunraku theater 4.jpg",
    "오사카 국립분라쿠극장의 실제 분라쿠 인형 공연 또는 전시 사진",
    "오사카 분라쿠극장에서 촬영된 사진이며 각 인형의 제작 시기는 따로 확인해야 합니다."
  ],
  "shamisen-japanese-three-string-instrument": [
    "Shamisen MET midp69.271.2a.jpg",
    "메트로폴리탄 미술관 소장 일본 전통 삼현악기 샤미센 실물",
    "실제 샤미센 악기 유물의 사진으로 연주 현장을 촬영한 것은 아닙니다."
  ],
  "ukiyoe-japanese-woodblock-art": [
    "MET 27 117 1 O2 sf.jpg",
    "메트로폴리탄 미술관 소장 일본 목판 삽화 제작용 실제 판목",
    "서적 삽화용 목판 유물로 모든 우키요에 다색판 제작 공정을 그대로 보여주는 사진은 아닙니다."
  ],
  "temari-japanese-thread-balls": [
    "Japanese Temari ball flanked by a maneki neko (01) (50532211976).jpg",
    "실로 촘촘한 기하학 무늬를 수놓은 일본식 테마리 공예품 실제 사진",
    "완성된 일본식 테마리 공예품 사례이며 일본 현지 공방 사진은 아닙니다."
  ],
  "sashiko-japanese-repair-stitching": [
    "Boro textile from Japan, with sashiko.jpg",
    "일본 보로 천에 기능과 장식을 더한 사시코 바느질 실제 직물 유물",
    "일본 직물의 사시코 바느질을 담은 실물 사진이며 실제 바느질 작업 장면은 아닙니다."
  ],
  "udon-japanese-regional-noodles": [
    "Udon noodles in a bowl in a restaurant in Hiroshima, Japan - September 2015.jpg",
    "2015년 히로시마 식당에서 촬영한 일본 우동 한 그릇",
    "히로시마 지역 식당 음식 사진으로 일본 전국의 우동 품종을 모두 보여주지는 않습니다."
  ],
  "yakitori-japanese-skewer-culture": [
    "MyPlate gov Cultural Food (20241025-USDA-FNS-UNK-0031).jpg",
    "닭고기와 파를 구운 일본식 네기마 야키토리 꼬치 요리 실제 사진",
    "미국 농무부의 요리 예시 사진으로 일본 현지 식당에서 촬영한 사진은 아닙니다."
  ],
  "onigiri-japanese-rice-ball": [
    "Onigiri 001.jpg",
    "김과 밥으로 만든 일본 전통 오니기리 삼각 주먹밥 실제 음식 사진",
    "일본에서 볼 수 있는 주먹밥 음식 예시이며 특정 편의점 제품 사진은 아닙니다."
  ],
  "konbini-japanese-convenience-store-life": [
    "Konbini drink corner 2009 (3819547946).jpg",
    "일본 편의점 내부의 실제 음료 진열 코너 촬영 사진",
    "2009년 촬영 자료이며 현재 판매 상품 및 진열 구성을 뜻하지 않습니다."
  ],
  "japanese-hightech-public-toilets": [
    "Japanese toilet buttons.jpg",
    "일본 비데식 화장실의 실제 세정·중지 조작 버튼 사진",
    "비데 조작 버튼 사례로 모든 일본 공중화장실에 동일한 버튼이 있다는 뜻은 아닙니다."
  ],
  "yatai-japanese-food-stalls": [
    "ObihiroYatai.jpg",
    "홋카이도 오비히로에 모인 일본식 야타이 노점 음식 거리 실제 사진",
    "홋카이도 오비히로의 겨울 야타이로 후쿠오카 야타이 현장 사진은 아닙니다."
  ],
  "omikuji-japanese-fortune": [
    "Kamakura omikuji.jpg",
    "가나가와현 가마쿠라 신사에 묶어둔 일본 오미쿠지 운세 종이 실제 사진",
    "가마쿠라 신사 운세의 한 가지 사례입니다."
  ],
  "japan-small-streets": [
    "Pontocho by Aleksander Dragnes.jpg",
    "교토 폰토초의 좁은 골목길을 담은 실제 거리 사진",
    "교토 폰토초 골목의 과거 촬영 자료이며 현재 가게 구성은 달라질 수 있습니다."
  ],
  "setsubun-japanese-beans": [
    "Hakone Shrine Setsubun mamemaki 02.jpg",
    "하코네 신사에서 열린 일본 세쓰분 마메마키 콩 뿌리기 행사 실제 사진",
    "하코네 신사의 실제 세쓰분 의례 사례로 매년 행사 운영 내용은 달라질 수 있습니다."
  ],
  "ume-japanese-plum-blossoms": [
    "Plum Kairakuen (201573725).jpeg",
    "이바라키현 미토 가이라쿠엔 공원의 일본 매화꽃 실제 사진",
    "가이라쿠엔 매화꽃 사례이며 현재 개화 상황을 나타내지 않습니다."
  ],
  "tsukimi-japanese-moon-viewing": [
    "Tsukimi,moon-viewing-party,japan.JPG",
    "일본 쓰키미 달맞이 상차림의 경단과 억새 장식 실제 사진",
    "일본 달맞이 행사 상차림 예시이며 특정 축제 개최장 사진은 아닙니다."
  ]
}
TSUSHIMA={}
assert len(CHOICES)==20 and len(TSUSHIMA)==0
report=json.loads(REPORT.read_text("utf-8"))
report.update(json.loads(Path("docs/v39-extra-research.json").read_text("utf-8")))
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
          "User-Agent":"Nipponferry-V39-editorial/1.0 (https://www.nipponferry.com/)",
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
        piece=piece.replace("<em>주제 안내 그래픽</em>","<em>주제 실사 · 출처 본문</em>",1)
        hub=hub[:a]+piece+hub[b:]
        path=SITE/f"things-to-do/{slug}/index.html"
        art=path.read_text("utf-8")
        photo_pat=r'<img\b(?![^>]*mascot\.png)[^>]*>'
        matches=list(re.finditer(photo_pat,art))
        if matches:
            art,pos=change_img(art,obj,photo_pat)
            note=f'<p class="v39-image-credit" style="font-size:12px;line-height:1.7;padding:9px 15px;background:#f0f7fc;color:#345b71">{credit(obj)}</p>'
            art=art[:pos]+note+art[pos:]
        else:
            h1=re.search(r'</h1>',art)
            if not h1:raise RuntimeError("No insertion point for "+slug)
            art=art[:h1.end()]+(f'<figure class="v39-article-photo" style="margin:18px auto;max-width:950px">'
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
print("V39 complete 20/20 subject-photo article+card+OG updates and 2/2 Tsushima actual food photos.")
