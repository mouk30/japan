#!/usr/bin/env python3
"""V173 source regression: preserve SEO, original photos, and all existing links for 4 port pages."""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
import sys, subprocess,json
BASE="0573ee3d36ef5c23e0e697ece16843593a9a5b55"
D={
"beppu":(["2,400엔","교환권","第4","마지막"] if False else ["2,400엔","교환권","가메노이버스","귀선"],["www.beppu-jigoku.com/fee/index.html","l-tike.com/order/?gLcode=84767","kamenoibus.com/scheduled_howto/"]),
"otaru":(["一般" ] if False else ["60일 전","1시간 전","중앙교","5-4"],["book.otaru.cc/products/1ebc1dee-2e41-5a6e-b866-dd1e1df95281","otaru.cc/standardv2/","otaru.cc/timetable/"]),
"shimizu":(["미호","현금만","16:35","16:50"],["www.shimizu-cruise.co.jp/fare/","www.shimizu-cruise.co.jp/access/"]),
"hiroshima":(["교통IC카드","20:30","15분 전","100엔"],["jr-miyajimaferry.co.jp/access/","www.aqua-net-h.co.jp/miyajimaguchi/reservation/","www.city.hatsukaichi.hiroshima.jp/soshiki/9/108494.html"])
}
class H(HTMLParser):
 def __init__(self):super().__init__();self.title=[];self.intitle=False;self.meta=[];self.canon=[];self.links=[];self.img=[];self.ids=[];self.h1=0
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=="title":self.intitle=True
  if t=="h1":self.h1+=1
  if t=="img":self.img.append(tuple(d.get(k,"") for k in ("src","alt","width","height")))
  if t=="a":self.links.append(d.get("href",""))
  if t=="link" and d.get("rel")=="canonical":self.canon.append(d.get("href",""))
  if t=="meta":self.meta.append((d.get("name",""),d.get("property",""),d.get("content","")))
  if "id" in d:self.ids.append(d["id"])
 def handle_data(self,s):
  if self.intitle:self.title.append(s)
 def handle_endtag(self,t):
  if t=="title":self.intitle=False
def parse(s):h=H();h.feed(s);return h
rows=[]
for slug,(claims,sources) in D.items():
 p=Path("site/things-to-do")/(slug+"-cruise-port-day-trip")/"index.html"
 now=p.read_text("utf-8");old=subprocess.check_output(["git","show",BASE+":"+str(p)],text=True)
 a,b=parse(now),parse(old)
 sec=now[now.index('id="nf-v173-'+slug+'"'):]
 sec=sec[:8000]
 checks={
  "one_correct_panel":a.ids.count("nf-v173-"+slug)==1,
  "exact_three_booking_transport_return_buttons":all(sec.count('data-nf-v173-action="'+v+'"')==1 for v in ("ticket","conditions","return")),
  "verified_content":all(x in sec for x in claims),
  "source_outgoing_links":all(x in sec for x in sources),
  "original_image_src_alt_width_height":a.img==b.img,
  "original_SEO_title_description_canonical_h1":a.title==b.title and a.canon==b.canon and a.h1==b.h1==1 and (a.meta==b.meta if slug!="otaru" else [(x[0],x[1]) for x in a.meta]==[(x[0],x[1]) for x in b.meta]),
  "all_prior_hrefs_preserved":Counter(a.links)>=Counter(b.links),
  "all_prior_DOM_ids_preserved":set(b.ids).issubset(set(a.ids)) and len(set(a.ids))==len(a.ids),
  "licensed_original_still_linked":all(x in a.links for x in b.links if "commons.wikimedia.org" in x or "creativecommons.org" in x),
  "responsive_buttons":'nf-v173-booking-path-style' in now and "min-height:52px" in now and "@media(max-width:630px)" in now
 }
 if slug=="otaru": checks["false_AI_caption_and_OG_corrected"]=("AI 생성 참고 이미지" not in now and "2009년 2월 촬영된 실제" in now)
 ok=all(checks.values());rows.append({"slug":slug,"ok":ok,"checks":checks})
 print("PASS" if ok else "FAIL",slug,checks,flush=True)
 try:
  origsm=subprocess.check_output(["git","show",BASE+":site/sitemap.xml"],text=True)
  if origsm!=Path("site/sitemap.xml").read_text("utf-8"): rows.append({"slug":"sitemap","ok":False})
 except Exception as e:rows.append({"slug":"sitemap","ok":False,"error":str(e)})
out=Path("audit-output/v173");out.mkdir(parents=True,exist_ok=True)
report={"version":"V173","original_guides":4,"new_articles":0,"rows":rows,"pass":all(x["ok"] for x in rows)}
(out/"source.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
print("SUMMARY",sum(x["ok"] for x in rows),"/",len(rows),flush=True)
if not report["pass"]:sys.exit(1)
