#!/usr/bin/env python3
"""V43: replace exactly 20 source-unknown editorial art with genuinely photographed images.
Preserve custom kimono/yukata editorial-comparison card. Fail closed on unverifiable
license, image, article binding, broken markup or preexisting photo credits.
"""
from pathlib import Path
from PIL import Image,ImageOps
import json,html,io,re,time,urllib.request,hashlib,copy
ROOT=Path("site")
HUB=ROOT/"things-to-do/index.html"
REPORT=Path("docs/v43-deployed-photo-credits.json")
CANDIDATES=Path("docs/v43-commons-candidates.json")
SUPPLEMENT=Path("docs/v43-commons-supplement.json")
AUDIT=Path("docs/v36-hub-cards-audit.json")
PICKS={
  "omamori-japanese-amulet-culture": [
    "Omamori of Fujisan Hongu Sengen Taisha.jpg",
    "후지산 혼구 센겐타이샤 신사의 오마모리 부적 실물",
    "실제 신사 오마모리 사진으로 모든 신사에서 같은 부적을 판매하는 것은 아닙니다."
  ],
  "ema-japanese-wish-wooden-plaques": [
    "Shinto shrine votive tablets in rural Fukui prefecture.jpg",
    "후쿠이현 신사의 소원 에마 나무패 실제 사진",
    "일본 신사에서 소원을 적는 에마 사례이며 특정 관광지의 운영시간과 관계없습니다."
  ],
  "goshuin-temple-shrine-stamps": [
    "Emma H. Leonhart's Goshuinchō 03.jpg",
    "2024년 일본 순례자가 받은 실제 고슈인 수첩의 한 페이지",
    "실제 고슈인 기록 사진이며 현재 특정 신사의 접수시간과 디자인은 다를 수 있습니다."
  ],
  "ryokan-japanese-inn-hospitality": [
    "Our room at Seikansō Ryokan (6156061472).jpg",
    "일본 세이칸소 료칸의 실제 전통 객실 내부",
    "실제 투숙객이 촬영한 료칸 객실이며 모든 료칸의 객실 구조를 대표하지는 않습니다."
  ],
  "tatami-floor-japanese-living": [
    "Japanese room with tatami mats.jpg",
    "다다미와 쇼지가 있는 실제 일본식 방",
    "다다미방 실사 사례이며 특정 숙소의 현재 객실 사진은 아닙니다."
  ],
  "futon-japanese-bedding-culture": [
    "Futons in a Ryokan.jpg",
    "다카야마 아스나로 료칸의 실제 일본식 후톤 침구",
    "현지 료칸 침구의 예시이며 모든 료칸에서 같은 침구를 사용하지는 않습니다."
  ],
  "shoji-fusuma-japanese-doors": [
    "Shōji and Engawa of the former Miura residence 6-10 Reisenmachi Hakata-ku Fukuoka 20240119.jpg",
    "후쿠오카 하카타 옛 미우라 가옥의 쇼지 종이문과 엔가와",
    "일본식 쇼지의 실제 사진이며 후스마와 쇼지를 한 화면에서 비교한 것은 아닙니다."
  ],
  "kotatsu-japanese-winter-table": [
    "Kotatsu Electric.jpg",
    "열판이 설치된 일본 전기 고타쓰 테이블의 실제 사진",
    "전기 난방 장치를 갖춘 고타쓰 사례이며 가족이 둘러앉은 생활 장면은 아닙니다."
  ],
  "furoshiki-japanese-wrapping-cloth": [
    "Traditional Japanese wrapping cloth,huroshiki,katori-city,japan.JPG",
    "지바현 가토리시의 전통 후로시키 포장천 실제 사진",
    "일본 후로시키 보자기의 실물 예시로 특정 포장법 전체를 설명한 사진은 아닙니다."
  ],
  "bento-japanese-lunchbox-everyday": [
    "TOKYO Cuisine,Japanese style lunch box (2030502153).jpg",
    "일본식 도시락에 밥과 반찬을 담은 벤토 실제 사진",
    "일본 도시락 구성 예시이며 모든 가정·지역의 벤토가 같다는 뜻은 아닙니다."
  ],
  "wagashi-japanese-seasonal-sweets": [
    "Wagashi closeup 13.jpg",
    "수국 등 계절 꽃을 표현한 전통 일본 화과자 실물",
    "계절별 디자인의 실제 화과자 사례이며 현재 판매되는 제품을 보장하지 않습니다."
  ],
  "matcha-sencha-japanese-green-tea": [
    "Matcha layout with leaf, tea, and powder.jpg",
    "말차 잎·분말·차를 배치한 실제 차 재료 사진",
    "말차에 관한 사진으로 센차의 추출 방식까지 동시에 보여주는 사진은 아닙니다."
  ],
  "toshikoshi-soba-newyear-tradition": [
    "New Year's Kansai style soba (38825836845).jpg",
    "일본 간사이식 연말 도시코시 소바 음식 실제 사진",
    "새해 전야에 먹는 도시코시 소바 사례이며 모든 지역에서 같은 재료를 사용하지는 않습니다."
  ],
  "ramen-japanese-noodle-evolution": [
    "Tsukemen at a Tokyo restaurant.jpg",
    "2014년 도쿄 로쿠린샤 식당에서 촬영한 쓰케멘 실물",
    "라멘에서 파생된 쓰케멘의 실사이며 모든 일본 라멘의 형태를 보여주는 것은 아닙니다."
  ],
  "izakaya-japanese-afterwork-culture": [
    "Quality izakaya in Ebisu 2.jpg",
    "도쿄 에비스의 실제 이자카야 음식점 풍경",
    "이자카야 문화를 보여주는 실제 사진이며 현재 영업 상황은 확인이 필요합니다."
  ],
  "osechi-ryori-japanese-new-year-food": [
    "Osechi.jpg",
    "일본 새해 음식 오세치를 찬합에 담은 실제 사진",
    "일본 오세치 요리 구성의 예시이며 특정 가정의 새해 풍습을 일반화하지 않습니다."
  ],
  "hanami-japanese-cherry-blossom-picnic": [
    "Hanami Matsuri picknick in Ueno park, Tokyo Japan.jpg",
    "도쿄 우에노공원에서 벚꽃 아래 피크닉을 즐기는 하나미 실사",
    "실제 하나미 소풍 사례이며 현재 개화 및 공원 규칙은 달라질 수 있습니다."
  ],
  "momijigari-japanese-autumn-leaves-culture": [
    "EikandoMomiji.jpg",
    "교토 에이칸도 사찰에서 촬영한 가을 단풍 실제 사진",
    "실제 가을 풍경의 한 시점이며 현재 단풍 현황을 나타내지 않습니다."
  ],
  "koinobori-childrens-day-japan": [
    "Koinobori matsuri at Sagami River, Sagamihara; May 2014 (09).jpg",
    "2014년 일본 사가미강 고이노보리 축제에서 촬영한 잉어깃발",
    "고이노보리 실사이며 해당 행사의 올해 개최 여부를 보장하지 않습니다."
  ],
  "tanabata-japanese-star-festival": [
    "Sendai-tanabata-streamers-aug2008.jpg",
    "2008년 센다이 다나바타 축제에 걸린 전통 장식 실제 사진",
    "실제 다나바타 축제 장식이며 현재 행사 일정 및 장소 운영과는 별개입니다."
  ]
}
assert len(PICKS)==20
sources=json.loads(CANDIDATES.read_text("utf-8"))
extra=json.loads(SUPPLEMENT.read_text("utf-8"))
inventory=json.loads(AUDIT.read_text("utf-8"))
eligible={x["slug"]:x for x in inventory["things"]["mappings"] if x["kind"]=="editorial-unverified"}
assert len(eligible)==20,len(eligible)
assert set(PICKS)==set(eligible),(set(PICKS)^set(eligible))
data={}
for slug,(filename,subject,note) in PICKS.items():
    options=[*sources.get(slug,{}).get("options",[]),*extra.get(slug,{}).get("options",[])]
    c=next((x for x in options if x["filename"]==filename),None)
    if c is None: raise RuntimeError("Commons original not present: "+slug+" "+filename)
    if not (c["licence"].startswith("CC BY") or c["licence"] in ("CC0","Public domain")):
        raise RuntimeError("Licence not compatible: "+slug)
    if c["width"]<550 or c["height"]<420:raise RuntimeError("Photo dimensions too small: "+slug)
    if not c["source_page"].startswith("https://commons.wikimedia.org/wiki/File:"):
        raise RuntimeError("Missing direct original URL: "+slug)
    data[slug]={"slug":slug,"subject":subject,"note":note,"source":c,
        "asset":f"/images/culture-verified/{slug}.webp"}
def download(item):
    url=item["source"]["remote"]
    for i in range(5):
        try:
            req=urllib.request.Request(url,headers={
                "User-Agent":"Nipponferry-V43-source-editor/1.0 (https://www.nipponferry.com/)",
                "Accept":"image/jpeg,image/png,image/webp,image/*;q=.8"})
            with urllib.request.urlopen(req,timeout=75) as stream:
                content=stream.read()
                mime=stream.headers.get("Content-Type","")
            if not mime.lower().startswith("image/") or len(content)<6000:
                raise RuntimeError(f"Invalid source {mime} {len(content)}")
            with Image.open(io.BytesIO(content)) as im:
                im.load()
                im=ImageOps.exif_transpose(im).convert("RGB")
                im.thumbnail((1440,1440),Image.Resampling.LANCZOS)
                buf=io.BytesIO()
                im.save(buf,format="WEBP",quality=83,method=5)
            result=buf.getvalue()
            if result[:4]!=b"RIFF" or result[8:12]!=b"WEBP":raise RuntimeError("Bad WebP magic")
            return result
        except Exception as exc:
            print("Retry",item["slug"],i,str(exc)[:180],flush=True)
            if i==4: raise
            time.sleep(2*(i+1))
# Download all before starting page modifications.
for n,item in enumerate(data.values(),1):
    item["_webp"]=download(item)
    print("V43 sourced photo",n,"/20",item["slug"],len(item["_webp"]),flush=True)
    time.sleep(.35)

def read_tag(htmlstr,i):
    q=None
    for j in range(i+4,len(htmlstr)):
        ch=htmlstr[j]
        if q:
            if ch==q:q=None
        elif ch in ('"',"'"):q=ch
        elif ch==">":return j+1
    raise RuntimeError("Unclosed image tag")
def replace_image_markup(body,item,expected):
    # Find actual photo by src attribute; never tamper with branding, lower page pictures
    images=[]
    for m in re.finditer(r'<img\b',body,re.I):
        tag=body[m.start():read_tag(body,m.start())]
        if f'src="{expected}"' in tag:images.append((m.start(),tag))
    if len(images)!=1:raise RuntimeError(f"Expected one exact original image: {item['slug']}: {len(images)}")
    i,tag=images[0]
    new=re.sub(r'\bsrc="[^"]+"',lambda _:f'src="{item["asset"]}"',tag,count=1)
    new=re.sub(r'\balt="[^"]*"',lambda _:f'alt="{html.escape(item["subject"],quote=True)}"',new,count=1)
    new=re.sub(r'\s+onerror="[^"]*"','',new,count=1)
    if 'alt="' not in new:new=new[:-1]+f' alt="{html.escape(item["subject"],quote=True)}">'
    c=item["source"]
    author=html.escape(c.get("author") or "Wikimedia Commons 사용자")
    origin=html.escape(c["source_page"],quote=True)
    licence=html.escape(c["licence"])
    licenseUrl=html.escape(c.get("licence_url") or c["source_page"],quote=True)
    caption=(f'<p class="v43-image-credit" style="font-size:12px;line-height:1.75;color:#3c5c70;'
        f'background:#f0f7fa;padding:9px 14px;margin:10px 0 20px;border-radius:6px">'
        f'실제 사진: <a href="{origin}" target="_blank" rel="noopener noreferrer">'
        f'{author} / Wikimedia Commons</a> · <a href="{licenseUrl}" target="_blank" '
        f'rel="noopener noreferrer">{licence}</a>. {html.escape(item["note"])} '
        f'원본 사진을 WebP로 변환·축소했습니다.</p>')
    return body[:i]+new+"\n"+caption+body[i+len(tag):]
def set_social(body,url):
    for name,attr in (("og:image","property"),("twitter:image","name")):
        pattern=re.compile(r'<meta\b(?=[^>]*\b'+attr+r'="'+re.escape(name)+r'")[^>]*>',re.I)
        target=f'<meta {attr}="{name}" content="{url}">'
        if pattern.search(body):body=pattern.sub(target,body,count=1)
        else:body=body.replace("</head>",target+"</head>",1)
        if body.count(f'{attr}="{name}"')!=1:raise RuntimeError("Duplicate social meta: "+name)
    return body
hub=HUB.read_text("utf-8")
pages={}
for slug,item in data.items():
    path=ROOT/"things-to-do"/slug/"index.html"
    original=eligible[slug]["image"]
    body=path.read_text("utf-8")
    body=replace_image_markup(body,item,original)
    body=set_social(body,"https://www.nipponferry.com"+item["asset"])
    if item["source"]["source_page"] not in body:raise RuntimeError("Missing visible attribution: "+slug)
    pages[path]=body
    cardkey=f'href="/things-to-do/{slug}/"'
    at=hub.find(cardkey)
    if at<0:raise RuntimeError("Missing card: "+slug)
    end=hub.find("</a>",at)
    segment=hub[at:end]
    if f'src="{original}"' not in segment:raise RuntimeError("Card has changed unexpectedly: "+slug)
    segment=segment.replace(f'src="{original}"',f'src="{item["asset"]}"',1)
    segment=segment.replace(f'alt="{html.escape(eligible[slug]["title"],quote=True)} 관련 게시글 대표 이미지"',
       f'alt="{html.escape(item["subject"],quote=True)}"')
    segment=segment.replace("<em>주제 편집 이미지</em>","<em>주제 실사 · 출처 본문</em>",1)
    if "<em>주제 실사 · 출처 본문</em>" not in segment:raise RuntimeError("Card badge not modified: "+slug)
    hub=hub[:at]+segment+hub[end:]
    eligible[slug].update({"image":item["asset"],"kind":"verified-real-photo",
      "photo_source":item["source"]["source_page"],"licence":item["source"]["licence"]})
inventory["last_quality_refresh"]="2026-10-15 V43"
counts={}
for v in inventory["things"]["mappings"]:counts[v["kind"]]=counts.get(v["kind"],0)+1
assert counts.get("editorial-unverified",0)==0 and counts.get("verified-real-photo")==131 and counts.get("editorial-comparison")==1,counts
inventory["things"]["kinds"]=counts
inventory["v43"]={"new_source_verified_photo_replacements":20,"cumulative_V37_to_V43_verified":131,
  "previously_credited_photo":20,"kept_comparative_editorial_illustrations":["kimono-vs-yukata-culture"],
  "editorial_unknown_source_remaining":0,"source_register":"docs/v43-deployed-photo-credits.json"}
inventory["caveat"]="V37–V43: 131 photo cards replaced by original Commons photographs with author/license plus 20 previous cards with on-page original photo credits. The kimono vs yukata comparison remains a clearly labeled editorial illustration, not a documentary photograph. Website photo loading, responsive layout QA and local mapping are separate verifications."
for p,s in pages.items():assert "v43-image-credit" in s and "name=\"twitter:image\"" in s
assert hub.count('class="v28-panel v36-photo-card"')==152
for slug,item in data.items():assert f'src="{item["asset"]}"' in hub
for p,s in pages.items():p.write_text(s,encoding="utf-8")
HUB.write_text(hub,encoding="utf-8")
for slug,item in data.items():
    path=ROOT/item["asset"].lstrip("/")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(item["_webp"])
AUDIT.write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding="utf-8")
REPORT.write_text(json.dumps([{"slug":v["slug"],"asset":v["asset"],"source_file":v["source"]["filename"],
    "photographer":v["source"].get("author"),"licence":v["source"]["licence"],"licence_url":v["source"]["licence_url"],
    "source_page":v["source"]["source_page"],"subject":v["subject"],"note":v["note"],
    "webp_bytes":len(v["_webp"]),"sha256":hashlib.sha256(v["_webp"]).hexdigest()}
    for v in data.values()],ensure_ascii=False,indent=2),encoding="utf-8")
print("V43 verified 20 photo originals; all editorial source unknown eliminated except explicitly marked comparison",counts,flush=True)
