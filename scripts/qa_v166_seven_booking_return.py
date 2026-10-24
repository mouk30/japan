#!/usr/bin/env python3
"""V166 immutable-baseline QA: 7 existing Japan cruise ports only.
Confirms official operator status/booking disruptions, true ferry port,
different ocean cruise ship return, original photos and SEO preserved.
No new pages, no actual paid booking or ship-boarding promise.
"""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
import json, subprocess, xml.etree.ElementTree as ET

ROOT=Path("site")
BASE="e73b755bebd9337f343af9af080aeac2b42de6d2"
H="https://heartlandferry.jp/2026/10/23/%E3%80%90%E5%88%A9%E7%A4%BC%E8%88%AA%E8%B7%AF%E3%80%91web%E4%BA%88%E7%B4%84%E3%82%B7%E3%82%B9%E3%83%86%E3%83%A0%E3%81%AE%E3%83%A1%E3%83%B3%E3%83%86%E3%83%8A%E3%83%B3%E3%82%B9/"
K="https://kyu-you.co.jp/whatsnew/detail/c1ea2c2e-5970-4af9-8dd9-33cd319efa89"
J="https://kyu-you.co.jp/whatsnew/detail/fb63ba8e-ae24-4bdb-99c6-2eb4b5e2a6c0"
P={
"wakkanai":{"links":["https://heartlandferry.jp/status/",H,"https://heartlandferry.jp/rishiri/"],"facts":["05:30","11월 초","0162-23-3780","귀선"]},
"rishiri-kutsugata":{"links":["https://heartlandferry.jp/status/",H,"https://heartlandferry.jp/rishiri/"],"facts":["오시도마리","굿쓰가타","11월 초","0162-23-3780","귀선"]},
"iki-gonoura":{"links":[K,J,"https://www.kyu-you.co.jp/"],"facts":["10월 22일","20:00","0920-47-0003","제트포일","귀선"]},
"tsushima-izuhara":{"links":[K,J,"https://www.kyu-you.co.jp/whatsnew/detail/9f0ff055-b62c-47a0-ad0b-199720c289ad"],"facts":["20:00","0920-52-0793","11월 1일","03:25","귀선"]},
"hakodate":{"links":["https://www.tsugarukaikyo.co.jp/cms/wp-content/uploads/2027hapmamedotsuku.pdf","https://www.tsugarukaikyo.co.jp/cms/wp-content/uploads/20261016.pdf","https://www.tsugarukaikyo.co.jp/service/reserve/internet/"],"facts":["2026년 10월 21일","2027년 3월 31일","2027년 1월 14일","2월 27일","귀선"]},
"aomori":{"links":["https://www.tsugarukaikyo.co.jp/cms/wp-content/uploads/2027hapmamedotsuku.pdf","https://www.tsugarukaikyo.co.jp/service/reserve/internet/","https://www.tsugarukaikyo.co.jp/service/timetable/hakodate-aomori/"],"facts":["2027년 1월 14일","2월 27일","13편","귀선"]},
"niigata":{"links":["https://www.snf.jp/kikobin-rule/","https://www.snf.jp/guide/time_schedule/","https://www.snf.jp/guide/access/"],"facts":["21:00","22:30","무효","환불","귀선"]}
}
class HTML(HTMLParser):
 def __init__(self):
  super().__init__();self.ids=[];self.images=[];self.links=[];self.title=[];self.in_title=False;self.meta=[];self.canonical=[];self.h1=0
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if "id" in a:self.ids.append(a["id"])
  if t=="a":self.links.append(a.get("href",""))
  if t=="img":self.images.append((a.get("src",""),a.get("alt",""),a.get("width",""),a.get("height","")))
  if t=="title":self.in_title=True
  if t=="meta" and a.get("name")=="description":self.meta.append(a.get("content",""))
  if t=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href",""))
  if t=="h1":self.h1+=1
 def handle_data(self,t):
  if self.in_title:self.title.append(t)
 def handle_endtag(self,t):
  if t=="title":self.in_title=False
def parse(s):
 o=HTML();o.feed(s);return o
def origin(path):
 return subprocess.check_output(["git","show",f"{BASE}:{path}"],text=True)

errors=[];rows=[]
for slug,requirements in P.items():
 path=ROOT/"things-to-do"/f"{slug}-cruise-port-day-trip"/"index.html"
 curr=path.read_text("utf-8");old=origin(path);now,before=parse(curr),parse(old)
 ix=curr.find(f'id="nf-v166-{slug}"');en=curr.find("</section>",ix)
 panel=curr[ix:en] if 0<=ix<en else ""
 checks={
 "one_versioned_panel":now.ids.count("nf-v166-"+slug)==1,
 "after_existing_hero_inside_article":ix>curr.find("</header>",curr.find("<article>"))>0 and ix<curr.find("</article>"),
 "three_human_action_cards":panel.count('class="nf-v166-card"')==3,
 "all_operator_sources_as_real_hrefs":all(u in panel and u in now.links for u in requirements["links"]),
 "latest_operator_dated_facts_and_ship_return":all(f in panel for f in requirements["facts"]),
 "three_secure_new_tab_operator_urls":panel.count('target="_blank"')==3 and panel.count('rel="noopener noreferrer"')==3,
 "original_links_kept":Counter(now.links)>=Counter(before.links),
 "three_extra_action_links_only":len(now.links)==len(before.links)+3,
 "original_photo_src_alt_dimensions_untouched":now.images==before.images,
 "original_webp_exists_locally":all(((ROOT / src.lstrip("/").split("?")[0])).is_file() for src,alt,w,h in now.images if src.startswith("/") and not src.startswith("//")),
 "original_license_and_wikimedia_attribution":all(x in now.links for x in before.links if "commons.wikimedia.org" in x or "creativecommons.org" in x),
 "unchanged_original_H1_title_description_canonical":now.h1==before.h1==1 and now.title==before.title and now.meta==before.meta and now.canonical==before.canonical==["https://www.nipponferry.com/things-to-do/"+slug+"-cruise-port-day-trip/"],
 "no_repeated_html_ids":len(now.ids)==len(set(now.ids)),
 "mobile_52px_buttons":'id="nf-v166-action-css"' in curr and "@media(max-width:620px)" in curr and "min-height:52px" in curr,
 "no_fake_booking_or_all_ocean_cruise_cancels":all(x not in panel for x in ["승선권 구매 완료","모든 외항 크루즈 결항","귀선이 보장됩니다"])
 }
 if slug in ("iki-gonoura","tsushima-izuhara"):
  checks["both_kinds_of_Kyushu_service_outage_shown"]="인터넷 예약" in panel and "운항정보" in panel and "전화" in panel
 if slug in ("wakkanai","rishiri-kutsugata"):
  checks["WEB_booking_disabled_no_false_online_buy"]="점검" in panel and "11월 초" in panel and "0162-23-3780" in panel
 if slug=="niigata":
  checks["No_refund_on_missed_return"]="환불되지" in panel and "21:00" in panel and "22:30" in panel
 failed=[name for name,ok in checks.items() if not ok]
 errors.extend([f"{slug}:{item}" for item in failed])
 rows.append({"slug":slug,"checks":len(checks),"passed":len(checks)-len(failed),"failed":failed})
 print(("FAIL" if failed else "PASS"),slug,len(checks)-len(failed),"/",len(checks),failed,flush=True)
sitemap=ROOT/"sitemap.xml"
txt=sitemap.read_text("utf-8")
if txt!=origin(sitemap):errors.append("sitemap_changed")
locs=[u.find("{*}loc").text for u in ET.fromstring(txt).findall("{*}url")]
for slug in P:
 if "https://www.nipponferry.com/things-to-do/"+slug+"-cruise-port-day-trip/" not in locs:errors.append(slug+":missing_original_sitemap_url")
out=Path("audit-output/v166");out.mkdir(parents=True,exist_ok=True)
report={"version":"V166","reference_day":"2026-10-24","edited_existing":len(P),"new_articles":0,"original_photo_or_SEO_changed":False,"paid_booking_or_analytics_not_verified":True,"errors":errors,"results":rows}
(out/"seven-original-guides-operator-booking-return-audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",sum(not r["failed"] for r in rows),"/",len(rows),"errors",len(errors),flush=True)
if errors:raise SystemExit(1)
