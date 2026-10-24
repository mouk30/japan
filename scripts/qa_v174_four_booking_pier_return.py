#!/usr/bin/env python3
"""V174 source regression vs pre-V174 immutable Git SHA."""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
import subprocess,json,sys
BASE="e5e30a58e608e9445a62dd4e3c6f4f86dc67a729"
D={
"yokohama":(["15명","045-662-6125","50%","피어 아카렌가"],["yokohama-cruising.jp/rouge/reservation/","yokohama-cruising.jp/operation/","yokohama-cruising.jp/rouge/access/"]),
"kanazawa":(["10월 19일~30일","오전 9시","e-tix","오하마 부두"],["kanazawa21.jp/data_list.php?d=1&g=120","asoview.com/channel/ticket/TEPUUS2F0o/ticket0000057382/","hokutetsu.co.jp/route-bus/timetable/"]),
"akita":(["무료","20:50","115","2026년 10월 1일"],["selion-akita.com/facility/","akita-chuoukotsu.co.jp/news.php","faq.snf.jp/"]),
"kushiro":(["10월 31일","10,000엔","2명","서항 제4부두"],["mizu-no-kamuy.com/reservation/form/28","ja.kushiro-lakeakan.com/things_to_do/14182/","city.kushiro.lg.jp/sangyou/umisora/1006541/1006598/1012111.html"])
}
class H(HTMLParser):
 def __init__(self):super().__init__();self.intitle=False;self.title=[];self.h1=0;self.meta=[];self.canonical=[];self.img=[];self.links=[];self.ids=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="title":self.intitle=True
  if tag=="h1":self.h1+=1
  if tag=="meta":self.meta.append((a.get("name",""),a.get("property",""),a.get("content","")))
  if tag=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href",""))
  if tag=="img":self.img.append(tuple(a.get(z,"") for z in ("src","alt","width","height")))
  if tag=="a":self.links.append(a.get("href",""))
  if "id" in a:self.ids.append(a["id"])
 def handle_data(self,z):
  if self.intitle:self.title.append(z)
 def handle_endtag(self,tag):
  if tag=="title":self.intitle=False
def p(s):h=H();h.feed(s);return h
results=[]
for slug,(keywords,links) in D.items():
 path=Path("site/things-to-do")/(slug+"-cruise-port-day-trip")/"index.html"
 now=path.read_text("utf-8");old=subprocess.check_output(["git","show",BASE+":"+str(path)],text=True);a,b=p(now),p(old)
 block=now[now.index('id="nf-v174-'+slug+'"'):][:7000]
 checks={
 "source_claims":all(k in block for k in keywords),
 "three_specific_operator_links":all(x in block for x in links),
 "exact_intent_links":all(block.count('data-nf-v174-action="'+x+'"')==1 for x in ("booking","conditions","return")),
 "one_panel":a.ids.count("nf-v174-"+slug)==1,
 "images_unchanged":a.img==b.img,
 "existing_hrefs_unchanged":Counter(a.links)>=Counter(b.links),
 "seo_title_H1_meta_canonical_unchanged":a.title==b.title and a.h1==b.h1==1 and a.meta==b.meta and a.canonical==b.canonical,
 "old_dom_ids_preserved":set(b.ids).issubset(a.ids) and len(a.ids)==len(set(a.ids)),
 "old_photo_license_preserved":all(x in a.links for x in b.links if "commons.wikimedia.org" in x or "creativecommons.org" in x),
 "responsive_CTA":'id="nf-v174-official-tickets-style"' in now and 'min-height:52px' in now and '@media(max-width:630px)' in now,
 }
 passed=all(checks.values());results.append({"slug":slug,"passed":passed,"checks":checks});print("PASS" if passed else "FAIL",slug,checks,flush=True)
 try:
  sm=subprocess.check_output(["git","show",BASE+":site/sitemap.xml"],text=True)==Path("site/sitemap.xml").read_text("utf-8")
 except Exception:sm=False
 if not sm:results.append({"slug":"sitemap","passed":False})
out=Path("audit-output/v174");out.mkdir(parents=True,exist_ok=True)
report={"version":"V174","existing_pages":4,"new_posts":0,"rows":results,"passed":all(r["passed"] for r in results)}
(out/"source.json").write_text(json.dumps(report,indent=2,ensure_ascii=False));print("SUMMARY",sum(x["passed"] for x in results),"/",len(results))
if not report["passed"]:sys.exit(1)
