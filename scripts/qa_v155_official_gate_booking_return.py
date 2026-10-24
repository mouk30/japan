#!/usr/bin/env python3
"""V155 five core Japan cruise ports: gate/booking/local transport/return reality.
New material adds official evidence and safe fallback only. All original photos,
meta, headings, links, copyright, and indexed pages remain unchanged.
"""
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
import subprocess,json,re,xml.etree.ElementTree as ET
ROOT=Path("site")
PORTS={
"naha-shuri-castle-cruise-sightseeing":(
 ["https://oki-park.jp/shurijo/ticket_guide/11414","https://oki-park.jp/shurijo/en/ticket_guide/"],
 ["2026년 11월 23일","환불은 이용 이틀 전까지","슈리역","귀선"]),
"ishigaki-cruise-new-port-shuttle":(
 ["https://www.city.ishigaki.okinawa.jp/kurashi_gyosei/shigoto_sangyo/kaihatsu_kenchiku/2033.html"],
 ["무료 셔틀","2~3시간","픽업","귀선"]),
"yokohama-daikoku-pier-cruise-terminal":(
 ["https://www.city.yokohama.lg.jp/kanko-bunka/minato/kyakusen/terminal.html",
 "https://navi.hamabus.city.yokohama.lg.jp/koutuu/pc/diagram/BusCourseSearch?busstopId=00090614"],
 ["109번","17번","보안","오산바시","귀선"]),
"hakata-port-tenjin-sightseeing":(
 ["https://hakataport.com/center/","https://hakataport.com/Access/","https://jik.nishitetsu.jp/"],
 ["국제여객터미널","크루즈센터","500m","80번","귀선"]),
"nagasaki-cruise-peace-park-tram":(
 ["https://www.discover-nagasaki.com/en/featured-topics/fromnagasakiport","https://www.naga-den.com/"],
 ["마쓰가에","5호선","1호선","150엔","귀선"])
}
class S(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.img=[];self.links=[];self.ids=[];self.canonical=[];self.description=[];self.titles=[];self.in_title=False
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="h1":self.h1+=1
  if tag=="img":self.img.append((a.get("src",""),a.get("alt",""),a.get("width"),a.get("height")))
  if tag=="a":self.links.append(a.get("href",""))
  if "id" in a:self.ids.append(a["id"])
  if tag=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href"))
  if tag=="meta" and a.get("name")=="description":self.description.append(a.get("content"))
  if tag=="title":self.in_title=True
 def handle_data(self,data):
  if self.in_title:self.titles.append(data)
 def handle_endtag(self,tag):
  if tag=="title":self.in_title=False
def parse(html):
 p=S();p.feed(html);return p
def before(path):
 return subprocess.check_output(["git","show","origin/main:"+str(path)],text=True)
errors=[];data=[]
def test(ok,label):
 if not ok:errors.append(label)
 return ok
for slug,(sources,claims) in PORTS.items():
 path=ROOT/"things-to-do"/slug/"index.html"
 txt=path.read_text(encoding="utf-8");orig=before(path)
 a,b=parse(txt),parse(orig)
 pos=txt.index('id="nf-v155-dayof-check"') if 'id="nf-v155-dayof-check"' in txt else -1
 excerpt=txt[pos:pos+7300] if pos>=0 else ""
 checks={
 "one_v155_panel":a.ids.count("nf-v155-dayof-check")==1,
 "three_actions":excerpt.count('class="nf-v155-step"')==3,
 "source_links":all(x in a.links for x in sources),
 "specific_official_facts":all(x in excerpt for x in claims),
 "user_return_decision":all(x in excerpt for x in ["승객","귀선","__:__","실시간","마감"]),
 "all_new_official_sources_have_rel":all('rel="noopener noreferrer"' in z for z in re.findall(r'<a\b[^>]*href="https:[^"]+"[^>]*>',excerpt)),
 "preexisting_v150_markers":a.ids.count("nf-v150-visitor-check")==1,
 "panel_above_v150":0<pos<txt.index('id="nf-v150-visitor-check"'),
 "original_photo_and_alt_unchanged":a.img==b.img,
 "original_real_photos_still_on_disk":all((ROOT/src.lstrip("/").split("?")[0]).is_file() for src,alt,w,h in a.img if src.startswith("/") and not src.startswith("//")),
 "original_source_and_CC_links_retained":all(link in a.links for link in b.links if "wikimedia.org" in link or "creativecommons.org" in link),
 "original_H1_SEO_meta":a.h1==b.h1==1 and a.canonical==b.canonical==["https://www.nipponferry.com/things-to-do/"+slug+"/"] and a.description==b.description and a.titles==b.titles,
 "original_links_not_lost":Counter(a.links)>=Counter(b.links),
 "no_double_ids":len(a.ids)==len(set(a.ids)),
 "responsive_at_610px_and_clickable_48px":'id="nf-v155-dayof-port-styles"' in txt and "@media(max-width:610px)" in txt and "min-height:48px" in txt,
 "not_fabricated_reservations":"예약완료를 보장" not in excerpt and "확정된 무료 셔틀" not in excerpt
 }
 for k,v in checks.items():test(v,slug+":"+k)
 data.append({"slug":slug,"passes":sum(checks.values()),"total":len(checks),"failures":[k for k,v in checks.items() if not v]})
 print("PASS" if all(checks.values()) else "FAIL",slug,data[-1]["failures"],flush=True)
hp=ROOT/"things-to-do/cruise-ports/index.html";hub=hp.read_text(encoding="utf-8");old=before(hp)
h,o=parse(hub),parse(old)
hubchecks={
 "one_existing_H1_and_canonical":h.h1==o.h1==1 and h.canonical==o.canonical,
 "original_images_and_rights":h.img==o.img,
 "all_existing_links_preserved":Counter(h.links)>=Counter(o.links),
 "exactly_five_new_links":len(h.links)==len(o.links)+5,
 "direct_to_official_panels":all("/things-to-do/"+slug+"/#nf-v155-dayof-check" in h.links for slug in PORTS),
 "no_duplicate_ids":len(h.ids)==len(set(h.ids)),
 "mobile_large_navigation":'id="nf-v155-port-shortcuts"' in hub and "@media(max-width:560px)" in hub
}
for k,v in hubchecks.items():test(v,"hub:"+k)
print("PASS" if all(hubchecks.values()) else "FAIL","hub",[k for k,v in hubchecks.items() if not v],flush=True)
oldxml=before(ROOT/"sitemap.xml");nowxml=(ROOT/"sitemap.xml").read_text(encoding="utf-8")
test(oldxml==nowxml,"sitemap_must_not_change")
url_list=[e.find("{*}loc").text for e in ET.fromstring(nowxml).findall("{*}url")]
test(all("https://www.nipponferry.com/things-to-do/"+slug+"/" in url_list for slug in PORTS),"no_existing_indexed_url_lost")
report={"version":"V155","existing_ports":len(PORTS),"new_posts":0,"new_pilot_cards":0,"added_hub_shortcuts":5,
 "existing_photos_and_license_preserved":all(row["total"]==row["passes"] for row in data),
 "search_and_ga4_metrics_unavailable_without_owner_data":True,
 "errors":errors,"port_checks":data,"hub_checks":hubchecks}
out=Path("audit-output/v155");out.mkdir(parents=True,exist_ok=True)
(out/"official-port-dayof-check.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",sum(d["total"]==d["passes"] for d in data),"/5","errors",len(errors))
if errors:raise SystemExit(1)
