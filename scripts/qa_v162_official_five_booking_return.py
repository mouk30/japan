#!/usr/bin/env python3
"""V162 immutable prechange comparison of five existing port guides.
Verifies original photos, SEO, source licenses, operator-specific official
2026-10-24 dates, booking entrances and ship return caveats. No new pages.
"""
from html.parser import HTMLParser
from collections import Counter
from pathlib import Path
import subprocess, json, xml.etree.ElementTree as ET

BASE="04c7f107ad9ef0ab4e3ee24643357201dc6969c8"
SITE=Path("site")
PORTS={
 "hirara-miyakojima":{
  "urls":["https://www.pref.okinawa.jp/machizukuri/doboku/1013660/1022503/1030425.html","https://www.city.miyakojima.lg.jp/","https://www.city.miyakojima.lg.jp/soshiki/shityo/kensetsu/kouwan/oshirase/2024-0222-0902-121.html"],
  "facts":["10월 24일","10:36","12:00","이라부대교","이케마대교","귀선"]},
 "motobu":{
  "urls":["https://www.iejima.org/","https://www.iejima.org/?pid=119","https://www.mlit.go.jp/kankocho/cruise/detail/073/index.html"],
  "facts":["10월 24일","10월 25일","4왕복","이에섬","귀선"]},
 "ishigaki":{
  "urls":["https://yaeyama.co.jp/","https://www.ishigaki-airport.co.jp/info/2026/10/30.html","https://aneikankou.co.jp/condition"],
  "facts":["10/24","10/25","야에야마","정오","귀선"]},
 "naha":{
  "urls":["https://ko-jet.com/news/","https://reserve.smart-theater.com/?projectId=kumejimaoceanjet-production","https://www.nahaport.jp/"],
  "facts":["10월 24일","25일","가네구스쿠","귀선"]},
 "amami-naze":{
  "urls":["https://marixline.com/service/downstream20261023/","https://ferry.smaku.app/","https://www.aline-ferry.com/"],
  "facts":["10월 23일","10월 24일","05:00","05:50","귀선"]}
}
class Parse(HTMLParser):
 def __init__(self):
  super().__init__();self.id=[];self.img=[];self.a=[];self.canon=[];self.meta=[];self.h1=0;self.title=[];self.in_title=False
 def handle_starttag(self,t,attrs):
  p=dict(attrs)
  if "id" in p:self.id.append(p["id"])
  if t=="img":self.img.append((p.get("src",""),p.get("alt",""),p.get("width",""),p.get("height","")))
  if t=="a":self.a.append(p.get("href",""))
  if t=="link" and p.get("rel")=="canonical":self.canon.append(p.get("href",""))
  if t=="meta" and p.get("name")=="description":self.meta.append(p.get("content",""))
  if t=="h1":self.h1+=1
  if t=="title":self.in_title=True
 def handle_data(self,d):
  if self.in_title:self.title.append(d)
 def handle_endtag(self,t):
  if t=="title":self.in_title=False
def parse(s):
 x=Parse();x.feed(s);return x
def orig(path):
 return subprocess.check_output(["git","show",f"{BASE}:{path}"],text=True)
fail=[];rows=[]
for slug,v in PORTS.items():
 path=SITE/"things-to-do"/(slug+"-cruise-port-day-trip")/"index.html"
 s=path.read_text("utf-8");b=orig(path);n=parse(s);o=parse(b)
 mark='id="nf-v162-'+slug+'"';start=s.find(mark);end=s.find("</section>",start)
 frag=s[start:end] if start>=0 and end>start else ""
 headline=s.index("<article>");header_end=s.find("</header>",headline)
 checks={
 "panel_unique":n.id.count("nf-v162-"+slug)==1,
 "in_article_after_original_hero":headline>=0 and header_end>=0 and start>header_end,
 "three_operator_action_cards":frag.count('class="nf-v162-card"')==3,
 "three_clickable_official_sources":all(u in frag and u in n.a for u in v["urls"]),
 "externals_new_tab_hardened":frag.count('target="_blank"')==3 and frag.count('rel="noopener noreferrer"')==3,
 "source_dated_and_last_return":all(f in frag for f in v["facts"]),
 "all_original_links_preserved":Counter(n.a)>=Counter(o.a),
 "only_three_new_anchor_links":len(n.a)==len(o.a)+3,
 "photos_exact_original_src_alt_sizes":n.img==o.img,
 "original_webp_assets_present":all((SITE/im.lstrip("/").split("?")[0]).is_file() for im,alt,w,h in n.img if im.startswith("/") and not im.startswith("//")),
 "original_wikimedia_license_links":all(url in n.a for url in o.a if "commons.wikimedia.org" in url or "creativecommons.org" in url),
 "unchanged_h1_meta_canonical_title":n.h1==o.h1==1 and n.title==o.title and n.canon==o.canon==["https://www.nipponferry.com/things-to-do/"+slug+"-cruise-port-day-trip/"] and n.meta==o.meta,
 "no_repeated_ids":len(n.id)==len(set(n.id)),
 "responsive_52px_tap_targets":'id="nf-v162-official-css"' in s and '@media(max-width:620px)' in s and "min-height:52px" in s,
 "not_all_cruise_ships_canceled":"크루즈 전체 결항 확정" not in frag and "귀선 보장" not in frag and "잔여석 확정" not in frag
 }
 bad=[k for k,x in checks.items() if not x]
 fail.extend(slug+":"+name for name in bad)
 rows.append({"port":slug,"pass":not bad,"passed":sum(checks.values()),"total":len(checks),"bad":bad})
 print(("PASS" if not bad else "FAIL"),slug,sum(checks.values()),"/",len(checks),bad,flush=True)
site_map=SITE/"sitemap.xml"
if site_map.read_text("utf-8") != orig(site_map):fail.append("sitemap_modified")
locs=[n.find("{*}loc").text for n in ET.fromstring(site_map.read_text("utf-8")).findall("{*}url")]
for slug in PORTS:
 if f"https://www.nipponferry.com/things-to-do/{slug}-cruise-port-day-trip/" not in locs:fail.append(slug+":original_path_missing")
result={"version":"V162","date":"2026-10-24","updated_existing":len(PORTS),"new_articles":0,"original_photos_changed":0,"actual_reservation_inventory_unverified":True,"failures":fail,"results":rows}
out=Path("audit-output/v162");out.mkdir(parents=True,exist_ok=True)
(out/"official-five-ports-booking-ship-return.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",len(rows)-sum(bool(x["bad"]) for x in rows),"/",len(rows),"failures",len(fail),flush=True)
if fail:raise SystemExit(1)
