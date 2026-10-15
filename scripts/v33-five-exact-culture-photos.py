#!/usr/bin/env python3
"""V33: five topic-exact, historically documented CC photo hero replacements.
Original pages/URLs/SEO copy remain intact. All five must download or no commit.
Licenses and authors were checked on Wikimedia Commons file description pages.
"""
from pathlib import Path
from urllib.parse import urlencode,quote
from urllib.request import Request,urlopen
from io import BytesIO
from html import escape
import re,json
from PIL import Image,ImageOps

ROOT=Path("site")
# slug, Wikimedia file title, precise Korean caption, creator, license, URL, year
PHOTOS=[
 ("origami-japanese-paper-folding-culture","Origami-crane.jpg","종이 한 장으로 접은 오리가미 학","Andreas Bauer","CC BY-SA 2.5","https://creativecommons.org/licenses/by-sa/2.5/","2006"),
 ("shinkansen-bullet-train-history","Shinkansen N700S and E2 Series at Tokyo Station 2025-05-31.jpg","도쿄역의 실제 신칸센 N700S·E2 차량","LMP 2001","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/","2025"),
 ("japan-snow-monkeys-hot-springs","Snow Monkeys at Jigokudani Monkey Park, Japan.jpg","나가노 지고쿠다니 원숭이공원 온천에 들어간 일본원숭이","Kelly Drewett","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/","2016"),
 ("japan-volcano-mount-aso","Mount Aso 20230102.jpg","구마모토 아소산의 실제 화산지형","Suicasmo","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/","2023"),
 ("japan-aomori-nebuta-floats","Float at Nebuta Museum Wa-rasse V.JPG","아오모리 네부타 와랏세 박물관에 전시된 대형 네부타 장식","Wmpearl","CC0 1.0","https://creativecommons.org/publicdomain/zero/1.0/","2018"),
]

def load_image(file,slug):
 encoded=quote(file.replace(" ","_"),safe="._()-")
 original="https://commons.wikimedia.org/wiki/Special:FilePath/"+encoded+"?width=1400"
 proxy="https://wsrv.nl/?"+urlencode({"url":original,"w":1400,"output":"jpg"})
 failures=[]
 for url in [proxy,original]:
  try:
   with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; NipponFerry/1.0)"}),timeout=50) as response:
    data=response.read()
   im=Image.open(BytesIO(data))
   im.load()
   if im.width<580 or im.height<380:raise RuntimeError("insufficient resolution "+str(im.size))
   im=ImageOps.exif_transpose(im).convert("RGB")
   im.thumbnail((1400,1050),Image.Resampling.LANCZOS)
   new=ROOT/"images"/"culture-verified"/(slug+".webp")
   new.parent.mkdir(parents=True,exist_ok=True)
   im.save(new,"WEBP",quality=84,method=6)
   if new.stat().st_size<10000:raise RuntimeError("invalid compressed photo")
   return "/images/culture-verified/"+slug+".webp",im.size,new.stat().st_size
  except Exception as e:failures.append(str(e)[:140])
 raise RuntimeError("Could not acquire exact original photograph: "+file+" ("+" | ".join(failures)+")")

evidence=[]
for slug,file,caption,author,license_name,license_link,year in PHOTOS:
 source="https://commons.wikimedia.org/wiki/File:"+quote(file.replace(" ","_"),safe="._()-")
 photo,size,bytesize=load_image(file,slug)
 page=ROOT/"things-to-do"/slug/"index.html"
 text=page.read_text(encoding="utf8")
 if 'class="v33-photo-credit"' in text:raise RuntimeError("Page already upgraded: "+slug)
 content_start=text.index("<main")
 hero=re.search(r'<img\b[^>]*src="(/images/editorial/[^"]+)"[^>]*>',text[content_start:])
 if not hero:raise RuntimeError("Cannot locate existing reference hero: "+slug)
 tag=hero.group(0);previous=hero.group(1)
 newtag=tag.replace('src="'+previous+'"','src="'+photo+'"')
 newtag=re.sub(r'alt="[^"]*"','alt="'+escape(caption,quote=True)+' 실제 촬영 사진"',newtag)
 newtag=re.sub(r'\s+onerror="[^"]*"','',newtag)
 newtag=re.sub(r'\s+(?:width|height)="\d+"','',newtag)
 newtag=newtag[:-1]+f' width="{size[0]}" height="{size[1]}" decoding="async">'
 text=text[:content_start]+text[content_start:].replace(tag,newtag,1)
 # Replace all old on-page SEO media pointers (Open Graph, Twitter, Article schema).
 text=text.replace("https://www.nipponferry.com"+previous,"https://www.nipponferry.com"+photo)
 text=text.replace('"'+previous+'"','"'+photo+'"')
 text=re.sub(r'<meta name="nf-topic-photo-note"[^>]*>','',text,count=1)
 credit_kind="원본·WebP 축소본은 CC BY-SA 조건을 준수합니다" if license_name.startswith("CC BY-SA") else "저작권자가 CC0로 공개한 작품입니다"
 special=" 이 사진은 박물관 전시 당시의 작품이며 현재 축제 진행 사진이나 올해 출품작이 아닙니다." if slug=="japan-aomori-nebuta-floats" else ""
 credit=(f'<p class="v33-photo-credit" style="width:min(1060px,calc(100% - 32px));margin:12px auto 22px;'
   f'font-size:12px;line-height:1.75;color:#425e6d">'
   f'실제 촬영 자료사진: {escape(caption)} ({year}년) · 사진: {escape(author)} · '
   f'<a href="{escape(source)}" target="_blank" rel="noopener noreferrer">Wikimedia Commons 원본</a> · '
   f'<a href="{escape(license_link)}" target="_blank" rel="noopener noreferrer">{escape(license_name)}</a> · '
   f'WebP 형식 변환·크기 최적화. {credit_kind}.'
   f'{special} 촬영 시점 이후 현장 상황은 달라질 수 있습니다.</p>')
 # These five article templates use <div class="w lay"> immediately after closing hero.
 marker='<div class="w lay">'
 if marker not in text[text.index('</h1>'):]:raise RuntimeError("Unsupported article layout "+slug)
 ix=text.index(marker,text.index('</h1>'))
 text=text[:ix]+credit+text[ix:]
 page.write_text(text,encoding="utf8")
 evidence.append({"slug":slug,"previous":previous,"image":photo,"source":source,"creator":author,
                  "license":license_name,"license_url":license_link,"year":year,
                  "caption":caption,"width":size[0],"height":size[1],"bytes":bytesize})
 print("V33_EXACT_PHOTO",slug,photo,bytesize,flush=True)
assert len(evidence)==5 and len({x["image"] for x in evidence})==5
out=Path("audit-reports/v33");out.mkdir(parents=True,exist_ok=True)
(out/"five-verified-cultural-photos.json").write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print("V33_DONE",json.dumps({"pages":len(evidence),"bytes":sum(x["bytes"] for x in evidence)},ensure_ascii=False),flush=True)
