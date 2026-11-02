#!/usr/bin/env python3
"""V303: exact old-page photo, rights, SEO, link and CTA regression.
This gate is intentionally strict: only presentation changes are approved.
"""
from __future__ import annotations
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import subprocess
ROOT=Path("site")
SLUGS={
 "things-to-do/naha-cruise-terminal-kokusai-dori":"port",
 "things-to-do/hakata-port-hakata-station-access":"port",
 "things-to-do/nagasaki-matsugae-glover-garden-cruise-access":"port",
 "things-to-do/ishigaki-cruise-kabira-bay-bus-taxi":"port",
 "guide/busan-osaka-ferry":"ferry",
 "guide/busan-fukuoka-ferry":"ferry",
 "guide/busan-shimonoseki-ferry":"ferry",
 "things-to-do/yokohama-red-brick-warehouse":"editorial",
}
class Scan(HTMLParser):
 def __init__(self):
  super().__init__()
  self.h1=0;self.h2=0;self.links=[];self.images=[];self.canonical=[];self.desc=[];self.robots=[];self.ids=[];self.scripts=[];self._ld=False;self._ld_text=""
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if tag=="h1":self.h1+=1
  if tag=="h2":self.h2+=1
  if tag=="a":self.links.append(d.get("href",""))
  if tag=="img":self.images.append(d)
  if "id" in d:self.ids.append(d["id"])
  if tag=="link" and d.get("rel")=="canonical":self.canonical.append(d.get("href"))
  if tag=="meta" and d.get("name")=="description":self.desc.append(d.get("content"))
  if tag=="meta" and d.get("name")=="robots":self.robots.append(d.get("content"))
  if tag=="script" and d.get("type")=="application/ld+json":self._ld=True;self._ld_text=""
 def handle_data(self,data):
  if self._ld:self._ld_text+=data
 def handle_endtag(self,tag):
  if tag=="script" and self._ld:
   self.scripts.append(self._ld_text);self._ld=False
def parse(text):
 p=Scan();p.feed(text);return p
def old(path):
 return subprocess.check_output(["git","show","origin/main:"+str(path)],text=True)
css=(ROOT/"nf-v303-detail-photo-cta.css").read_text()
for fragment in ["nf303-port-guide","nf303-ferry-guide","nf303-editorial-guide","aspect-ratio:4/3","@media(max-width:700px)",".nf303-actions"]:
 assert fragment in css,("missing design component",fragment)
for slug,kind in SLUGS.items():
 path=ROOT/slug/"index.html"
 text=path.read_text();before=old(path)
 cur,base=parse(text),parse(before)
 assert cur.h1==base.h1==1,(slug,"H1 changed")
 assert cur.h2==base.h2,(slug,"existing section headings changed")
 assert cur.canonical==base.canonical==["https://www.nipponferry.com/"+slug+"/"],(slug,"canonical changed")
 assert cur.desc==base.desc and cur.robots==base.robots,(slug,"meta changed")
 assert cur.scripts==base.scripts,(slug,"JSON-LD changed")
 assert Counter(cur.links)>=Counter(base.links),(slug,"original links/attribution lost")
 assert len(cur.ids)==len(set(cur.ids)),(slug,"duplicate ID")
 assert cur.images==base.images,(slug,"photo/alt/dimension changed")
 for img in cur.images:
  src=img.get("src","")
  if src.startswith("/") and not src.startswith("//"):
   assert (ROOT/src.split("?")[0].lstrip("/")).is_file(),(slug,"missing local image",src)
 assert "nf-v303-detail-photo-cta.css" in text and ("nf303-"+kind+"-guide") in text,(slug,"style not enabled")
 assert text.count('class="nf303-photo-caption"')==1,(slug,"missing photo caption")
 assert text.count('class="nf303-actions"')==1,(slug,"missing/duplicate actions")
 assert text.count('href="#nf-v148-photo-credits"')==1,(slug,"photo rights jump missing")
 assert 'id="nf-v148-photo-credits"' in text,(slug,"rights panel missing")
 if kind=="port":
  assert 'class="nf303-hero-photo"' in text,(slug,"4:3 cover wrapper missing")
  assert 'href="#nf-v147-port-visitor"' in text,(slug,"safe port return CTA missing")
  assert 'id="nf-v147-port-visitor"' in text,(slug,"return target missing")
  assert 'href="/booking/japan-cruise/"' in text,(slug,"booking guidance missing")
  assert text.count('class="nf-q80-card"')==3,(slug,"three checks lost")
 elif kind=="ferry":
  assert 'class="nf303-ferry-figure"' in text,(slug,"photo wrapper missing")
  assert 'href="#nf86-official-entry"' in text,(slug,"official entry missing")
  assert 'id="nf86-official-entry"' in text,(slug,"official booking anchor missing")
  assert 'id="nf87-verified-operations"' in text,(slug,"operator facts anchor missing")
  assert 'href="#nf87-verified-operations"' in text,(slug,"facts CTA missing")
 else:
  assert 'class="editorial-hero"' in text
  assert 'href="#nf-official-port-20261018"' in text
  assert 'id="nf-official-port-20261018"' in text
 assert "예약이 확정되었습니다" not in text,(slug,"invented reservation")
 print("PASS",slug,"old photos/H1/meta/JSON-LD/links, new responsive CTA")
print("V303 PASS: 8 existing details, no articles added, no source/rights/SEO changes")
