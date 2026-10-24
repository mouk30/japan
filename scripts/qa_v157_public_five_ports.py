#!/usr/bin/env python3
"""V157 public production HTTP regression.
Tests real www.nipponferry.com five EXISTING cruise guides, five local WebP
photos and sitemap after source-verified operations update. This cannot prove
real-time seats, port shuttle inventory, official reservation completion or GA4.
"""
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from html.parser import HTMLParser
from datetime import datetime,timezone
from pathlib import Path
import json,time,xml.etree.ElementTree as ET
BASE="https://www.nipponferry.com"
DATA={
"aomori":{"photo":"/images/venues/aomori-nebuta-warasse.webp","links":["https://www.pref.aomori.lg.jp/soshiki/kendo/kowan/2023-aomori-cruise.html","https://www.nebuta.jp/warasse/shisetsu/business-day.html","https://www.city.aomori.aomori.jp/koutsu/noriba_location-system_jikokuhyou/1002332.html"],"words":["신추오","오키다테","17:30","귀선"]},
"hakodate":{"photo":"/images/venues/hakodate-goryokaku-tower.webp","links":["https://334.co.jp/news/2026/0406-22668/","https://hakobus.co.jp/info/2639/","https://www.city.hakodate.hokkaido.jp/docs/2014031100439/"],"words":["10월 20일","11월 8일","전편 운휴","귀선"]},
"kagoshima":{"photo":"/images/venues/kagoshima-ioworld-aquarium.webp","links":["https://www.kagoshima-kankou.com/cruise/marineport/top","https://www.city.kagoshima.lg.jp/sakurajima-ferry/howtouse/hajimete.html","https://www.kagoshima-kankou.com/course/53184"],"words":["마린포트","북부두","04:00","23:30","귀선"]},
"beppu":{"photo":"/images/venues/beppu-umi-jigoku.webp","links":["https://pref.oita.jp/site/beppu17003/2026cruising.html","https://beppu-jigoku.com/fee/index.html","https://kamenoibus.com/scheduled_howto/"],"words":["제4부두","2,400엔","1,200엔","귀선"]},
"kanazawa":{"photo":"/images/venues/kanazawa-higashi-chaya.webp","links":["https://www.kanazawa-cruise.jp/access/","https://www.kanazawa-cruise.jp/"],"words":["09:00","21:00","5km","귀선"]}
}
class Parse(HTMLParser):
 def __init__(self):
  super().__init__();self.links=[];self.images=[];self.ids=[];self.canonicals=[];self.h1=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="a":self.links.append(a.get("href",""))
  if tag=="img":self.images.append((a.get("src",""),a.get("alt","")))
  if "id" in a:self.ids.append(a["id"])
  if tag=="h1":self.h1+=1
  if tag=="link" and a.get("rel")=="canonical":self.canonicals.append(a.get("href",""))
def fetch(path,binary=False):
 last=""
 for attempt in range(4):
  try:
   with urlopen(Request(BASE+path,headers={"User-Agent":"Mozilla/5.0 (NIPPONFERRY-V157-PublicQA/1.0)","Cache-Control":"no-cache"}),timeout=24) as r:
    blob=r.read(4_000_000)
    return r.status,r.headers.get("content-type",""),blob if binary else blob.decode("utf-8","replace")
  except (HTTPError,URLError,TimeoutError) as e:
   last=str(e);time.sleep(1+attempt)
 raise RuntimeError(path+" "+last)
rows=[]
def result(path,checks,more={}):
 ok=all(checks.values())
 rows.append({"path":path,"pass":ok,"checks":checks,**more})
 print("PASS" if ok else "FAIL",path,[k for k,v in checks.items() if not v],flush=True)
for slug,d in DATA.items():
 path="/things-to-do/"+slug+"-cruise-port-day-trip/"
 try:
  status,ct,s=fetch(path);p=Parse();p.feed(s)
  idx=s.index('id="nf-v157-'+slug+'"') if 'id="nf-v157-'+slug+'"' in s else -1
  new=s[idx:idx+8800] if idx>=0 else ""
  checks={
   "html200":status==200 and "html" in ct.lower(),
   "canonical":p.canonicals==[BASE+path],
   "one_h1":p.h1==1,
   "one_v157":p.ids.count("nf-v157-"+slug)==1,
   "3_official_cards":new.count('class="nf-v157-step"')==3,
   "official_links_unmodified":all(x in p.links for x in d["links"]),
   "updated_facts":all(x in new for x in d["words"]),
   "old_port_section_present":p.ids.count("v69-berth-qa")==1,
   "new_panel_before_old":0<idx<s.index('id="v69-berth-qa"'),
   "real_original_photo_alt":any(src==d["photo"] and len(alt)>15 for src,alt in p.images),
   "mobile_52px_touch":'@media(max-width:600px)' in s and "min-height:52px" in s,
   "safe_return_text":"귀선 중단 기준" in new,
   "no_fake_ticket_claims":"예약완료 확정" not in new,
   "no_noindex":"noindex" not in s[:5000].lower()}
  result(path,checks,{"existing_photo":d["photo"]})
 except Exception as ex:result(path,{"http_fetch":False},{"error":str(ex)})
for photo in [d["photo"] for d in DATA.values()]:
 try:
  status,ct,blob=fetch(photo,binary=True)
  result(photo,{"webp200":status==200 and "image/webp" in ct.lower(),
  "real_webp_signature":blob[:4]==b"RIFF" and blob[8:12]==b"WEBP"})
 except Exception as ex:result(photo,{"http_fetch":False},{"error":str(ex)})
try:
 status,ct,s=fetch("/sitemap.xml")
 urls=[e.find("{*}loc").text for e in ET.fromstring(s).findall("{*}url")]
 result("/sitemap.xml",{"http200":status==200,
 "five_original_urls_retained":all(BASE+"/things-to-do/"+slug+"-cruise-port-day-trip/" in urls for slug in DATA),
 "no_duplicates":len(urls)==len(set(urls))},{"total_indexed":len(urls)})
except Exception as ex:result("/sitemap.xml",{"http_fetch":False},{"error":str(ex)})
summary={"utc":datetime.now(timezone.utc).isoformat(),"passed":sum(x["pass"] for x in rows),"checked":len(rows),
 "added_articles":0,"ga4_gsc_and_real_booking_stock_not_tested":True,"rows":rows}
out=Path("audit-output/v157-public");out.mkdir(parents=True,exist_ok=True)
(out/"five-current-ports-real-public.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",summary["passed"],"/",summary["checked"],flush=True)
if summary["passed"]!=summary["checked"]:raise SystemExit(1)
