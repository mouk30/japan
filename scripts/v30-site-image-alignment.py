#!/usr/bin/env python3
"""V30: site image/topic relevance correction in preexisting hubs.
Correct demonstrably wrong matches (train on bus guide; Okinawa on Osaka,
goshuin on IC card, etc). Prefer topical assets over artificial uniqueness.
Seven verified Commons originals are optional; no invented licenses.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode,quote
from html import escape
from io import BytesIO
import re,json
from PIL import Image,ImageOps

root=Path("site")
# Keys are existing article URL slugs. All values are repo-local image sources.
SHOP={
"fukuoka-souvenirs":"/images/editorial/fukuoka-hakata-ori-textiles.webp",
"fukuoka-shopping-list":"/images/fukuoka.jpg",
"fukuoka-convenience":"/images/convenience.jpg",
"fukuoka-drugstore":"/images/convenience.jpg",
"fukuoka-taxfree":"/images/cash.jpg",
"osaka-souvenirs":"/images/editorial/osaka-sakai-knife-workshops.webp",
"osaka-shopping-list":"/images/osaka.jpg",
"osaka-convenience":"/images/convenience.jpg",
"osaka-drugstore":"/images/convenience.jpg",
"osaka-taxfree":"/images/cash.jpg",
"tsushima-souvenirs":"/images/tsushima.jpg",
"tsushima-shopping-list":"/images/tsushima.jpg",
"tsushima-convenience":"/images/convenience.jpg",
"tsushima-drugstore":"/images/convenience.jpg",
"tsushima-taxfree":"/images/cash.jpg",
"shimonoseki-souvenirs":"/images/shimonoseki.jpg",
"shimonoseki-shopping-list":"/images/shimonoseki.jpg",
"shimonoseki-convenience":"/images/convenience.jpg",
"shimonoseki-drugstore":"/images/convenience.jpg",
"shimonoseki-taxfree":"/images/cash.jpg"}
PRACT={
"japan-esim-setup":"/images/esim.jpg",
"japan-esim-iphone":"/images/esim.jpg",
"japan-esim-galaxy":"/images/esim.jpg",
"japan-esim-troubleshooting":"/images/esim.jpg",
"japan-esim-vs-sim-wifi":"/images/esim.jpg",
"japan-data-usage":"/images/esim.jpg",
"japan-airport-bus-guide":"/images/transport.jpg",
"japan-highway-bus-booking":"/images/transport.jpg",
"japan-night-bus-checklist":"/images/transport.jpg",
"tokyo-osaka-bus-vs-shinkansen":"/images/rail.jpg",
"osaka-fukuoka-highway-bus":"/images/transport.jpg",
"japan-bus-seat-types":"/images/transport.jpg",
"japan-sightseeing-train-guide":"/images/editorial/sagano-scenic-railway.webp",
"kyoto-tango-kuromatsu":"/images/rail.jpg",
"setsugekka-train":"/images/rail.jpg",
"shimabara-cafe-train":"/images/rail.jpg",
"japan-sightseeing-train-couple":"/images/editorial/sagano-scenic-railway.webp",
"japan-bus-tour-guide":"/images/transport.jpg",
"mt-fuji-day-bus-tour":"/images/editorial/shimizu-port-mount-fuji-day-trip.webp",
"hokkaido-winter-bus-tour":"/images/hokkaido.jpg",
"kyoto-bus-tour-vs-free":"/images/editorial/kyoto-kiyomizu-stage-structure.webp",
"japan-half-day-tour":"/images/transport.jpg",
"japan-theme-park-guide":"/images/venues/osaka-usj-entrance.webp",
"fujiq-highland-guide":"/images/venues/beppu-kijima-jupiter.webp",
"nagashima-spaland-guide":"/images/venues/osaka-tempozan-wheel.webp",
"ghibli-museum-guide":"/images/editorial/japanese-garden-hero.webp",
"nijigen-no-mori-guide":"/images/venues/osaka-usj-entrance.webp",
"japan-theme-park-couple":"/images/venues/yokohama-cosmo-world.webp",
"japan-ic-card-guide":"/images/transport.jpg",
"japan-coin-locker-guide":"/images/rail.jpg",
"japan-luggage-delivery":"/images/car.jpg",
"japan-atm-cash-guide":"/images/cash.jpg",
"japan-power-adapter-guide":"/images/esim.jpg",
"japan-translation-app-guide":"/images/esim.jpg"}
COUPLE={
"korea-japan-couple-reality":"/images/couple.jpg",
"korea-japan-couple-language":"/images/couple.jpg",
"korea-japan-couple-before-marriage":"/images/couple.jpg",
"japan-couple-messaging-culture":"/images/couple.jpg",
"japan-christmas-date":"/images/venues/kobe-meriken-park-night.webp",
"japan-valentine-white-day":"/images/editorial/wagashi-japanese-seasonal-sweets.webp",
"joshiryoku-modern-japan":"/images/city.jpg",
"japanese-women-stereotypes":"/images/couple.jpg",
"fukuoka-night-date":"/images/venues/fukuoka-tower.webp",
"tokyo-night-view-date":"/images/editorial/tokyo-cruise-port-day-trip.webp",
"ocean-view-cabin-couple":"/images/cabin.jpg",
"japan-couple-trip-planning":"/images/transport.jpg"}
SEASONS={
"hokkaido-winter-packing":"/images/seasons/v29-season-03.webp",
"japan-winter-budget":"/images/cash.jpg",
"japan-cherry-blossom-guide":"/images/editorial/hanami-japanese-cherry-blossom-picnic.webp"}
# Commons items: media original / creator / reuse license. Acquiring is best-effort.
COMMONS={
"bus":("JR-Bus-kanto D670-21501.jpg","MaedaAkihiko","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/"),
"coin":("Coin-operated locker at Kibukawa station.jpg","Motokoka","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/"),
"ghibli":("Ghibli Museum.jpg","Douglas Paul Perkins","Public domain","https://creativecommons.org/publicdomain/mark/1.0/"),
"nagashima":("Giant Wheel of Nagashima Spa Land.jpg","Christophe95","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/"),
"fujiq":("Fuji-Q Highland (5900036032).jpg","Roller Coaster Philosophy","CC BY 2.0","https://creativecommons.org/licenses/by/2.0/"),
"ic":("JRE Koiwa-STA IC-card-only-Gate.jpg","MaedaAkihiko","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/"),
"shinkansen":("N700S-J1.jpg","MaedaAkihiko","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/")
}
def grab(key,entry):
 filename,creator,license,licenseurl=entry
 remote="https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(filename.replace(" ","_"),safe="._()-")+"?width=1200"
 proxy="https://wsrv.nl/?"+urlencode({"url":remote,"output":"jpg","w":1200})
 for src in [proxy,remote]:
  try:
   with urlopen(Request(src,headers={"User-Agent":"Mozilla/5.0"}),timeout=42) as res: data=res.read()
   im=Image.open(BytesIO(data));im.load()
   if im.width<600 or im.height<400:raise ValueError("small or wrong source image")
   im=ImageOps.exif_transpose(im).convert("RGB")
   im.thumbnail((1200,800),Image.Resampling.LANCZOS)
   dest=root/"images"/"topic-matched"/("v30-"+key+".webp");dest.parent.mkdir(parents=True,exist_ok=True)
   im.save(dest,"WEBP",quality=82,method=5)
   if dest.stat().st_size<10000:raise ValueError("very small WebP")
   return {"image":"/"+str(dest.relative_to(root)),"creator":creator,"license":license,
           "licenseurl":licenseurl,
           "original":"https://commons.wikimedia.org/wiki/File:"+quote(filename.replace(" ","_"),safe="._()-"),
           "bytes":dest.stat().st_size}
  except Exception as exc:print("V30_DOWNLOAD_RETRY",key,str(exc)[:110],flush=True)
 return None
photos={}
for key,val in COMMONS.items():
 result=grab(key,val)
 if result:photos[key]=result;print("V30_MATCHED_PHOTO",key,result["image"],flush=True)
# If verified on Commons, specific exact-location imagery replaces generic fallback images.
if "bus" in photos:
 for key in ["japan-airport-bus-guide","japan-highway-bus-booking","japan-night-bus-checklist","osaka-fukuoka-highway-bus","japan-bus-seat-types","japan-bus-tour-guide"]:
  PRACT[key]=photos["bus"]["image"]
if "coin" in photos:PRACT["japan-coin-locker-guide"]=photos["coin"]["image"]
if "ghibli" in photos:PRACT["ghibli-museum-guide"]=photos["ghibli"]["image"]
if "nagashima" in photos:PRACT["nagashima-spaland-guide"]=photos["nagashima"]["image"]
if "fujiq" in photos:PRACT["fujiq-highland-guide"]=photos["fujiq"]["image"]
if "ic" in photos:PRACT["japan-ic-card-guide"]=photos["ic"]["image"]
if "shinkansen" in photos:PRACT["tokyo-osaka-bus-vs-shinkansen"]=photos["shinkansen"]["image"]

all_sources=[r["image"] for r in photos.values()]
for mapping in [SHOP,PRACT,COUPLE,SEASONS]:
 for img in mapping.values():
  if not (root/img.lstrip("/")).is_file():raise RuntimeError("Missing replacement "+img)
changes=[]
def edit_cards(folder,prefix,mapping):
 filepath=root/folder/"index.html"
 src=filepath.read_text(encoding="utf8")
 actual=[]
 def swap(m):
  nonlocal actual
  href,imagetag,after=m.group(1),m.group(2),m.group(3)
  slug=href.rstrip("/").rsplit("/",1)[-1]
  if slug not in mapping:return m.group()
  old=re.search(r'src="([^"]+)"',imagetag)
  if not old:raise RuntimeError("No card image: "+href)
  orig=old[1];new=mapping[slug]
  if orig==new:return m.group()
  tag=imagetag.replace('src="'+orig+'"','src="'+new+'"')
  # 'related reference photograph' does not imply another city is the exact destination.
  alt=re.search(r'alt="([^"]*)"',tag)
  if alt:
   tag=tag.replace(alt[0], 'alt="'+escape(after,quote=True)+' 관련 '+('자료사진' if new in all_sources else '주제 참고 이미지')+'"')
  actual.append({"page":folder,"slug":slug,"article_title":after,"from":orig,"to":new})
  return '<a class="dircard" href="'+href+'">'+tag
 # Card matching ends at h2, not the image, for title-based alt text.
 pattern=re.compile(r'<a class="dircard" href="([^"]+)">(<img[^>]*>)(?:<div class="dirin"><small>[^<]*</small><h2>([^<]*)</h2>)')
 def replacement(m):
  href,tag,title=m.group(1),m.group(2),m.group(3)
  slug=href.rstrip("/").rsplit("/",1)[-1]
  if slug not in mapping:return m.group()
  new=mapping[slug]
  old=re.search(r'src="([^"]+)"',tag)
  if not old:raise RuntimeError("no image "+slug)
  if new==old.group(1):return m.group()
  tag=tag.replace(old[0],'src="'+new+'"')
  tag=re.sub(r'alt="[^"]*"', 'alt="'+escape(title,quote=True)+(' 관련 현장 자료사진' if new in all_sources else ' 관련 주제 참고 이미지')+'"',tag)
  actual.append({"page":folder,"slug":slug,"article_title":title,"from":old.group(1),"to":new})
  return m.group().replace(m.group(2),tag,1)
 edited=pattern.sub(replacement,src)
 if folder=="seasons":
  # Seasons cards contain a source label before div and therefore use separate pattern.
  if not actual:
   pattern2=re.compile(r'<a class="dircard" href="([^"]+)">(<img[^>]*>)(<span class="season-photo-note">[^<]*</span>)(<div class="dirin"><small>[^<]*</small><h2>([^<]*)</h2>)')
   def rep2(m):
    href,tag,notice,lead,title=m.groups()
    slug=href.rstrip("/").rsplit("/",1)[-1]
    if slug not in mapping:return m.group()
    img=mapping[slug];prev=re.search(r'src="([^"]+)"',tag)
    if not prev or img==prev[1]:return m.group()
    tag=tag.replace(prev[0],'src="'+img+'"')
    tag=re.sub(r'alt="[^"]*"', 'alt="'+escape(title,quote=True)+' 관련 주제 참고 이미지"',tag)
    newnotice='<span class="season-photo-note">여행 주제 이미지</span>'
    actual.append({"page":folder,"slug":slug,"article_title":title,"from":prev[1],"to":img})
    return '<a class="dircard" href="'+href+'">'+tag+newnotice+lead
   edited=pattern2.sub(rep2,edited)
   # Non-matching if no actual detected will be asserted downstream.
 if actual: filepath.write_text(edited,encoding="utf8")
 changes.extend(actual)
 print("V30_ALIGNED",folder,len(actual),flush=True)
 return edited

for folder,mapping in [("shopping",SHOP),("practical",PRACT),("couple",COUPLE),("seasons",SEASONS)]:
 edit_cards(folder,"",mapping)
# Add Commons attribution to practical hub without moving article text; exact local photo source metadata.
if photos:
 file=root/"practical/index.html";s=file.read_text()
 if 'class="topic-match-credits"' not in s:
  lines=[]
  for key,d in photos.items():
   lines.append(f'<li>{escape(key)}: {escape(d["creator"])} · <a href="{escape(d["original"])}" rel="noopener noreferrer" target="_blank">사진 원본</a> · '
                f'<a href="{escape(d["licenseurl"])}" rel="noopener noreferrer" target="_blank">{escape(d["license"])}</a> · WebP 변환·크기 조정. '
                '해당 주제의 예시 사진으로 정확한 서비스·노선의 최신 상태를 의미하지 않습니다.</li>')
  section='<section class="wrap topic-match-credits" aria-label="실사 이미지 출처"><details><summary>주제별 실제 사진 출처 및 라이선스 확인</summary><ul>'+''.join(lines)+'</ul></details></section>'
  s=s.replace('<footer class="site-footer">',section+'<footer class="site-footer">',1)
  s=s.replace('</head>','<style>.topic-match-credits{margin:35px auto}.topic-match-credits details{background:#f1f7fb;padding:16px;border-radius:12px;border:1px solid #cfe5ed}.topic-match-credits summary{cursor:pointer;font-weight:800}.topic-match-credits li{font-size:12px;margin:7px 0;overflow-wrap:anywhere}.topic-match-credits a{text-decoration:underline;color:#006789}</style></head>',1)
  file.write_text(s)
result={"pages_checked":["shopping","practical","couple","seasons"],"corrections":len(changes),"changes":changes,"new_verified_photos":photos}
Path("audit-reports/v30").mkdir(parents=True,exist_ok=True)
Path("audit-reports/v30/image-alignment.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
print("V30_RESULT",json.dumps({"fixes":len(changes),"verified_sources":len(photos),"hubs":len(result["pages_checked"])},ensure_ascii=False))
