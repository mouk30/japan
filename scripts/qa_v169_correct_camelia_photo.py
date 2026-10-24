#!/usr/bin/env python3
"""V169 actual source regression: two Busan-Fukuoka New Camellia sections.
The previous /images/ferry.jpg wrongly depicted PanStar instead.
Only ship-specific image/alt/credit/presentation change; all SEO and URLs stay.
"""
from pathlib import Path
from html.parser import HTMLParser
import subprocess,json,re
BASE="3e13015089924ee4572164f50e1189d04c6dfba5"
SHIP="/images/venues/nf-v134-new-camellia-busan-2026-real.webp"
LICENSE="https://creativecommons.org/licenses/by/4.0/"
AUTHOR="Midnight cadet"
files={
 "site/japan/fukuoka/index.html":"ferry",
 "site/busan-fukuoka-cruise/index.html":"route"
}
class H(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.canon=[];self.meta=[];self.links=[];self.title=[];self.in_title=False
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=="h1":self.h1+=1
  if t=="link" and a.get("rel")=="canonical":self.canon.append(a.get("href",""))
  if t=="meta":self.meta.append((a.get("name"),a.get("property"),a.get("content")))
  if t=="a":self.links.append(a.get("href"))
  if t=="title":self.in_title=True
 def handle_data(self,s):
  if self.in_title:self.title.append(s)
 def handle_endtag(self,t):
  if t=="title":self.in_title=False
def parsed(s):
 x=H();x.feed(s);return x
fail=[];results=[]
for path,mode in files.items():
 txt=Path(path).read_text("utf-8")
 old=subprocess.check_output(["git","show",f"{BASE}:{path}"],text=True)
 now,before=parsed(txt),parsed(old)
 if mode=="ferry":
  region=txt[txt.index('<section class="fk-section" id="ferry">'):txt.index("</section>",txt.index('<section class="fk-section" id="ferry">'))]
  pic=re.findall(r'<img\b[^>]*class="fk-photo fk-photo--new-camellia"[^>]*>',region)
  tests={
    "new_Camellia_in_correct_content_card":len(pic)==1 and SHIP in pic[0],
    "real_ship_subject_alt_and_dimensions":len(pic)==1 and "뉴카멜리아" in pic[0] and 'width="1400" height="934"' in pic[0],
    "source_attribution_below_correct_ship":AUTHOR in region and LICENSE in region and 'class="nf169-ferry-photo-credit"' in region,
    "no_wrong_credit_in_next_transit_section":'nf169-ferry-photo-credit' not in txt[txt.index('<section class="fk-section" id="arrival">'):],
    "source_image_shown_uncropped":'.fk-photo--new-camellia{object-fit:contain' in txt
  }
 else:
  tests={
    "hero_and_main_photo_both_actual_ship":txt.count(SHIP)==2,
    "right_operator_subject_alt":'뉴카멜리아 실제 국제 여객선' in txt,
    "hero_background_points_to_actual_ship":f"background:url('{SHIP}')" in txt,
    "main_photo_not_force_cropped":"nf169-camellia{object-fit:contain" in txt,
    "source_attribution_near_card":LICENSE in txt and AUTHOR in txt and "nf169-camellia-credit" in txt
  }
 tests.update({
 "no_wrong_panstar_asset":"/images/ferry.jpg" not in txt,
 "original_shown_image_exists":Path("site"+SHIP).is_file(),
 "all_existing_anchors_preserved":all(z in now.links for z in before.links),
 "original_title_description_canonical_H1_unchanged":now.title==before.title and now.meta==before.meta and now.canon==before.canon and now.h1==before.h1==1,
 "original_indexable":"noindex" not in txt[:5000]
 })
 bad=[k for k,v in tests.items() if not v]
 fail.extend(path+":"+k for k in bad)
 results.append({"file":path,"checks":tests,"passed":not bad})
 print("PASS" if not bad else "FAIL",path,bad,flush=True)
r={"version":"V169","updated_existing_pages":2,"new_articles":0,"fixed_subject":"New Camellia instead of PanStar in Busan-Fukuoka","base_sha":BASE,"passed":len(results)-len(set(x.split(":")[0] for x in fail)),"total":len(results),"errors":fail,"rows":results}
out=Path("audit-output/v169");out.mkdir(parents=True,exist_ok=True)
(out/"photo-subject-and-SEO-source.json").write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding="utf-8")
print("SUMMARY",sum(x["passed"] for x in results),"/",len(results),flush=True)
if fail:raise SystemExit(1)
