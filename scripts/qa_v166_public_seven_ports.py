#!/usr/bin/env python3
"""V166 real production HTTP validation: 7 original cruise-port HTMLs,
7 unchanged licensed WebP venue photographs and sitemap, 15 objects.
This checks rendered official links, NOT actual operator reservations.
"""
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime,timezone
import time,json,xml.etree.ElementTree as ET

BASE="https://www.nipponferry.com"
H="https://heartlandferry.jp/2026/10/23/%E3%80%90%E5%88%A9%E7%A4%BC%E8%88%AA%E8%B7%AF%E3%80%91web%E4%BA%88%E7%B4%84%E3%82%B7%E3%82%B9%E3%83%86%E3%83%A0%E3%81%AE%E3%83%A1%E3%83%B3%E3%83%86%E3%83%8A%E3%83%B3%E3%82%B9/"
K="https://kyu-you.co.jp/whatsnew/detail/c1ea2c2e-5970-4af9-8dd9-33cd319efa89"
J="https://kyu-you.co.jp/whatsnew/detail/fb63ba8e-ae24-4bdb-99c6-2eb4b5e2a6c0"
P={
"wakkanai":{"photo":"/images/venues/nf-v114-wakkanai-real.webp","official":["https://heartlandferry.jp/status/",H],"facts":["11월 초","0162-23-3780","귀선"]},
"rishiri-kutsugata":{"photo":"/images/venues/nf-v127-rishiri-kutsugata-cruise-port-day-trip-real.webp","official":["https://heartlandferry.jp/status/",H,"https://heartlandferry.jp/rishiri/"],"facts":["오시도마리","굿쓰가타","0162-23-3780","귀선"]},
"iki-gonoura":{"photo":"/images/venues/nf-v125-iki-gonoura-cruise-port-day-trip-real.webp","official":[K,J],"facts":["20:00","0920-47-0003","인터넷 예약","귀선"]},
"tsushima-izuhara":{"photo":"/images/venues/v62-izuhara-port-real.webp","official":[K,J,"https://www.kyu-you.co.jp/whatsnew/detail/9f0ff055-b62c-47a0-ad0b-199720c289ad"],"facts":["20:00","0920-52-0793","03:25","귀선"]},
"hakodate":{"photo":"/images/venues/hakodate-goryokaku-tower.webp","official":["https://www.tsugarukaikyo.co.jp/cms/wp-content/uploads/20261016.pdf","https://www.tsugarukaikyo.co.jp/cms/wp-content/uploads/2027hapmamedotsuku.pdf"],"facts":["2027년 3월 31일","2027년 1월 14일","2월 27일","귀선"]},
"aomori":{"photo":"/images/venues/aomori-nebuta-warasse.webp","official":["https://www.tsugarukaikyo.co.jp/cms/wp-content/uploads/2027hapmamedotsuku.pdf","https://www.tsugarukaikyo.co.jp/service/reserve/internet/"],"facts":["2027년 1월 14일","13편","귀선"]},
"niigata":{"photo":"/images/venues/nf-v113-niigata-real.webp","official":["https://www.snf.jp/kikobin-rule/","https://www.snf.jp/guide/time_schedule/"],"facts":["21:00","22:30","환불","귀선"]}
}
class Page(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.canonical=[];self.ids=[];self.photos=[];self.links=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if "id" in a:self.ids.append(a["id"])
  if t=="h1":self.h1+=1
  if t=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href",""))
  if t=="img":self.photos.append((a.get("src",""),a.get("alt","")))
  if t=="a":self.links.append(a.get("href",""))
def fetch(path,binary=False):
 last=""
 for n in range(4):
  try:
   with urlopen(Request(BASE+path,headers={"User-Agent":"Mozilla/5.0 NIPPONFERRY-V166-Public-QA","Cache-Control":"no-cache"}),timeout=24) as r:
    data=r.read(5_000_000)
    return r.status,r.headers.get("Content-Type",""),data if binary else data.decode("utf-8","replace")
  except (HTTPError,URLError,TimeoutError) as e:
   last=str(e);time.sleep(1+n)
 raise RuntimeError(path+": "+last)

rows=[]
def record(path,checks,error=None):
 x={"url":BASE+path,"pass":all(checks.values()),"checks":checks}
 if error:x["error"]=error
 rows.append(x)
 print(("PASS" if x["pass"] else "FAIL"),path,[k for k,v in checks.items() if not v],flush=True)
for slug,info in P.items():
 path=f"/things-to-do/{slug}-cruise-port-day-trip/"
 try:
  status,ct,html=fetch(path);p=Page();p.feed(html)
  start=html.find('id="nf-v166-'+slug+'"');end=html.find("</section>",start)
  panel=html[start:end] if start>=0 and end>start else ""
  checks={
   "production_http_200":status==200 and "html" in ct.lower(),
   "original_canonical":p.canonical==[BASE+path],
   "one_original_h1":p.h1==1,
   "one_added_V166_panel":p.ids.count("nf-v166-"+slug)==1,
   "three_useful_operator_steps":panel.count('class="nf-v166-card"')==3,
   "real_official_links_visible_and_clickable":all(u in panel and u in p.links for u in info["official"]),
   "date_sensitive_rules_and_correct_last_return":all(f in panel for f in info["facts"]),
   "existing_real_venue_photo_and_alt":any(src==info["photo"] and len(alt)>20 for src,alt in p.photos),
   "photo_source_and_rights_retained":any("commons.wikimedia.org" in (l or "") for l in p.links),
   "responsive_large_touch_targets":'id="nf-v166-action-css"' in html and "min-height:52px" in html and "@media(max-width:620px)" in html,
   "keep_index_follow":'name="robots" content="index,follow' in html[:8500],
   "avoid_false_paid_booking_or_ship_return":"승선권 구매 완료" not in panel and "귀선이 보장됩니다" not in panel
  }
  record(path,checks)
 except Exception as err:record(path,{"public_http":False},str(err))
for info in P.values():
 path=info["photo"]
 try:
  status,ct,data=fetch(path,binary=True)
  record(path,{"200_webp":status==200 and "webp" in ct.lower(),"real_webp_file_header":data[:4]==b"RIFF" and data[8:12]==b"WEBP"})
 except Exception as err:record(path,{"public_http":False},str(err))
try:
 status,ct,xml=fetch("/sitemap.xml")
 urls=[u.find("{*}loc").text for u in ET.fromstring(xml).findall("{*}url")]
 record("/sitemap.xml",{"http_200":status==200,"seven_existing_paths":all(BASE+f"/things-to-do/{s}-cruise-port-day-trip/" in urls for s in P),"no_duplicate_sitemap_links":len(urls)==len(set(urls))})
except Exception as err:record("/sitemap.xml",{"public_http":False},str(err))
rep={"version":"V166","utc":datetime.now(timezone.utc).isoformat(),"new_articles":0,"updated_existing":7,"objects":len(rows),"passed":sum(x["pass"] for x in rows),"live_operator_seats_GA4_payments_not_checked":True,"rows":rows}
out=Path("audit-output/v166-public");out.mkdir(parents=True,exist_ok=True)
(out/"seven-ports-original-WebP-sitemap.json").write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",rep["passed"],"/",rep["objects"],flush=True)
if rep["passed"]!=rep["objects"]:raise SystemExit(1)
