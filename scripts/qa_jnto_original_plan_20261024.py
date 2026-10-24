#!/usr/bin/env python3
"""Audit original JNTO-inspired V145-V148 content plan: 20 existing + 1 new pilot.
Only confirmed existing edits and one approved pilot. Compare photos, rights, URLs,
canonical, H1, local pictures, original links against unchanged origin/main.
"""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import json,re,subprocess,xml.etree.ElementTree as ET
ROOT=Path("site")
CORE="naoshima-art-ferry-return teshima-art-ferry-return shodoshima-ferry-island-access takamatsu-cruise-port-day-trip amami-naze-cruise-port-day-trip goto-fukue-cruise-port-day-trip nagasaki-cruise-4-6-8-hour-itinerary matsuyama-cruise-port-day-trip sado-ogi-cruise-port-day-trip japan-amami-oshima-tsumugi".split()
RELATED="japan-kagawa-udon-pilgrimage kagawa-marugame-uchiwa-fans nagasaki-dejima-island-trade nagasaki-cruise-parents-guide hakata-cruise-parents-guide ishigaki-cruise-parents-guide nagasaki-glover-garden nagasaki-cruise-family-guide local-food-market-guide udon-japanese-regional-noodles".split()
PILOT="takamatsu-cruise-udon-market-return"
assert len(CORE)==10 and len(RELATED)==10 and len(set(CORE+RELATED))==20
class Scan(HTMLParser):
 def __init__(self):
  super().__init__();self.images=[];self.canonical=[];self.titles=[];self.in_title=False;self.desc=[];self.links=[];self.ids=[];self.h1=0;self.ld=0;self.robots=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="img":self.images.append((a.get("src",""),a.get("alt","")))
  if tag=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href",""))
  if tag=="a":self.links.append(a.get("href",""))
  if "id" in a:self.ids.append(a["id"])
  if tag=="h1":self.h1+=1
  if tag=="title":self.in_title=True
  if tag=="meta" and a.get("name")=="description":self.desc.append(a.get("content",""))
  if tag=="meta" and a.get("name")=="robots":self.robots.append(a.get("content",""))
  if tag=="script" and a.get("type")=="application/ld+json":self.ld+=1
 def handle_data(self,txt):
  if self.in_title:self.titles.append(txt)
 def handle_endtag(self,tag):
  if tag=="title":self.in_title=False
def readold(path):
 return subprocess.check_output(["git","show","origin/main:"+path.as_posix()],text=True)
def scan(doc):
 parser=Scan();parser.feed(doc);return parser
def verify(ok,label):
 if not ok:failures.append(label)
def local_images_exist(a):
 return all((ROOT / img[0].lstrip("/").split("?")[0]).is_file() for img in a.images if img[0].startswith("/") and not img[0].startswith("//"))
failures=[];results=[]
for slug in CORE+RELATED:
 path=ROOT/"things-to-do"/slug/"index.html"
 updated=path.read_text(encoding="utf-8");baseline=readold(path)
 a,b=scan(updated),scan(baseline)
 group="core" if slug in CORE else "related"
 marker="nf-jnto-journey-20261024" if group=="core" else "nf-jnto-experience-links-20261024"
 checks={
  "correct_plan_marker":a.ids.count(marker)==1 and b.ids.count(marker) in (0,1),
  "single_H1_preserved":a.h1==b.h1==1,
  "original_images_and_alts_unchanged":a.images==b.images and local_images_exist(a),
  "canonical_unchanged":a.canonical==b.canonical==["https://www.nipponferry.com/things-to-do/"+slug+"/"],
  "description_unchanged":a.desc==b.desc,
  "title_unchanged":a.titles==b.titles,
  "structured_data_retained":a.ld==b.ld,
  "original_internal_and_external_links_retained":Counter(a.links)>=Counter(b.links),
  "original_CC_links_retained":all(url in a.links for url in b.links if "commons.wikimedia.org" in url or "creativecommons.org" in url),
  "existing_section_anchors_preserved":Counter(a.ids)>=Counter(b.ids),
  "at_least_three_navigation_links":(len(a.links)-len(b.links)>=3 if b.ids.count(marker)==0 else
    (len(re.findall(r'<a\b[^>]*href=',updated[updated.index('id="'+marker+'"'):updated.index('id="'+marker+'"')+6500]))>=3)),
  "no_duplicate_ids":len(a.ids)==len(set(a.ids)),
  "no_live_inventory_promise":"예약 완료" not in updated[updated.find('id="'+marker+'"'):updated.find('id="'+marker+'"')+1800],
 }
 for name,ok in checks.items():verify(ok,slug+":"+name)
 results.append({"slug":slug,"group":group,"pass":all(checks.values()),"checks":checks})
pilot_path=ROOT/"things-to-do"/PILOT/"index.html"
pdoc=pilot_path.read_text(encoding="utf-8");pilot=scan(pdoc)
pilotchecks={
 "one_H1":pilot.h1==1,
 "exact_canonical":pilot.canonical==["https://www.nipponferry.com/things-to-do/"+PILOT+"/"],
 "original_pilot_image_local":pilot.images==[("/images/culture-verified/japan-kagawa-udon-pilgrimage.webp",pilot.images[0][1])] and local_images_exist(pilot),
 "no_other_regions_mislabelled":all(x in pdoc for x in ["가가와현","도쿠시마","고치","다카마쓰","우동","라멘","히로메시장"]),
 "official_food_sources":all(u in pilot.links for u in ["https://www.my-kagawa.jp/en/see-and-do/10132","https://discovertokushima.net/ko/cuisines/","https://visitkochijapan.com/ko/see-and-do/10024"]),
 "photo_creator_and_cc":all(u in pilot.links for u in ["https://commons.wikimedia.org/wiki/File:Kama-age_sanuki_udon_by_sekido_in_Takamatsu%2C_Kagawa.jpg","https://creativecommons.org/licenses/by/2.0"]),
 "image_photo_credit_collapsed":pilot.ids.count("nf-v148-photo-credits")==1 and "<summary>사진 출처 보기</summary>" in pdoc,
 "four_port_return_fields":all(x in pdoc for x in ["최종 귀선","__:__","하선 부두","교통"]),
 "internal_links_to_existing_guides":all("/things-to-do/"+x+"/" in pilot.links or any(y.startswith("/things-to-do/"+x+"/#") for y in pilot.links) for x in ["takamatsu-cruise-port-day-trip","japan-kagawa-udon-pilgrimage","naoshima-art-ferry-return","teshima-art-ferry-return"]),
 "SEO_JSONLD":pilot.ld>=1 and len(pilot.desc)==1 and len(pilot.titles)>=1,
 "indexable":all("noindex" not in x for x in pilot.robots)
}
for k,v in pilotchecks.items():verify(v,PILOT+":"+k)
sitemap=(ROOT/"sitemap.xml").read_text(encoding="utf-8");oldsite=readold(ROOT/"sitemap.xml")
def urls(doc):
 root=ET.fromstring(doc)
 return [((node.find("{*}loc").text or ""),node.find("{*}lastmod").text if node.find("{*}lastmod") is not None else None) for node in root.findall("{*}url")]
before,after=urls(oldsite),urls(sitemap)
before_set=Counter(url for url,date in before);after_set=Counter(url for url,date in after)
extra=[u for u in after_set if u not in before_set]
removed=[u for u in before_set if u not in after_set]
expected="https://www.nipponferry.com/things-to-do/"+PILOT+"/"
verify((extra==([] if expected in before_set else [expected])) and not removed,"sitemap pilot URLs changed unexpectedly")
verify(len(after)==len(before)+(0 if expected in before_set else 1),"sitemap size invalid")
verify(all(after_set[u]==1 for u in after_set),"sitemap duplicate URL")
after_dates=dict(after)
verify(all(after_dates.get("https://www.nipponferry.com/things-to-do/"+x+"/")=="2026-10-24" for x in CORE+RELATED+[PILOT]),"sitemap 21 updated lastmod dates missing")
try:
 preExisting=[url for url,date in before if url not in {expected} and not any(url.endswith("/things-to-do/"+x+"/") for x in CORE+RELATED)]
 verify(all(dict(before).get(u)==dict(after).get(u) for u in preExisting),"unrelated sitemap modification")
except Exception as ex:failures.append("sitemap: "+str(ex))
# Existing article photo already CC licensed and exactly same URL as new pilot.
photo=ROOT/"things-to-do/japan-kagawa-udon-pilgrimage/index.html"
verify('src="/images/culture-verified/japan-kagawa-udon-pilgrimage.webp"' in photo.read_text(encoding="utf-8"),"pilot licensed photograph not matched to previous verified article")
report={"date":"2026-10-24","original_10_deepened":sum(x["pass"] for x in results if x["group"]=="core"),
"related_10_connected":sum(x["pass"] for x in results if x["group"]=="related"),
"pilot_total":3,"pilot_preexisting":2,"pilot_new":1,
"new_total_article_urls":len(extra),"ga4_booking_clicks":"not verified: owner account / measurement ID access required",
"search_console_impressions_and_clicks":"not verified: access required",
"sitemap_before":len(before),"sitemap_after":len(after),"pilot_pass":all(pilotchecks.values()),
"pilot_checks":pilotchecks,"errors":failures,"pages":results}
out=Path("audit-output/jnto-plan-20261024");out.mkdir(parents=True,exist_ok=True)
(out/"source-seo-plan.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in report.items() if k not in ("pages","pilot_checks")},ensure_ascii=False))
if failures:
 for f in failures[:30]:print("FAIL",f)
 raise SystemExit(1)
