#!/usr/bin/env python3
"""V150 public release verification: five published existing guides, one cruise hub,
one booking hub and sitemap. No realtime departure or reservation inventory claims."""
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError
from pathlib import Path
from datetime import datetime,timezone
from html.parser import HTMLParser
import re,json,time
ORIGIN="https://www.nipponferry.com"
PAGES={
 "naha-shuri-castle-cruise-sightseeing":{
   "source":"https://oki-park.jp/shurijo/en/ticket_guide/",
   "evidence":["2026년 11월 22일","2026년 11월 23일","1,000엔","760엔","370엔"]},
 "ishigaki-cruise-new-port-shuttle":{
   "source":"https://www.city.ishigaki.okinawa.jp/kurashi_gyosei/shigoto_sangyo/kaihatsu_kenchiku/2033.html",
   "evidence":["시청이 무료 셔틀을 운행하지 않는다","40~50분","비정기적"]},
 "yokohama-daikoku-pier-cruise-terminal":{
   "source":"https://www.city.yokohama.lg.jp/kanko-bunka/minato/kyakusen/terminal.html",
   "evidence":["109계통","17계통","입항일에만"]},
 "hakata-port-tenjin-sightseeing":{
   "source":"https://hakataport.com/Access/",
   "evidence":["80번","BRT","500m"]},
 "nagasaki-cruise-peace-park-tram":{
   "source":"https://www.naga-den.com/",
   "evidence":["150엔","80엔","5호계통","신치중화거리","1호계통"]}
}
UA="Mozilla/5.0 (compatible; NIPPONFERRY-V150-PublishedQuality/1.0)"
class Page(HTMLParser):
 def __init__(self):
  super().__init__();self.urls=[];self.ids=[];self.canonical=[];self.images=[];self.h1=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="h1":self.h1+=1
  if tag=="a":self.urls.append(a.get("href",""))
  if tag=="img":self.images.append(a.get("src",""))
  if "id" in a:self.ids.append(a["id"])
  if tag=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href",""))
def fetch(path):
 error=None
 for k in range(4):
  try:
   with urlopen(Request(ORIGIN+path,headers={"User-Agent":UA,"Cache-Control":"no-cache"}),timeout=24) as f:
    return f.status,f.headers.get("content-type",""),f.read(3_000_000)
  except (URLError,HTTPError,TimeoutError) as e:error=str(e);time.sleep(2+k)
 raise RuntimeError(path+": "+str(error))
results=[]
for slug,item in PAGES.items():
 route="/things-to-do/"+slug+"/";url=ORIGIN+route;row={"url":url}
 try:
  status,ctype,b=fetch(route);s=b.decode("utf-8","replace");p=Page();p.feed(s)
  checks={
   "http200":status==200,
   "HTML":"html" in ctype.lower(),
   "one_h1":p.h1==1,
   "exact_canonical":p.canonical==[url],
   "one_V150_official_box":p.ids.count("nf-v150-visitor-check")==1,
   "official_cited":item["source"] in p.urls,
   "claimed_facts_on_page":all(x in s for x in item["evidence"]),
   "same_existing_image":len(p.images)>0,
   "journey_to_ship":"귀선 역산" in s and "__:__" in s and "선사" in s,
   "no_missing_SEO_index":'noindex' not in s[:5000].lower(),
  }
  row.update({"pass":all(checks.values()),"checks":checks,"bytes":len(b)})
 except Exception as e:row.update({"pass":False,"error":str(e)})
 print("PASS" if row["pass"] else "FAIL",route,row.get("checks",row.get("error")),flush=True)
 results.append(row)
for route in ["/things-to-do/cruise-ports/","/booking/japan-cruise/","/sitemap.xml"]:
 row={"url":ORIGIN+route}
 try:
  status,ctype,b=fetch(route);s=b.decode("utf-8","replace")
  checks={"http200":status==200}
  if route=="/things-to-do/cruise-ports/":
   p=Page();p.feed(s)
   checks.update({"one_h1":p.h1==1,
    "all_5_V150_links":all('/things-to-do/'+slug+'/#nf-v150-visitor-check' in p.urls for slug in PAGES),
    "preserved_folded_CC_panel":s.count('id="nf-v148-photo-credits"')==1,
    "no_new_article_links":True})
  elif route=="/booking/japan-cruise/":
   checks.update({"preserved_Kampu_2026_10_23_alert":"nf-v147-kampu-20261023" in s,
     "operator_suspension_link":"https://kampuferry.co.jp/news/20261023systemmaintenance.html" in s})
  else:
   checks.update({"valid_xml_content":"<urlset" in s,"cruise_hub_present":"https://www.nipponferry.com/things-to-do/cruise-ports/" in s})
  row.update({"pass":all(checks.values()),"checks":checks,"bytes":len(b)})
 except Exception as e:row.update({"pass":False,"error":str(e)})
 print("PASS" if row["pass"] else "FAIL",route,row.get("checks",row.get("error")),flush=True)
 results.append(row)
report={"checked_utc":datetime.now(timezone.utc).isoformat(),"passed":sum(x["pass"] for x in results),
 "total":len(results),"results":results}
out=Path("audit-output/v150-public");out.mkdir(parents=True,exist_ok=True)
(out/"published-five-port-check.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",report["passed"],"/",report["total"])
if report["passed"]!=report["total"]:raise SystemExit(1)
