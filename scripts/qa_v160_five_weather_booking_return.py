#!/usr/bin/env python3
"""V160 audit: five EXISTING cruise guides; 2026-10-24 typhoon closure and
MITSUI OCEAN FUJI itinerary replacement. No tickets or booked seats claimed.
Immutable V159 baseline provides original SEO/photo attribution guarantees.
"""
from html.parser import HTMLParser
from collections import Counter
from pathlib import Path
import subprocess,json,xml.etree.ElementTree as ET

ROOT=Path("site")
BASE_SHA="eb9d99121230f102908322db5e4c24118edb05f1"
CASES={
 "ishigaki":{
   "sources":["https://aneikankou.co.jp/condition","https://aneikankou.co.jp/","https://www.city.ishigaki.okinawa.jp/soshiki/kowan/kuruzusenn/370.html"],
   "facts":["10월 24일","11:18","전편 결항","10월 25일","12:30","13:00","귀선"]},
 "motobu":{
   "sources":["https://www.mitsuioceancruises.com/news/20261020.html","https://www.mitsuioceancruises.com/contact/","https://www.mlit.go.jp/kankocho/cruise/detail/073/index.html"],
   "facts":["10월 25일","07:00","18:00","취소","귀선"]},
 "naha":{
   "sources":["https://www.mitsuioceancruises.com/news/20261020.html","https://www.mitsuioceancruises.com/","https://www.nahaport.jp/"],
   "facts":["10월 23일","나하","하카타","취소","귀선"]},
 "sasebo":{
   "sources":["https://www.mitsuioceancruises.com/news/20261020.html","https://english.huistenbosch.co.jp/ticket/?lang=ko","https://www.city.sasebo.lg.jp/kouwan/koukanri/terminal-info.html"],
   "facts":["10월 24일","08:00","18:00","우라가시라","귀선"]},
 "hakata":{
   "sources":["https://www.mitsuioceancruises.com/news/20261020.html","https://www.mitsuioceancruises.com/contact/","https://hakataport.com/Access/"],
   "facts":["10월 23일","10월 28일","17:00","09:00","귀선"]}
}
class P(HTMLParser):
 def __init__(self):
  super().__init__();self.links=[];self.ids=[];self.images=[];self.h1=0;self.canonical=[];self.desc=[];self.title=[];self.in_title=False
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if "id" in a:self.ids.append(a["id"])
  if t=="a":self.links.append(a.get("href",""))
  if t=="img":self.images.append((a.get("src",""),a.get("alt",""),a.get("width",""),a.get("height","")))
  if t=="h1":self.h1+=1
  if t=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href",""))
  if t=="meta" and a.get("name")=="description":self.desc.append(a.get("content",""))
  if t=="title":self.in_title=True
 def handle_data(self,value):
  if self.in_title:self.title.append(value)
 def handle_endtag(self,t):
  if t=="title":self.in_title=False
def parse(t):
 p=P();p.feed(t);return p
def origin(path):
 return subprocess.check_output(["git","show",f"{BASE_SHA}:{path}"],text=True)
out=[];errors=[]
for slug,item in CASES.items():
 path=ROOT/"things-to-do"/f"{slug}-cruise-port-day-trip"/"index.html"
 html=path.read_text("utf-8");old=origin(path);p,q=parse(html),parse(old)
 marker=f'id="nf-v160-{slug}"'
 i=html.find(marker)
 j=html.find("</section>",i)+len("</section>") if i>=0 else -1
 frag=html[i:j] if j>i>=0 else ""
 steps=frag.split('class="nf-v160-step"')
 checks={
  "exactly_one_action_panel":p.ids.count("nf-v160-"+slug)==1,
  "three_independent_steps":len(steps)==4,
  "official_operator_links":all(x in p.links and x in frag for x in item["sources"]),
  "new_three_destination_links":len(p.links)==len(q.links)+3,
  "dated_specific_change_and_return":all(x in frag for x in item["facts"]),
  "all_new_external_links_target_safe":frag.count('rel="noopener noreferrer"')==3 and frag.count('target="_blank"')==3,
  "original_links_retained":Counter(p.links)>=Counter(q.links),
  "original_photo_src_alt_size":p.images==q.images,
  "original_local_webp_files_present":all((ROOT/src.lstrip("/").split("?")[0]).is_file() for src,alt,w,h in p.images if src.startswith("/") and not src.startswith("//")),
  "original_photo_origin_license_preserved":all(u in p.links for u in q.links if "commons.wikimedia.org" in u or "creativecommons.org" in u),
  "seo_h1_title_canonical_desc_preserved":p.h1==q.h1==1 and p.title==q.title and p.canonical==q.canonical==["https://www.nipponferry.com/things-to-do/"+slug+"-cruise-port-day-trip/"] and p.desc==q.desc,
  "no_duplicate_ids":len(p.ids)==len(set(p.ids)),
  "mobile_touch_52px":'id="nf-v160-operational-css"' in html and "@media(max-width:620px)" in html and "min-height:52px" in html,
  "no_fake_booking_or_last_shuttle":"잔여석 확보 완료" not in frag and "귀선 보장" not in frag and "무료 셔틀 확정" not in frag
 }
 row={"slug":slug,"passes":sum(checks.values()),"total":len(checks),"failed":[k for k,v in checks.items() if not v]}
 out.append(row)
 errors.extend([slug+":"+name for name in row["failed"]])
 print(("FAIL" if row["failed"] else "PASS"),slug,row["passes"],"/",row["total"],row["failed"],flush=True)
sitemap=ROOT/"sitemap.xml"
if sitemap.read_text("utf-8")!=origin(sitemap):errors.append("sitemap_changed")
urls=[u.find("{*}loc").text for u in ET.fromstring(sitemap.read_text("utf-8")).findall("{*}url")]
for slug in CASES:
 if "https://www.nipponferry.com/things-to-do/"+slug+"-cruise-port-day-trip/" not in urls:errors.append("missing_original_sitemap:"+slug)
audit={"version":"V160","date":"2026-10-24","new_articles":0,"existing_guides":5,"photo_and_seo_preserved":not errors,"realtime_booking_and_GA4_not_verified":True,"failed":errors,"results":out}
target=Path("audit-output/v160");target.mkdir(parents=True,exist_ok=True)
(target/"existing-five-cancellations-and-safe-return.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",sum(not r["failed"] for r in out),"/",len(out),"errors",len(errors),flush=True)
if errors:raise SystemExit(1)
