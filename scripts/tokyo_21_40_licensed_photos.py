#!/usr/bin/env python3
"""Replace Tokyo cards 21-40 with distinct licensed documentary photographs.
Commons licensing + creator credited; shared itinerary photos are descriptive references, not exact route proof."""
import urllib.request,urllib.parse,urllib.error,json,html,re,io,pathlib,time
from PIL import Image,ImageOps
ROOT=pathlib.Path("site")
targets={
"tokyo-donki-shinjuku-kabukicho":"Don Quijote Shinjuku.JPG",
"tokyo-disneyland-ticket-guide":"Tokyo Disneyland 001.jpg",
"tokyo-disneysea-ticket-guide":"Tokyo DisneySea-Volcania.jpg",
"tokyo-disneysea-fantasy-springs":"Fantasy Springs - Frozen Kingdom.jpg",
"tokyo-disney-maihama-transport":"Maihama Resort-Liner leaves Tokyo-DisneySea-Station 20120219.jpg",
"tokyo-disney-hotel-stay-guide":"東京ディズニーセレブレーションホテル.jpg",
"tokyo-odaiba-waterfront-yurikamome":"New Transit Yurikamome train from Yume-no-Ohashi Bridge @ Odaiba Ariake (9493163228).jpg",
"tokyo-teamlab-planets-ticket-guide":"At teamLab Planets (48277793276).jpg",
"tokyo-ueno-park-museums-zoo":"Road separating Ueno Park Zoo from Tokyo Metropolitan Art Museum 01 (15567014488).jpg",
"tokyo-tsukiji-market-street-food":"Sashimi at the Tsukiji Markets - Tokyo Japan (Unsplash).jpg",
"tokyo-toyosu-market-auction-guide":"Toyosu Market.jpg",
"tokyo-ghibli-museum-booking":"Ghibli Museum, Mitaka, Tokyo, 20240823 1131 5545.jpg",
"tokyo-one-day-best-route":"Shinjuku Gyoen National Garden and NTT DoCoMo Yoyogi Building, Tokyo, Japan.jpg",
"tokyo-two-day-district-plan":"Tokyo Tower and Skyscrapers from Shibuya Sky Observation Deck (53416648661).jpg",
"tokyo-three-day-highlights":"Tokyo Tower and moon seen from Shibuya Stream.jpg",
"tokyo-family-cruise-shore-plan":"Tokyo International Cruise Terminal.jpg"
}
head={"User-Agent":"NipponferryTokyoEditorial/1.0 (https://www.nipponferry.com)","Accept":"application/json,image/*"}
def req(url):
 for i in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers=head),timeout=65) as f:return f.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or i==3:raise
   time.sleep(8*(i+1))
  except Exception:
   if i==3:raise
   time.sleep(7*(i+1))
def clean(s):return html.unescape(re.sub(r"<[^>]+>","",s)).strip()
dest=ROOT/"images"/"tokyo-verified";dest.mkdir(parents=True,exist_ok=True)
results={};errors={}
for slug,name in targets.items():
 try:
  params=urllib.parse.urlencode({"action":"query","format":"json","titles":"File:"+name,"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"1200"})
  api=json.loads(req("https://commons.wikimedia.org/w/api.php?"+params))
  page=next(iter(api["query"]["pages"].values()))
  if "missing" in page:raise ValueError("Commons file missing")
  info=page["imageinfo"][0];ext=info.get("extmetadata",{})
  lic=clean(ext.get("LicenseShortName",{}).get("value",""))
  if not (lic.startswith("CC BY") or lic=="CC0"):raise ValueError("Nonapproved license "+lic)
  author=clean(ext.get("Artist",{}).get("value",""))[:200] or "Wikimedia Commons contributor"
  src=info.get("thumburl") or info["url"]
  data=req(src);im=Image.open(io.BytesIO(data));im.load()
  if min(im.size)<350:raise ValueError("Image too small")
  im=ImageOps.exif_transpose(im).convert("RGB");im.thumbnail((1200,900))
  file=dest/(slug+".webp");im.save(file,"WEBP",quality=86,method=6)
  record={"src":"/images/tokyo-verified/"+slug+".webp","alt":name+" 관련 현장 사진","caption":"사진: "+author+" · "+lic+" · 원본: Wikimedia Commons","source":info.get("descriptionurl","https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(name.replace(" ","_"))),"license":lic,"author":author,"source_file":name,"editorial_note":"실제 장소의 공개 사진. 정보형 글에서 사진은 예약 조건이나 이동 경로를 입증하지 않음."}
  results[slug]=record
 except Exception as exc:
  errors[slug]=str(exc)[:220]
  print("SKIP",slug,errors[slug],flush=True)
 time.sleep(1.2)
js=ROOT/"tokyo-card-photos.js";text=js.read_text(encoding="utf8")
m=re.search(r"const map=(\{.*?\});document\.querySelectorAll",text,re.S)
if not m:raise RuntimeError("photo map format changed")
mapping=json.loads(m.group(1))
mapping.update(results)
text=text[:m.start(1)]+json.dumps(mapping,ensure_ascii=False,separators=(",",":"))+text[m.end(1):]
# Image caption: use exact photo source rather than suggesting the entire itinerary was photographed.
js.write_text(text,encoding="utf8")
out=pathlib.Path("audit-reports/tokyo-21-40-photographic-replacement.json")
out.write_text(json.dumps({"requested":20,"new_photos":len(results),"previously_verified_photos_kept":4,"not_replaced":errors,"entries":results},ensure_ascii=False,indent=2),encoding="utf8")
print(json.dumps({"new_photos":len(results),"unresolved":len(errors),"mapped_photos":sum(1 for s in mapping if mapping[s]["src"].endswith(".webp"))},ensure_ascii=False))
