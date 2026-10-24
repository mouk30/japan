#!/usr/bin/env python3
"""V154: 3 pilot OFFICIAL booking -> local transfer -> safe return evidence QA.
Checks original page SEO, links and original photo licensing against origin/main;
no new pages, no fabricated booking inventory, no actual GA4 numbers.
"""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
import re,subprocess,json,xml.etree.ElementTree as ET
ROOT=Path("site")
DATA={
 "naoshima-art-ferry-return":{
 "sources":[
  "https://benesse-artsite.jp/en/faq/chichu_art_museumonline_tickets.html",
  "https://www.benesse-artsite.jp/en/access/naoshima/",
  "https://shikokukisen.com/en-routes/"],
 "claims":["구매 후","취소","시간 변경","미야노우라","쓰쓰지소","승선 부두","귀항","운항"],
 "actions":["museum_info","island_transport","ferry_schedule","return_plan"]
 },
 "teshima-art-ferry-return":{
 "sources":["https://benesse-artsite.jp/en/general-information.html",
    "https://teshima-navi.jp/en/access/",
    "https://www.shodoshima-ferry.co.jp/timetable/"],
 "claims":["이에우라항","가라토항","현금","정리권","400엔","승선","귀선"],
 "actions":["museum_info","island_transport","ferry_schedule","return_plan"]
 },
 "takamatsu-cruise-udon-market-return":{
 "sources":["/things-to-do/takamatsu-cruise-port-day-trip/#nf-jnto-journey-20261024",
    "https://www.kensanpin.org/marche/schedule/","#return"],
 "claims":["다카마쓰","도쿠시마","고치","10월 18일","10월 25일","연기일",
   "11월 15일","11월 22일","귀선","선사"],
 "actions":["port_return","official_food","return_plan"]
}}
class Scan(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.links=[];self.images=[];self.canonical=[];self.desc=[];self.title=[];self.in_title=False;self.ids=[];self.scripts=[];self.ldjson=[];self.ld=False;self.ldbuf=[];self.modified=[];self.actions=[];self.styles=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="h1":self.h1+=1
  if tag=="a":self.links.append(a.get("href",""));self.actions.extend([a["data-nf-pilot-action"]] if "data-nf-pilot-action" in a else [])
  if tag=="img":self.images.append((a.get("src",""),a.get("alt",""),a.get("width"),a.get("height")))
  if tag=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href",""))
  if tag=="meta" and a.get("name")=="description":self.desc.append(a.get("content",""))
  if tag=="title":self.in_title=True
  if "id" in a:self.ids.append(a["id"])
  if tag=="script" and a.get("type")=="application/ld+json":self.ld=True;self.ldbuf=[]
 def handle_data(self,txt):
  if self.in_title:self.title.append(txt)
  if self.ld:self.ldbuf.append(txt)
 def handle_endtag(self,tag):
  if tag=="title":self.in_title=False
  if tag=="script" and self.ld:self.ldjson.append("".join(self.ldbuf));self.ld=False
def parse(doc):
 p=Scan();p.feed(doc);return p
def origin(path):return subprocess.check_output(["git","show","origin/main:"+str(path)],text=True)
failures=[];results=[]
def check(name,yes):
 if not yes:failures.append(name)
def check_article_schema(doc):
 ld=re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',doc,re.S)
 try:
  objs=[json.loads(x) for x in ld]
  queue=list(objs)
  while queue:
   x=queue.pop(0)
   if isinstance(x,list):queue.extend(x);continue
   if not isinstance(x,dict):continue
   if x.get("@type")=="Article":return x
   if "@graph" in x:queue.append(x["@graph"])
 except json.JSONDecodeError:return None
 return None
for slug, spec in DATA.items():
 path=ROOT/"things-to-do"/slug/"index.html"
 s=path.read_text(encoding="utf-8");old=origin(path)
 p,q=parse(s),parse(old)
 pos=s.index('id="nf-v154-depart-book-return"') if 'id="nf-v154-depart-book-return"' in s else -1
 pre=s[:pos] if pos>=0 else ""
 sec=s[pos:pos+7400] if pos>=0 else ""
 keys={
  "section_single":p.ids.count("nf-v154-depart-book-return")==1,
  "section_present_early":pos>0 and pos<s.index("<img",s.index("<body")) if slug!="takamatsu-cruise-udon-market-return" else pos<s.index('<section class="box">'),
  "3_separate_steps":sec.count('class="nf-v154-step"')==3,
  "official_sources_linked":all(src in p.links for src in spec["sources"]),
  "action_names_whitelisted":all(act in p.actions for act in spec["actions"]),
  "claims_scoped":all(x in sec for x in spec["claims"]),
  "travel_warnings":all(t in sec for t in ["운항","귀선","실시간"] if t in ["운항","귀선","실시간"]) if slug!="takamatsu-cruise-udon-market-return" else all(t in sec for t in ["크루즈","귀선","실시간"]),
  "return_link_twice":sum(1 for x in p.links if x in ["#checklist","#return"])>=2,
  "existing_photo_paths_and_alt_kept":p.images==q.images and all((ROOT/src.lstrip("/").split("?")[0]).is_file() for src,alt,w,h in p.images if src.startswith("/") and not src.startswith("//")),
  "original_photo_licensing":all(x in p.links for x in q.links if "commons.wikimedia.org" in x or "creativecommons.org" in x),
  "original_links_preserved":Counter(p.links)>=Counter(q.links),
  "original_h1_and_SEO":p.h1==q.h1==1 and p.canonical==q.canonical==["https://www.nipponferry.com/things-to-do/"+slug+"/"] and p.desc==q.desc and p.title==q.title,
  "original_article_and_photo_credits_preserved":p.ids.count("nf-v148-photo-credits")==q.ids.count("nf-v148-photo-credits")==1,
  "responsive_large_44px_buttons":'id="nf-v154-journey-style"' in s and "min-height:44px" in s and "@media(max-width:610px)" in s,
  "no_duplicate_sections":len(p.ids)==len(set(p.ids)),
  "no_ticket_stock_or_booking_success_claim":not any(x in sec for x in ["예약완료 보장","현장 잔여석 100%","구매 완료로 귀선 보장"]),
 }
 article=check_article_schema(s)
 if article:keys["Article_dateModified_20261024"]=article.get("dateModified")=="2026-10-24"
 else:keys["Article_dateModified_20261024"]=False
 for k,v in keys.items():check(slug+":"+k,v)
 results.append({"slug":slug,"passed":all(keys.values()),"checks":keys})
 print("PASS" if all(keys.values()) else "FAIL",slug,[k for k,v in keys.items() if not v],flush=True)
site=(ROOT/"sitemap.xml").read_text(encoding="utf-8")
check("sitemap_no_new_pages",site==origin(ROOT/"sitemap.xml"))
check("no_new_HTML_files",len([x for x in DATA if not (ROOT/"things-to-do"/x/"index.html").exists()])==0)
out=Path("audit-output/v154");out.mkdir(parents=True,exist_ok=True)
result={"pilot_guides_maintained":3,"new_articles":0,"original_photos_and_rights_preserved":all(x["checks"].get("existing_photo_paths_and_alt_kept") and x["checks"].get("original_photo_licensing") for x in results),"real_GA4_measured":False,
"failures":failures,"details":results}
(out/"booking-transport-safe-return.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",len(results)-sum(not x["passed"] for x in results),"/",len(results),"errors",len(failures))
if failures:raise SystemExit(1)
