#!/usr/bin/env python3
"""V176 existing 4 guides, official bookings and immutable SEO source regression."""
from pathlib import Path
from html.parser import HTMLParser
import json, subprocess, sys
BASE="dd2698b6b80a8b3641602aa6ac14013736624491"
CASES={
 "tomakomai":(["서항","이리후네","12월 29일","30번"],["city.tomakomai.hokkaido.jp/kankojoho/cruise/kita_irifunefuto.html","city.tomakomai.hokkaido.jp/shizen/sonotanoshisetsu/utonai/access.html","michinoeki-utonaiko.com/"]),
 "nanao":(["20:30","500엔","매월 25일","오타 부두"],["wakura.or.jp/brochure/brochure-660-2/","mlit.go.jp/kankocho/cruise/detail/023/index.html"]),
 "miyazaki":(["4일 전","2개월 전","국제관광선","아오시마"],["booking.miyazakicarferry.com/","miyazakicarferry.com/booking/web/","miyakoh.co.jp/rosen/timetable-rosen.html"]),
 "imabari":(["520엔","420엔","제1잔교","16:30"],["city.imabari.ehime.jp/museum/imabarijo/info/","city.imabari.ehime.jp/kouwan/imabari/imabari.html","geiyokisen.com/"])
}
class Reader(HTMLParser):
 def __init__(self):super().__init__();self.intitle=False;self.title=[];self.h1=0;self.meta=[];self.canon=[];self.images=[];self.hrefs=[];self.ids=[]
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if t=="title":self.intitle=True
  if t=="h1":self.h1+=1
  if t=="img":self.images.append(tuple(d.get(k,"") for k in ("src","alt","width","height","onerror")))
  if t=="meta":self.meta.append((d.get("name",""),d.get("property",""),d.get("content","")))
  if t=="link" and d.get("rel")=="canonical":self.canon.append(d.get("href",""))
  if t=="a":self.hrefs.append(d.get("href",""))
  if "id" in d:self.ids.append(d["id"])
 def handle_data(self,data):
  if self.intitle:self.title.append(data)
 def handle_endtag(self,t):
  if t=="title":self.intitle=False
def parse(s):p=Reader();p.feed(s);return p
rows=[]
for slug,(keywords,links) in CASES.items():
 path=Path("site/things-to-do")/(slug+"-cruise-port-day-trip")/"index.html"
 old=subprocess.check_output(["git","show",BASE+":"+str(path)],text=True)
 current=path.read_text("utf-8");a,b=parse(current),parse(old)
 section=current[current.index('id="nf-v176-'+slug+'"'):][:7800].replace("&amp;","&")
 checks={
  "claims_from_official_sources":all(k in section for k in keywords),
  "specific_outbound_provider_links":all(link in section for link in links),
  "three_valid_actions":all(section.count('data-nf-v176-action="'+key+'"')==1 for key in ("booking","conditions","return")),
  "one_new_operational_panel":a.ids.count("nf-v176-"+slug)==1,
  "all_old_photo_src_alt_dimensions":a.images==b.images,
  "old_photo_rights_link_preserved":all(x in a.hrefs for x in b.hrefs if "commons.wikimedia.org" in x or "creativecommons.org" in x),
  "SEO_title_meta_canonical_h1_identical":a.title==b.title and a.meta==b.meta and a.canon==b.canon and a.h1==b.h1==1,
  "all_original_links_kept":set(b.hrefs).issubset(set(a.hrefs)),
  "all_original_DOM_IDs_kept":set(b.ids).issubset(set(a.ids)) and len(a.ids)==len(set(a.ids)),
  "responsive_CTA_min_52px":'id="nf-v176-official-style"' in current and "min-height:52px" in current and "@media(max-width:630px)" in current,
  "no_misleading_generic_facility_CTA":slug not in ("nanao","imabari") or "입장·예약 운영기관 안내 확인 ↗" not in current
 }
 ok=all(checks.values());rows.append({"slug":slug,"pass":ok,"checks":checks});print("PASS" if ok else "FAIL",slug,checks,flush=True)
unchanged_sitemap=subprocess.check_output(["git","show",BASE+":site/sitemap.xml"],text=True)==Path("site/sitemap.xml").read_text("utf-8")
rows.append({"slug":"sitemap","pass":unchanged_sitemap})
out=Path("audit-output/v176");out.mkdir(parents=True,exist_ok=True)
report={"version":"V176","existing_pages":4,"new_posts":0,"checks":rows,"success":all(r["pass"] for r in rows)}
(out/"source.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print("SUMMARY",sum(x["pass"] for x in rows),"/",len(rows))
if not report["success"]:sys.exit(1)
