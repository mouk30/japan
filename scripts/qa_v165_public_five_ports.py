#!/usr/bin/env python3
"""V165 postdeployment public HTTP check: five original cruise guides,
five authentic existing WebP images, and original sitemap.
Only checks live HTML/photo delivery and action hrefs, not ferry seats,
actual payment, price or final vessel boarding.
"""
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime,timezone
import json,time,xml.etree.ElementTree as ET
BASE="https://www.nipponferry.com"
PORTS={
"goto-fukue":{
 "photo":"/images/venues/nf-v118-goto-fukue-cruise-port-day-trip-real.webp",
 "official":["https://goto-ryokyakusen.com/","https://kyusho.co.jp/reserve"],
 "facts":["15:20","17:15","10/25~26","귀선"]},
"aokata":{
 "photo":"/images/venues/nf-v115-aokata-real.webp",
 "official":["https://www.nomo.co.jp/taiko/news/status.html","https://www.mlit.go.jp/kankocho/cruise/detail/061/index.html"],
 "facts":["11월 8~9일","11월 23일","아오카타","귀선"]},
"sasebo":{
 "photo":"/images/venues/sasebo-huis-ten-bosch.webp",
 "official":["https://kyusho.co.jp/status","https://kyusho.co.jp/reserve","https://kyusho.co.jp/shuttle"],
 "facts":["10월 25일","12:05","15:50","나라오","귀선"]},
"hakata":{
 "photo":"/images/venues/fukuoka-ohori-park.webp",
 "official":["https://www.city.fukuoka.lg.jp/kowan/k-kikaku/hakata-port/cruise1.html","https://hakataport.com/Access/"],
 "facts":["10월 24일","11월 3일","LUMINARA","하코자키","귀선"]},
"yakushima-miyanoura":{
 "photo":"/images/venues/nf-v114-yakushima-miyanoura-real.webp",
 "official":["https://www.yakushimaferry.com/2026/08/24/post-163/","https://www.yakushimaferry.com/flight_status/"],
 "facts":["10월 5일","11월 15일","42일","부겐빌레아","귀선"]}
}
class Page(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.canon=[];self.ids=[];self.img=[];self.links=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=="h1":self.h1+=1
  if t=="link" and a.get("rel")=="canonical":self.canon.append(a.get("href",""))
  if t=="img":self.img.append((a.get("src",""),a.get("alt","")))
  if t=="a":self.links.append(a.get("href",""))
  if "id" in a:self.ids.append(a["id"])
def fetch(path,binary=False):
 last=""
 for n in range(4):
  try:
   with urlopen(Request(BASE+path,headers={"User-Agent":"Mozilla/5.0 NIPPONFERRY-V165-QA","Cache-Control":"no-cache"}),timeout=24) as r:
    b=r.read(5_000_000)
    return r.status,r.headers.get("Content-Type",""),b if binary else b.decode("utf-8","replace")
  except (URLError,HTTPError,TimeoutError) as exc:
   last=str(exc);time.sleep(n+1)
 raise RuntimeError(path+": "+last)
rows=[]
def record(path,checks,error=None):
 x={"url":BASE+path,"ok":all(checks.values()),"checks":checks}
 if error:x["error"]=error
 rows.append(x)
 print("PASS" if x["ok"] else "FAIL",path,[k for k,v in checks.items() if not v],flush=True)
for slug,item in PORTS.items():
 path=f"/things-to-do/{slug}-cruise-port-day-trip/"
 try:
  status,ct,html=fetch(path);p=Page();p.feed(html)
  start=html.find(f'id="nf-v165-{slug}"');end=html.find("</section>",start)
  panel=html[start:end] if end>start>=0 else ""
  checks={
   "200_html":status==200 and "html" in ct.lower(),
   "original_canonical":p.canon==[BASE+path],
   "one_h1":p.h1==1,
   "one_new_panel":p.ids.count("nf-v165-"+slug)==1,
   "three_actual_decision_cards":panel.count('class="nf-v165-card"')==3,
   "official_booking_status_urls_rendered":all(u in panel and u in p.links for u in item["official"]),
   "dated_operational_and_safe_return_facts":all(t in panel for t in item["facts"]),
   "original_venue_photo_and_accessible_alt":any(src==item["photo"] and len(alt)>20 for src,alt in p.img),
   "original_photo_attribution":any("commons.wikimedia.org" in (u or "") for u in p.links),
   "52px_mobile_tap_targets":'id="nf-v165-ops-css"' in html and "@media(max-width:620px)" in html and "min-height:52px" in html,
   "indexable_robots":'name="robots" content="index,follow' in html[:8500],
   "no_invented_booked_seats":"실시간 예약 잔여석 보장" not in panel and "크루즈 귀선 완료 보장" not in panel
  }
  record(path,checks)
 except Exception as exc:record(path,{"public_HTTP":False},str(exc))
for item in PORTS.values():
 path=item["photo"]
 try:
  status,ct,b=fetch(path,binary=True)
  record(path,{"http_200_webp":status==200 and "webp" in ct.lower(),"actual_RIFF_WEBP":b[:4]==b"RIFF" and b[8:12]==b"WEBP"})
 except Exception as exc:record(path,{"public_HTTP":False},str(exc))
try:
 code,ct,xml=fetch("/sitemap.xml")
 urls=[e.find("{*}loc").text for e in ET.fromstring(xml).findall("{*}url")]
 record("/sitemap.xml",{"http_200_xml":code==200,"all_original_five_urls_in_sitemap":all(BASE+f"/things-to-do/{slug}-cruise-port-day-trip/" in urls for slug in PORTS),"no_duplicate_sitemap_urls":len(urls)==len(set(urls))})
except Exception as exc:record("/sitemap.xml",{"public_HTTP":False},str(exc))
report={"version":"V165","checked_at_utc":datetime.now(timezone.utc).isoformat(),"original_guides_updated":len(PORTS),"new_articles":0,"checks":len(rows),"passed":sum(x["ok"] for x in rows),"real_inventory_payments_GA4_not_verified":True,"rows":rows}
p=Path("audit-output/v165-public");p.mkdir(parents=True,exist_ok=True)
(p/"five-real-ports-original-WebP-sitemap.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",report["passed"],"/",report["checks"],flush=True)
if report["passed"]!=report["checks"]:raise SystemExit(1)
