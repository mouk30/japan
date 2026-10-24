#!/usr/bin/env python3
"""V167 site-wide image candidate audit and strict four-page content/SEO check.
A low-resolution or repeated photo is a REVIEW CANDIDATE, not proof of mislabel.
Reports all HTML and local images, ranks homepage and region directory issues.
Does not assert every site's editorial copyright and identity has been inspected.
"""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter,defaultdict
from PIL import Image,UnidentifiedImageError
import re,json,subprocess,hashlib

ROOT=Path("site")
BASE="054e2937dcdb22f81b8e58446171910c1ea6f4c7"
KEY=[
"site/japan/osaka/index.html",
"site/japan/hokkaido/index.html",
"site/japan/index.html",
"site/busan-osaka-cruise/index.html",
]
class ImgParser(HTMLParser):
 def __init__(self):
  super().__init__();self.img=[];self.links=[];self.canon=[];self.title=[];self.in_title=False;self.meta=[];self.h1=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="img":self.img.append((a.get("src",""),a.get("alt",""),a.get("class","")))
  if tag=="a":self.links.append(a.get("href",""))
  if tag=="link" and a.get("rel")=="canonical":self.canon.append(a.get("href",""))
  if tag=="meta" and a.get("name")=="description":self.meta.append(a.get("content",""))
  if tag=="title":self.in_title=True
  if tag=="h1":self.h1+=1
 def handle_data(self,data):
  if self.in_title:self.title.append(data)
 def handle_endtag(self,tag):
  if tag=="title":self.in_title=False
def parse(s):
 p=ImgParser();p.feed(s);return p

def check(cond,name,errors):
 if not cond:errors.append(name)
results=[];errors=[]
for p in KEY:
 s=Path(p).read_text("utf-8");o=subprocess.check_output(["git","show",BASE+":"+p],text=True)
 a,b=parse(s),parse(o)
 rules={}
 def c(k,ok):rules[k]=bool(ok);check(ok,p+":"+k,errors)
 c("title_unchanged",a.title==b.title)
 c("original_meta_description_unchanged",a.meta==b.meta)
 c("canonical_unchanged",a.canon==b.canon)
 c("h1_count_unchanged",a.h1==b.h1==1)
 c("all_original_navigation_links_kept",set(b.links).issubset(set(a.links)))
 if p.endswith("/japan/hokkaido/index.html"):
  hi=s[s.indexOf('<section class="city-section" id="highlights">'):s.indexOf("</section>",s.indexOf('<section class="city-section" id="highlights">'))]
  photos=[x[0] for x in parse(hi).img]
  c("three_unique_cards",len(photos)==3 and len(set(photos))==3)
  c("snow_festival_is_actual_Sapporo",photos[0]=="/images/venues/nf-v143-sapporo-snow-festival-2014-real.webp")
  c("Otaru_is_real_winter_canal",photos[1]=="/images/venues/nf-v144-otaru-snow-light-2014-real.webp")
  c("Noboribetsu_CC0_local_on_site",photos[2]=="/images/v167/noboribetsu-onsen-lawsonstu-cc0-2015.webp")
  c("all_images_exist",all((ROOT/x.lstrip("/")).is_file() for x in photos))
  c("original_Kyoto_foliage_not_used",'/images/hokkaido.jpg' not in s and '/images/photo.jpg' not in hi and '/images/onsen.jpg' not in hi)
  c("real_photo_license_visible","Noboribetsu_Onsen_hot_spring.jpg" in s and "Lawsonstu" in s and "CC0" in s)
  c("card_aspect_4_3",".city-card img{display:block;width:100%;height:auto;aspect-ratio:4/3" in s)
 elif p.endswith("/japan/osaka/index.html"):
  block=s[s.indexOf('<section class="os-section" id="cruise">'):s.indexOf("</section>",s.indexOf('<section class="os-section" id="cruise">'))]
  c("official_actual_PanStar_Miracle","https://www.panstar.co.kr/uploads/media/cruise-miracle-ship.jpg" in block)
  c("wrong_legacy_ship_no_longer_shown",'/images/ferry.jpg' not in block)
  c("operator_credits_and_original","https://www.panstar.co.kr/business/cruise/miracle" in block and "ⓒ PanStar" in block)
  c("ship_no_upsampling_crop","object-fit:contain" in s)
 elif p.endswith("/japan/index.html"):
  c("Fukuoka_19_wrong_city_reuse_removed",s.count('src="/images/fukuoka.jpg"')==0 and o.count('src="/images/fukuoka.jpg"')==19)
  c("Fukuoka_topic_cards_still_19",s.count('class="dircard" href="/japan/fukuoka')==19)
  c("Fukuoka_sweets_wagashi_not_yatai",'href="/japan/fukuoka-dessert/"><img alt="일본 화과자' in s)
 elif p.endswith("/busan-osaka-cruise/index.html"):
  c("correct_ship_operator_photo",'src="https://www.panstar.co.kr/uploads/media/cruise-miracle-ship.jpg"' in s)
  c("legacy_image_removed_from_ship_card", "class='im' src='/images/ferry.jpg'" not in s)
 results.append({"page":p,"passed":sum(rules.values()),"total":len(rules),"failed":[k for k,v in rules.items() if not v]})

# Full site image audit: never confuse the same standard logo with content duplicates
files=list(ROOT.rglob("*.html"));assets=list((ROOT/"images").rglob("*"))
usage=defaultdict(list); missing=defaultdict(list);same_page=[];hero_low=[];low_candidates=[];bad_jpg=[];local_n=0
for f in files:
 rel=str(f);s=f.read_text("utf-8",errors="replace");im=parse(s).img
 content=[u for u,alt,cl in im if u.startswith("/images/") and not any(t in u.lower() for t in ("kakao","favicon","icon","logo"))]
 n=Counter(content)
 for url,nn in n.items():
  if nn>=2:
   same_page.append({"page":rel,"img":url,"count":nn,"different_alts":list(set(a for src,a,cl in im if src==url))[:6]})
 for src,alt,cl in im:
  if src.startswith("/images/"):
   local_n+=1;usage[src].append({"html":rel,"alt":alt,"class":cl})
   path=ROOT/src.lstrip("/")
   if not path.is_file():missing[src].append(rel)
for f in assets:
 if f.is_file() and f.suffix.lower() in (".jpg",".jpeg",".png",".webp"):
  try:
   with Image.open(f) as im:
    w,h=im.size;w0=w;h0=h
    if w<640 or h<330:low_candidates.append({"path":str(f),"px":[w,h],"bytes":f.stat().st_size,"usage":len(usage.get("/"+str(f.relative_to(ROOT)),[]))})
  except (UnidentifiedImageError,OSError):bad_jpg.append(str(f))
# classify by number of distinct pages: repeated pictures not automatically mislocated.
highest_repeat=sorted([{"image":k,"uses":len(v),"example_alt":list(set(z["alt"] for z in v))[:5]} for k,v in usage.items() if len(v)>=4],key=lambda x:-x["uses"])
out=Path("audit-output/v167");out.mkdir(parents=True,exist_ok=True)
report={
 "v":167,"page_count":len(files),"assets_scanned":len([f for f in assets if f.is_file()]),"local_img_tags":local_n,
 "unique_local_references":len(usage),"missing_local_images":{k:v[:20] for k,v in missing.items()},
 "same_image_reused_inside_one_page":same_page[:200],"same_page_count":len(same_page),
 "asset_small_dimension_candidates":sorted(low_candidates,key=lambda x:(-x["usage"],x["px"][0]))[:300],
 "small_candidate_count":len(low_candidates),"repeat_image_candidates":highest_repeat[:180],
 "uncodable_assets":bad_jpg,
 "priority_page_rules":results,
 "priority_errors":errors,
 "disclaimer":"A filename, repeated use, or dimension alone is not enough to certify actual location or copyright. Human photo-original inspection remains required.",
}
(out/"sitewide-image-dimensions-repeat-source-audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
summary={"site_html":len(files),"images":len(assets),"local_references":local_n,"unique_references":len(usage),"missing":len(missing),"within_page_duplicate_candidates":len(same_page),"small_image_candidates":len(low_candidates),"priority_fails":len(errors),"priority_rules":results,"high_repeat":highest_repeat[:12],"low_images":sorted(low_candidates,key=lambda x:-x["usage"])[:12]}
(out/"v167-image-audit-summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
if errors or missing:raise SystemExit(1)
