#!/usr/bin/env python3
"""V178 immutable original assets, official booking states and berth return QA."""
from pathlib import Path
from html.parser import HTMLParser
import json,subprocess,sys
BASE="1a5dd767bd4de68ef6b45ca072933883056ef30b"
DATA={
"ofunato":(["2,500엔","2명 이상","전날까지","노노다부두"],["goishi.info/anatoshisen/","city.ofunato.iwate.jp/archive/p20260210145238"]),
"tsuruga":(["400엔","100엔","16:30","북안벽"],["tsuruga-akarenga.jp/modules/info/index.php?action=PageView&page_id=5","ticket.rakuten.co.jp/event/event-other/rtvg096/","tsurugaport.jp/category/news/"]),
"sakaiminato":(["JTB","1,000엔","16:30","10월 26일"],["jtb.co.jp/leisure/fp/qKS008605/","mizuki.sakaiminato.net/information/","sakai-tottori.jp/archives/3375"]),
"shimonoseki":(["10월 23일","일시 중단","083-224-3000","support@kampuferry.co.jp"],["kampuferry.co.jp/news/20261023systemmaintenance.html","mlit.go.jp/kankocho/cruise/jp/detail/047/index.html"])
}
class HTML(HTMLParser):
 def __init__(self):super().__init__();self.title=[];self.in_title=False;self.h1=0;self.meta=[];self.canonical=[];self.imgs=[];self.href=[];self.ids=[]
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if t=="title":self.in_title=True
  if t=="h1":self.h1+=1
  if t=="meta":self.meta.append((d.get("name",""),d.get("property",""),d.get("content","")))
  if t=="link" and d.get("rel")=="canonical":self.canonical.append(d.get("href",""))
  if t=="img":self.imgs.append(tuple(d.get(k,"") for k in ("src","alt","width","height","onerror")))
  if t=="a":self.href.append(d.get("href",""))
  if "id" in d:self.ids.append(d["id"])
 def handle_data(self,s):
  if self.in_title:self.title.append(s)
 def handle_endtag(self,t):
  if t=="title":self.in_title=False
def read(s):o=HTML();o.feed(s);return o
rows=[]
for slug,(keywords,links) in DATA.items():
 path=Path("site/things-to-do")/(slug+"-cruise-port-day-trip")/"index.html"
 old=subprocess.check_output(["git","show",BASE+":"+str(path)],text=True)
 now=path.read_text(encoding="utf-8");a,b=read(now),read(old)
 block=now[now.index('id="nf-v178-'+slug+'"'):][:7300].replace("&amp;","&")
 tests={
 "official_claims":all(t in block for t in keywords),
 "operator_direct_links":all(t in block for t in links),
 "three_purpose_actions":all(block.count('data-nf-v178-action="'+q+'"')==1 for q in ("ticket","conditions","return")),
 "single_panel":a.ids.count("nf-v178-"+slug)==1,
 "original_images_untouched":a.imgs==b.imgs,
 "original_links_preserved":set(b.href).issubset(set(a.href)),
 "seo_title_meta_canonical_and_h1":a.title==b.title and a.meta==b.meta and a.canonical==b.canonical and a.h1==b.h1==1,
 "original_ids_preserved":set(b.ids).issubset(set(a.ids)) and len(a.ids)==len(set(a.ids)),
 "photo_attribution_and_ai_disclosure":all(x in a.href for x in b.href if "creativecommons.org" in x or "commons.wikimedia.org" in x) and ("AI 생성 참고 이미지" in now)==("AI 생성 참고 이미지" in old),
 "mobile_52px_cta":'id="nf-v178-style"' in now and 'min-height:52px' in now and '@media(max-width:630px)' in now,
 "bad_old_booking_portal_fixed":slug not in ("ofunato","tsuruga") or "입장·예약 운영기관 안내 확인 ↗" not in now
 }
 passed=all(tests.values());rows.append({"slug":slug,"pass":passed,"checks":tests});print("PASS" if passed else "FAIL",slug,tests,flush=True)
try:same=Path("site/sitemap.xml").read_text("utf-8")==subprocess.check_output(["git","show",BASE+":site/sitemap.xml"],text=True)
except Exception:same=False
rows.append({"slug":"sitemap","pass":same})
out=Path("audit-output/v178");out.mkdir(parents=True,exist_ok=True)
result={"version":"V178","pages":4,"new_posts":0,"checks":rows,"passed":all(r["pass"] for r in rows)}
(out/"source.json").write_text(json.dumps(result,indent=2,ensure_ascii=False))
print("SUMMARY",sum(r["pass"] for r in rows),"/",len(rows))
if not result["passed"]:sys.exit(1)
