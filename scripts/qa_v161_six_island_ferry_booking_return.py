#!/usr/bin/env python3
"""V161: preserve original cruise port guides while adding genuine
2026-10-24 Tokai Kisen typhoon fee waiver, 10/9-28 replacement service,
official booking and final ship/boarding port decision.
NOTE: Tokai Kisen island ferry policy != third party ocean cruise operation.
"""
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
import subprocess,json,re,xml.etree.ElementTree as ET

BASE="30ebb5e65bd7c9d7aaffeab1dfaf60732821ed4d"
ROOT=Path("site")
S={
 "tokyo":{"official":["https://www.tokaikisen.co.jp/news/836684/","https://www.tokaikisenyoyaku.com/app/web-front/precautions","https://www.tokaikisen.co.jp/schedule/"],
          "facts":["10월 25일","10월 27일","다케시바","귀선"]},
 "okata-izu-oshima":{"official":["https://www.tokaikisen.co.jp/schedule/","https://www.tokaikisen.co.jp/news/836684/","https://www.tokaikisen.co.jp/contact/"],
          "facts":["오카타","모토마치","04992-2-5522","귀선"]},
 "niijima":{"official":["https://www.tokaikisen.co.jp/news/826444/","https://www.tokaikisenyoyaku.com/app/web-front/precautions","https://www.tokaikisen.co.jp/schedule/"],
          "facts":["10월 9~28일","니지마","흑근","귀선"]},
 "kozushima":{"official":["https://www.tokaikisen.co.jp/news/826444/","https://www.tokaikisen.co.jp/news/836684/","https://www.tokaikisen.co.jp/schedule/"],
          "facts":["10월 9~28일","마에하마","04992-8-1111","귀선"]},
 "miike-miyakejima":{"official":["https://www.tokaikisen.co.jp/news/826444/","https://www.tokaikisen.co.jp/news/836684/","https://www.tokaikisen.co.jp/schedule/"],
          "facts":["미이케항","사비가하마","이케야항","04994-5-0221","귀선"]},
 "kaminato-hachijojima":{"official":["https://www.tokaikisen.co.jp/news/826444/","https://www.tokaikisen.co.jp/news/836684/","https://www.tokaikisen.co.jp/schedule/"],
          "facts":["소코도","야에네","04996-2-1211","귀선"]},
}
class Parse(HTMLParser):
 def __init__(self):
  super().__init__();self.ids=[];self.images=[];self.links=[];self.canon=[];self.descriptions=[];self.title=[];self.in_title=False;self.h1=0
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if "id" in d:self.ids.append(d["id"])
  if t=="img":self.images.append((d.get("src",""),d.get("alt",""),d.get("width",""),d.get("height","")))
  if t=="a":self.links.append(d.get("href",""))
  if t=="link" and d.get("rel")=="canonical":self.canon.append(d.get("href",""))
  if t=="meta" and d.get("name")=="description":self.descriptions.append(d.get("content",""))
  if t=="h1":self.h1+=1
  if t=="title":self.in_title=True
 def handle_data(self,d):
  if self.in_title:self.title.append(d)
 def handle_endtag(self,t):
  if t=="title":self.in_title=False
def parse(s):
 x=Parse();x.feed(s);return x
def from_base(p):
 return subprocess.check_output(["git","show",f"{BASE}:{p}"],text=True)
report=[];fail=[]
for slug,info in S.items():
 p=ROOT/"things-to-do"/f"{slug}-cruise-port-day-trip"/"index.html"
 body=p.read_text("utf-8");prev=from_base(p);a,b=parse(body),parse(prev)
 idval="nf-v161-"+slug
 pos=body.find('id="'+idval+'"')
 stop=body.find("</section>",pos)+len("</section>") if pos>=0 else -1
 frag=body[pos:stop] if stop>pos>=0 else ""
 oldguide=b.ids[0] if b.ids else ""
 checks={
  "one_v161_panel":a.ids.count(idval)==1,
  "placed_before_original_sections":oldguide in a.ids and 0<pos<body.find('id="'+oldguide+'"'),
  "three_action_cards":frag.count('class="nf-v161-item"')==3,
  "all_actual_operator_links":all(u in frag and u in a.links for u in info["official"]),
  "three_secure_external_links":frag.count('rel="noopener noreferrer"')==3 and frag.count('target="_blank"')==3,
  "date_and_return_facts":all(f in frag for f in info["facts"]),
  "original_photo_alt_size_unchanged":a.images==b.images,
  "original_webp_files_exist":all((ROOT/src.lstrip("/").split("?")[0]).is_file() for src,alt,w,h in a.images if src.startswith("/") and not src.startswith("//")),
  "photo_license_source_links_kept":all(u in a.links for u in b.links if "commons.wikimedia.org" in u or "creativecommons.org" in u),
  "existing_links_preserved":Counter(a.links)>=Counter(b.links),
  "three_new_links_not_new_pages":len(a.links)==len(b.links)+3,
  "SEO_title_meta_canonical_unchanged":a.title==b.title and a.descriptions==b.descriptions and a.canon==b.canon==["https://www.nipponferry.com/things-to-do/"+slug+"-cruise-port-day-trip/"] and a.h1==b.h1==1,
  "no_duplicate_ids":len(a.ids)==len(set(a.ids)),
  "mobile_52px_tap_target":'id="nf-v161-operator-css"' in body and '@media(max-width:620px)' in body and 'min-height:52px' in body,
  "no_blanket_cruise_cancel":'모든 크루즈선이 결항 확정' not in frag and '전편 결항 확정' not in frag and '예약확정 완료' not in frag
 }
 bad=[k for k,v in checks.items() if not v]
 row={"slug":slug,"pass":not bad,"tests":len(checks),"passed":len(checks)-len(bad),"failures":bad}
 report.append(row)
 fail.extend(slug+":"+reason for reason in bad)
 print(("PASS" if not bad else "FAIL"),slug,row["passed"],"/",row["tests"],bad,flush=True)
smap=ROOT/"sitemap.xml"
if smap.read_text("utf-8")!=from_base(smap):fail.append("sitemap_diff")
urls=[u.find("{*}loc").text for u in ET.fromstring(smap.read_text("utf-8")).findall("{*}url")]
for slug in S:
 if "https://www.nipponferry.com/things-to-do/"+slug+"-cruise-port-day-trip/" not in urls:fail.append(slug+":missing_original_sitemap")
out=Path("audit-output/v161");out.mkdir(parents=True,exist_ok=True)
(out/"six-existing-ports-operator-weather-booking-return.json").write_text(json.dumps({"date":"2026-10-24","new_articles":0,"existing_guides":6,"photos_replaced":0,"analytics_or_real_reservation_not_checked":True,"failures":fail,"results":report},ensure_ascii=False,indent=2),encoding="utf-8")
print("RESULT",len(report)-sum(not r["pass"] for r in report),"/",len(report),"failures",len(fail),flush=True)
if fail:raise SystemExit(1)
