#!/usr/bin/env python3
"""Batch upgrade Tokyo station guides 41–60 with licensed matching Wikimedia Commons photos.
Fail closed on weak title matches; retain existing SVG if no suitable Commons photo.
"""
import io,json,re,html,time,pathlib,urllib.parse,urllib.request,urllib.error,random
from PIL import Image,ImageOps
site=pathlib.Path("site"); hub=(site/"japan/tokyo/index.html").read_text(encoding="utf-8")
slugs=[x.strip("/").split("/")[-1] for x in re.findall(r'<a\s+class="tky-card"[^>]*href="([^"]+)"',hub)[80:100]]
assert len(slugs)==20
stations={
"disney-1day-admission-vs-dpa":("Tokyo Disneyland entrance",["disneyland"]),
"disney-dpa-app-purchase":("Tokyo Disney Resort smartphone ticket",["disney"]),
"disney-dpa-price-attractions":("Tokyo Disneyland attractions",["disneyland"]),
"disney-dpa-parade-show":("Tokyo Disneyland parade",["disneyland","parade"]),
"disney-priority-pass-free":("Tokyo Disneyland entrance gate",["disneyland"]),
"disney-standby-pass-store":("Tokyo DisneySea store",["disneysea"]),
"disney-entry-request-show":("Tokyo DisneySea show",["disneysea"]),
"disney-mobile-order-food":("Tokyo Disneyland restaurant",["disneyland","restaurant"]),
"disney-priority-seating-restaurants":("Tokyo DisneySea restaurant",["disneysea","restaurant"]),
"disney-character-dining-booking":("Tokyo Disneyland character dining",["disneyland"]),
"disney-disability-passport":("Tokyo Disneyland entrance access",["disneyland"]),
"disney-children-ticket-age":("Tokyo Disneyland family",["disneyland"]),
"disney-hopper-limited-period":("Tokyo DisneySea entrance",["disneysea"]),
"disney-ticket-date-change":("Tokyo Disneyland entrance ticket",["disneyland"]),
"disney-ticket-sold-out":("Tokyo DisneySea entrance",["disneysea"]),
"disney-happy-entry-hotel-list":("Tokyo Disneyland Hotel",["disneyland","hotel"]),
"disney-happy-entry-construction":("Tokyo DisneySea Station",["disneysea","station"]),
"disney-hotel-park-ticket-bundle":("Tokyo DisneySea Hotel MiraCosta",["miracosta"]),
"disney-park-app-ticket-share":("Tokyo Disneyland ticket gate",["disneyland"]),
"disney-ride-height-safety":("Tokyo Disneyland ride",["disneyland"]),
}
assert set(slugs)==set(stations)
headers={"User-Agent":"NipponferryTokyoTravelImages/1.0 (https://www.nipponferry.com)","Accept":"application/json,image/*"}
def get(url):
 for attempt in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=55) as r:return r.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or attempt==3:raise
   time.sleep(8*(attempt+1))
  except Exception:
   if attempt==3:raise
   time.sleep(5*(attempt+1))
def clean(x):return html.unescape(re.sub("<[^>]+>","",x)).strip()
mapfile=site/"tokyo-card-photos.js";js=mapfile.read_text(encoding="utf-8")
m=re.search(r"const map=(\{.*?\});document\.querySelectorAll",js,re.S)
if not m:raise RuntimeError("Unexpected JS photo registry structure")
mapping=json.loads(m.group(1))
folder=site/"images"/"tokyo-verified";folder.mkdir(exist_ok=True)
success={};rejected={}
for slug in slugs:
 query,tokens=stations[slug]
 params=urllib.parse.urlencode({"action":"query","format":"json","generator":"search","gsrsearch":query+" filetype:bitmap","gsrnamespace":6,"gsrlimit":35,"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":1200})
 try:
  pages=json.loads(get("https://commons.wikimedia.org/w/api.php?"+params)).get("query",{}).get("pages",{})
  candidates=[]
  for page in pages.values():
   name=page.get("title","").lower()
   if not all(t in name for t in tokens):continue
   if any(s in name for s in ["map","diagram","route map","svg","logo","poster","model railway","train simulator"]):continue
   info=(page.get("imageinfo") or [{}])[0]
   meta=info.get("extmetadata",{})
   license_name=clean(meta.get("LicenseShortName",{}).get("value",""))
   if not (license_name.startswith("CC BY") or license_name=="CC0"):continue
   width=info.get("width",1200);height=info.get("height",800)
   candidates.append((name,page["title"],info,meta,license_name))
  if not candidates:raise ValueError("No licensed subject-matched resort photo")
  candidates.sort(key=lambda x:(0 if "entrance" in x[0] or "exterior" in x[0] else 1,len(x[0])))
  _,name,info,meta,license_name=candidates[0]
  im=Image.open(io.BytesIO(get(info.get("thumburl") or info["url"])));im.load()
  if min(im.size)<360:raise ValueError("Image too small")
  im=ImageOps.exif_transpose(im).convert("RGB");im.thumbnail((1200,900))
  imagepath=folder/(slug+".webp");im.save(imagepath,"WEBP",quality=85,method=6)
  creator=clean(meta.get("Artist",{}).get("value",""))[:120] or "Wikimedia Commons"
  record={"src":"/images/tokyo-verified/"+slug+".webp","alt":clean(name.removeprefix("File:"))+" 관련 역 사진","caption":"사진: "+creator+" · "+license_name+" · Wikimedia Commons","source":info.get("descriptionurl"),"license":license_name,"author":creator,"source_file":name}
  success[slug]=record
 except Exception as e:rejected[slug]=str(e)[:200]
 time.sleep(2)
mapping.update(success)
js=js[:m.start(1)]+json.dumps(mapping,ensure_ascii=False,separators=(",",":"))+js[m.end(1):]
mapfile.write_text(js,encoding="utf-8")
audit=pathlib.Path("audit-reports/tokyo-81-100-photographic-replacement.json")
audit.write_text(json.dumps({"total":20,"new_photos":len(success),"retained_illustration":rejected,"entries":success,"note":"Filename and Commons license verified; physical accuracy of exit/route directions and public-browser rendering not certified."},ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"updated":len(success),"not_matched":len(rejected)},ensure_ascii=False))
