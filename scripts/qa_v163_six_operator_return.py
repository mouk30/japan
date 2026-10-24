#!/usr/bin/env python3
"""V163: immutable-baseline QA for six EXISTING cruise-port articles.
Checks confirmed operator bulletins, practical reservation/booking entry,
different ferry vs cruise terminals and final return, canonical/meta and
licensed venue photos unchanged. No new published pages.
"""
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
import subprocess,json,xml.etree.ElementTree as ET

BASE="04c7f107ad9ef0ab4e3ee24643357201dc6969c8"
ROOT=Path("site")
D={
"sado-ogi":{"official":["https://www.sadokisen.co.jp/forecast/","https://www.sadokisen.co.jp/reservation/seat-availability/?route=2","https://www.sadokisen.co.jp/reservation/service-status/?route=2"],"facts":["10월 26~28일","10:35","17:25","귀선"]},
"naoetsu":{"official":["https://www.sadokisen.co.jp/forecast/","https://www.sadokisen.co.jp/reservation/seat-availability/?route=2","https://www.sadokisen.co.jp/reservation/service-status/?route=2"],"facts":["10월 26~28일","07:10","14:00","귀선"]},
"yakushima-miyanoura":{"official":["https://ferryyakusima2.com/news/15696","https://ferryyakusima2.com/about","https://yakukan.jp/safe-travel/transportation.html"],"facts":["10월 24일","10월 26일","10월 25일","099-226-0731","귀선"]},
"osaka":{"official":["https://www.ferry-sunflower.co.jp/news/article/3010231024.html","https://booking.ferry-sunflower.co.jp/web/yoyaku/","https://www.ferry-sunflower.co.jp/faq/"],"facts":["10월 23일","10월 24일","기리시마","사쓰마","귀선"]},
"nagasaki":{"official":["https://kyusho.co.jp/status","https://kyusho.co.jp/reserve","https://www.discover-nagasaki.com/en/featured-topics/fromnagasakiport"],"facts":["14:28","14:00","15:45","나라오","귀선"]},
"aokata":{"official":["https://www.goto-sangyo.co.jp/","https://www.goto-sangyo.co.jp/pickup/%E4%BA%88%E7%B4%84%E3%82%B5%E3%83%BC%E3%83%93%E3%82%B9%E3%80%8E%E3%83%99%E3%83%AB%E3%83%88%E3%83%A9%E3%80%8F%E3%81%A7%E4%B9%97%E8%88%B9%E4%BA%88%E7%B4%84%E3%81%8C%E5%8F%AF%E8%83%BD%E3%81%AB%E3%81%AA/","https://www.mlit.go.jp/kankocho/cruise/detail/061/index.html"],"facts":["10월 24일","10월 25일","13:30","16:00","귀선"]}
}
class Tags(HTMLParser):
 def __init__(self):
  super().__init__();self.ids=[];self.images=[];self.links=[];self.canon=[];self.meta=[];self.title=[];self.in_title=False;self.h1=0
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if "id" in d:self.ids.append(d["id"])
  if t=="img":self.images.append((d.get("src",""),d.get("alt",""),d.get("width",""),d.get("height","")))
  if t=="a":self.links.append(d.get("href",""))
  if t=="link" and d.get("rel")=="canonical":self.canon.append(d.get("href",""))
  if t=="meta" and d.get("name")=="description":self.meta.append(d.get("content",""))
  if t=="title":self.in_title=True
  if t=="h1":self.h1+=1
 def handle_endtag(self,t):
  if t=="title":self.in_title=False
 def handle_data(self,s):
  if self.in_title:self.title.append(s)
def parse(t):
 r=Tags();r.feed(t);return r
def origin(path):
 return subprocess.check_output(["git","show",f"{BASE}:{path}"],text=True)

errors=[];records=[]
for slug,info in D.items():
 path=ROOT/"things-to-do"/f"{slug}-cruise-port-day-trip"/"index.html"
 curr=path.read_text("utf-8");old=origin(path);n,o=parse(curr),parse(old)
 pos=curr.find(f'id="nf-v163-{slug}"')
 finish=curr.find("</section>",pos)
 frag=curr[pos:finish] if pos>=0 and finish>pos else ""
 hstart=curr.find("<article>");hend=curr.find("</header>",hstart)
 checks={
  "new_panel_once":n.ids.count("nf-v163-"+slug)==1,
  "after_original_hero_before_existing_content":hstart>=0 and hend>=0 and pos>hend and curr.index(f'id="nf-v163-{slug}"') < curr.find("</article>"),
  "three_action_cards":frag.count('class="nf-v163-step"')==3,
  "three_official_destinations":all(u in frag and u in n.links for u in info["official"]),
  "source_dated_and_return":all(f in frag for f in info["facts"]),
  "new_external_links_secure":frag.count('target="_blank"')==3 and frag.count('rel="noopener noreferrer"')==3,
  "all_old_links_kept":Counter(n.links)>=Counter(o.links),
  "only_three_extra_links":len(n.links)==len(o.links)+3,
  "same_original_images_alt_sizes":n.images==o.images,
  "webp_files_exist_locally":all((ROOT/src.lstrip("/").split("?")[0]).is_file() for src,alt,w,h in n.images if src.startswith("/") and not src.startswith("//")),
  "original_photo_authorship_licenses":all(u in n.links for u in o.links if "commons.wikimedia.org" in u or "creativecommons.org" in u),
  "same_h1_title_desc_canonical":n.h1==o.h1==1 and n.title==o.title and n.meta==o.meta and n.canon==o.canon==["https://www.nipponferry.com/things-to-do/"+slug+"-cruise-port-day-trip/"],
  "no_duplicate_ids":len(n.ids)==len(set(n.ids)),
  "mobile_52px_actions":'id="nf-v163-ops-style"' in curr and "@media(max-width:620px)" in curr and "min-height:52px" in curr,
  "no_false_total_cruise_cancellation":'전 크루즈 결항 확정' not in frag and '잔여석 확보 완료' not in frag and '모든 예약 자동 환불 완료' not in frag
 }
 failed=[k for k,v in checks.items() if not v]
 errors.extend(f"{slug}:{c}" for c in failed)
 records.append({"slug":slug,"passed":len(checks)-len(failed),"total":len(checks),"failed":failed})
 print(("PASS" if not failed else "FAIL"),slug,len(checks)-len(failed),"/",len(checks),failed,flush=True)

smap=ROOT/"sitemap.xml"
if smap.read_text("utf-8")!=origin(smap):errors.append("sitemap_modified")
allurls=[u.find("{*}loc").text for u in ET.fromstring(smap.read_text("utf-8")).findall("{*}url")]
for slug in D:
 if f"https://www.nipponferry.com/things-to-do/{slug}-cruise-port-day-trip/" not in allurls:errors.append(slug+":sitemap_missing")
out=Path("audit-output/v163");out.mkdir(parents=True,exist_ok=True)
report={"version":"V163","as_of":"2026-10-24","edited_existing_pages":len(D),"new_articles":0,"no_new_photos":True,"booking_inventory_not_verified":True,"errors":errors,"pages":records}
(out/"source-six-ports-operator-booking-return.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",sum(not r["failed"] for r in records),"/",len(records),"errors",len(errors),flush=True)
if errors:raise SystemExit(1)
