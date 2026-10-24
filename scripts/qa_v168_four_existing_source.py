#!/usr/bin/env python3
"""V168: verify four EXISTING cruise guides with official service, booking,
refund and last-return facts. Immutable pre-V168 SEO/photo/link baseline.
No new articles; no claims about real-time reservations or last ship boarding.
"""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
import subprocess,json,xml.etree.ElementTree as ET
ROOT=Path("site")
BASE="4318111cb6e3fffa6edc614ba9e9235092b096e3"
D={
"amami-naze":{"links":["https://www.aline-ferry.com/status/status-route/route-amami/","https://www.aline-ferry.com/amami/reserve/","https://www.aline-ferry.com/kagoshima/access/"],"facts":["페리 아마미","5월 16일","주 3편","10월 23일","24일","099-222-2338","귀선"]},
"naha":{"links":["https://www.vill.tokashiki.okinawa.jp/","https://www.vill.zamami.okinawa.jp/ship/","https://yoyaku.vill.zamami.okinawa.jp/zamami_web/res0301%21doFormOpenNologSp.action"],"facts":["10월 24일","도카시키","12월 3일","고속선","승선","귀선"]},
"motobu":{"links":["https://www.aline-ferry.com/status/status-route/route-kagoshima/","https://www.aline-ferry.com/kagoshima/reserve/","https://www.aline-ferry.com/kagoshima/access/"],"facts":["나미노우에","10월 24일","25일","27일","수수료","귀선"]},
"kagoshima":{"links":["https://www.tokara.jp/ferryinfo/ferrytoshima/","https://ferry-toshima.sakura.ne.jp/","https://nakagawaunyu.jp/toshima/"],"facts":["도시마2","10월 23일","10월 26일","09:30","21:00","귀선"]}
}
class Tags(HTMLParser):
 def __init__(self):
  super().__init__();self.img=[];self.links=[];self.ids=[];self.h1=0;self.title=[];self.in_title=False;self.meta=[];self.canon=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=="img":self.img.append((a.get("src",""),a.get("alt",""),a.get("width",""),a.get("height","")))
  if t=="a":self.links.append(a.get("href",""))
  if "id" in a:self.ids.append(a["id"])
  if t=="h1":self.h1+=1
  if t=="meta":self.meta.append((a.get("name",""),a.get("property",""),a.get("content","")))
  if t=="link" and a.get("rel")=="canonical":self.canon.append(a.get("href",""))
  if t=="title":self.in_title=True
 def handle_data(self,t):
  if self.in_title:self.title.append(t)
 def handle_endtag(self,t):
  if t=="title":self.in_title=False
def parse(txt):
 p=Tags();p.feed(txt);return p
def origin(path):
 return subprocess.check_output(["git","show",f"{BASE}:{path}"],text=True)
errs=[];rows=[]
for slug,item in D.items():
 path=ROOT/"things-to-do"/f"{slug}-cruise-port-day-trip"/"index.html"
 now_txt=path.read_text("utf-8");old_txt=origin(path)
 now,before=parse(now_txt),parse(old_txt)
 st=now_txt.find(f'id="nf-v168-{slug}"');ed=now_txt.find("</section>",st)
 panel=now_txt[st:ed] if 0<=st<ed else ""
 cond={
 "one_new_v168_panel":now.ids.count("nf-v168-"+slug)==1,
 "inside_original_article_after_hero":st>now_txt.find("</header>",now_txt.find("<article>"))>0 and st<now_txt.find("</article>"),
 "three_distinct_cards":panel.count('class="nf-v168-card"')==3,
 "real_official_links_in_cards":all(url in panel and url in now.links for url in item["links"]),
 "dated_operator_status_booking_and_return":all(f in panel for f in item["facts"]),
 "only_three_secure_new_window_links":panel.count('target="_blank"')==3 and panel.count('rel="noopener noreferrer"')==3,
 "old_links_all_retained":Counter(now.links)>=Counter(before.links),
 "only_three_additional_links":len(now.links)==len(before.links)+3,
 "all_original_venue_photos_alt_and_size_unchanged":now.img==before.img,
 "original_local_WebP_files_exist":all((ROOT/src.lstrip("/").split("?")[0]).is_file() for src,alt,w,h in now.img if src.startswith("/") and not src.startswith("//")),
 "Wikimedia_and_CC_original_attribution_retained":all(u in now.links for u in before.links if "commons.wikimedia.org" in u or "creativecommons.org" in u),
 "original_H1_title_meta_canonical_kept":now.h1==before.h1==1 and now.title==before.title and now.meta==before.meta and now.canon==before.canon==[f"https://www.nipponferry.com/things-to-do/{slug}-cruise-port-day-trip/"],
 "all_DOM_ids_unique":len(now.ids)==len(set(now.ids)),
 "mobile_52px_action_cards":'id="nf-v168-official-css"' in now_txt and "@media(max-width:620px)" in now_txt and "min-height:52px" in now_txt,
 "do_not_conflate_cruise_with_ferry":("크루즈" in panel and "정기선" in panel and "귀선" in panel),
 "no_invented_available_paid_inventory":all(x not in panel for x in ("잔여석 확보 완료","승선권 구매 완료","크루즈 귀선 보장"))
 }
 failed=[key for key,value in cond.items() if not value]
 errs.extend(f"{slug}: {x}" for x in failed)
 rows.append({"slug":slug,"passed":len(cond)-len(failed),"total":len(cond),"failed":failed})
 print(("PASS" if not failed else "FAIL"),slug,len(cond)-len(failed),"/",len(cond),failed,flush=True)

sitemap=ROOT/"sitemap.xml"
if sitemap.read_text("utf-8")!=origin(sitemap):errs.append("original sitemap changed")
locs=[x.find("{*}loc").text for x in ET.fromstring(sitemap.read_text("utf-8")).findall("{*}url")]
for slug in D:
 if f"https://www.nipponferry.com/things-to-do/{slug}-cruise-port-day-trip/" not in locs:errs.append(slug+": missing from sitemap")
out=Path("audit-output/v168");out.mkdir(parents=True,exist_ok=True)
report={"version":"V168","date":"2026-10-24","updated_existing_pages":len(D),"new_articles":0,"original_photo_replacement":0,
 "paid_ticket_inventory_payment_and_last_cruise_gate_not_verified":True,"errors":errs,"pages":rows}
(out/"four-existing-service-refund-return-source-qa.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",sum(not x["failed"] for x in rows),"/",len(rows),"errors",len(errs),flush=True)
if errs:raise SystemExit(1)
