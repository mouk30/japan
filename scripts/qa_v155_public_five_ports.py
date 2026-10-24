#!/usr/bin/env python3
"""V155 real website: check five existing priority cruise port guides, guide hub,
and sitemap after Vercel release. These checks verify *links on site*, not
real-time ticket inventory, shuttle availability or Analytics metrics.
"""
from html.parser import HTMLParser
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError
from datetime import datetime,timezone
from pathlib import Path
import json,time,xml.etree.ElementTree as ET
BASE="https://www.nipponferry.com"
PORTS={
 "naha-shuri-castle-cruise-sightseeing":["https://oki-park.jp/shurijo/ticket_guide/11414","https://oki-park.jp/shurijo/en/ticket_guide/"],
 "ishigaki-cruise-new-port-shuttle":["https://www.city.ishigaki.okinawa.jp/kurashi_gyosei/shigoto_sangyo/kaihatsu_kenchiku/2033.html"],
 "yokohama-daikoku-pier-cruise-terminal":["https://www.city.yokohama.lg.jp/kanko-bunka/minato/kyakusen/terminal.html","https://navi.hamabus.city.yokohama.lg.jp/koutuu/pc/diagram/BusCourseSearch?busstopId=00090614"],
 "hakata-port-tenjin-sightseeing":["https://hakataport.com/Access/","https://jik.nishitetsu.jp/"],
 "nagasaki-cruise-peace-park-tram":["https://www.discover-nagasaki.com/en/featured-topics/fromnagasakiport","https://www.naga-den.com/"]
}
class H(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.ids=[];self.links=[];self.canonical=[];self.images=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="h1":self.h1+=1
  if tag=="a":self.links.append(a.get("href",""))
  if tag=="img":self.images.append((a.get("src",""),a.get("alt","")))
  if "id" in a:self.ids.append(a["id"])
  if tag=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href"))
def fetch(path):
 last=""
 for attempt in range(4):
  try:
   with urlopen(Request(BASE+path,headers={"User-Agent":"Mozilla/5.0 (NIPPONFERRY-V155-PublicQA/1.0)","Cache-Control":"no-cache"}),timeout=25) as r:
    return r.status,r.headers.get("content-type",""),r.read(4_000_000).decode("utf-8","replace")
  except (URLError,HTTPError,TimeoutError) as e:
   last=str(e);time.sleep(1+attempt)
 raise RuntimeError(path+" "+last)
report=[]
def record(path,checks,extra={}):
 val=all(checks.values());report.append({"path":path,"pass":val,"checks":checks,**extra})
 print("PASS" if val else "FAIL",path,[k for k,v in checks.items() if not v],flush=True)
for slug,sources in PORTS.items():
 path="/things-to-do/"+slug+"/"
 try:
  code,ctype,html=fetch(path);h=H();h.feed(html)
  pos=html.index('id="nf-v155-dayof-check"') if 'id="nf-v155-dayof-check"' in html else -1
  panel=html[pos:pos+7300] if pos>=0 else ""
  checks={
   "http200":code==200,"is_html":"html" in ctype.lower(),
   "canonical":h.canonical==[BASE+path],"one_h1":h.h1==1,
   "no_noindex":"noindex" not in html[:6000].lower(),
   "v155_3step":h.ids.count("nf-v155-dayof-check")==1 and panel.count('class="nf-v155-step"')==3,
   "official_sources":all(x in h.links for x in sources),
   "preexisting_v150_checks":h.ids.count("nf-v150-visitor-check")==1,
   "v155_before_v150":0<pos<html.index('id="nf-v150-visitor-check"'),
   "real_photo_alt_retained":any(src.startswith("/images/") and len(alt)>15 for src,alt in h.images),
   "return_clock_and_stoprule":all(x in panel for x in ["중단 기준","__:__","귀선","실시간"]),
   "mobile_and_48px_links":'@media(max-width:610px)' in html and "min-height:48px" in html,
   "no_fabricated_booking_confirmation":"예약 완료 확인" not in panel}
  record(path,checks,{"image_src":h.images[0][0] if h.images else None})
 except Exception as ex:record(path,{"live_http":False},{"error":str(ex)})
try:
 path="/things-to-do/cruise-ports/"
 code,ctype,html=fetch(path);h=H();h.feed(html)
 checks={"http200":code==200,"canonical":h.canonical==[BASE+path],"one_h1":h.h1==1,
 "new_direct_port_anchors":all("/things-to-do/"+slug+"/#nf-v155-dayof-check" in h.links for slug in PORTS),
 "existing_five_port_cards_remain":all("/things-to-do/"+slug+"/#nf-v150-visitor-check" in h.links for slug in PORTS),
 "no_duplicate_section":h.ids.count("nf-v155-port-shortcuts")==1,
 "mobile_shortcut":'@media(max-width:560px)' in html}
 record(path,checks)
except Exception as ex:record("/things-to-do/cruise-ports/",{"live_http":False},{"error":str(ex)})
try:
 code,ctype,xml=fetch("/sitemap.xml")
 locs=[x.find("{*}loc").text for x in ET.fromstring(xml).findall("{*}url")]
 checks={"http200":code==200,"no_duplicate_urls":len(locs)==len(set(locs)),
 "all_five_indexed":all(BASE+"/things-to-do/"+slug+"/" in locs for slug in PORTS),
 "cruise_hub_indexed":BASE+"/things-to-do/cruise-ports/" in locs}
 record("/sitemap.xml",checks,{"url_count":len(locs)})
except Exception as ex:record("/sitemap.xml",{"live_http":False},{"error":str(ex)})
summary={"checked_utc":datetime.now(timezone.utc).isoformat(),"checked":len(report),
 "passed":sum(x["pass"] for x in report),"new_posts":0,
 "actual_booking_or_GSC_GA4_events_read":False,"pages":report}
out=Path("audit-output/v155-public");out.mkdir(parents=True,exist_ok=True)
(out/"real-five-port-visit-return.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",summary["passed"],"/",summary["checked"],flush=True)
if summary["passed"]!=summary["checked"]:raise SystemExit(1)
