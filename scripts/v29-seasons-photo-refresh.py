#!/usr/bin/env python3
"""Refresh existing 34 seasons hub cards, no new articles.

Download attributed Commons location photographs to local optimized WebP;
keep existing editorial image sources where an exact source is not appropriate.
Fail closed if insufficient Commons photographs are delivered; never mislabel
historical festival photographs as contemporary 2027 events.
"""
from pathlib import Path
from urllib.parse import urlencode,quote
from urllib.request import Request,urlopen
from io import BytesIO
from html import escape
import json,re,os,time
from PIL import Image,ImageOps

COMMONS={
 1:("Sapporo Snow festival.JPG","Daigaku2051","CC BY-SA 3.0","https://creativecommons.org/licenses/by-sa/3.0/"),
 2:("Sapporo City Skyline.jpg","ノボホショコロトソ","CC BY 4.0","https://creativecommons.org/licenses/by/4.0/"),
 4:("Rural road in Hokkaido in winter showing edge markers.jpg","Wikimedia Commons photographer","CC BY-SA (see original)",""),
 5:("The 66th Sapporo Snow Festival - panoramio.jpg","t-konno","CC BY-SA 3.0","https://creativecommons.org/licenses/by-sa/3.0/"),
 6:("SAPPORO SNOW FESTIVAL 2010 - panoramio.jpg","t-konno","CC BY-SA 3.0","https://creativecommons.org/licenses/by-sa/3.0/"),
 7:("Odori Park Sapporo Snow Festival 2007.JPG","Arcimboldo","CC BY 2.0 DE","https://creativecommons.org/licenses/by/2.0/de/"),
 8:("Sapporo Snow Festival Odori-Site At Night Panorama 1.jpg","京浜にけ","CC BY-SA 3.0","https://creativecommons.org/licenses/by-sa/3.0/"),
 9:("第65回さっぽろ雪まつり（SAPPORO SNOW FESTIVAL 65th） - panoramio (2).jpg","t-konno","CC BY-SA 3.0","https://creativecommons.org/licenses/by-sa/3.0/"),
 12:("SAPPORO SNOW FESTIVAL 2011 観光大国宣言！北海道 - panoramio.jpg","t-konno","CC BY-SA 3.0","https://creativecommons.org/licenses/by-sa/3.0/"),
 14:("Otaru Snow Light Path 2013 - panoramio.jpg","t-konno","CC BY-SA 3.0","https://creativecommons.org/licenses/by-sa/3.0/"),
 15:("小樽雪あかりの路（Otaru Snow Light Path Festival） - panoramio (3).jpg","t-konno","CC BY-SA 3.0","https://creativecommons.org/licenses/by-sa/3.0/"),
 16:("小樽運河-雪景.jpg","Rogerchang1133","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/"),
 18:("Otaru Snow Story 01.jpg","逃亡者","public domain",""),
 19:("JozankeiOnsen2004-12.jpg","Wikimedia Commons photographer","public domain",""),
 20:("定山渓雪灯路2013（Jozankei snow light path 2013） - panoramio (1).jpg","t-konno","CC BY-SA 3.0","https://creativecommons.org/licenses/by-sa/3.0/"),
 22:("Asahikawa Winter Festival Snow Statue 2.JPG","京浜にけ","CC BY 3.0","https://creativecommons.org/licenses/by/3.0/"),
 26:("定山渓雪灯路2013（Jozankei snow light path 2013） - panoramio.jpg","t-konno","CC BY-SA 3.0","https://creativecommons.org/licenses/by-sa/3.0/"),
 27:("小樽雪あかりの路（Otaru Snow Light Path Festival） - panoramio (2).jpg","t-konno","CC BY-SA 3.0","https://creativecommons.org/licenses/by-sa/3.0/"),
 32:("Fireworks of Japan Rhine summer festival from Kakamigahara side of beside Kiso river.jpg","KKPCW","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/"),
 33:("Momiji (Japanese maple) leaves in Ryoan-ji, Kyoto (3256663267).jpg","KimonBerlin","CC BY-SA 2.0","https://creativecommons.org/licenses/by-sa/2.0/")
}
FALLBACK=[
"/images/hokkaido.jpg",             # 1
"/images/editorial/hakodate-port-day-trip.webp", # 2
"/images/editorial/kotatsu-japanese-winter-table.webp", # 3 clothes comfort
"/images/car.jpg",                   # 4 road
"/images/couple.jpg",                # 5 couple
"/images/editorial/hakodate-goryokaku-fort.webp", # 6 family in north
"/images/ferry.jpg",                 # 7 short winter trip
"/images/editorial/aomori-hakodate-seikan-tunnel.webp", # 8
"/images/photo.jpg",                 # 9
"/images/ramen-close.jpg",           #10
"/images/editorial/omiyage-hero.webp",#11
"/images/transport.jpg",             #12
"/images/rail.jpg",                  #13
"/images/venues/otaru-v27-real-location.webp",#14
"/images/editorial/ryokan-japanese-inn-hospitality.webp",#15
"/images/editorial/otaru-cruise-port-day-trip.webp",#16
"/images/editorial/ramen-japanese-noodle-evolution.webp",#17 food
"/images/editorial/furoshiki-japanese-wrapping-cloth.webp",#18
"/images/onsen.jpg",                 #19
"/images/editorial/akita-nyuto-onsen-beech-forest.webp",#20
"/images/editorial/beppu-port-onsen-day-trip.webp",#21
"/images/season.jpg",                #22
"/images/editorial/okinawa-palm-coast-drive.webp",#23
"/images/editorial/futon-japanese-bedding-culture.webp",#24
"/images/editorial/nagano-kamikochi-azusa-river.webp",#25
"/images/editorial/japanese-garden-stones-moss.webp",#26
"/images/editorial/okinawa-sunset-rock.webp",#27
"/images/editorial/osechi-ryori-japanese-new-year-food.webp",#28
"/images/editorial/hanami-japanese-cherry-blossom-picnic.webp",#29
"/images/editorial/japanese-garden-hero.webp",#30
"/images/editorial/yukata-summer-festival.webp",#31
"/images/editorial/okinawa-eisa-festival.webp",#32
"/images/editorial/momijigari-japanese-autumn-leaves-culture.webp",#33
"/images/editorial/wagashi-japanese-seasonal-sweets.webp"#34
]
assert len(FALLBACK)==34 and len(set(FALLBACK))==34
root=Path("site")
for f in FALLBACK:
 assert (root/f.lstrip("/")).is_file(),f

def download_file(file,i):
 # Commons source provenance stays unchanged through proxy.
 src="https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(file.replace(" ","_"),safe="._()-")+"?width=1200"
 proxy="https://wsrv.nl/?"+urlencode({"url":src,"w":"1200","output":"jpg"})
 attempts=[proxy,src]
 for url in attempts:
  try:
   with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; NIPPONFERRY editorial image attribution)"}),timeout=44) as resp:
    content=resp.read()
   image=Image.open(BytesIO(content))
   image.load()
   if image.width<560 or image.height<400:raise RuntimeError("small image")
   image=ImageOps.exif_transpose(image).convert("RGB")
   image.thumbnail((1200,800),Image.Resampling.LANCZOS)
   dest=root/"images"/"seasons"/f"v29-season-{i:02d}.webp"
   dest.parent.mkdir(parents=True,exist_ok=True)
   image.save(dest,"WEBP",quality=82,method=5)
   if dest.stat().st_size<10000:raise RuntimeError("small WebP")
   return "/"+str(dest.relative_to(root)),image.size,dest.stat().st_size
  except Exception as error:
   print("V29_SOURCE_RETRY",i,str(error)[:120],flush=True)
 return None

sourcephotos={}
for i,(name,author,lic,licurl) in COMMONS.items():
 got=download_file(name,i)
 if got:
  link="https://commons.wikimedia.org/wiki/File:"+quote(name.replace(" ","_"),safe="._()-")
  sourcephotos[i]={"src":got[0],"author":author,"license":lic,"license_url":licurl,"url":link,"width":got[1][0],"height":got[1][1],"bytes":got[2][2] if False else got[2]}
  print("V29_DOWNLOADED",i,got[0],got[2],flush=True)
# At least half of the priority real winter+festival photographs must arrive.
if len(sourcephotos)<11:raise RuntimeError("Only "+str(len(sourcephotos))+" source photos; no risky half-finished publish")
f=root/"seasons"/"index.html"
s=f.read_text(encoding="utf-8")
regex=r'<a class="dircard" href="([^"]+)"><img[^>]*><div class="dirin"><small>([^<]*)</small><h2>([^<]*)</h2><p>([^<]*)</p></div></a>'
matches=list(re.finditer(regex,s))
if len(matches)!=34:raise RuntimeError("Unexpected directory card count: "+str(len(matches)))
report=[]
for i,m in enumerate(matches,1):
 href,tag,title,descr=m.groups()
 detail=sourcephotos.get(i)
 src=detail["src"] if detail else FALLBACK[i-1]
 # Editorial assets remain illustrative; only Commons file-backed cards claim real photos.
 alt=f"{title} 관련 {'현장 자료사진' if detail else '여행 주제 참고 이미지'}"
 tag_photo='<span class="season-photo-note">'+('과거 촬영 실사 · 출처 하단' if detail else '여행 주제 이미지')+'</span>'
 image=f'<img src="{src}" alt="{escape(alt,quote=True)}" width="1200" height="750" loading="lazy" decoding="async">{tag_photo}'
 full=f'<a class="dircard" href="{href}">{image}<div class="dirin"><small>{tag}</small><h2>{title}</h2><p>{descr}</p></div></a>'
 s=s.replace(m.group(0),full,1)
 report.append({"order":i,"href":href,"title":title,"image":src,"real_photo":bool(detail)})
# Article URLs and text preserved, one valid main landmark not nested.
s=s.replace('<main class="wrap hub-main"><main class="directory"><div class="wrap"><div class="dirgrid">',
 '<main class="wrap hub-main seasons-hub"><section class="directory" aria-label="일본 사계절 여행 가이드"><div class="wrap"><div class="dirgrid">')
s=s.replace('</div></div></main></main><footer class="site-footer">','</div></div></section></main><footer class="site-footer">')
if s.count("<main ")!=1 or s.count("</main>")!=1:raise RuntimeError("Bad main landmarks")
# Link to source author and license in a reader-accessible, collapsed disclosure.
if sourcephotos:
 lis=[]
 for i,detail in sorted(sourcephotos.items()):
  lic_label=escape(detail["license"])
  lic_anchor=(f'<a href="{escape(detail["license_url"])}" rel="noopener noreferrer" target="_blank">{lic_label}</a>'
             if detail["license_url"] else lic_label)
  lis.append(f'<li>{escape(matches[i-1][2])} — 사진: {escape(detail["author"])} · {lic_anchor} · '
             f'<a href="{escape(detail["url"])}" rel="noopener noreferrer" target="_blank">Commons 원본 사진</a> · WebP 변환·크기 조정. '
             '과거 촬영한 자료사진으로 2027년 행사 현장 사진이 아닙니다.</li>')
 credit='<section class="wrap seasons-image-credits"><details><summary>대표사진 원본·저작자·라이선스 확인 ('+str(len(lis))+'건)</summary><ol>'+''.join(lis)+'</ol></details></section>'
 s=s.replace('<footer class="site-footer">',credit+'<footer class="site-footer">',1)
css='<style>/* V29 seasons: magazine image-first seasonal cards */ .seasons-hub .directory > .wrap{width:100%;max-width:none}.seasons-hub .dirgrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}.seasons-hub .dircard{position:relative;display:flex;flex-direction:column;min-width:0;overflow:hidden;background:#fff;border-radius:16px;border:1px solid #d8e8ee;box-shadow:0 5px 18px #063a5c0a}.seasons-hub .dircard>img{display:block;width:100%;height:auto;aspect-ratio:16/10;object-fit:cover;background:#e9f1f6}.seasons-hub .dirin{padding:15px 18px 20px;display:flex;flex-direction:column;gap:6px;flex:1}.seasons-hub .dirin small{font-size:12px;color:#077994;font-weight:900}.seasons-hub .dirin h2{font-size:19px;line-height:1.4;color:#103f60;margin:0;overflow-wrap:anywhere}.seasons-hub .dirin p{font-size:13px;color:#627989;line-height:1.65;margin:0}.seasons-hub .season-photo-note{position:absolute;top:10px;left:10px;background:#063e54d6;color:#fff;font-size:10px;font-weight:700;border-radius:999px;padding:4px 9px;line-height:1.35}.seasons-image-credits{margin:0 auto 50px}.seasons-image-credits details{padding:15px 18px;background:#f1f7fa;border:1px solid #d4e6ef;border-radius:12px}.seasons-image-credits summary{font-weight:800;color:#174b64;cursor:pointer}.seasons-image-credits li{font-size:12px;line-height:1.75;margin:6px 0;overflow-wrap:anywhere}.seasons-image-credits a{color:#07648d;text-decoration:underline}@media(max-width:900px){.seasons-hub .dirgrid{grid-template-columns:repeat(2,minmax(0,1fr));gap:13px}}@media(max-width:560px){.seasons-hub .dirgrid{grid-template-columns:1fr}.seasons-hub .dirin{padding:14px 16px 18px}.seasons-hub .dirin h2{font-size:18px}}</style>'
s=s.replace('</head>',css+'</head>')
f.write_text(s,encoding="utf8")
result={"page":"seasons","cards":len(report),"photos":len(sourcephotos),"allUnique":len(set(x["image"] for x in report))==34,"photo_sources":sourcephotos,"cards_manifest":report}
if not result["allUnique"]:raise RuntimeError("Duplicated resulting images")
Path("audit-reports/v29").mkdir(parents=True,exist_ok=True)
Path("audit-reports/v29/seasons.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print("V29_SEASONS_RESULT",json.dumps({k:v for k,v in result.items() if k not in ("photo_sources","cards_manifest")},ensure_ascii=False),flush=True)
