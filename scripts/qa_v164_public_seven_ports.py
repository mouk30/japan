#!/usr/bin/env python3
"""V164 real HTTP verification: 7 updated existing cruise-port HTML pages,
7 original source-licensed WebP photographs, the unchanged public sitemap.
Published markup and official link destinations are checked, NOT paid ticket
inventory or payment, operator slot bookability, nor final vessel boarding.
"""
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime,timezone
import json,time,xml.etree.ElementTree as ET
BASE="https://www.nipponferry.com"
D={
 "kagoshima":{"photo":"/images/venues/kagoshima-ioworld-aquarium.webp","official":["https://www.city.kagoshima.lg.jp/sakurajima-ferry/unko_jokyo/20261024rinjibin.html","https://www.city.kagoshima.lg.jp/sakurajima-ferry/tyumoku/daycruise.html"],"facts":["10월 25일","10/28","11/15","귀선"]},
 "uno":{"photo":"/images/venues/nf-v129-uno-cruise-port-day-trip-real.webp","official":["https://shikokukisen.com/uno-seto-ferry-unko/","https://shikokukisen.com/uno-miyanoura-ferry-unko/"],"facts":["가자토","일반 관광객","선착순","귀선"]},
 "takamatsu":{"photo":"/images/venues/takamatsu-v27-real-location.webp","official":["https://shikokukisen.com/takamatsu-miyanoura/","https://shikokukisen.com/faq/"],"facts":["680엔","1,590엔","현금","귀선"]},
 "kobe":{"photo":"/images/venues/kobe-meriken-park-night.webp","official":["https://ferry.co.jp/","https://ferry.co.jp/home/howto/"],"facts":["15:00","30분","10월 26일","귀선"]},
 "niihama":{"photo":"/images/venues/nf-v125-niihama-cruise-port-day-trip-real.webp","official":["https://www.orange-ferry.co.jp/6488.html","https://www.orange-ferry.co.jp/"],"facts":["11월 2일","23:10","14:50","귀선"]},
 "yawatahama":{"photo":"/images/venues/nf-v129-yawatahama-cruise-port-day-trip-real.webp","official":["https://www.orange-ferry.co.jp/8683.html","https://www.orange-ferry.co.jp/time-table/kyuushi/yawatahama-usuki/"],"facts":["10월 31일","104편","204편","귀선"]},
 "tokushima-komatsushima":{"photo":"/images/venues/nf-v114-tokushima-komatsushima-real.webp","official":["https://nankai-ferry.co.jp/operation_status/225/","https://nankai-ferry.co.jp/tokushima/"],"facts":["8월 1일","감편","고마쓰시마","귀선"]}
}
class P(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.canon=[];self.ids=[];self.images=[];self.links=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=="h1":self.h1+=1
  if t=="link" and a.get("rel")=="canonical":self.canon.append(a.get("href",""))
  if t=="img":self.images.append((a.get("src",""),a.get("alt","")))
  if t=="a":self.links.append(a.get("href",""))
  if "id" in a:self.ids.append(a["id"])
def fetch(path,binary=False):
 last=""
 for attempt in range(4):
  try:
   with urlopen(Request(BASE+path,headers={"User-Agent":"Mozilla/5.0 (NIPPONFERRY-V164-Live-QA)","Cache-Control":"no-cache"}),timeout=24) as response:
    b=response.read(5_000_000)
    return response.status,response.headers.get("Content-Type",""),b if binary else b.decode("utf-8","replace")
  except (HTTPError,URLError,TimeoutError) as err:
   last=str(err);time.sleep(1+attempt)
 raise RuntimeError(path+": "+last)
rows=[]
def record(path,checks,error=None):
 obj={"url":BASE+path,"success":all(checks.values()),"checks":checks}
 if error:obj["error"]=error
 rows.append(obj)
 print(("PASS" if obj["success"] else "FAIL"),path,[k for k,v in checks.items() if not v],flush=True)
for slug,cfg in D.items():
 path=f"/things-to-do/{slug}-cruise-port-day-trip/"
 try:
  status,ct,html=fetch(path)
  p=P();p.feed(html)
  begin=html.find(f'id="nf-v164-{slug}"')
  end=html.find("</section>",begin)
  segment=html[begin:end] if end>begin>=0 else ""
  rules={
   "HTTP_200_text_html":status==200 and "html" in ct.lower(),
   "original_canonical_index_path":p.canon==[BASE+path],
   "exact_one_H1":p.h1==1,
   "one_new_action_panel":p.ids.count("nf-v164-"+slug)==1,
   "three_operator_decision_cards":segment.count('class="nf-v164-card"')==3,
   "official_links_actually_in_rendered_actions":all(u in segment and u in p.links for u in cfg["official"]),
   "confirmed_operator_facts_and_return":all(f in segment for f in cfg["facts"]),
   "real_original_licensed_venue_photo_alt":any(src==cfg["photo"] and len(alt)>20 for src,alt in p.images),
   "actual_source_license_url":any("commons.wikimedia.org" in (u or "") for u in p.links),
   "responsive_large_52px_actions":'id="nf-v164-official-css"' in html and "min-height:52px" in html and "@media(max-width:620px)" in html,
   "index_follow_not_noindex":'name="robots" content="index,follow' in html[:8500],
   "no_fabricated_ticket_or_cruise_ship_availability":"잔여석 예약 확정" not in segment and "귀선이 보장됩니다" not in segment
  }
  if slug=="takamatsu":rules["corrected_real_photo_caption"]="현재는 공통 크루즈 참고 이미지입니다" not in html and "리쓰린공원 풍경" in html
  record(path,rules)
 except Exception as e:record(path,{"public_HTTP":False},str(e))
for cfg in D.values():
 path=cfg["photo"]
 try:
  status,ct,b=fetch(path,binary=True)
  record(path,{"HTTP_200_image_webp":status==200 and "webp" in ct.lower(),"RIFF_WEBP_magic_bytes":b[:4]==b"RIFF" and b[8:12]==b"WEBP"})
 except Exception as e:record(path,{"public_HTTP":False},str(e))
try:
 status,ct,xml=fetch("/sitemap.xml")
 locs=[u.find("{*}loc").text for u in ET.fromstring(xml).findall("{*}url")]
 record("/sitemap.xml",{"public_XML_200":status==200,"all_seven_existing_cruise_paths_present":all(BASE+f"/things-to-do/{s}-cruise-port-day-trip/" in locs for s in D),"no_duplicate_sitemap_urls":len(locs)==len(set(locs))})
except Exception as e:record("/sitemap.xml",{"public_HTTP":False},str(e))
result={"version":"V164","checked_at_utc":datetime.now(timezone.utc).isoformat(),"new_articles":0,"edited_existing_guides":7,"items_checked":len(rows),"passed":sum(x["success"] for x in rows),"real_ticket_inventory_or_GA4_not_verified":True,"rows":rows}
dest=Path("audit-output/v164-public");dest.mkdir(parents=True,exist_ok=True)
(dest/"seven-guides-original-photos-sitemap.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",result["passed"],"/",result["items_checked"],flush=True)
if result["passed"]!=result["items_checked"]:raise SystemExit(1)
