#!/usr/bin/env python3
"""V165: five existing cruise ports 2026-10-24 official schedule and booking QA.
Compare untouched original photo, SEO, licenses, headings and links against
the final pre-V165 HEAD; distinguish ferry operators from ocean cruise piers.
"""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
import json,subprocess,xml.etree.ElementTree as ET

BASE="316790832f238929e628b25fff90ca28e37f1c8b"
ROOT=Path("site")
PORTS={
 "goto-fukue":{"urls":["https://goto-ryokyakusen.com/","https://kyusho.co.jp/reserve"],"facts":["15:20","10월 24일","17:15","10/25~26","귀선"]},
 "aokata":{"urls":["https://www.nomo.co.jp/taiko/news/status.html","https://www.mlit.go.jp/kankocho/cruise/detail/061/index.html"],"facts":["10월 25일","11월 23일","11월 8~9일","아오카타","귀선"]},
 "sasebo":{"urls":["https://kyusho.co.jp/status","https://kyusho.co.jp/reserve","https://kyusho.co.jp/shuttle"],"facts":["17:35","08:35","12:05","15:50","16:55","전편 결항","나라오","귀선"]},
 "hakata":{"urls":["https://www.city.fukuoka.lg.jp/kowan/k-kikaku/hakata-port/cruise1.html","https://hakataport.com/Access/"],"facts":["10월 24일","11월 3일","LUMINARA","하코자키","21:00","귀선"]},
 "yakushima-miyanoura":{"urls":["https://www.yakushimaferry.com/2026/08/24/post-163/","https://www.yakushimaferry.com/bougenbilia-basic-information/","https://www.mlit.go.jp/kankocho/cruise/detail/072/index.html"],"facts":["10월 5일","11월 15일","42일","부겐빌레아","차량 운전자","12명","동승자는","귀선"]}
}
class Parser(HTMLParser):
 def __init__(self):
  super().__init__();self.ids=[];self.images=[];self.links=[];self.title=[];self.ontitle=False;self.canon=[];self.desc=[];self.h1=0
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if "id" in d:self.ids.append(d["id"])
  if t=="a":self.links.append(d.get("href",""))
  if t=="img":self.images.append((d.get("src",""),d.get("alt",""),d.get("width",""),d.get("height","")))
  if t=="title":self.ontitle=True
  if t=="link" and d.get("rel")=="canonical":self.canon.append(d.get("href",""))
  if t=="meta" and d.get("name")=="description":self.desc.append(d.get("content",""))
  if t=="h1":self.h1+=1
 def handle_endtag(self,t):
  if t=="title":self.ontitle=False
 def handle_data(self,t):
  if self.ontitle:self.title.append(t)
def parse(data):
 x=Parser();x.feed(data);return x
def original(path):
 return subprocess.check_output(["git","show",f"{BASE}:{path}"],text=True)

allerr=[];results=[]
for slug,source in PORTS.items():
 path=ROOT/"things-to-do"/(slug+"-cruise-port-day-trip")/"index.html"
 new=path.read_text("utf-8");old=original(path);p=parse(new);q=parse(old)
 start=new.find(f'id="nf-v165-{slug}"')
 end=new.find("</section>",start)
 panel=new[start:end] if start>=0 and end>start else ""
 checks={
 "one_new_v165_panel":p.ids.count("nf-v165-"+slug)==1,
 "correct_position_in_existing_guide":start>new.find("</header>",new.find("<article>"))>0 and start<new.find("</article>"),
 "three_operator_decision_cards":panel.count('class="nf-v165-card"')==3,
 "official_links_direct_from_panel":all(url in panel and url in p.links for url in source["urls"]),
 "dated_operator_facts_and_last_ship_return":all(s in panel for s in source["facts"]),
 "three_secure_blank_target_links":panel.count('target="_blank"')==3 and panel.count('rel="noopener noreferrer"')==3,
 "no_stale_operator_notice":("14:28" not in panel if slug=="sasebo" else True),
 "cargo_ferry_not_sold_as_tourist_ticket":("일반 관광객 승선권" in panel and "최대 12명" in panel and "동승자는" in panel if slug=="yakushima-miyanoura" else True),
 "all_existing_links_unmodified":Counter(p.links)>=Counter(q.links),
 "three_extra_action_links_only":len(p.links)==len(q.links)+3,
 "original_image_sources_alts_sizes_unchanged":p.images==q.images,
 "all_original_webp_present":all((ROOT/src.lstrip("/").split("?")[0]).is_file() for src,alt,w,h in p.images if src.startswith("/") and not src.startswith("//")),
 "license_and_photo_attribution_kept":all(u in p.links for u in q.links if "commons.wikimedia.org" in u or "creativecommons.org" in u),
 "original_SEO_H1_title_description_canonical_kept":p.h1==q.h1==1 and p.title==q.title and p.desc==q.desc and p.canon==q.canon==["https://www.nipponferry.com/things-to-do/"+slug+"-cruise-port-day-trip/"],
 "all_DOM_ids_unique":len(p.ids)==len(set(p.ids)),
 "mobile_minimum_52px_buttons":'id="nf-v165-ops-css"' in new and "@media(max-width:620px)" in new and "min-height:52px" in new,
 "no_false_bookability_or_ocean_cruise_cancel":all(x not in panel for x in ["모든 외항 크루즈 전편 결항 확정","실시간 예약 잔여석 보장","크루즈 귀선 완료 보장"])
 }
 missing=[k for k,v in checks.items() if not v]
 allerr.extend([f"{slug}: {m}" for m in missing])
 results.append({"slug":slug,"passed":len(checks)-len(missing),"total":len(checks),"failed":missing})
 print("PASS" if not missing else "FAIL",slug,len(checks)-len(missing),"/",len(checks),missing,flush=True)

sitemap=ROOT/"sitemap.xml"
if sitemap.read_text("utf-8")!=original(sitemap):allerr.append("sitemap_changed")
locs=[a.find("{*}loc").text for a in ET.fromstring(sitemap.read_text("utf-8")).findall("{*}url")]
for slug in PORTS:
 if f"https://www.nipponferry.com/things-to-do/{slug}-cruise-port-day-trip/" not in locs:allerr.append("missing original sitemap: "+slug)
out=Path("audit-output/v165");out.mkdir(parents=True,exist_ok=True)
report={"version":"V165","as_of":"2026-10-24","edited_existing":len(PORTS),"new_articles":0,"image_files_changed":0,"booking_inventory_GA4_not_checked":True,"errors":allerr,"rows":results}
(out/"five-existing-port-official-booking-return.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",sum(not x["failed"] for x in results),"/",len(results),"errors",len(allerr),flush=True)
if allerr:raise SystemExit(1)
