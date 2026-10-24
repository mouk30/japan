#!/usr/bin/env python3
"""V156 source/rights/SEO regression: exact original links/images preserved, only
checked official booking/terminal/taxi notices added to FOUR original pages.
Do not assert online booking or live ticket inventory.
"""
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
import subprocess, json, re
ROOT=Path("site")
CASES={
"things-to-do/shimonoseki-cruise-port-day-trip/index.html":{
"id":"nf-v156-shimonoseki-port","source":[
"https://www.shimonoseki-port.com/57635.html",
"https://www.shimonoseki-port.com/120177.html",
"https://www.kampuferry.co.jp/news/20261023systemmaintenance.html"],
"facts":["장주데지마","아루카포트","본항지구","국제여객터미널","크루즈","귀선"]},
"things-to-do/sado-ogi-cruise-port-day-trip/index.html":{
"id":"nf-v156-sado-ogi","source":[
"https://www.sado-bus.com/sightseeing/",
"https://www.sado-bus.com/news/5492/",
"https://www.sado-bus.com/route/ogi/"],
"facts":["운행중단","11월 30일","15:30","예약","오기항","귀선"]},
"guide/busan-shimonoseki-ferry/index.html":{
"id":"nf-v156-kampu-guide","source":[
"https://www.kampuferry.co.jp/news/20261023systemmaintenance.html",
"https://www.kampuferry.co.jp/lang_kor/passenger_info/t_access/"],
"facts":["해외 고객","이메일","재개일","2개월","객실","승선","귀국"]},
"booking/japan-cruise/index.html":{
"id":"nf-v156-kampu-booking","source":[
"https://www.kampuferry.co.jp/news/20261023systemmaintenance.html",
"mailto:support@kampuferry.co.jp",
"https://www.kampuferry.co.jp/lang_kor/passenger_info/t_access/checkin.html"],
"facts":["이메일","2026년 10월 23일","인터넷 예약","회신","체크인","귀국"]}
}
class P(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.canonical=[];self.desc=[];self.links=[];self.images=[];self.ids=[];self.meta=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="h1":self.h1+=1
  if tag=="a":self.links.append(a.get("href"))
  if tag=="img":self.images.append((a.get("src"),a.get("alt"),a.get("width"),a.get("height")))
  if "id" in a:self.ids.append(a["id"])
  if tag=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href"))
  if tag=="meta" and a.get("name")=="description":self.desc.append(a.get("content"))
def parse(s):
 p=P();p.feed(s);return p
def base(p):
 return subprocess.check_output(["git","show","origin/main:"+str(p)],text=True)
results=[];fail=[]
for path,conf in CASES.items():
 fp=ROOT/path
 s=fp.read_text(encoding="utf-8");old=base(fp);p,o=parse(s),parse(old)
 loc=s.index('id="'+conf["id"]+'"') if 'id="'+conf["id"]+'"' in s else -1
 chunk=s[loc:loc+7800] if loc>=0 else ""
 checks={
 "one_new_scoped_section":p.ids.count(conf["id"])==1,
 "three_operational_steps":chunk.count('class="nf-v156-step"')==3,
 "proven_operator_sources":all(url in p.links for url in conf["source"]),
 "specific_gate_or_booking_facts":all(f in chunk for f in conf["facts"]),
 "callout_above_other_details":loc>0 and (loc<s.index('id="nf-v148-photo-credits"') if 'id="nf-v148-photo-credits"' in s else True),
 "original_images_alt_and_dimensions_retained":p.images==o.images,
 "original_real_photos_exist":all((ROOT/src.lstrip("/").split("?")[0]).is_file() for src,alt,w,h in p.images if src and src.startswith("/") and not src.startswith("//")),
 "original_links_retained":Counter(p.links)>=Counter(o.links),
 "original_CC_attributions_retained":all(link in p.links for link in o.links if link and ("commons.wikimedia" in link or "creativecommons.org" in link)),
 "SEO_h1_canonical_description_same":p.h1==o.h1==1 and p.canonical==o.canonical and p.desc==o.desc,
 "all_ids_unique":len(p.ids)==len(set(p.ids)),
 "responsive_mobile_and_large_tap_area":'id="nf-v156-journey-style"' in s and "min-height:48px" in s and "@media(max-width:630px)" in s,
 "no_booking_invented":"예약 확정되었습니다" not in chunk and "잔여석 확보 완료" not in chunk,
 "only_four_new_links":len(p.links)==len(o.links)+4
 }
 for key,v in checks.items():
  if not v:fail.append(path+":"+key)
 row={"path":path,"checks":checks,"failed":[k for k,v in checks.items() if not v]}
 results.append(row);print("PASS" if not row["failed"] else "FAIL",path,row["failed"],flush=True)
sp=ROOT/"sitemap.xml"
smap=sp.read_text(encoding="utf-8")
if smap!=base(sp):fail.append("sitemap_should_not_change")
report={"new_articles":0,"corrected_existing_pages":len(CASES),"source_qa_checks":len(results)*len(results[0]["checks"]),"failed":fail,"results":results,
 "GA4_and_search_metrics_not_claimed":True,"booking_availability_not_measured":True}
out=Path("audit-output/v156");out.mkdir(parents=True,exist_ok=True)
(out/"booking-gate-return-source.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",sum(not r["failed"] for r in results),"/",len(results),"errors",len(fail),flush=True)
if fail:raise SystemExit(1)
