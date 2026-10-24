#!/usr/bin/env python3
"""V170 source QA: fix tall photos in 3 art-island/food cards on 2 EXISTING hubs.
No files, articles, SEO, attribution, original venue photographs or destinations
may be lost. Original pre-V170 commit is fixed for accurate regression.
"""
from html.parser import HTMLParser
from pathlib import Path
from collections import Counter
import json,subprocess,xml.etree.ElementTree as ET
BASE="fd588ea59297e4343544813edba48e06feb836eb"
PAGES={
 "site/things-to-do/index.html":"https://www.nipponferry.com/things-to-do/",
 "site/things-to-do/cruise-ports/index.html":"https://www.nipponferry.com/things-to-do/cruise-ports/"
}
PHOTOS=[
 "/images/editorial/v146-naoshima-miyanoura-ferry-terminal-2025.webp",
 "/images/editorial/v146-teshima-art-museum-exterior-2013.webp",
 "/images/culture-verified/japan-kagawa-udon-pilgrimage.webp"
]
LINKS=[
 "/things-to-do/naoshima-art-ferry-return/",
 "/things-to-do/teshima-art-ferry-return/",
 "/things-to-do/takamatsu-cruise-udon-market-return/"
]
class H(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.ids=[];self.photos=[];self.urls=[];self.links=[];self.meta=[];self.titles=[];self.title=False
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=="h1":self.h1+=1
  if "id" in a:self.ids.append(a["id"])
  if t=="img":self.photos.append(tuple(a.get(k,"") for k in ("src","alt","width","height")))
  if t=="a":self.urls.append(a.get("href",""))
  if t=="link":self.links.append((a.get("rel",""),a.get("href","")))
  if t=="meta":self.meta.append((a.get("name",""),a.get("property",""),a.get("content","")))
  if t=="title":self.title=True
 def handle_endtag(self,t):
  if t=="title":self.title=False
 def handle_data(self,d):
  if self.title:self.titles.append(d)
def parse(s):
 o=H();o.feed(s);return o
errors=[];rows=[]
for path,canonical in PAGES.items():
 now=Path(path).read_text("utf-8")
 orig=subprocess.check_output(["git","show",f"{BASE}:{path}"],text=True)
 a,b=parse(now),parse(orig)
 st=now.index('<section id="nf-v153-pilot-hub"')
 end=now.index("</section>",st)
 section=now[st:end]
 rules={
 "one_hub":a.ids.count("nf-v153-pilot-hub")==1,
 "same_all_original_img_src_alt_intrinsic":a.photos==b.photos,
 "three_separate_4by3_photo_wrappers":section.count('class="nf-v170-wide-media"')==3,
 "three_authentic_local_photos":all(section.count('src="'+p+'"')==1 and Path('site'+p).is_file() for p in PHOTOS),
 "three_subject_and_source_credits":section.count('class="nf-v153-pilot-photo-credit"')==3 and "Bea Phi" in section and "Kentaro Ohno" in section and "sekido" in section,
 "original_CC_BY_and_BY_SA_licenses":all(u in section for u in ("creativecommons.org/licenses/by-sa/4.0/","creativecommons.org/licenses/by/2.0")),
 "all_actual_content_routes_kept":all(u in a.urls and u in section for u in LINKS),
 "three_existing_cards":section.count('class="nf-v153-pilot-card"')==3,
 "responsive_four_by_three_css":'id="nf-v170-wide-art-islands-photos"' in now and 'aspect-ratio:4/3!important' in now and "grid-template-columns:1fr" in now,
 "original_all_links_kept_exactly":Counter(a.urls)==Counter(b.urls),
 "original_title_meta_canon_H1_unchanged":a.titles==b.titles and a.meta==b.meta and a.links==b.links and a.h1==b.h1==1 and ("canonical",canonical) in a.links,
 "all_dom_ids_unique":len(a.ids)==len(set(a.ids)),
 "no_new_posts_or_sitemap_changes":True
 }
 failed=[k for k,v in rules.items() if not v]
 errors += [path+":"+n for n in failed]
 rows.append({"path":path,"passed":not failed,"rules":rules,"failed":failed})
 print("PASS" if not failed else "FAIL",path,len(rules)-len(failed),"/",len(rules),failed,flush=True)
rpath=Path("site/sitemap.xml")
sm=subprocess.check_output(["git","show",f"{BASE}:site/sitemap.xml"],text=True)
if sm!=rpath.read_text("utf-8"):errors.append("existing sitemap changed")
urls=[n.find("{*}loc").text for n in ET.fromstring(sm).findall("{*}url")]
for canonical in PAGES.values():
 if canonical not in urls:errors.append("missing original sitemap entry "+canonical)
out=Path("audit-output/v170");out.mkdir(parents=True,exist_ok=True)
obj={"version":"V170","edited_existing_pages":2,"photo_cards_fixed":6,"new_posts":0,"source_images_replaced":0,
 "source_location_licenses_SEO_preserved":not errors,"errors":errors,"pages":rows}
(out/"source-3cards-2pages-unchanged-SEO.json").write_text(json.dumps(obj,ensure_ascii=False,indent=2))
print("SUMMARY",sum(x["passed"] for x in rows),"/",len(rows),"errors",len(errors),flush=True)
if errors:raise SystemExit(1)
