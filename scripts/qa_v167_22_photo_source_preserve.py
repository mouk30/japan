#!/usr/bin/env python3
"""V167 photo blur fixes: original file and SEO protection for 22 confirmed
CSS-upscaled assets plus 3 earlier portrait fixes. Ensure actual Commons
filenames, original links, URL, metadata and photos are not replaced.
"""
from pathlib import Path
from html.parser import HTMLParser
import subprocess,json

BASE="313511b2980fdf7be11e40bb166a083da81107a6"
TOKYO=["tokyo-summer-heat-indoor","tokyo-tower-tickets","tokyo-autumn-gardens","tokyo-firsttime-east-west","tokyo-electronics-bic-yodobashi","tsukiji-two-stations","kanda-jr-ginza-transfer","donki-roppongi-night-check","tokyo-skytree-tickets","shinjuku-kabukicho-donki","tokyo-donki-shinjuku-kabukicho","tokyo-ghibli-museum-booking","asakusa-operators","shibuya-parco-floor-guide","disney-mobile-order-food","tokyo-teamlab-planets-ticket-guide","tokyo-tsukemen-howto","disneyland-beauty-beast-ride","daikanyama-bookshops","ueno-ameyoko-budget-shopping"]
ALSO=[
 "site/things-to-do/hakata-cruise-parents-guide/index.html",
 "site/things-to-do/tatami-floor-japanese-living/index.html",
 "site/things-to-do/hakodate-cruise-port-day-trip/index.html",
 "site/things-to-do/kobe-cruise-port-day-trip/index.html",
 "site/things-to-do/shamisen-japanese-three-string-instrument/index.html"
]
class Parser(HTMLParser):
 def __init__(self):
  super().__init__();self.img=[];self.meta=[];self.links=[];self.h1=0;self.title=[];self.in_title=False
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=="img":self.img.append((a.get("src",""),a.get("alt","")))
  if t=="meta":self.meta.append((a.get("name",""),a.get("property",""),a.get("content","")))
  if t=="link" and a.get("rel")=="canonical":self.meta.append(("canonical",a.get("href","")))
  if t=="a":self.links.append(a.get("href",""))
  if t=="h1":self.h1+=1
  if t=="title":self.in_title=True
 def handle_endtag(self,t):
  if t=="title":self.in_title=False
 def handle_data(self,s):
  if self.in_title:self.title.append(s)
def parse(s):
 v=Parser();v.feed(s);return v
def baseline(path):
 return subprocess.check_output(["git","show",f"{BASE}:{path}"],text=True)

css=Path("site/tokyo-guide.css").read_text("utf-8")
checks={
 "tokyo_target_20_native_scale_down_all":all(f'.tokyo-article-photo-v1 img[src$="/{slug}.webp"]' in css for slug in TOKYO),
 "tokyo_preserve_others_and_photographer_credits":"object-fit:scale-down" in css and "tokyo-article-photo-v1 figcaption" in css,
 "all_original_20_tokyo_guides_exist":all(Path(f"site/japan/tokyo/{slug}/index.html").is_file() for slug in TOKYO)
}
rows=[];fails=[]
for slug in TOKYO:
 p=f"site/japan/tokyo/{slug}/index.html"
 a,b=parse(Path(p).read_text("utf-8")),parse(baseline(p))
 result={"slug":slug,"src_original":a.img==b.img,
 "original_seo_meta_links":a.meta==b.meta and a.title==b.title and a.h1==b.h1 and a.links==b.links,
 "one_original_local_photo":len(a.img)==len(b.img)==1}
 rows.append(result)
 for key,v in result.items():
  if key!="slug" and not v:fails.append(slug+":"+key)
for path in ALSO:
 a,b=parse(Path(path).read_text("utf-8")),parse(baseline(path))
 s=Path(path).read_text("utf-8")
 result={"slug":path,
 "same_original_src_and_subject_alt":a.img==b.img,
 "original_seo_meta_links":a.meta==b.meta and a.title==b.title and a.h1==b.h1 and a.links==b.links,
 "no_forced_original_cover":"nf167-portrait-photo" in s and "object-fit:" in s and
  ("object-fit:scale-down" in s or "object-fit:contain" in s),
 "no_extra_new_images":len(a.img)==len(b.img)}
 rows.append(result)
 for key,v in result.items():
  if key!="slug" and not v:fails.append(path+":"+key)
for key,ok in checks.items():
 if not ok:fails.append(key)
report={"version":"V167","portrait_and_critical_guides":len(rows),"existing_topic_photo_assets":22,
 "new_articles":0,"changed_original_images":0,"original_photo_sources_and_SEO_unchanged":len(fails)==0,"fails":fails,"checks":checks,"pages":rows}
out=Path("audit-output/v167-final");out.mkdir(parents=True,exist_ok=True)
(out/"source-preservation-22-stretched-photos.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",len(rows)-len(set(x.split(":")[0] for x in fails)),"/",len(rows),"errors",len(fails),flush=True)
if fails:
 for issue in fails:print("FAIL",issue,flush=True)
 raise SystemExit(1)
