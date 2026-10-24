#!/usr/bin/env python3
"""V150 static audit of exactly five existing travel guides and their port-hub links.
Never invent schedule/bookability. Compare with the unmodified main branch for legal/SEO preservation.
Requires: git fetch origin main:refs/remotes/origin/main.
"""
from html.parser import HTMLParser
from pathlib import Path
from collections import Counter
import re,subprocess,json
ROOT=Path("site")
PORT=ROOT/"things-to-do/cruise-ports/index.html"
DATA={
"naha-shuri-castle-cruise-sightseeing":{"source":"https://oki-park.jp/shurijo/en/ticket_guide/",
 "tokens":["2026년 11월 22일","2026년 11월 23일","1,000엔","760엔","370엔","40~50분","90~120분"],
 "related":"/things-to-do/naha-cruise-terminal-kokusai-dori/#nf-v147-port-visitor"},
"ishigaki-cruise-new-port-shuttle":{"source":"https://www.city.ishigaki.okinawa.jp/kurashi_gyosei/shigoto_sangyo/kaihatsu_kenchiku/2033.html",
 "tokens":["시청이 무료 셔틀을 운행하지 않는다","비정기적","40~50분","0980-82-2054","0980-87-5882"],
 "related":"/things-to-do/ishigaki-cruise-kabira-bay-bus-taxi/#nf-v147-port-visitor"},
"yokohama-daikoku-pier-cruise-terminal":{"source":"https://www.city.yokohama.lg.jp/kanko-bunka/minato/kyakusen/terminal.html",
 "tokens":["입항일에만","승객과 관계자 외 출입이 제한","109계통","17계통","8분","9분"],
 "related":"/things-to-do/yokohama-red-brick-warehouse/#nf-v147-port-visitor"},
"hakata-port-tenjin-sightseeing":{"source":"https://hakataport.com/Access/",
 "tokens":["솔라리아스테이지 앞 2A","80번","BRT","500m","최종"],
 "related":"/things-to-do/hakata-port-hakata-station-access/#nf-v147-port-visitor"},
"nagasaki-cruise-peace-park-tram":{"source":"https://www.naga-den.com/",
 "tokens":["150엔","80엔","5호계통","신치중화거리","1호계통","평화공원"],
 "related":"/things-to-do/nagasaki-matsugae-glover-garden-cruise-access/#nf-v147-port-visitor"}
}
class P(HTMLParser):
 def __init__(self):
  super().__init__();self.anchors=[];self.images=[];self.ids=[];self.h1=0;self.canonical=[];self.meta_description=[];self.title=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="a":self.anchors.append(a.get("href",""))
  if tag=="img":self.images.append((a.get("src"),a.get("alt")))
  if tag=="h1":self.h1+=1
  if "id" in a:self.ids.append(a["id"])
  if tag=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href"))
  if tag=="meta" and a.get("name")=="description":self.meta_description.append(a.get("content"))
def parse(doc):
 p=P();p.feed(doc);return p
def base(path):
 return subprocess.check_output(["git","show","origin/main:"+str(path).replace("\\","/")],text=True)
errors=[];rows=[]
for slug,item in DATA.items():
 path=ROOT/"things-to-do"/slug/"index.html"
 now=path.read_text(encoding="utf-8");before=base(path)
 a,b=parse(now),parse(before)
 checks={
 "exactly_one_v150_panel":a.ids.count("nf-v150-visitor-check")==1,
 "has_one_h1":a.h1==b.h1==1,
 "same_canonical":a.canonical==b.canonical==["https://www.nipponferry.com/things-to-do/"+slug+"/"],
 "same_meta_description":a.meta_description==b.meta_description,
 "same_image_sources_alts":a.images==b.images,
 "original_links_and_attribution_preserved":Counter(a.anchors)>=Counter(b.anchors),
 "original_anchor_ids_retained":Counter(a.ids)>=Counter(b.ids),
 "official_primary_source":item["source"] in a.anchors,
 "related_existing_verified_guide":item["related"] in a.anchors,
 "official_tokens":all(t in now for t in item["tokens"]),
 "mobile_one_column":'grid-template-columns:minmax(0,1fr)' in now,
 "booking_vehicle_return":all(w in now for w in ["예약","이동","귀선","선사 최종","__ : __"]) or
                       all(w in now for w in ["예약","이동","귀선","선사 최종","__:__"]),
 "all_existing_image_paths_local":all((ROOT/src.lstrip("/").split("?")[0]).is_file() for src,alt in a.images if src and src.startswith("/")),
 }
 bad=[name for name,ok in checks.items() if not ok]
 row={"slug":slug,"pass":not bad,"failed":bad,"checks":checks};rows.append(row)
 errors.extend((slug,name) for name in bad)
 print("PASS" if not bad else "FAIL",slug,bad)
hub=PORT.read_text(encoding="utf-8");oldhub=base(PORT);orig=parse(oldhub);new=parse(hub)
hub_checks={
 "hub_images_unchanged":all(any(photo==old_image for photo in new.images) for old_image in orig.images) and all(old in new.images for old in orig.images),
 "hub_exact_three_V153_extra_images":len(new.images)==len(orig.images)+(3 if 'id="nf-v153-pilot-hub"' in hub and 'id="nf-v153-pilot-hub"' not in oldhub else 0),
 "hub_canonical_unchanged":new.canonical==orig.canonical,
 "hub_h1_unchanged":new.h1==orig.h1==1,
 "hub_photo_credits_unchanged":hub.count('id="nf-v148-photo-credits"')==oldhub.count('id="nf-v148-photo-credits"')==1,
 "hub_five_links":all('/things-to-do/'+slug+'/#nf-v150-visitor-check' in new.anchors for slug in DATA),
 "hub_no_old_links":all('/things-to-do/'+slug+'/' not in new.anchors for slug in DATA),
 "hub_link_total_unchanged":Counter(new.anchors)>=Counter(orig.anchors) and len(new.anchors)==len(orig.anchors)+(9 if 'id="nf-v153-pilot-hub"' in hub else 0),
}
for k,v in hub_checks.items():
 if not v:errors.append(("cruise_hub",k))
if base(ROOT/"sitemap.xml")!=(ROOT/"sitemap.xml").read_text(encoding="utf-8"):errors.append(("sitemap","changed"))
report={"new_articles":0,"existing_guide_count":len(DATA),"pages":rows,
 "hub_checks":hub_checks,"errors":errors}
out=Path("audit-output/v150");out.mkdir(parents=True,exist_ok=True)
(out/"five-existing-guides.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",sum(x["pass"] for x in rows),"/",len(rows),"hub",all(hub_checks.values()),"errors",errors)
if errors:raise SystemExit(1)
