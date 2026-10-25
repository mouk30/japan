#!/usr/bin/env python3
"""V177 regression: 4 original cruise guides and official checkout vs port CTA, photos, canonical."""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
import subprocess, json, sys
BASE="60312cbc863130276dd2de3365393f2c53b00893"
CASES={
 "muroran":(["3일 전","출항 20분 전","슈쿠쓰부두","중앙부두"],["star-marine.co.jp/reserve.html","star-marine.co.jp/cruise/access.html","city.muroran.lg.jp/content/?content=5662"]),
 "mojiko":(["1,700엔","당일","마린게이트 모지","히비키"],["webket.jp/pc/ticket/index?ac=9000&fc=80054","mojiko-retoro9.jp/ticket/","kanmon-kisen.co.jp/route/kanmon.html"]),
 "sakata":(["1,300엔","16:30","고미나토부두","2026년 4월 1일"],["homma-museum.or.jp/use/","city.sakata.lg.jp/bunka/bunkazai/bunkazaishisetsu/sankyosouko.html","city.sakata.lg.jp/sangyo/kotsu/kouwan/shoko0320191023.html"]),
 "sendai":(["15분 전","6개월","2,400엔","16:00"],["asoview.com/channel/tickets/CfQ553fPJ6/","uminomori.jp/umino/webket/index.html","transfer.navitime.biz/miyagikotsu/pc/transfer/DepArrTimeList?gnode=00330517&snode=00332351"])
}
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.intitle=False;self.title=[];self.meta=[];self.canonical=[];self.h1=0;self.images=[];self.links=[];self.ids=[]
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if t=="title":self.intitle=True
  if t=="meta":self.meta.append((d.get("name",""),d.get("property",""),d.get("content","")))
  if t=="link" and d.get("rel")=="canonical":self.canonical.append(d.get("href",""))
  if t=="h1":self.h1+=1
  if t=="img":self.images.append(tuple(d.get(k,"") for k in ("src","alt","width","height","onerror")))
  if t=="a":self.links.append(d.get("href",""))
  if "id" in d:self.ids.append(d["id"])
 def handle_data(self,z):
  if self.intitle:self.title.append(z)
 def handle_endtag(self,t):
  if t=="title":self.intitle=False
def parse(s):p=Parser();p.feed(s);return p
results=[]
for slug,(keywords,links) in CASES.items():
 path=Path("site/things-to-do")/(slug+"-cruise-port-day-trip")/"index.html"
 current=path.read_text("utf-8")
 old=subprocess.check_output(["git","show",BASE+":"+str(path)],text=True)
 a,b=parse(current),parse(old)
 panel=current[current.index('id="nf-v177-'+slug+'"'):][:7200].replace("&amp;","&")
 checks={
  "official_operating_facts":all(k in panel for k in keywords),
  "three_matching_provider_urls":all(u in panel for u in links),
  "exact_booking_terms_return_actions":all(panel.count('data-nf-v177-action="'+x+'"')==1 for x in ("ticket","conditions","return")),
  "unique_new_panel":a.ids.count("nf-v177-"+slug)==1,
  "original_image_source_credit_dimensions":a.images==b.images,
  "unchanged_title_meta_canonical_H1":a.title==b.title and a.meta==b.meta and a.canonical==b.canonical and a.h1==b.h1==1,
  "all_old_links_preserved":Counter(a.links)>=Counter(b.links) if slug=="sendai" else set(b.links).issubset(set(a.links)),
  "all_old_DOM_IDs_preserved":set(b.ids).issubset(set(a.ids)) and len(a.ids)==len(set(a.ids)),
  "licensed_image_attribution_preserved":all(url in a.links for url in b.links if "creativecommons.org" in url or "commons.wikimedia.org" in url),
  "responsive_52px_buttons":'id="nf-v177-official-style"' in current and "min-height:52px" in current and "@media(max-width:630px)" in current,
  "misleading_portal_booking_CTA_corrected":slug=="sendai" or ("입장·예약 운영기관 안내 확인 ↗" not in current)
 }
 passed=all(checks.values());print("PASS" if passed else "FAIL",slug,checks,flush=True);results.append({"slug":slug,"pass":passed,"checks":checks})
try:
 original_sitemap=subprocess.check_output(["git","show",BASE+":site/sitemap.xml"],text=True)
 sitemap_unchanged=original_sitemap==Path("site/sitemap.xml").read_text("utf-8")
except Exception as exc:sitemap_unchanged=False;print("sitemap ERROR",str(exc))
results.append({"slug":"sitemap","pass":sitemap_unchanged})
out=Path("audit-output/v177");out.mkdir(parents=True,exist_ok=True)
report={"version":"V177","existing_pages":4,"new_articles":0,"checks":results,"passed":all(x["pass"] for x in results)}
(out/"source.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print("SUMMARY",sum(x["pass"] for x in results),"/",len(results))
if not report["passed"]:sys.exit(1)
