#!/usr/bin/env python3
"""V153 published-domain verification: 4 existing hub pages + 3 target guides +
3 verified 4:3 WebP photos + tracker asset + sitemap. No private GA4 claim.
Runs without credentials. Fails if visitors cannot follow the editorial cards.
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError
from datetime import datetime,timezone
import json,re,time,xml.etree.ElementTree as ET
ORIGIN="https://www.nipponferry.com"
PILOTS={
"naoshima":("naoshima-art-ferry-return","/images/editorial/v146-naoshima-miyanoura-ferry-terminal-2025.webp","https://commons.wikimedia.org/wiki/File:Naoshima_Ferry_Terminal.jpg","https://creativecommons.org/licenses/by-sa/4.0/"),
"teshima":("teshima-art-ferry-return","/images/editorial/v146-teshima-art-museum-exterior-2013.webp","https://commons.wikimedia.org/wiki/File:Teshima_Art_Museum_exterior_view_201310.jpg","https://creativecommons.org/licenses/by/2.0/"),
"shikoku_food":("takamatsu-cruise-udon-market-return","/images/culture-verified/japan-kagawa-udon-pilgrimage.webp","https://commons.wikimedia.org/wiki/File:Kama-age_sanuki_udon_by_sekido_in_Takamatsu%2C_Kagawa.jpg","https://creativecommons.org/licenses/by/2.0")
}
HUBS={
"/things-to-do/":["naoshima","teshima","shikoku_food"],
"/things-to-do/cruise-ports/":["naoshima","teshima","shikoku_food"],
"/things-to-do/food-experience/":["shikoku_food"],
"/food/":["shikoku_food"]
}
class Page(HTMLParser):
 def __init__(self):
  super().__init__();self.entries=[];self.hrefs=[];self.images=[];self.ids=[];self.canonicals=[];self.h1=0;self.data_ga4=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="a":
   self.hrefs.append(a.get("href",""))
   if "data-nf-pilot-entry" in a:self.entries.append((a.get("data-nf-pilot-entry"),a.get("href")))
  if tag=="h1":self.h1+=1
  if tag=="img":self.images.append((a.get("src",""),a.get("alt","")))
  if tag=="link" and a.get("rel")=="canonical":self.canonicals.append(a.get("href"))
  if "id" in a:self.ids.append(a["id"])
  if tag=="script" and a.get("data-nf-ga4"):self.data_ga4.append(a.get("data-nf-ga4"))
def fetch(path,maxbytes=3_000_000):
 last=""
 for i in range(4):
  try:
   with urlopen(Request(ORIGIN+path,headers={"User-Agent":"Mozilla/5.0 (NIPPONFERRY-V153-Public-QA/1.0)","Cache-Control":"no-cache"}),timeout=22) as resp:
    return resp.status,resp.headers.get("content-type",""),resp.read(maxbytes)
  except (URLError,HTTPError,TimeoutError) as e:
   last=str(e);time.sleep(1+i)
 raise RuntimeError(path+": "+last)
rows=[]
def record(path,checks,other={}):
 row={"url":ORIGIN+path,"checks":checks,"pass":all(checks.values()),**other};rows.append(row)
 print("PASS" if row["pass"] else "FAIL",path,{k:v for k,v in checks.items() if not v},flush=True)
for path,ids in HUBS.items():
 try:
  st,ct,data=fetch(path);html=data.decode("utf-8","replace");parser=Page();parser.feed(html)
  wanted=[(k,"/things-to-do/"+PILOTS[k][0]+"/") for k in ids]
  checks={
   "http200":st==200,
   "html":"html" in ct.lower(),
   "one_h1":parser.h1==1,
   "canonical":parser.canonicals==[ORIGIN+path],
   "one_visual_pilot_panel":parser.ids.count("nf-v153-pilot-hub")==1,
   "correct_8_cards_distribution":sorted(parser.entries)==sorted(wanted),
   "mobile_one_column":"grid-template-columns:minmax(0,1fr)" in html,
   "4by3_photo_crop":"aspect-ratio:4/3" in html,
   "accessible_buttons":'nf-v153-pilot-cta' in html,
   "no_forced_GA4_tracking":not any("googletagmanager.com/gtag/js" in el for el in html.split('<script src="')[1:]),
   "no_false_booking_inventory":"실시간 잔여석 확인 완료" not in html
  }
  for k in ids:
   slug,img,source,license=PILOTS[k]
   checks[k+"_real_image"]=any(src==img and len(alt)>15 for src,alt in parser.images)
   checks[k+"_source_license"]=source in parser.hrefs and license in parser.hrefs
  record(path,checks,{"GA4_id_in_page":bool(parser.data_ga4),"cards":len(parser.entries)})
 except Exception as e:record(path,{"http_ok":False},{"error":str(e)})
for k,(slug,img,source,license) in PILOTS.items():
 path="/things-to-do/"+slug+"/"
 try:
  st,ct,b=fetch(path);s=b.decode("utf-8","replace");p=Page();p.feed(s)
  checks={"http200":st==200,"html":"html" in ct.lower(),"one_h1":p.h1==1,
   "canonical":p.canonicals==[ORIGIN+path],"same_pilot_image":any(src==img for src,alt in p.images),
   "photo_license_retained":source in p.hrefs and license in p.hrefs,"no_noindex":"noindex" not in s[:6000]}
  if k!="shikoku_food":checks["official_return_steps"]=all(id in p.ids for id in ("checklist","route","official"))
  else:checks["official_return_steps"]="return" in p.ids
  record(path,checks)
 except Exception as e:record(path,{"http_ok":False},{"error":str(e)})
for k,(slug,img,source,license) in PILOTS.items():
 try:
  st,ct,data=fetch(img)
  checks={"http200":st==200,"webp_mimetype":"image/webp" in ct.lower(),"webp_header":data[:4]==b"RIFF" and data[8:12]==b"WEBP"}
  record(img,checks,{"size_bytes":len(data)})
 except Exception as e:record(img,{"http_ok":False},{"error":str(e)})
try:
 st,ct,data=fetch("/nf-v93-booking-clicks.js?v=20261024-v153")
 script=data.decode("utf-8","replace")
 checks={"http200":st==200,"single_entry_event":"nf_pilot_entry_click" in script,
 "original_view_event":"nf_pilot_guide_view" in script,
 "original_action_event":"nf_pilot_action_click" in script,
 "consent_gate":"if (!event.isTrusted || !enabled)" in script,
 "hub_origin_validation":"dest.hostname.toLowerCase()" in script}
 record("/nf-v93-booking-clicks.js?v=20261024-v153",checks)
except Exception as e:record("/nf-v93-booking-clicks.js?v=20261024-v153",{"http_ok":False},{"error":str(e)})
try:
 st,ct,data=fetch("/sitemap.xml");root=ET.fromstring(data)
 locs=[x.find("{*}loc").text for x in root.findall("{*}url")]
 checks={"http200":st==200,"3_pilot_guide_urls_preserved":all(ORIGIN+"/things-to-do/"+p[0]+"/" in locs for p in PILOTS.values()),
 "4_hub_urls_preserved":all(ORIGIN+p in locs for p in HUBS),
 "no_duplicate_urls":len(locs)==len(set(locs))}
 record("/sitemap.xml",checks,{"url_count":len(locs)})
except Exception as e:record("/sitemap.xml",{"http_ok":False},{"error":str(e)})
report={"checked_utc":datetime.now(timezone.utc).isoformat(),"pages_and_assets_checked":len(rows),
"pass":sum(x["pass"] for x in rows),"new_articles":0,
"featured_pilot_cards":8,
"measured_search_clicks_or_GA4_conversions":False,
"real_GA4_ID_on_all_hubs":all(x.get("GA4_id_in_page") for x in rows if x["url"].removeprefix(ORIGIN) in HUBS),
"rows":rows}
out=Path("audit-output/v153-public");out.mkdir(parents=True,exist_ok=True)
(out/"live-card-source-and-intent.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",report["pass"],"/",len(rows),"GA4-ID-configured",report["real_GA4_ID_on_all_hubs"])
if report["pass"]!=len(rows):raise SystemExit(1)
