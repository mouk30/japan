#!/usr/bin/env python3
"""V160 production HTTP: five original pages, their exact licensed WebP
and indexed sitemap. Distinguishes published markup from operator
live availability, actual ticket purchases or analytics.
"""
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime,timezone
import time,json,xml.etree.ElementTree as ET
BASE="https://www.nipponferry.com"
D={
 "ishigaki":{"photo":"/images/venues/ishigaki-kabira-bay.webp","sources":["https://aneikankou.co.jp/condition","https://aneikankou.co.jp/"],"facts":["10월 24일","전편 결항","10월 25일","귀선"]},
 "motobu":{"photo":"/images/venues/nf-v114-motobu-real.webp","sources":["https://www.mitsuioceancruises.com/news/20261020.html","https://www.mitsuioceancruises.com/contact/"],"facts":["10월 25일","취소","귀선"]},
 "naha":{"photo":"/images/venues/naha-kokusai-street.webp","sources":["https://www.mitsuioceancruises.com/news/20261020.html","https://www.mitsuioceancruises.com/"],"facts":["10월 23일","나하","하카타","귀선"]},
 "sasebo":{"photo":"/images/venues/sasebo-huis-ten-bosch.webp","sources":["https://www.mitsuioceancruises.com/news/20261020.html","https://english.huistenbosch.co.jp/ticket/?lang=ko"],"facts":["10월 24일","08:00","18:00","귀선"]},
 "hakata":{"photo":"/images/venues/fukuoka-ohori-park.webp","sources":["https://www.mitsuioceancruises.com/news/20261020.html","https://hakataport.com/Access/"],"facts":["10월 23일","10월 28일","귀선"]}
}
class H(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.canon=[];self.images=[];self.links=[];self.ids=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=="h1":self.h1+=1
  if t=="link" and a.get("rel")=="canonical":self.canon.append(a.get("href",""))
  if t=="img":self.images.append((a.get("src",""),a.get("alt","")))
  if t=="a":self.links.append(a.get("href",""))
  if "id" in a:self.ids.append(a["id"])
def fetch(path,binary=False):
 failure=""
 for n in range(3):
  try:
   with urlopen(Request(BASE+path,headers={"User-Agent":"Mozilla/5.0 NIPPONFERRY V160 live QA","Cache-Control":"no-cache"}),timeout=22) as r:
    data=r.read(5_000_000)
    return r.status,r.headers.get("Content-Type",""),data if binary else data.decode("utf-8","replace")
  except (URLError,HTTPError,TimeoutError) as e:
   failure=str(e);time.sleep(n+1)
 raise RuntimeError(path+": "+failure)
rows=[]
def add(path,checks,error=None):
 r={"url":BASE+path,"ok":all(checks.values()),"checks":checks}
 if error:r["error"]=error
 rows.append(r)
 print(("PASS" if r["ok"] else "FAIL"),path,[x for x,v in checks.items() if not v],flush=True)
for slug,info in D.items():
 path=f"/things-to-do/{slug}-cruise-port-day-trip/"
 try:
  status,ct,html=fetch(path);p=H();p.feed(html)
  start=html.find('id="nf-v160-'+slug+'"')
  end=html.find("</section>",start)
  frag=html[start:end] if start>=0 and end>start else ""
  checks={
   "public_html_200":status==200 and "html" in ct.lower(),
   "exact_original_canonical":p.canon==[BASE+path],
   "single_h1":p.h1==1,
   "visible_v160_action":p.ids.count("nf-v160-"+slug)==1,
   "three_decision_steps":frag.count('class="nf-v160-step"')==3,
   "direct_operator_links":all(x in p.links for x in info["sources"]),
   "dated_change_return_rule":all(x in frag for x in info["facts"]),
   "original_photo_and_correct_alt":any(src==info["photo"] and len(alt)>20 for src,alt in p.images),
   "photo_copyright_source":any("commons.wikimedia.org" in (x or "") for x in p.links),
   "52px_mobile_cta":'id="nf-v160-operational-css"' in html and "min-height:52px" in html,
   "still_indexable":'name="robots" content="index,follow' in html[:7000],
   "no_fabricated_bookings":"잔여석 확보 완료" not in frag and "귀선 보장" not in frag
  }
  add(path,checks)
 except Exception as e:add(path,{"public_http":False},str(e))
for info in D.values():
 path=info["photo"]
 try:
  status,ct,img=fetch(path,binary=True)
  add(path,{"public_200_webp":status==200 and "webp" in ct.lower(),"valid_WEBP_binary":img[:4]==b"RIFF" and img[8:12]==b"WEBP"})
 except Exception as e:add(path,{"public_http":False},str(e))
try:
 status,ct,xml=fetch("/sitemap.xml")
 locs=[x.find("{*}loc").text for x in ET.fromstring(xml).findall("{*}url")]
 add("/sitemap.xml",{"public_200":status==200,"original_five_indexed":all(BASE+f"/things-to-do/{slug}-cruise-port-day-trip/" in locs for slug in D),"no_duplicate_urls":len(locs)==len(set(locs))})
except Exception as e:add("/sitemap.xml",{"public_http":False},str(e))
report={"utc":datetime.now(timezone.utc).isoformat(),"new_articles":0,"checked":len(rows),"passed":sum(x["ok"] for x in rows),"failed":sum(not x["ok"] for x in rows),"does_not_verify_booking_inventory_or_GA4_GSC":True,"rows":rows}
folder=Path("audit-output/v160-public");folder.mkdir(parents=True,exist_ok=True)
(folder/"five-pages-five-photos-sitemap.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",report["passed"],"/",report["checked"],flush=True)
if report["failed"]:raise SystemExit(1)
