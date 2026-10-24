#!/usr/bin/env python3
"""V164 QA: compare seven existing cruise-port HTML pages to immutable
pre-V164 baseline and verify official 2026 operator changes, booking routes,
actual/final return rules, original photos, licensed sources and SEO.
No new published articles; no claims about real ticket inventory.
"""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import json, subprocess, xml.etree.ElementTree as ET

SITE=Path("site")
BEFORE="976932da884ba99f2a5fb5b8bc929607a775298f"
CASES={
 "kagoshima":{
 "links":["https://www.city.kagoshima.lg.jp/sakurajima-ferry/unko_jokyo/20261024rinjibin.html","https://www.city.kagoshima.lg.jp/sakurajima-ferry/tyumoku/daycruise.html","https://www.city.kagoshima.lg.jp/sakurajima-ferry/unko_jokyo/unnkoujyoukyou_20261023.html"],
 "facts":["10월 25일","10/28","11/15","마린포트","귀선"]},
 "uno":{
 "links":["https://shikokukisen.com/uno-seto-ferry-unko/","https://shikokukisen.com/uno-miyanoura-ferry-unko/","https://shikokukisen.com/uno-miyanoura/"],
 "facts":["가자토","일반 관광객","선착순","귀선"]},
 "takamatsu":{
 "links":["https://shikokukisen.com/takamatsu-miyanoura/","https://shikokukisen.com/faq/","https://shikokukisen.com/"],
 "facts":["680엔","1,590엔","현금","17:00","귀선"]},
 "kobe":{
 "links":["https://ferry.co.jp/","https://ferry.co.jp/home/howto/","https://www.city.kobe.lg.jp/a14075/kanko/leisure/harbor/passenger/terminal/index.html"],
 "facts":["15:00","30분","10월 26일","정상 운항 예정","귀선"]},
 "niihama":{
 "links":["https://www.orange-ferry.co.jp/6488.html","https://www.orange-ferry.co.jp/","https://www.mlit.go.jp/kankocho/cruise/detail/103/index.html"],
 "facts":["10월 20일","11월 2일","23:10","14:50","귀선"]},
 "yawatahama":{
 "links":["https://www.orange-ferry.co.jp/8683.html","https://www.orange-ferry.co.jp/time-table/kyuushi/yawatahama-usuki/","https://www.mlit.go.jp/kankocho/cruise/detail/125/index.html"],
 "facts":["10월 31일","104편","204편","106·206편","귀선"]},
 "tokushima-komatsushima":{
 "links":["https://nankai-ferry.co.jp/operation_status/225/","https://nankai-ferry.co.jp/tokushima/","https://nankai-ferry.co.jp/timetable/"],
 "facts":["8월 1일","감편","고마쓰시마","귀선"]}
}
class Parser(HTMLParser):
 def __init__(self):
  super().__init__();self.ids=[];self.images=[];self.links=[];self.h1=0;self.canon=[];self.desc=[];self.title=[];self.in_title=False
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if "id" in a:self.ids.append(a["id"])
  if t=="img":self.images.append((a.get("src",""),a.get("alt",""),a.get("width",""),a.get("height","")))
  if t=="a":self.links.append(a.get("href",""))
  if t=="h1":self.h1+=1
  if t=="link" and a.get("rel")=="canonical":self.canon.append(a.get("href",""))
  if t=="meta" and a.get("name")=="description":self.desc.append(a.get("content",""))
  if t=="title":self.in_title=True
 def handle_endtag(self,t):
  if t=="title":self.in_title=False
 def handle_data(self,s):
  if self.in_title:self.title.append(s)
def parse(content):
 p=Parser();p.feed(content);return p
def original(path):
 return subprocess.check_output(["git","show",f"{BEFORE}:{path}"],text=True)
errors=[];rows=[]
for slug,item in CASES.items():
 path=SITE/"things-to-do"/f"{slug}-cruise-port-day-trip"/"index.html"
 now=path.read_text(encoding="utf-8");prev=original(path);a,b=parse(now),parse(prev)
 key=f'id="nf-v164-{slug}"'
 start=now.find(key);end=now.find("</section>",start)
 section=now[start:end] if 0<=start<end else ""
 checks={
  "single_new_panel":a.ids.count("nf-v164-"+slug)==1,
  "new_section_after_original_article_hero":start>now.find("</header>",now.find("<article>"))>0,
  "exactly_three_action_cards":section.count('class="nf-v164-card"')==3,
  "operator_official_pages_are_direct_links":all(u in section and u in a.links for u in item["links"]),
  "three_secure_ext_tabs":section.count('target="_blank"')==3 and section.count('rel="noopener noreferrer"')==3,
  "dated_information_and_last_return":all(f in section for f in item["facts"]),
  "original_links_all_retained":Counter(a.links)>=Counter(b.links),
  "exactly_three_new_links":len(a.links)==len(b.links)+3,
  "exactly_original_imgs_alt_and_dimensions":a.images==b.images,
  "original_images_exist":all((SITE/src.lstrip("/").split("?")[0]).is_file() for src,alt,w,h in a.images if src.startswith("/") and not src.startswith("//")),
  "original_wikimedia_license_links_retained":all(u in a.links for u in b.links if "commons.wikimedia.org" in u or "creativecommons.org" in u),
  "same_original_title_H1_meta_and_canonical":a.h1==b.h1==1 and a.title==b.title and a.desc==b.desc and a.canon==b.canon==["https://www.nipponferry.com/things-to-do/"+slug+"-cruise-port-day-trip/"],
  "id_values_unique":len(a.ids)==len(set(a.ids)),
  "responsive_mobile_52px_action":'id="nf-v164-official-css"' in now and "@media(max-width:620px)" in now and "min-height:52px" in now,
  "no_fake_assumed_cruise_or_ticket_availability":all(x not in section for x in ["모든 외항 크루즈 결항 확정","잔여석 예약 확정","크루즈 귀선 보장"])
 }
 if slug=="takamatsu":
  checks["obsolete_photo_placeholder_corrected"]="현재는 공통 크루즈 참고 이미지입니다" not in now and "리쓰린공원 풍경" in now
 bad=[key for key,ok in checks.items() if not ok]
 errors.extend(f"{slug}:{f}" for f in bad)
 row={"slug":slug,"passed":len(checks)-len(bad),"total":len(checks),"failed":bad}
 rows.append(row)
 print("PASS" if not bad else "FAIL",slug,row["passed"],"/",row["total"],bad,flush=True)

sitemap=SITE/"sitemap.xml";current=sitemap.read_text("utf-8")
if current!=original(sitemap):errors.append("original_sitemap_altered")
locs=[u.find("{*}loc").text for u in ET.fromstring(current).findall("{*}url")]
for slug in CASES:
 if "https://www.nipponferry.com/things-to-do/"+slug+"-cruise-port-day-trip/" not in locs:errors.append(slug+":original_sitemap_url_missing")
report={"version":"V164","as_of":"2026-10-24","new_articles":0,"existing_pages":len(CASES),"images_replaced":0,"live_booking_inventory_and_GA4_not_verified":True,"failures":errors,"rows":rows}
dest=Path("audit-output/v164");dest.mkdir(parents=True,exist_ok=True)
(dest/"seven-original-ports-booking-ship-return.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",sum(not row["failed"] for row in rows),"/",len(rows),"total_rule_errors",len(errors),flush=True)
if errors:raise SystemExit(1)
