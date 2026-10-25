#!/usr/bin/env python3
"""V179 regression against immutable original SEO, photo licensing, original URLs."""
from pathlib import Path
from html.parser import HTMLParser
import json,subprocess,sys
BASE="730104fe844215e5f91f625a44d0e2d9d4c28915"
DATA={
 "nagoya":(["11월 30일","2,030엔","긴조부두","10월 31일"],["nagoyaaqua.jp/fee/","nagoyaaqua.jp/garden-pier/news2/porthouse/29959/","port-of-nagoya.jp/kanko/senpaku/1002548/index.html"]),
 "kumamoto":(["3시간 전","10분 전","1,600엔","유메사키지마"],["kumamotoferry.co.jp/reserve/","kumamotoferry.co.jp/timefare/","mlit.go.jp/kankocho/cruise/detail/089/index.html"]),
 "yatsushiro":(["임시 휴원","10월 21일","11월 18일","8km"],["pref.kumamoto.jp/soshiki/108/274730.html","kumamonport8246.com/cruise/","kinasse-yatsushiro.jp/news/detail/FAQ_kumamonport"]),
 "shingu":(["538","10월 28일","11월 3일","사노 3호"],["kumanohayatama.jp/access/","shinguu.jp/spots/detail/A0002","city.shingu.lg.jp/info/2891"])
}
class Doc(HTMLParser):
 def __init__(self):super().__init__();self.intitle=False;self.titles=[];self.h1=0;self.meta=[];self.canonical=[];self.images=[];self.hrefs=[];self.ids=[]
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if t=="title":self.intitle=True
  if t=="h1":self.h1+=1
  if t=="meta":self.meta.append((d.get("name",""),d.get("property",""),d.get("content","")))
  if t=="link" and d.get("rel")=="canonical":self.canonical.append(d.get("href",""))
  if t=="img":self.images.append(tuple(d.get(k,"") for k in ("src","alt","width","height","onerror")))
  if t=="a":self.hrefs.append(d.get("href",""))
  if "id" in d:self.ids.append(d["id"])
 def handle_data(self,s):
  if self.intitle:self.titles.append(s)
 def handle_endtag(self,t):
  if t=="title":self.intitle=False
def parse(s):p=Doc();p.feed(s);return p
rows=[]
for slug,(phrases,links) in DATA.items():
 p=Path("site/things-to-do")/(slug+"-cruise-port-day-trip")/"index.html"
 old=subprocess.check_output(["git","show",BASE+":"+str(p)],text=True)
 now=p.read_text("utf-8")
 a,b=parse(now),parse(old)
 panel=now[now.index('id="nf-v179-'+slug+'"'):][:8300].replace("&amp;","&")
 checks={
 "current_operator_conditions":all(x in panel for x in phrases),
 "actual_official_operator_urls":all(x in panel for x in links),
 "distinct_ticket_conditions_return_cta":all(panel.count('data-nf-v179-action="'+x+'"')==1 for x in ("ticket","conditions","return")),
 "new_guide_once":a.ids.count("nf-v179-"+slug)==1,
 "original_photo_unchanged":a.images==b.images,
 "existing_photo_license_attribution":all(h in a.hrefs for h in b.hrefs if "commons.wikimedia.org" in h or "creativecommons.org" in h),
 "original_title_meta_canonical_and_h1":a.titles==b.titles and a.meta==b.meta and a.canonical==b.canonical and a.h1==b.h1==1,
 "original_hrefs":set(b.hrefs).issubset(set(a.hrefs)),
 "original_ids":set(b.ids).issubset(set(a.ids)) and len(a.ids)==len(set(a.ids)),
 "responsive_52px_tap_targets":'id="nf-v179-official-style"' in now and 'min-height:52px' in now and '@media(max-width:630px)' in now,
 "misleading_portal_cta_removed":slug not in ("yatsushiro","shingu") or "입장·예약 운영기관 안내 확인 ↗" not in now
 }
 passed=all(checks.values());rows.append({"slug":slug,"passed":passed,"checks":checks})
 print("PASS" if passed else "FAIL",slug,checks,flush=True)
try:site_unchanged=Path("site/sitemap.xml").read_text("utf-8")==subprocess.check_output(["git","show",BASE+":site/sitemap.xml"],text=True)
except Exception:site_unchanged=False
rows.append({"slug":"sitemap","passed":site_unchanged})
out=Path("audit-output/v179");out.mkdir(parents=True,exist_ok=True)
report={"version":"V179","existing_pages":4,"new_posts":0,"checks":rows,"passed":all(r["passed"] for r in rows)}
(out/"source.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print("SUMMARY",sum(r["passed"] for r in rows),"/",len(rows))
if not report["passed"]:sys.exit(1)
