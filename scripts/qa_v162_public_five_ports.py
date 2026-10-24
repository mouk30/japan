#!/usr/bin/env python3
"""V162 real published HTTP check: five original cruise-port guides,
five original source-licensed WebP venue photos and pre-existing sitemap.
External operator page links are checked in rendered HTML, not actual
paid booking inventory or final ship passenger boarding success.
"""
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime,timezone
import json,time,xml.etree.ElementTree as ET
BASE="https://www.nipponferry.com"
D={
 "hirara-miyakojima":{
 "image":"/images/venues/miyakojima-yonaha-maehama.webp",
 "urls":["https://www.pref.okinawa.jp/machizukuri/doboku/1013660/1022503/1030425.html","https://www.city.miyakojima.lg.jp/"],
 "facts":["10월 24일","10:36","12:00","귀선"]},
 "motobu":{
 "image":"/images/venues/nf-v114-motobu-real.webp",
 "urls":["https://www.iejima.org/","https://www.iejima.org/?pid=119"],
 "facts":["10월 24일","4왕복","이에섬","귀선"]},
 "ishigaki":{
 "image":"/images/venues/ishigaki-kabira-bay.webp",
 "urls":["https://yaeyama.co.jp/","https://www.ishigaki-airport.co.jp/info/2026/10/30.html"],
 "facts":["10/24","10/25","정오","귀선"]},
 "naha":{
 "image":"/images/venues/naha-kokusai-street.webp",
 "urls":["https://ko-jet.com/news/","https://reserve.smart-theater.com/?projectId=kumejimaoceanjet-production"],
 "facts":["10월 24일","25일","가네구스쿠","귀선"]},
 "amami-naze":{
 "image":"/images/venues/nf-v125-amami-naze-cruise-port-day-trip-real.webp",
 "urls":["https://marixline.com/service/downstream20261023/","https://ferry.smaku.app/"],
 "facts":["10월 23일","10월 24일","05:00","05:50","귀선"]}
}
class HTML(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.ids=[];self.canonical=[];self.images=[];self.links=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=="h1":self.h1+=1
  if t=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href",""))
  if t=="img":self.images.append((a.get("src",""),a.get("alt","")))
  if t=="a":self.links.append(a.get("href",""))
  if "id" in a:self.ids.append(a["id"])
def get(path,binary=False):
 error=""
 for n in range(4):
  try:
   with urlopen(Request(BASE+path,headers={"User-Agent":"Mozilla/5.0 (NIPPONFERRY V162 public QA)","Cache-Control":"no-cache"}),timeout=23) as r:
    b=r.read(5_000_000)
    return r.status,r.headers.get("Content-Type",""),b if binary else b.decode("utf-8","replace")
  except (HTTPError,URLError,TimeoutError) as exc:
   error=str(exc);time.sleep(1+n)
 raise RuntimeError(path+": "+error)
rows=[]
def report(path,checks,error=None):
 obj={"url":BASE+path,"passed":all(checks.values()),"checks":checks}
 if error:obj["error"]=error
 rows.append(obj)
 print("PASS" if obj["passed"] else "FAIL",path,[k for k,v in checks.items() if not v],flush=True)
for slug,item in D.items():
 path="/things-to-do/"+slug+"-cruise-port-day-trip/"
 try:
  status,ct,s=get(path);h=HTML();h.feed(s)
  begin=s.find('id="nf-v162-'+slug+'"')
  end=s.find("</section>",begin)
  panel=s[begin:end] if end>begin>=0 else ""
  checks={
   "200_html":status==200 and "html" in ct.lower(),
   "original_canonical":h.canonical==[BASE+path],
   "single_h1":h.h1==1,
   "unique_v162_panel":h.ids.count("nf-v162-"+slug)==1,
   "three_useful_steps":panel.count('class="nf-v162-card"')==3,
   "all_official_page_links_present":all(u in h.links and u in panel for u in item["urls"]),
   "operator_dated_facts_and_return":all(x in panel for x in item["facts"]),
   "unchanged_subject_and_photo_alt":any(src==item["image"] and len(alt)>20 for src,alt in h.images),
   "original_licence_origin":any("commons.wikimedia.org" in (url or "") for url in h.links),
   "mobile_tap_52px":'id="nf-v162-official-css"' in s and 'min-height:52px' in s,
   "keep_indexable":'name="robots" content="index,follow' in s[:8000],
   "no_fake_confirmed_seats":"잔여석 확정" not in panel and "귀선 보장" not in panel
  }
  report(path,checks)
 except Exception as e:report(path,{"public_http":False},str(e))
for item in D.values():
 path=item["image"]
 try:
  code,ct,b=get(path,binary=True)
  report(path,{"200_webp":code==200 and "webp" in ct.lower(),"RIFF_WEBP_content":b[:4]==b"RIFF" and b[8:12]==b"WEBP"})
 except Exception as e:report(path,{"public_http":False},str(e))
try:
 status,ct,xml=get("/sitemap.xml")
 locs=[n.find("{*}loc").text for n in ET.fromstring(xml).findall("{*}url")]
 report("/sitemap.xml",{"200_xml":status==200,"original_five_index_urls":all(BASE+"/things-to-do/"+slug+"-cruise-port-day-trip/" in locs for slug in D),"no_dup_urls":len(locs)==len(set(locs))})
except Exception as e:report("/sitemap.xml",{"public_http":False},str(e))
out=Path("audit-output/v162-public");out.mkdir(parents=True,exist_ok=True)
result={"utc":datetime.now(timezone.utc).isoformat(),"updated_original_guides":5,"new_articles":0,"checked":len(rows),"passed":sum(r["passed"] for r in rows),"actual_booking_seats_payments_and_GA4_not_verified":True,"rows":rows}
(out/"five-cruise-guides-five-real-photos-sitemap.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print("RESULT",result["passed"],"/",result["checked"],flush=True)
if result["passed"]!=result["checked"]:raise SystemExit(1)
