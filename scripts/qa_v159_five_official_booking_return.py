#!/usr/bin/env python3
"""V159: existing Japan cruise port operational / booking / last-return QA.
Compare every existing document with the known 2026-10-24 V158 baseline.
Preserve all images, source licences, metadata, and existing URLs.
"""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import json, re, subprocess, xml.etree.ElementTree as ET

ROOT = Path("site")
BASE = "c2b89eb78003d5730da3fa95864df88065127ce6"
CASES = {
 "shimizu": {
  "links": ["https://www.shimizu-port.jp/shipinfo_R08.html", "https://www.shimizu-cruise.co.jp/news/detail/934", "https://www.shimizu-cruise.co.jp/fare/"],
  "facts": ["2026년 11월 1일", "1,000엔", "500엔", "귀선"]},
 "osaka": {
  "links": ["https://www.city.osaka.lg.jp/port/page/0000442982.html", "https://www.kaiyukan.com/info/ticket/kaiyukan/", "https://www.city.osaka.lg.jp/port/page/0000002874.html"],
  "facts": ["SOLAS", "중앙돌제", "가이유칸", "사전신청", "귀선"]},
 "sasebo": {
  "links": ["https://www.city.sasebo.lg.jp/kouwan/koukanri/terminal-info.html", "https://english.huistenbosch.co.jp/ticket/?lang=ko", "https://www.city.sasebo.lg.jp/kouwan/cruise/cruise.html"],
  "facts": ["우라가시라", "요코우", "342-2", "1-42", "귀선"]},
 "sakaiminato": {
  "links": ["https://www.sakai-tottori.jp/archives/3375", "https://mizuki.sakaiminato.net/", "https://www.sakai-tottori.jp/"],
  "facts": ["10월 26일", "16:30", "JTB", "택시", "귀선"]},
 "otaru": {
  "links": ["https://www.city.otaru.lg.jp/docs/2020112000666/", "https://otaru.cc/standardv2/", "https://otaru.cc/timetable/"],
  "facts": ["제3부두", "가쓰나이", "60일", "1시간", "귀선"]}
}

class Inspector(HTMLParser):
 def __init__(self):
  super().__init__(); self.ids=[]; self.links=[]; self.img=[]; self.canon=[];self.desc=[];self.titles=[];self.in_title=False;self.h1=0
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if "id" in d: self.ids.append(d["id"])
  if t=="a": self.links.append(d.get("href",""))
  if t=="img": self.img.append((d.get("src"),d.get("alt"),d.get("width"),d.get("height")))
  if t=="link" and d.get("rel")=="canonical":self.canon.append(d.get("href",""))
  if t=="meta" and d.get("name")=="description":self.desc.append(d.get("content",""))
  if t=="title": self.in_title=True
  if t=="h1": self.h1+=1
 def handle_endtag(self,t):
  if t=="title": self.in_title=False
 def handle_data(self,s):
  if self.in_title:self.titles.append(s)

def parse(s):
 p=Inspector();p.feed(s);return p
def old(path):
 return subprocess.check_output(["git","show",f"{BASE}:{path}"],text=True)

fails=[]; results=[]
for slug, info in CASES.items():
 path = ROOT/"things-to-do"/(slug+"-cruise-port-day-trip")/"index.html"
 txt = path.read_text(encoding="utf-8")
 prev = old(path)
 p, q = parse(txt),parse(prev)
 marker = 'id="nf-v159-'+slug+'"'
 begin = txt.find(marker)
 finish = txt.find("</section>",begin) + len("</section>") if begin>=0 else -1
 fragment=txt[begin:finish] if begin>=0 and finish>begin else ""
 old_section = 'id="v73-verification"' if slug=="otaru" else 'id="v69-berth-qa"'
 checks = {
  "one_new_panel":p.ids.count("nf-v159-"+slug)==1,
  "three_real_actions":fragment.count('class="nf-v159-card"')==3,
  "placed_above_original_guide":begin>=0 and old_section in txt and begin < txt.index(old_section),
  "official_sources_direct":all(url in p.links and url in fragment for url in info["links"]),
  "source_backed_facts":all(f in fragment for f in info["facts"]),
  "new_links_open_securely":all('rel="noopener noreferrer"' in a and 'target="_blank"' in a for a in re.findall(r'<a\b[^>]+href="https?[^"]+"[^>]*>',fragment)),
  "photos_src_alt_size_unchanged":p.img==q.img,
  "all_local_images_present":all((ROOT/src.lstrip("/").split("?")[0]).is_file() for src,alt,w,h in p.img if src and src.startswith("/") and not src.startswith("//")),
  "preserve_licence_origins":all(link in p.links for link in q.links if "commons.wikimedia.org" in link or "creativecommons.org" in link),
  "all_old_links_preserved":Counter(p.links)>=Counter(q.links),
  "exactly_three_new_official_links":len(p.links)==len(q.links)+3,
  "unchanged_title_desc_canonical":p.h1==q.h1==1 and p.canon==q.canon==["https://www.nipponferry.com/things-to-do/"+slug+"-cruise-port-day-trip/"] and p.desc==q.desc and p.titles==q.titles,
  "unique_dom_ids":len(p.ids)==len(set(p.ids)),
  "mobile_52px_actions":'id="nf-v159-port-ops-css"' in txt and "@media(max-width:620px)" in txt and "min-height:52px" in txt,
  "no_assumed_inventory_or_ship_shuttle":not any(v in fragment for v in ["잔여석 보장","예약 확정입니다","무료 셔틀 확정","귀선 보장"])
 }
 missing=[k for k,v in checks.items() if not v]
 if missing:fails.extend([slug+":"+name for name in missing])
 results.append({"slug":slug,"passed":len(checks)-len(missing),"total":len(checks),"failed":missing})
 print(("FAIL" if missing else "PASS"),slug,len(checks)-len(missing),"/",len(checks),missing,flush=True)

current = (ROOT/"sitemap.xml").read_text(encoding="utf-8")
if current != old(ROOT/"sitemap.xml"):fails.append("sitemap_modified")
urlset={u.find("{*}loc").text for u in ET.fromstring(current).findall("{*}url")}
for slug in CASES:
 if f"https://www.nipponferry.com/things-to-do/{slug}-cruise-port-day-trip/" not in urlset:fails.append(slug+":sitemap_url_missing")
out=Path("audit-output/v159");out.mkdir(parents=True,exist_ok=True)
report={"version":"V159","as_of":"2026-10-24","new_articles":0,"updated_existing_guides":len(CASES),"images_changed":0,"booking_inventory_verified":False,"private_analytics_verified":False,"failures":fails,"results":results}
(out/"five-verified-port-booking-return.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",sum(not r["failed"] for r in results),"/",len(results),"errors",len(fails),flush=True)
if fails:raise SystemExit(1)
