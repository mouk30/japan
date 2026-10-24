#!/usr/bin/env python3
"""V158 public HTTP QA: 5 original updated cruise guides, 5 original photos,
sitemap. Verify dated berth/ferry changes and real source destinations, not
live ticket stock or actual booking/boarding claims.
"""
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime,timezone
import json,time,xml.etree.ElementTree as ET
BASE="https://www.nipponferry.com"
D={
"kochi":{"photo":"/images/venues/kochi-v26-real-location.webp","official":["https://www.pref.kochi.lg.jp/doc/kochi_cruise/","https://www.princesscruises.jp/pdf/ports_shuttlebus.pdf"],"facts":["7-3안벽","7-2안벽","10월 24일","귀선"]},
"matsuyama":{"photo":"/images/venues/matsuyama-v26-real-location.webp","official":["https://www.city.matsuyama.ehime.jp/shisei/keikaku/kanko/cruisezyoho.html","https://www.princesscruises.jp/pdf/ports_shuttlebus.pdf","https://dogo.jp/"],"facts":["제1부두","2호안벽","유료","미쓰역","귀선"]},
"niigata":{"photo":"/images/venues/nf-v113-niigata-real.webp","official":["https://www.niigata-airport.gr.jp/access/liner/sado/?lang=ko","https://www.sadokisen.co.jp/"],"facts":["10월 25일","15:30","16:15","13명","현금","귀선"]},
"hiroshima":{"photo":"/images/venues/hiroshima-v26b5-real-location.webp","official":["https://hiroshima-minato.jp/enaccessitsukaichi/","https://jr-miyajimaferry.co.jp/","https://jr-miyajimaferry.co.jp/timetable/"],"facts":["10월 24일","일반 시간표","증편","이쓰카이치","귀선"]},
"kobe":{"photo":"/images/venues/kobe-meriken-park-night.webp","official":["https://www.city.kobe.lg.jp/a14075/kanko/leisure/harbor/passenger/schedule/index.html","https://www.city.kobe.lg.jp/a14075/kanko/leisure/harbor/passenger/terminal/index.html"],"facts":["4Q","4O","NAKA","포트라이너","귀선"]}
}
class H(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.ids=[];self.links=[];self.images=[];self.canonical=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="h1":self.h1+=1
  if tag=="a":self.links.append(a.get("href",""))
  if tag=="img":self.images.append((a.get("src",""),a.get("alt","")))
  if "id" in a:self.ids.append(a["id"])
  if tag=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href",""))
def get(path,binary=False):
 err=""
 for attempt in range(4):
  try:
   with urlopen(Request(BASE+path,headers={"User-Agent":"Mozilla/5.0 (NIPPONFERRY-V158-Public-QA/1.0)","Cache-Control":"no-cache"}),timeout=24) as r:
    d=r.read(4_000_000)
    return r.status,r.headers.get("content-type",""),d if binary else d.decode("utf-8","replace")
  except (HTTPError,URLError,TimeoutError) as e:
   err=str(e);time.sleep(1+attempt)
 raise RuntimeError(f"{path}: {err}")
outrows=[]
def row(path,checks,more=None):
 obj={"url":BASE+path,"pass":all(checks.values()),"checks":checks}
 if more:obj.update(more)
 outrows.append(obj)
 print("PASS" if obj["pass"] else "FAIL",path,[k for k,v in checks.items() if not v],flush=True)
for slug,v in D.items():
 path=f"/things-to-do/{slug}-cruise-port-day-trip/"
 try:
  status,ct,doc=get(path);p=H();p.feed(doc)
  pos=doc.index('id="nf-v158-'+slug+'"') if 'id="nf-v158-'+slug+'"' in doc else -1
  frag=doc[pos:pos+9200] if pos>=0 else ""
  oldid="v70-port-official" if slug=="hiroshima" else "v69-berth-qa"
  checks={
   "200_html":status==200 and "html" in ct.lower(),
   "original_indexable_canonical":p.canonical==[BASE+path],
   "one_H1":p.h1==1,
   "new_single_panel":p.ids.count("nf-v158-"+slug)==1,
   "three_operator_step_cards":frag.count('class="nf-v158-step"')==3,
   "actual_official_destinations":all(u in p.links for u in v["official"]),
   "dated_dock_venue_or_last_return_facts":all(x in frag for x in v["facts"]),
   "old_port_guide_retained":p.ids.count(oldid)==1,
   "new_before_old":0<pos<doc.index('id="'+oldid+'"'),
   "original_photo_with_subject_alt":any(src==v["photo"] and len(alt)>15 for src,alt in p.images),
   "mobile_52px_tap_targets":'@media(max-width:620px)' in doc and "min-height:52px" in doc,
   "return_stop_rule":"귀선 안전 / 관광 축소 기준" in frag,
   "no_false_confirmed_bookings":"예약 완료 보장" not in frag and "잔여석 확정" not in frag,
   "no_noindex":"noindex" not in doc[:6000].lower()
  }
  row(path,checks)
 except Exception as e:row(path,{"http":False},{"error":str(e)})
for v in D.values():
 path=v["photo"]
 try:
  status,ct,b=get(path,binary=True)
  row(path,{"image_webp200":status==200 and "image/webp" in ct.lower(),
      "real_webp_magic":b[:4]==b"RIFF" and b[8:12]==b"WEBP"})
 except Exception as e:row(path,{"http":False},{"error":str(e)})
try:
 status,ct,xml=get("/sitemap.xml")
 locs=[r.find("{*}loc").text for r in ET.fromstring(xml).findall("{*}url")]
 row("/sitemap.xml",{"200_xml":status==200,
    "5_original_cruise_paths_exist":all(BASE+f"/things-to-do/{slug}-cruise-port-day-trip/" in locs for slug in D),
    "no_duplicate_urls":len(locs)==len(set(locs))},{"count":len(locs)})
except Exception as e:row("/sitemap.xml",{"http":False},{"error":str(e)})
result={"utc":datetime.now(timezone.utc).isoformat(),"checked":len(outrows),"passed":sum(x["pass"] for x in outrows),
"new_articles":0,"real_ticket_inventory_or_GA4_GSC_metrics_not_verified":True,"rows":outrows}
p=Path("audit-output/v158-public");p.mkdir(parents=True,exist_ok=True)
(p/"five-ports-booking-gate-return.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",result["passed"],"/",result["checked"],flush=True)
if result["checked"]!=result["passed"]:raise SystemExit(1)
