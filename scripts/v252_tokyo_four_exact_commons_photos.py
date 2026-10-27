#!/usr/bin/env python3
"""V252: replace FOUR generic Tokyo photo fallbacks with exact Commons subjects.

Only accepts Commons-hosted CC BY/CC BY-SA/CC0 photos and preserves attribution.
Download and validate all four BEFORE modifying any pages. No new URLs/pages.
"""
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from PIL import Image,ImageOps
import json,html,re,io,time
SITE=Path("site")
OUT=Path("audit-reports/v252")
OUT.mkdir(parents=True,exist_ok=True)
HEADERS={"User-Agent":"NipponferryV252ExactTokyoPhotography/1.0 (https://www.nipponferry.com; editorial QA)",
         "Accept":"application/json,image/*"}
# Actual licensed Commons photographs, with accurate time/location caveats.
SOURCES={
 "tokyo-melonpan-bakery":(
  "File:Melonpan.jpg",
  "일본의 실제 멜론빵을 촬영한 사진(2006년). 아사쿠사 특정 가게 사진은 아닙니다."),
 "sugamo-jizo-shopping":(
  "File:Sugamo_jizodori.jpg",
  "도쿄 스가모 지조도리 상점가를 촬영한 사진(2009년). 현재 매장 배치와 다를 수 있습니다."),
 "tokyo-hands-diy-gifts":(
  "File:Tokyu-Hands-Shibuya-2022-11-04_04.jpg",
  "도쿄 시부야 핸즈 매장을 2022년에 촬영한 사진. 현재 매장 구성과 다를 수 있습니다."),
 "tokyo-drugstore-cosmetics":(
  "File:Shinjuku Matsumoto Kiyoshi Takeshita Street store in Tokyo, 2019 - 129.jpg",
  "도쿄 다케시타 거리 마쓰모토키요시 드러그스토어 실제 사진(2019년). 현재 상품 구성은 다릅니다."),
}
def cleaned(text):
 return html.unescape(re.sub(r"<[^>]*>"," ",str(text))).strip()
def get(url,timeout=60):
 req=Request(url,headers=HEADERS)
 with urlopen(req,timeout=timeout) as response:
  return response.read()
def attr(v):return html.escape(str(v),quote=True)
results={}
failures={}
# First phase: downloads and license checks. No repo writes yet.
for slug,(title,description) in SOURCES.items():
 try:
  url="https://commons.wikimedia.org/w/api.php?"+urlencode({
   "action":"query","format":"json","titles":title,"prop":"imageinfo",
   "iiprop":"url|extmetadata|size","iiurlwidth":1280})
  data=json.loads(get(url,45))
  page=next(iter(data["query"]["pages"].values()))
  if page.get("missing") or not page.get("imageinfo"):
   raise ValueError("Commons source not found: "+title)
  info=page["imageinfo"][0]
  meta=info.get("extmetadata",{})
  license_name=cleaned(meta.get("LicenseShortName",{}).get("value",""))
  license_url=meta.get("LicenseUrl",{}).get("value","")
  artist=cleaned(meta.get("Artist",{}).get("value",""))[:100] or "Wikimedia Commons contributor"
  if not (license_name.startswith("CC BY") or license_name in ("CC0","Public domain")):
   raise ValueError("license not yet verified: "+license_name)
  if not (info.get("descriptionurl","").startswith("https://commons.wikimedia.org/")):
   raise ValueError("source URL not Commons")
  raw=get(info.get("thumburl") or info["url"],90)
  image=Image.open(io.BytesIO(raw))
  image.load()
  if min(image.size)<550:raise ValueError("image too small")
  image=ImageOps.exif_transpose(image).convert("RGB")
  image=ImageOps.fit(image,(1280,720),method=Image.Resampling.LANCZOS)
  output=io.BytesIO()
  image.save(output,"WEBP",quality=84,method=5)
  if len(output.getvalue())<9000:raise ValueError("photo too small after conversion")
  results[slug]={
   "data":output.getvalue(),"src":"/images/tokyo-verified/v252-"+slug+".webp",
   "alt":description,"caption":"사진: "+artist+" · "+license_name+
       " · Wikimedia Commons · "+description,
   "source":info["descriptionurl"],"license":license_name,
   "license_url":license_url,"author":artist,"source_file":page["title"],
   "editorial_note":description}
 except Exception as exc:
  failures[slug]=str(exc)[:360]
 time.sleep(0.5)
if failures:
 (OUT/"tokyo-exact-photo-import-errors.json").write_text(
  json.dumps({"downloaded":list(results),"failures":failures},ensure_ascii=False,indent=2)+"\n")
 raise SystemExit("ABORT: Commons provenance/import needs correction: "+str(failures))
jsfile=SITE/"tokyo-card-photos.js"
js=jsfile.read_text("utf-8")
before,tail=js.split("const map=",1)
maptext,after=tail.split(";document.querySelectorAll",1)
mapping=json.loads(maptext)
hubfile=SITE/"japan/tokyo/index.html"
hub=hubfile.read_text("utf-8")
article_updates={}
for slug,photo in results.items():
 p={k:v for k,v in photo.items() if k!="data"}
 mapping[slug]=p
 marker='href="/japan/tokyo/'+slug+'/"'
 at=hub.find(marker)
 if at<0:raise RuntimeError("Tokyo hub card missing: "+slug)
 start=hub.find('<span class="tky-card-photo">',at)
 end=hub.find('</span></span>',start)+len('</span></span>')
 if start<0 or end<14 or start>at+400:raise RuntimeError("unexpected Tokyo card: "+slug)
 figure='<span class="tky-card-photo"><img src="'+attr(photo["src"])+
   '" alt="'+attr(photo["alt"])+
   '" width="720" height="405" loading="lazy" decoding="async"><span class="tky-photo-label">'+
   html.escape(photo["caption"])+'</span></span>'
 hub=hub[:start]+figure+hub[end:]
 f=SITE/"japan/tokyo"/slug/"index.html"
 page=f.read_text("utf-8")
 figure='<figure class="tokyo-article-photo-v1"><img src="'+attr(photo["src"])+
   '" alt="'+attr(photo["alt"])+
   '" width="1280" height="720" loading="lazy" decoding="async"><figcaption>'+
   html.escape(photo["caption"])+
   ' · <a href="'+attr(photo["source"])+
   '" target="_blank" rel="noopener noreferrer">사진 원본 및 이용허가</a></figcaption></figure>'
 page,count=re.subn(r'<figure class="tokyo-article-photo-v1">[\s\S]*?</figure>',
                   lambda _:figure,page,count=1)
 if count!=1:raise RuntimeError("article lead figure missing: "+slug)
 article_updates[f]=page
# All validity checks complete: write files and sync JS + HTML + photos.
for slug,photo in results.items():
 target=SITE/photo["src"].lstrip("/")
 target.parent.mkdir(parents=True,exist_ok=True)
 target.write_bytes(photo["data"])
for f,page in article_updates.items():f.write_text(page,"utf-8")
hubfile.write_text(hub,"utf-8")
jsfile.write_text(before+"const map="+json.dumps(mapping,ensure_ascii=False,separators=(",",":"))+
                  ";document.querySelectorAll"+after,"utf-8")
summary={slug:{k:v for k,v in p.items() if k!="data"} for slug,p in results.items()}
(OUT/"tokyo-exact-licensed-photos.json").write_text(
 json.dumps({"replaced":summary,"failures":{}},ensure_ascii=False,indent=2)+"\n","utf-8")
print("V252_EXACT_PHOTOS",json.dumps({"replaced":list(summary),"errors":[]},ensure_ascii=False))
