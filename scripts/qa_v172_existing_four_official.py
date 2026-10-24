#!/usr/bin/env python3
"""V172 original 4 port guide source audit: explicit 2026 fact references and immutable photos/SEO."""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
import subprocess,json,sys,xml.etree.ElementTree as ET
BASE="9ecde5f83cba67c6b64c401137eef4760b63d9f3"
S={
"kure":(["운항일 2일 전","구레 중앙잔교","2026년 4월 23일"],["bunker-supply.com/service/sightseeing_cruise/","yamato-museum.com"]),
"fukuyama":(["2026년 10월 16일","240엔","고시키이와","084-982-2115"],["city.fukuyama.hiroshima.jp/soshiki/kanko/91534.html","city.fukuyama.hiroshima.jp/site/miryoku2023/287776.html"]),
"sakaide":(["하야시다 A호","2024년 12월 17일","마지막 입장 16:30"],["city.sakaide.lg.jp/soshiki/kouwanka/cruise.html","city.sakaide.lg.jp/soshiki/sangyoukankou/kinenkouen.html"]),
"maizuru":(["서항 제2부두","마에지마부두","10월 운행일은 18일과 25일","출항 30분 전"],["city.maizuru.kyoto.jp/kankou/0000014705.html","city.maizuru.kyoto.jp/kankou/0000015405.html","snf.jp/guide/embark/maizuru/"])
}
class P(HTMLParser):
 def __init__(self):super().__init__();self.title=[];self.intitle=False;self.h1=0;self.meta=[];self.links=[];self.img=[];self.canon=[];self.ids=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=="title":self.intitle=True
  if t=="h1":self.h1+=1
  if t=="img":self.img.append(tuple(a.get(k,"") for k in ("src","alt","width","height")))
  if t=="a":self.links.append(a.get("href",""))
  if t=="link" and a.get("rel")=="canonical":self.canon.append(a.get("href",""))
  if t=="meta":self.meta.append(tuple(a.get(k,"") for k in ("name","property","content")))
  if "id" in a:self.ids.append(a["id"])
 def handle_data(self,s):
  if self.intitle:self.title.append(s)
 def handle_endtag(self,t):
  if t=="title":self.intitle=False
def p(s):x=P();x.feed(s);return x
rows=[]
for slug,(claims,links) in S.items():
 path=Path("site/things-to-do")/(slug+"-cruise-port-day-trip")/"index.html"
 now=path.read_text("utf-8");old=subprocess.check_output(["git","show",BASE+":"+str(path)],text=True)
 a,b=p(now),p(old);sec=now[now.index('id="nf-v172-official-'+slug+'"'):][:5000]
 test={
 "single_version_panel":a.ids.count("nf-v172-official-"+slug)==1,
 "all_operational_claims":all(x in sec for x in claims),
 "all_official_links":all(x in sec for x in links),
 "three_usable_original_links":sec.count('class="nf-v172-card"')==3 and sec.count('data-nf-v172-action=')==3,
 "original_photo_src_alt_dimensions":a.img==b.img,
 "original_photo_license_links":all(x in a.links for x in b.links if "commons.wikimedia.org" in x or "creativecommons.org" in x),
 "original_all_links_preserved":Counter(a.links)>=Counter(b.links),
 "original_meta_canonical_title_H1":a.title==b.title and a.meta==b.meta and a.canon==b.canon and a.h1==b.h1==1,
 "all_original_DOM_ids_unchanged":set(a.ids)-{"nf-v172-official-"+slug}==set(b.ids) and len(a.ids)==len(set(a.ids)),
 "responsive_tall_CTA":"nf-v172-verified-boarding-return-style" in now and "min-height:52px" in now and "@media(max-width:630px)" in now
 }
 passed=all(test.values());rows.append({"slug":slug,"pass":passed,"checks":test});print("PASS" if passed else "FAIL",slug,test,flush=True)
 original_sm=subprocess.check_output(["git","show",BASE+":site/sitemap.xml"],text=True)
 if original_sm!=Path("site/sitemap.xml").read_text("utf-8"):rows.append({"slug":"sitemap","pass":False})
out=Path("audit-output/v172");out.mkdir(parents=True,exist_ok=True)
rep={"version":"V172","pages":4,"new_articles":0,"source_checked":True,"rows":rows,"passed":all(r["pass"] for r in rows)}
(out/"source.json").write_text(json.dumps(rep,ensure_ascii=False,indent=2))
print("SUMMARY",sum(r["pass"] for r in rows),"/",len(rows))
if not rep["passed"]:sys.exit(1)
