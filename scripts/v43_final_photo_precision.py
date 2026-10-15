#!/usr/bin/env python3
"""V43 final subject visual precision patch: 5 original photos reselected.
Photo source and author are updated in both article and public audit register.
"""
from pathlib import Path
from PIL import Image,ImageOps
import json,html,io,time,urllib.request,hashlib,re

SITE=Path("site")
PICKS={
  "ryokan-japanese-inn-hospitality": [
    "My traditional accomodation at Toshiharu Ryokan (48885681992).jpg",
    "일본 도시하루 료칸의 실제 밝은 다다미 객실과 후톤 침구",
    "실제 료칸 객실 사진이며 현재 객실 배치나 예약 가능 여부를 나타내지 않습니다."
  ],
  "kotatsu-japanese-winter-table": [
    "こたつ (3251928073).jpg",
    "일본식 방에 이불이 둘러진 고타쓰 난방 테이블 실사",
    "전기 난방 테이블을 이불로 감싼 고타쓰 예시이며 현재 특정 숙소의 모습은 아닙니다."
  ],
  "wagashi-japanese-seasonal-sweets": [
    "Summer wagashi 10.jpg",
    "해바라기 등 여름 계절을 표현한 여러 종류의 일본 화과자 실제 사진",
    "일본 여름 화과자의 실제 디자인 사례이며 현재 판매되는 제품은 아닙니다."
  ],
  "izakaya-japanese-afterwork-culture": [
    "Gion Kappa Restaurant in Kyoto.jpg",
    "교토 기온 갓파 이자카야 식당 내부에서 조리 중인 실제 장면",
    "일본 이자카야의 실제 조리·식당 장면으로 현재 영업 상태 및 메뉴는 별도 확인해야 합니다."
  ],
  "ramen-japanese-noodle-evolution": [
    "Tonkotsu ramen in Tokyo.jpg",
    "도쿄에서 촬영된 돈코츠 국물 라멘 한 그릇 실제 사진",
    "일본식 돈코츠 라멘 예시이며 모든 지역의 라멘 조리법을 보여주지는 않습니다."
  ]
}
C1=json.loads(Path("docs/v43-commons-candidates.json").read_text("utf-8"))
C2=json.loads(Path("docs/v43-commons-supplement.json").read_text("utf-8"))
registry=Path("docs/v43-deployed-photo-credits.json")
rows=json.loads(registry.read_text("utf-8"))
auditfile=Path("docs/v36-hub-cards-audit.json")
audit=json.loads(auditfile.read_text("utf-8"))
hubfile=SITE/"things-to-do/index.html"
hub=hubfile.read_text("utf-8")
updates={}
for slug,(filename,subject,note) in PICKS.items():
 pool=[*C1.get(slug,{}).get("options",[]),*C2.get(slug,{}).get("options",[])]
 source=next((x for x in pool if x["filename"]==filename),None)
 assert source,("Original Commons source not researched",slug)
 assert source["licence"].startswith("CC BY") or source["licence"] in ("CC0","Public domain")
 assert min(source["width"],source["height"])>500
 for retry in range(5):
  try:
   req=urllib.request.Request(source["remote"],headers={"User-Agent":"Nipponferry-V43-final-photoaccuracy/1.0 (https://www.nipponferry.com/)"})
   with urllib.request.urlopen(req,timeout=65) as response:
    raw=response.read()
    mime=response.headers.get("Content-Type","")
   assert mime.lower().startswith("image/") and len(raw)>5000
   with Image.open(io.BytesIO(raw)) as im:
    im.load()
    im=ImageOps.exif_transpose(im).convert("RGB")
    im.thumbnail((1440,1440),Image.Resampling.LANCZOS)
    stream=io.BytesIO()
    im.save(stream,format="WEBP",quality=82,method=5)
   b=stream.getvalue()
   assert b[:4]==b"RIFF" and b[8:12]==b"WEBP"
   updates[slug]={"source":source,"subject":subject,"note":note,"bytes":b}
   break
  except Exception as e:
   print("Retry",slug,retry,str(e)[:160],flush=True)
   if retry==4:raise
   time.sleep(3*(retry+1))
pages={}
for slug,item in updates.items():
 path=SITE/"things-to-do"/slug/"index.html"
 content=path.read_text("utf-8")
 local=f'/images/culture-verified/{slug}.webp'
 old=next(x for x in rows if x["slug"]==slug)
 assert old["asset"]==local
 assert old["source_page"] in content
 # Existing alt of exact cover; substitute only first one.
 oldtag=re.search(r'<img\b[^>]*\bsrc="'+re.escape(local)+r'"[^>]*>',content)
 assert oldtag,slug
 tag=re.sub(r'\balt="[^"]*"',lambda _:f'alt="{html.escape(item["subject"],quote=True)}"',oldtag.group(),count=1)
 content=content[:oldtag.start()]+tag+content[oldtag.end():]
 photo=item["source"]
 author=html.escape(photo.get("author") or "Wikimedia Commons 사용자")
 src=html.escape(photo["source_page"],quote=True)
 lic=html.escape(photo["licence"])
 licurl=html.escape(photo.get("licence_url") or photo["source_page"],quote=True)
 note=html.escape(item["note"])
 credit=(f'<p class="v43-image-credit" style="font-size:12px;line-height:1.75;color:#3c5c70;background:#f0f7fa;padding:9px 14px;margin:10px 0 20px;border-radius:6px">'
         f'실제 사진: <a href="{src}" target="_blank" rel="noopener noreferrer">{author} / Wikimedia Commons</a>'
         f' · <a href="{licurl}" target="_blank" rel="noopener noreferrer">{lic}</a>. {note}'
         f' 원본 사진을 WebP로 변환·축소했습니다.</p>')
 content,changes=re.subn(r'<p class="v43-image-credit"[^>]*>[\s\S]*?</p>',lambda _:credit,content,count=1)
 assert changes==1,(slug,"caption update missing")
 assert photo["source_page"] in content,slug
 pages[path]=content
 card=f'href="/things-to-do/{slug}/"'
 a=hub.index(card);e=hub.index("</a>",a)
 section=hub[a:e]
 oldimg=re.search(r'<img\b[^>]*\bsrc="'+re.escape(local)+r'"[^>]*>',section)
 assert oldimg,slug
 newimg=re.sub(r'\balt="[^"]*"',lambda _:f'alt="{html.escape(item["subject"],quote=True)}"',oldimg.group(),count=1)
 section=section[:oldimg.start()]+newimg+section[oldimg.end():]
 hub=hub[:a]+section+hub[e:]
 old.update({"source_file":photo["filename"],"photographer":photo["author"],
    "licence":photo["licence"],"licence_url":photo["licence_url"],
    "source_page":photo["source_page"],"subject":item["subject"],"note":item["note"],
    "webp_bytes":len(item["bytes"]),"sha256":hashlib.sha256(item["bytes"]).hexdigest()})
 aitem=next(x for x in audit["things"]["mappings"] if x["slug"]==slug)
 aitem.update({"photo_source":photo["source_page"],"licence":photo["licence"]})
for path,content in pages.items():path.write_text(content,encoding="utf-8")
for slug,item in updates.items():
 image=SITE/f"images/culture-verified/{slug}.webp"
 image.write_bytes(item["bytes"])
 with Image.open(image) as im:assert im.format=="WEBP"
hubfile.write_text(hub,encoding="utf-8")
registry.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
auditfile.write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding="utf-8")
Path("docs/v43-photo-visual-corrections.json").write_text(json.dumps({
   "corrected":list(updates),"sources":{k:v["source"]["source_page"] for k,v in updates.items()},
   "reason":"visually inspected original 20+ alternatives and chose clearer article-matching photography"
},ensure_ascii=False,indent=2),encoding="utf-8")
print("V43 final 5 visual accuracy corrections completed",list(updates),flush=True)
