#!/usr/bin/env python3
"""V180 retain original SEO/photography and verify official purchase/return panels on only four existing port pages."""
from pathlib import Path
from html.parser import HTMLParser
import subprocess,json,sys
BASE="9caa695884d7eeaf3b92a2dbc0687aede9cca61d"
DATA={
 "himeji":(["10월 31일","11월 1일","2,500엔","11월 25일"],["himeji-kanko.book.ntmg.jp/","city.himeji.lg.jp/castle/0000030310.html","himeji-port.com/enterportplan"]),
 "tokoname":(["1,500엔","5일 전","50%","센트레아"],["reserva.be/potteryguide","tokoname.wixsite.com/potterypath","mlit.go.jp/kankocho/cruise/detail/120/index.html"]),
 "onahama":(["1,850엔","6개월","1년","3·4호"],["asoview.com/item/ticket/ticket0000012060/","aquamarine.or.jp/guide/info/","mlit.go.jp/kankocho/cruise/jp/detail/097/index.html"]),
 "abashiri":(["990엔","1,500엔","2026년 10월 1일","제4부두"],["ryuhyokan.com/use/","kangoku.jp/info/visit","abashiribus.com/regular-sightseeing-bus/"])
}
class R(HTMLParser):
 def __init__(self):super().__init__();self.in_title=False;self.title=[];self.h1=0;self.meta=[];self.canon=[];self.images=[];self.links=[];self.ids=[]
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if t=="title":self.in_title=True
  if t=="h1":self.h1+=1
  if t=="meta":self.meta.append((d.get("name",""),d.get("property",""),d.get("content","")))
  if t=="link" and d.get("rel")=="canonical":self.canon.append(d.get("href",""))
  if t=="img":self.images.append(tuple(d.get(k,"") for k in ("src","alt","width","height","onerror")))
  if t=="a":self.links.append(d.get("href",""))
  if "id" in d:self.ids.append(d["id"])
 def handle_data(self,s):
  if self.in_title:self.title.append(s)
 def handle_endtag(self,t):
  if t=="title":self.in_title=False
def parse(s):p=R();p.feed(s);return p
out=Path("audit-output/v180");out.mkdir(parents=True,exist_ok=True)
rows=[]
for slug,(words,urls) in DATA.items():
 p=Path("site/things-to-do")/(slug+"-cruise-port-day-trip")/"index.html"
 prev=subprocess.check_output(["git","show",BASE+":"+str(p)],text=True)
 now=p.read_text("utf-8");a,b=parse(now),parse(prev)
 block=now[now.index('id="nf-v180-'+slug+'"'):][:8600].replace("&amp;","&")
 tests={
  "new_claims_in_panel":all(w in block for w in words),
  "official_providers_linked":all(u in block for u in urls),
  "three_separate_links":all(block.count('data-nf-v180-action="'+x+'"')==1 for x in ("ticket","conditions","return")),
  "one_current_panel":a.ids.count("nf-v180-"+slug)==1,
  "no_original_image_changed":a.images==b.images,
  "all_original_metadata_and_h1":a.title==b.title and a.h1==b.h1==1 and a.meta==b.meta and a.canon==b.canon,
  "original_links_remain":set(b.links).issubset(set(a.links)),
  "original_ids_unique_and_retained":set(b.ids).issubset(set(a.ids)) and len(a.ids)==len(set(a.ids)),
  "licensed_photo_or_ai_disclosure":all(x in a.links for x in b.links if "commons.wikimedia.org" in x or "creativecommons.org" in x) and (("AI 생성" in prev)==("AI 생성" in now)),
  "52px_cta_responsive":'id="nf-v180-style"' in now and 'min-height:52px' in now and '@media(max-width:630px)' in now,
  "old_misleading_booking_cta_replaced":"입장·예약 운영기관 안내 확인 ↗" not in now
 }
 ok=all(tests.values());rows.append({"slug":slug,"pass":ok,"checks":tests});print("PASS" if ok else "FAIL",slug,tests,flush=True)
try:unchanged=Path("site/sitemap.xml").read_text("utf-8")==subprocess.check_output(["git","show",BASE+":site/sitemap.xml"],text=True)
except Exception as e:unchanged=False;print("sitemapERROR",e)
rows.append({"slug":"sitemap","pass":unchanged})
result={"version":"V180","existing_pages":4,"new_posts":0,"tests":rows,"passed":all(r["pass"] for r in rows)}
(out/"originals.json").write_text(json.dumps(result,ensure_ascii=False,indent=2))
print("SUMMARY",sum(x["pass"] for x in rows),"/",len(rows),flush=True)
if not result["passed"]:sys.exit(1)
