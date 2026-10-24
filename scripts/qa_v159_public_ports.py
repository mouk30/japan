#!/usr/bin/env python3
"""V159 public website validation for five updated existing cruise guides,
original licensed WebP photos and unchanged original sitemap entries.
This is a post-deploy HTTP check, not a real-time paid booking verification.
"""
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime, timezone
import json, time, xml.etree.ElementTree as ET

BASE="https://www.nipponferry.com"
CASES={
 "shimizu":{"image":"/images/venues/shimizu-chibi-maruko-host-building.webp","official":["https://www.portofshimizu.com/overview/%E5%AE%A2%E8%88%B9-%E5%B8%86%E8%88%B9/","https://www.shimizu-cruise.co.jp/news/detail/934","https://www.shimizu-cruise.co.jp/fare/"],"facts":["1,000엔","500엔","11월 1일","귀선"]},
 "osaka":{"image":"/images/venues/osaka-kaiyukan-aquarium.webp","official":["https://www.city.osaka.lg.jp/port/page/0000442982.html","https://www.kaiyukan.com/info/ticket/kaiyukan/","https://www.city.osaka.lg.jp/port/page/0000002874.html"],"facts":["SOLAS","가이유칸","귀선"]},
 "sasebo":{"image":"/images/venues/sasebo-huis-ten-bosch.webp","official":["https://www.city.sasebo.lg.jp/kouwan/koukanri/terminal-info.html","https://english.huistenbosch.co.jp/ticket/?lang=ko","https://www.city.sasebo.lg.jp/kouwan/cruise/cruise.html"],"facts":["우라가시라","요코우","귀선"]},
 "sakaiminato":{"image":"/images/venues/sakaiminato-v27-real-location.webp","official":["https://www.sakai-tottori.jp/archives/3375","https://mizuki.sakaiminato.net/","https://www.sakai-tottori.jp/"],"facts":["10월 26일","16:30","JTB","귀선"]},
 "otaru":{"image":"/images/venues/otaru-v27-real-location.webp","official":["https://www.city.otaru.lg.jp/docs/2020112000666/","https://otaru.cc/standardv2/","https://otaru.cc/timetable/"],"facts":["제3부두","가쓰나이","60일","귀선"]}
}
class P(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.canon=[];self.ids=[];self.links=[];self.images=[]
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if t=="h1": self.h1+=1
  if t=="link" and d.get("rel")=="canonical": self.canon.append(d.get("href",""))
  if t=="a":self.links.append(d.get("href",""))
  if t=="img":self.images.append((d.get("src",""),d.get("alt","")))
  if "id" in d:self.ids.append(d["id"])
def fetch(path, binary=False):
 problem=""
 for attempt in range(4):
  try:
   url=BASE+path
   with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0 (NIPPONFERRY V159 QA)","Cache-Control":"no-cache"}),timeout=22) as res:
    payload=res.read(5000000)
    return res.status,res.headers.get("Content-Type",""),payload if binary else payload.decode("utf-8","replace")
  except (HTTPError,URLError,TimeoutError) as e:
   problem=str(e);time.sleep(1+attempt)
 raise RuntimeError(path+": "+problem)
rows=[]
def record(path,checks,error=None):
 result={"url":BASE+path,"passed":all(checks.values()),"checks":checks}
 if error:result["error"]=error
 rows.append(result)
 print("PASS" if result["passed"] else "FAIL",path,[k for k,v in checks.items() if not v],flush=True)
for slug,conf in CASES.items():
 path="/things-to-do/"+slug+"-cruise-port-day-trip/"
 try:
  status,ct,html=fetch(path)
  p=P();p.feed(html)
  start=html.find('id="nf-v159-'+slug+'"')
  end=html.find("</section>",start)
  fragment=html[start:end] if start>0 and end>start else ""
  checks={
   "http200_html":status==200 and "html" in ct.lower(),
   "exact_original_canonical":p.canon==[BASE+path],
   "exact_one_h1":p.h1==1,
   "new_action_panel_once":p.ids.count("nf-v159-"+slug)==1,
   "three_explicit_operational_steps":fragment.count('class="nf-v159-card"')==3,
   "direct_official_destinations":all(u in p.links for u in conf["official"]),
   "critical_operation_and_last_return_facts":all(x in fragment for x in conf["facts"]),
   "original_photo_and_alt":any(src==conf["image"] and len(alt)>20 for src,alt in p.images),
   "copyright_information_preserved":any("commons.wikimedia.org" in url for url in p.links),
   "mobile_large_action_targets":'id="nf-v159-port-ops-css"' in html and "min-height:52px" in html,
   "no_noindex":'name="robots" content="index,follow' in html[:8000],
   "no_fake_tickets_or_shuttle_claims":"잔여석 보장" not in fragment and "무료 셔틀 확정" not in fragment
  }
  record(path,checks)
 except Exception as ex:record(path,{"public_http":False},str(ex))
for conf in CASES.values():
 path=conf["image"]
 try:
  code,ct,im=fetch(path,binary=True)
  record(path,{"200_webp":code==200 and "webp" in ct.lower(),"valid_riff_webp":im[:4]==b"RIFF" and im[8:12]==b"WEBP"})
 except Exception as ex:record(path,{"public_http":False},str(ex))
try:
 code,ct,xml=fetch("/sitemap.xml")
 urls=[p.find("{*}loc").text for p in ET.fromstring(xml).findall("{*}url")]
 record("/sitemap.xml",{"public_xml200":code==200,"all_five_original_urls":all(BASE+f"/things-to-do/{slug}-cruise-port-day-trip/" in urls for slug in CASES),"no_duplicate_locations":len(urls)==len(set(urls))})
except Exception as ex:record("/sitemap.xml",{"public_http":False},str(ex))
report={"utc":datetime.now(timezone.utc).isoformat(),"new_articles":0,"pages_updated":5,"count":len(rows),"passed":sum(row["passed"] for row in rows),"failed":len(rows)-sum(row["passed"] for row in rows),"real_booking_inventory_verified":False,"GA4_GSC_numbers_verified":False,"rows":rows}
out=Path("audit-output/v159-public");out.mkdir(parents=True,exist_ok=True)
(out/"ports-photos-sitemap-http.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",report["passed"],"/",report["count"],flush=True)
if report["failed"]:raise SystemExit(1)
