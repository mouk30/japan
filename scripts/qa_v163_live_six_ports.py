#!/usr/bin/env python3
"""V163 LIVE production QA: 6 original cruise guides, 6 actual original
WebP venue photos and sitemap, checking official data/booking links rendered.
Only published HTTP content, not actual seats, payment, or cruise return.
"""
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime,timezone
import json,time,xml.etree.ElementTree as ET
BASE="https://www.nipponferry.com"
D={
"sado-ogi":{"img":"/images/venues/nf-v114-sado-ogi-real.webp","official":["https://www.sadokisen.co.jp/forecast/","https://www.sadokisen.co.jp/reservation/seat-availability/?route=2","https://www.sadokisen.co.jp/reservation/service-status/?route=2"],"facts":["10월 26~28일","10:35","귀선"]},
"naoetsu":{"img":"/images/venues/nf-v126-naoetsu-cruise-port-day-trip-real.webp","official":["https://www.sadokisen.co.jp/forecast/","https://www.sadokisen.co.jp/reservation/seat-availability/?route=2","https://www.sadokisen.co.jp/reservation/service-status/?route=2"],"facts":["10월 26~28일","07:10","귀선"]},
"yakushima-miyanoura":{"img":"/images/venues/nf-v114-yakushima-miyanoura-real.webp","official":["https://ferryyakusima2.com/news/15696","https://ferryyakusima2.com/about","https://yakukan.jp/safe-travel/transportation.html"],"facts":["10월 24일","10월 26일","10월 25일","귀선"]},
"osaka":{"img":"/images/venues/osaka-kaiyukan-aquarium.webp","official":["https://www.ferry-sunflower.co.jp/news/article/3010231024.html","https://booking.ferry-sunflower.co.jp/web/yoyaku/","https://www.ferry-sunflower.co.jp/faq/"],"facts":["10월 24일","기리시마","사쓰마","귀선"]},
"nagasaki":{"img":"/images/venues/nagasaki-glover-garden.webp","official":["https://kyusho.co.jp/status","https://kyusho.co.jp/reserve","https://www.discover-nagasaki.com/en/featured-topics/fromnagasakiport"],"facts":["14:28","14:00","나라오","귀선"]},
"aokata":{"img":"/images/venues/nf-v115-aokata-real.webp","official":["https://www.goto-sangyo.co.jp/","https://www.goto-sangyo.co.jp/pickup/%E4%BA%88%E7%B4%84%E3%82%B5%E3%83%BC%E3%83%93%E3%82%B9%E3%80%8E%E3%83%99%E3%83%AB%E3%83%88%E3%83%A9%E3%80%8F%E3%81%A7%E4%B9%97%E8%88%B9%E4%BA%88%E7%B4%84%E3%81%8C%E5%8F%AF%E8%83%BD%E3%81%AB%E3%81%AA/","https://www.mlit.go.jp/kankocho/cruise/detail/061/index.html"],"facts":["10월 25일","13:30","16:00","귀선"]}
}
class H(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.images=[];self.canon=[];self.links=[];self.ids=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=="h1":self.h1+=1
  if t=="img":self.images.append((a.get("src",""),a.get("alt","")))
  if t=="link" and a.get("rel")=="canonical":self.canon.append(a.get("href",""))
  if t=="a":self.links.append(a.get("href",""))
  if "id" in a:self.ids.append(a["id"])
def get(path,binary=False):
 err=""
 for i in range(4):
  try:
   with urlopen(Request(BASE+path,headers={"User-Agent":"Mozilla/5.0 (NIPPONFERRY V163 live QA)","Cache-Control":"no-cache"}),timeout=24) as r:
    data=r.read(5_000_000)
    return r.status,r.headers.get("Content-Type",""),data if binary else data.decode("utf-8","replace")
  except (HTTPError,URLError,TimeoutError) as e:
   err=str(e);time.sleep(1+i)
 raise RuntimeError(path+": "+err)
result=[]
def push(path,checks,error=None):
 r={"url":BASE+path,"ok":all(checks.values()),"checks":checks}
 if error:r["error"]=error
 result.append(r)
 print(("PASS" if r["ok"] else "FAIL"),path,[k for k,v in checks.items() if not v],flush=True)
for slug,info in D.items():
 path=f"/things-to-do/{slug}-cruise-port-day-trip/"
 try:
  status,ct,s=get(path)
  p=H();p.feed(s)
  start=s.find(f'id="nf-v163-{slug}"');end=s.find("</section>",start)
  frag=s[start:end] if start>=0 and end>start else ""
  checks={
   "HTTP_200_HTML":status==200 and "html" in ct.lower(),
   "unchanged_original_canonical":p.canon==[BASE+path],
   "one_h1":p.h1==1,
   "one_V163_panel":p.ids.count("nf-v163-"+slug)==1,
   "three_action_cards":frag.count('class="nf-v163-step"')==3,
   "official_operator_and_booking_links":all(x in frag and x in p.links for x in info["official"]),
   "dated_official_decisions_and_ship_return":all(x in frag for x in info["facts"]),
   "original_venue_photo_and_alt":any(src==info["img"] and len(alt)>20 for src,alt in p.images),
   "original_photo_copyright_source":any("commons.wikimedia.org" in (u or "") for u in p.links),
   "large_mobile_tap_area":'id="nf-v163-ops-style"' in s and "min-height:52px" in s,
   "original_indexable_robots":'name="robots" content="index,follow' in s[:8500],
   "no_inventory_or_ship_return_guarantee":"잔여석 확보 완료" not in frag and "귀선 보장" not in frag
  }
  push(path,checks)
 except Exception as e:push(path,{"public_http":False},str(e))
for item in D.values():
 path=item["img"]
 try:
  status,ct,b=get(path,binary=True)
  push(path,{"webp_200":status==200 and "webp" in ct.lower(),"webp_magic":b[:4]==b"RIFF" and b[8:12]==b"WEBP"})
 except Exception as e:push(path,{"public_http":False},str(e))
try:
 status,ct,xml=get("/sitemap.xml")
 locs=[u.find("{*}loc").text for u in ET.fromstring(xml).findall("{*}url")]
 push("/sitemap.xml",{"xml_200":status==200,"six_existing_urls":all(BASE+f"/things-to-do/{slug}-cruise-port-day-trip/" in locs for slug in D),"no_dupes":len(locs)==len(set(locs))})
except Exception as e:push("/sitemap.xml",{"public_http":False},str(e))
report={"version":"V163","utc":datetime.now(timezone.utc).isoformat(),"new_articles":0,"updated_guides":6,"checked":len(result),"passed":sum(x["ok"] for x in result),"real_booking_stock_and_paid_results_not_verified":True,"rows":result}
out=Path("audit-output/v163-public");out.mkdir(parents=True,exist_ok=True)
(out/"six-original-ports-webp-sitemap-http.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",report["passed"],"/",report["checked"],flush=True)
if report["passed"]!=report["checked"]:raise SystemExit(1)
