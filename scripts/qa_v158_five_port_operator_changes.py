#!/usr/bin/env python3
"""V158 5 existing port pages, no new articles. Verify source-backed
changed docking/transport details AND all original photos, copyright, SEO.
"""
from html.parser import HTMLParser
from pathlib import Path
from collections import Counter
import subprocess,json,re,xml.etree.ElementTree as ET
BASE=Path("site")
D={
 "kochi":{"sources":["https://www.pref.kochi.lg.jp/doc/kochi_cruise/","https://www.princesscruises.jp/pdf/ports_shuttlebus.pdf"],"facts":["7-3안벽","7-2안벽","10월 24일","귀선"]},
 "matsuyama":{"sources":["https://www.city.matsuyama.ehime.jp/shisei/keikaku/kanko/cruisezyoho.html","https://www.princesscruises.jp/pdf/ports_shuttlebus.pdf","https://dogo.jp/"],"facts":["제1부두","2호안벽","유료","미쓰역","귀선"]},
 "niigata":{"sources":["https://www.niigata-airport.gr.jp/access/liner/sado/?lang=ko","https://www.sadokisen.co.jp/"],"facts":["10월 25일","15:30","16:15","13명","현금"]},
 "hiroshima":{"sources":["https://hiroshima-minato.jp/enaccessitsukaichi/","https://jr-miyajimaferry.co.jp/","https://jr-miyajimaferry.co.jp/timetable/"],"facts":["10월 24일","일반 시간표","증편","이쓰카이치","귀선"]},
 "kobe":{"sources":["https://www.city.kobe.lg.jp/a14075/kanko/leisure/harbor/passenger/schedule/index.html","https://www.city.kobe.lg.jp/a14075/kanko/leisure/harbor/passenger/terminal/index.html"],"facts":["4Q","4O","NAKA","포트라이너","귀선"]}
}
class P(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.links=[];self.img=[];self.ids=[];self.can=[];self.desc=[];self.titles=[];self.intitle=False
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="h1":self.h1+=1
  if tag=="a":self.links.append(a.get("href",""))
  if tag=="img":self.img.append((a.get("src",""),a.get("alt",""),a.get("width"),a.get("height")))
  if "id" in a:self.ids.append(a["id"])
  if tag=="link" and a.get("rel")=="canonical":self.can.append(a.get("href",""))
  if tag=="meta" and a.get("name")=="description":self.desc.append(a.get("content",""))
  if tag=="title":self.intitle=True
 def handle_data(self,t):
  if self.intitle:self.titles.append(t)
 def handle_endtag(self,t):
  if t=="title":self.intitle=False
def parse(s):
 p=P();p.feed(s);return p
def origin(path):return subprocess.check_output(["git","show","origin/main:"+str(path)],text=True)
bad=[];results=[]
for slug,v in D.items():
 path=BASE/"things-to-do"/(slug+"-cruise-port-day-trip")/"index.html"
 s=path.read_text("utf-8");prev=origin(path)
 p,q=parse(s),parse(prev)
 start=s.find('id="nf-v158-'+slug+'"')
 frag=s[start:start+8800] if start>=0 else ""
 oldid="v70-port-official" if slug=="hiroshima" else "v69-berth-qa"
 checks={
  "new_panel_once":p.ids.count("nf-v158-"+slug)==1,
  "three_official_source_cards":frag.count('class="nf-v158-step"')==3,
  "operator_links":all(u in p.links for u in v["sources"]),
  "real_date_or_berth_conditions":all(x in frag for x in v["facts"]),
  "source_links_safe":all('rel="noopener noreferrer"' in z for z in re.findall(r'<a[^>]+href="https?[^"]+"[^>]*>',frag)),
  "original_relevant_port_section":p.ids.count(oldid)==q.ids.count(oldid)==1,
  "new_action_above_old_details":start>=0 and start<s.index('id="'+oldid+'"'),
  "original_image_src_alt_dimensions_same":p.img==q.img,
  "original_local_photo_files":all((BASE/src.lstrip("/").split("?")[0]).is_file() for src,alt,w,h in p.img if src.startswith("/") and not src.startswith("//")),
  "photo_license_citations_retained":all(x in p.links for x in q.links if "commons.wikimedia.org" in x or "creativecommons.org" in x),
  "all_original_link_destinations_retained":Counter(p.links)>=Counter(q.links),
  "new_links_just_four":len(p.links)==len(q.links)+4,
  "h1_canonical_meta_title_original":p.h1==q.h1==1 and p.can==q.can==["https://www.nipponferry.com/things-to-do/"+slug+"-cruise-port-day-trip/"] and p.desc==q.desc and p.titles==q.titles,
  "no_duplicate_dom_ids":len(p.ids)==len(set(p.ids)),
  "mobile_52px_tap_targets":'id="nf-v158-guides-style"' in s and '@media(max-width:620px)' in s and "min-height:52px" in s,
  "no_fake_booking_or_shuttle_guarantee":not any(x in frag for x in ["잔여석 실시간 확정","예약 완료 보장","무료 셔틀 확정 운행"])
 }
 for k,ok in checks.items():
  if not ok:bad.append(slug+":"+k)
 results.append({"slug":slug,"pass":all(checks.values()),"checks":checks})
 print("PASS" if all(checks.values()) else "FAIL",slug,[k for k,v in checks.items() if not v],flush=True)
sitemap=BASE/"sitemap.xml";newxml=sitemap.read_text("utf-8")
if newxml!=origin(sitemap):bad.append("sitemap_modified")
index=[z.find("{*}loc").text for z in ET.fromstring(newxml).findall("{*}url")]
if not all("https://www.nipponferry.com/things-to-do/"+s+"-cruise-port-day-trip/" in index for s in D):bad.append("five_original_indexed_urls_missing")
out=Path("audit-output/v158");out.mkdir(parents=True,exist_ok=True)
(out/"five-actual-operating-changes.json").write_text(json.dumps({"new_posts":0,"existing_pages":5,"images_replaced":0,"private_ga4_gsc_not_checked":True,"failures":bad,"details":results},ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",sum(x["pass"] for x in results),"/5","errors",len(bad),flush=True)
if bad:raise SystemExit(1)
