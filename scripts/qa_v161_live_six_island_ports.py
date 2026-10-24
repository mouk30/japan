#!/usr/bin/env python3
"""V161 public production verification of six updated existing island port guides,
the exact original source-licensed WebP files, and unchanged sitemap.
Does not verify real bookings, phone calls, ship return cutoffs, or analytics.
"""
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime,timezone
import json,time,xml.etree.ElementTree as ET
BASE="https://www.nipponferry.com"
D={
 "tokyo":{"photo":"/images/venues/tokyo-v27-real-location.webp","official":["https://www.tokaikisen.co.jp/news/836684/","https://www.tokaikisenyoyaku.com/app/web-front/precautions","https://www.tokaikisen.co.jp/schedule/"],"facts":["10월 25일","10월 27일","다케시바","귀선"]},
 "okata-izu-oshima":{"photo":"/images/venues/nf-v127-okata-izu-oshima-cruise-port-day-trip-real.webp","official":["https://www.tokaikisen.co.jp/schedule/","https://www.tokaikisen.co.jp/news/836684/","https://www.tokaikisen.co.jp/contact/"],"facts":["오카타","모토마치","04992-2-5522","귀선"]},
 "niijima":{"photo":"/images/venues/nf-v127-niijima-cruise-port-day-trip-real.webp","official":["https://www.tokaikisen.co.jp/news/826444/","https://www.tokaikisenyoyaku.com/app/web-front/precautions","https://www.tokaikisen.co.jp/schedule/"],"facts":["10월 9~28일","니지마","흑근","귀선"]},
 "kozushima":{"photo":"/images/venues/nf-v126-kozushima-cruise-port-day-trip-real.webp","official":["https://www.tokaikisen.co.jp/news/826444/","https://www.tokaikisen.co.jp/news/836684/","https://www.tokaikisen.co.jp/schedule/"],"facts":["10월 9~28일","마에하마","04992-8-1111","귀선"]},
 "miike-miyakejima":{"photo":"/images/venues/nf-v126-miike-miyakejima-cruise-port-day-trip-real.webp","official":["https://www.tokaikisen.co.jp/news/826444/","https://www.tokaikisen.co.jp/news/836684/","https://www.tokaikisen.co.jp/schedule/"],"facts":["미이케항","사비가하마","이케야항","04994-5-0221","귀선"]},
 "kaminato-hachijojima":{"photo":"/images/venues/nf-v125-kaminato-hachijojima-cruise-port-day-trip-real.webp","official":["https://www.tokaikisen.co.jp/news/826444/","https://www.tokaikisen.co.jp/news/836684/","https://www.tokaikisen.co.jp/schedule/"],"facts":["소코도","야에네","04996-2-1211","귀선"]}
}
class H(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.canonical=[];self.ids=[];self.links=[];self.images=[]
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
   with urlopen(Request(BASE+path,headers={"User-Agent":"Mozilla/5.0 (NIPPONFERRY-V161-public-QA)","Cache-Control":"no-cache"}),timeout=23) as r:
    data=r.read(5_000_000)
    return r.status,r.headers.get("Content-Type",""),data if binary else data.decode("utf-8","replace")
  except (HTTPError,URLError,TimeoutError) as e:
   error=str(e);time.sleep(1+n)
 raise RuntimeError(path+": "+error)
rows=[]
def log(path,checks,error=None):
 r={"url":BASE+path,"pass":all(checks.values()),"checks":checks}
 if error:r["error"]=error
 rows.append(r)
 print(("PASS" if r["pass"] else "FAIL"),path,[k for k,v in checks.items() if not v],flush=True)
for slug,item in D.items():
 path="/things-to-do/"+slug+"-cruise-port-day-trip/"
 try:
  status,ctype,html=get(path);p=H();p.feed(html)
  index=html.find('id="nf-v161-'+slug+'"')
  stop=html.find("</section>",index)
  frag=html[index:stop] if index>=0 and stop>index else ""
  check={
   "200_html":status==200 and "html" in ctype.lower(),
   "original_index_canonical":p.canonical==[BASE+path],
   "one_h1":p.h1==1,
   "single_v161_panel":p.ids.count("nf-v161-"+slug)==1,
   "three_real_action_cards":frag.count('class="nf-v161-item"')==3,
   "official_booking_status_and_port_links":all(u in p.links and u in frag for u in item["official"]),
   "direct_real_ticket_booking_for_all_six":"https://www.tokaikisenyoyaku.com/app/web-front/precautions" in p.links and "https://www.tokaikisenyoyaku.com/app/web-front/precautions" in frag,
   "source_date_and_last_return_facts":all(f in frag for f in item["facts"]),
   "original_local_license_photo_and_alt":any(img==item["photo"] and len(alt)>20 for img,alt in p.images),
   "original_licence_links_present":any("commons.wikimedia.org" in (v or "") for v in p.links),
   "large_52px_mobile_target":'id="nf-v161-operator-css"' in html and 'min-height:52px' in html and '@media(max-width:620px)' in html,
   "still_indexable":'name="robots" content="index,follow' in html[:8000],
   "no_invented_bookings":'실시간 좌석 확정' not in frag and '귀선 보장' not in frag
  }
  log(path,check)
 except Exception as e:log(path,{"public_http":False},str(e))
for item in D.values():
 path=item["photo"]
 try:
  status,ct,data=get(path,binary=True)
  log(path,{"200_webp":status==200 and "webp" in ct.lower(),"actual_webp_magic":data[:4]==b"RIFF" and data[8:12]==b"WEBP"})
 except Exception as e:log(path,{"public_http":False},str(e))
try:
 status,ct,xml=get("/sitemap.xml")
 urls=[x.find("{*}loc").text for x in ET.fromstring(xml).findall("{*}url")]
 log("/sitemap.xml",{"200_xml":status==200,"all_original_six_cruise_urls":all(BASE+"/things-to-do/"+slug+"-cruise-port-day-trip/" in urls for slug in D),"no_dupes":len(urls)==len(set(urls))})
except Exception as e:log("/sitemap.xml",{"public_http":False},str(e))
result={"utc":datetime.now(timezone.utc).isoformat(),"new_articles":0,"changed_guides":6,"checked":len(rows),"passed":sum(x["pass"] for x in rows),"no_live_booking_or_GA4_checked":True,"rows":rows}
out=Path("audit-output/v161-public");out.mkdir(parents=True,exist_ok=True)
(out/"six-ports-six-real-photos-sitemap.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",result["passed"],"/",result["checked"],flush=True)
if result["passed"]!=result["checked"]:raise SystemExit(1)
