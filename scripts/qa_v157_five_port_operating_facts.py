#!/usr/bin/env python3
"""V157 quality: five EXISTING cruise-port guides, verified operator notices,
real return instructions, original photographs/license/canonical integrity.
"""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
import subprocess,re,json,xml.etree.ElementTree as ET
ROOT=Path("site")
DATA={
"aomori":{
 "sources":["https://www.pref.aomori.lg.jp/soshiki/kendo/kowan/2023-aomori-cruise.html","https://www.nebuta.jp/warasse/shisetsu/business-day.html","https://www.city.aomori.aomori.jp/koutsu/noriba_location-system_jikokuhyou/1002332.html"],
 "facts":["신추오","오키다테","17:30","귀선"]},
"hakodate":{
 "sources":["https://334.co.jp/news/2026/0406-22668/","https://hakobus.co.jp/info/2639/","https://www.city.hakodate.hokkaido.jp/docs/2014031100439/"],
 "facts":["10월 20일","11월 8일","전편 운휴","와카마쓰","귀선"]},
"kagoshima":{
 "sources":["https://www.kagoshima-kankou.com/cruise/marineport/top","https://www.city.kagoshima.lg.jp/sakurajima-ferry/howtouse/hajimete.html","https://www.kagoshima-kankou.com/course/53184"],
 "facts":["마린포트","북부두","04:00","23:30","24시간","귀선"]},
"beppu":{
 "sources":["https://pref.oita.jp/site/beppu17003/2026cruising.html","https://beppu-jigoku.com/fee/index.html","https://kamenoibus.com/scheduled_howto/"],
 "facts":["제4부두","2,400엔","1,200엔","08:00","17:00","귀선"]},
"kanazawa":{
 "sources":["https://www.kanazawa-cruise.jp/access/","https://www.kanazawa-cruise.jp/"],
 "facts":["09:00","21:00","5km","호쿠리쿠철도","귀선"]}}
class P(HTMLParser):
 def __init__(self):
  super().__init__();self.links=[];self.images=[];self.ids=[];self.h1=0;self.canon=[];self.desc=[];self.title=[];self.in_title=False
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="a":self.links.append(a.get("href",""))
  if tag=="img":self.images.append((a.get("src",""),a.get("alt",""),a.get("width"),a.get("height")))
  if "id" in a:self.ids.append(a["id"])
  if tag=="h1":self.h1+=1
  if tag=="link" and a.get("rel")=="canonical":self.canon.append(a.get("href",""))
  if tag=="meta" and a.get("name")=="description":self.desc.append(a.get("content",""))
  if tag=="title":self.in_title=True
 def handle_data(self,txt):
  if self.in_title:self.title.append(txt)
 def handle_endtag(self,tag):
  if tag=="title":self.in_title=False
def parse(s):
 x=P();x.feed(s);return x
def old(fp):
 return subprocess.check_output(["git","show","origin/main:"+str(fp)],text=True)
errors=[];results=[]
for slug,info in DATA.items():
 fp=ROOT/"things-to-do"/f"{slug}-cruise-port-day-trip"/"index.html"
 s=fp.read_text("utf-8");o=old(fp);p,q=parse(s),parse(o)
 start=s.index('id="nf-v157-'+slug+'"') if 'id="nf-v157-'+slug+'"' in s else -1
 excerpt=s[start:start+8800] if start>=0 else ""
 checks={
  "single_three_steps":p.ids.count("nf-v157-"+slug)==1 and excerpt.count('class="nf-v157-step"')==3,
  "direct_verified_operator_links":all(url in p.links for url in info["sources"]),
  "new_content_operational_facts":all(fact in excerpt for fact in info["facts"]),
  "source_link_newtab_security":all('rel="noopener noreferrer"' in a for a in re.findall(r'<a\b[^>]*href="https?[^"]+"[^>]*>',excerpt)),
  "original_current_port_section_preserved":p.ids.count("v69-berth-qa")==q.ids.count("v69-berth-qa")==1,
  "visible_before_original_guide":0<start<s.index('id="v69-berth-qa"'),
  "all_original_images_unmodified":p.images==q.images,
  "local_photos_exist":all((ROOT/src.lstrip("/").split("?")[0]).is_file() for src,alt,w,h in p.images if src.startswith("/") and not src.startswith("//")),
  "license_and_source_links_preserved":all(x in p.links for x in q.links if "commons.wikimedia.org" in x or "creativecommons.org" in x),
  "original_all_links_preserved":Counter(p.links)>=Counter(q.links),
  "new_links_only_four":len(p.links)==len(q.links)+4,
  "seo_original_H1_canonical_meta":p.h1==q.h1==1 and p.canon==q.canon==["https://www.nipponferry.com/things-to-do/"+slug+"-cruise-port-day-trip/"] and p.desc==q.desc and p.title==q.title,
  "no_repeated_dom_ids":len(p.ids)==len(set(p.ids)),
  "mobile_52px_touch_action":'id="nf-v157-official-action-css"' in s and "@media(max-width:600px)" in s and "min-height:52px" in s,
  "no_fabricated_ticket_inventory":not any(x in excerpt for x in ["잔여석 100% 보장","예약완료 확정","현재 예약 완료"])
 }
 for name,value in checks.items():
  if not value:errors.append(slug+":"+name)
 results.append({"slug":slug,"ok":all(checks.values()),"checks":checks})
 print("PASS" if all(checks.values()) else "FAIL",slug,[k for k,v in checks.items() if not v],flush=True)
sitemap=ROOT/"sitemap.xml";current=sitemap.read_text("utf-8");original=old(sitemap)
if current!=original:errors.append("sitemap_changed")
urls=[a.find("{*}loc").text for a in ET.fromstring(current).findall("{*}url")]
if not all("https://www.nipponferry.com/things-to-do/"+slug+"-cruise-port-day-trip/" in urls for slug in DATA):errors.append("original_sitemap_entry_lost")
out=Path("audit-output/v157");out.mkdir(parents=True,exist_ok=True)
(out/"five-port-current-official-operations.json").write_text(json.dumps({"new_articles":0,"existing_guides":5,"source_data_as_of":"2026-10-24","analytics_and_booking_stock_not_measured":True,"errors":errors,"results":results},ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",sum(x["ok"] for x in results),"/5","errors",len(errors),flush=True)
if errors:raise SystemExit(1)
