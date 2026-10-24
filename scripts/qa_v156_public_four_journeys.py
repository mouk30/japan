#!/usr/bin/env python3
"""Check true www.nipponferry.com V156 content, photo WebPs and source links.
Does NOT infer ticket stock, replies to reservation emails or account metrics.
"""
from urllib.request import Request, urlopen
from urllib.error import URLError,HTTPError
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime,timezone
import json, time, xml.etree.ElementTree as ET
BASE="https://www.nipponferry.com"
PAGES={
"/things-to-do/shimonoseki-cruise-port-day-trip/":{
"id":"nf-v156-shimonoseki-port",
"source":["https://www.shimonoseki-port.com/57635.html","https://www.shimonoseki-port.com/120177.html",
 "https://www.kampuferry.co.jp/news/20261023systemmaintenance.html"],
"photo":"/images/venues/v62-karato-market-real.webp",
"facts":["장주데지마","아루카포트","본항지구","귀선"]},
"/things-to-do/sado-ogi-cruise-port-day-trip/":{
"id":"nf-v156-sado-ogi",
"source":["https://www.sado-bus.com/sightseeing/","https://www.sado-bus.com/news/5492/",
 "https://www.sado-bus.com/route/ogi/"],
"photo":"/images/venues/nf-v114-sado-ogi-real.webp",
"facts":["운행중단","11월 30일","15:30","오기항","귀선"]},
"/guide/busan-shimonoseki-ferry/":{
"id":"nf-v156-kampu-guide",
"source":["https://www.kampuferry.co.jp/news/20261023systemmaintenance.html",
 "https://www.kampuferry.co.jp/lang_kor/passenger_info/t_access/"],
"photo":"/images/venues/nf-v135-shimonoseki-international-terminal-2021-real.webp",
"facts":["국제고객","여객수속","귀국","재개일"]},
"/booking/japan-cruise/":{
"id":"nf-v156-kampu-booking",
"source":["https://www.kampuferry.co.jp/news/20261023systemmaintenance.html",
 "mailto:support@kampuferry.co.jp",
 "https://www.kampuferry.co.jp/lang_kor/passenger_info/t_access/checkin.html"],
"facts":["온라인","회신","귀국","2026년 10월 23일"]}
}
class P(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.ids=[];self.links=[];self.images=[];self.canonicals=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="h1":self.h1+=1
  if tag=="a":self.links.append(a.get("href",""))
  if tag=="img":self.images.append((a.get("src",""),a.get("alt","")))
  if tag=="link" and a.get("rel")=="canonical":self.canonicals.append(a.get("href"))
  if "id" in a:self.ids.append(a["id"])
def fetch(path,binary=False):
 last=""
 for attempt in range(4):
  try:
   req=Request(BASE+path,headers={"User-Agent":"Mozilla/5.0 (NIPPONFERRY-V156-LiveVerification/1.0)","Cache-Control":"no-cache"})
   with urlopen(req,timeout=22) as resp:
    st=resp.status;ct=resp.headers.get("content-type","");b=resp.read(3_000_000)
    return st,ct,b if binary else b.decode("utf-8","replace")
  except (HTTPError,URLError,TimeoutError) as e:
   last=str(e);time.sleep(1+attempt)
 raise RuntimeError(path+": "+last)
rows=[]
def report(path,c,more=None):
 obj={"url":BASE+path,"pass":all(c.values()),"checks":c}
 if more:obj.update(more)
 rows.append(obj)
 print("PASS" if obj["pass"] else "FAIL",path,[k for k,v in c.items() if not v],flush=True)
for path,d in PAGES.items():
 try:
  status,ct,html=fetch(path);p=P();p.feed(html)
  start=html.index('id="'+d["id"]+'"') if 'id="'+d["id"]+'"' in html else -1
  section=html[start:start+9000] if start>=0 else ""
  checks={
   "http200_html":status==200 and "html" in ct.lower(),
   "same_canonical_and_one_h1":p.canonicals==[BASE+path] and p.h1==1,
   "one_v156_panel":p.ids.count(d["id"])==1,
   "3_operational_steps":section.count('class="nf-v156-step"')==3,
   "official_direct_destination_links":all(x in p.links for x in d["source"]),
   "specific_live_operator_notice":all(f in section for f in d["facts"]),
   "responsive_48px_actions":'@media(max-width:630px)' in html and "min-height:48px" in html,
   "safe_return_warning":'class="nf-v156-safe"' in section and "귀선" in section,
   "no_false_100percent_bookability":"잔여 좌석 실시간 확정" not in section,
   "preserved_photo_source":True if not d.get("photo") else any(src==d["photo"] and len(alt)>15 for src,alt in p.images),
   "original_photo_credits":p.ids.count("nf-v148-photo-credits")==1 if "nf-v148-photo-credits" in html else True
  }
  report(path,checks,{"photo":d.get("photo")})
 except Exception as e:report(path,{"http_fetch":False},{"error":str(e)})
for photo in sorted({p["photo"] for p in PAGES.values() if p.get("photo")}):
 try:
  status,ct,b=fetch(photo,binary=True)
  report(photo,{"http200_webp":status==200 and "image/webp" in ct.lower(),
    "webp_signature":b[:4]==b"RIFF" and b[8:12]==b"WEBP"},{"bytes":len(b)})
 except Exception as e:report(photo,{"http_fetch":False},{"error":str(e)})
try:
 status,ct,xml=fetch("/sitemap.xml")
 locs=[x.find("{*}loc").text for x in ET.fromstring(xml).findall("{*}url")]
 report("/sitemap.xml",{"http200":status==200,
  "all_four_existing_indexable_paths":all(BASE+x in locs for x in PAGES),
  "no_duplicate_sitemap_urls":len(locs)==len(set(locs))},{"total_urls":len(locs)})
except Exception as e:report("/sitemap.xml",{"http_fetch":False},{"error":str(e)})
summary={"utc":datetime.now(timezone.utc).isoformat(),"passed":sum(r["pass"] for r in rows),
 "checked":len(rows),"new_articles":0,
 "booking_and_analytics_status":"live ticket availability and GA4/GSC private metrics NOT checked",
 "records":rows}
out=Path("audit-output/v156-live");out.mkdir(parents=True,exist_ok=True)
(out/"production-existing-four-journeys.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",summary["passed"],"/",summary["checked"],flush=True)
if summary["passed"]!=summary["checked"]:raise SystemExit(1)
