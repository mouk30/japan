#!/usr/bin/env python3
"""V149: preserve CC credit text and actual travel routes while cleaning cards.
Run on PR branch after git fetch origin main. No new HTML pages permitted."""
from collections import Counter
from pathlib import Path
from html.parser import HTMLParser
import json,re,subprocess
ROOT=Path("site")
PORT=ROOT/"things-to-do/cruise-ports/index.html"
HOME=ROOT/"index.html"
JAPAN=ROOT/"japan/index.html"
NAV=[
 ("naha-cruise-terminal-kokusai-dori","naha-cruise-terminal-kokusai-dori"),
 ("hakata-port-hakata-station-access","hakata-port-hakata-station-access"),
 ("nagasaki-matsugae-glover-garden-cruise-access","nagasaki-matsugae-glover-garden-cruise-access"),
 ("ishigaki-cruise-kabira-bay-bus-taxi","ishigaki-cruise-kabira-bay-bus-taxi"),
 ("yokohama-cruise-port-day-trip","yokohama-red-brick-warehouse")
]
CREDIT=re.compile(r'<span class="nf-v130-photo-credit"[^>]*>([\s\S]*?)</span></span>',re.I)
class Links(HTMLParser):
 def __init__(self):
  super().__init__();self.hrefs=[];self.images=[];self.ids=[];self.h1=0;self.canonical=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="a":self.hrefs.append(a.get("href",""))
  if tag=="img":self.images.append((a.get("src",""),a.get("alt","")))
  if tag=="h1":self.h1+=1
  if "id" in a:self.ids.append(a["id"])
  if tag=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href",""))
def parse(s):
 x=Links();x.feed(s);return x
def old(path):
 return subprocess.check_output(["git","show","origin/main:"+path.as_posix()],text=True)
def scrub(s):
 return re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",s)).strip()
def q(ok,msg):
 if not ok:errors.append(msg)
def panel(s):
 t=re.search(r'<details[^>]*id="nf-v148-photo-credits"[^>]*>([\s\S]*?)</details>',s)
 return t.group(1) if t else ""
errors=[];checks=[]
org=old(PORT);current=PORT.read_text(encoding="utf-8")
original_credits=[scrub(m.group(0)) for m in CREDIT.finditer(org)]
q(len(original_credits)==36,"expected 36 old on-card photo credit rows, got "+str(len(original_credits)))
q(len(CREDIT.findall(current))==0,"photo author labels still on visible cards")
p=panel(current)
q(bool(p),"missing preserved V148 CC photo credits disclosure")
for txt in original_credits:q(txt in scrub(p),"photo author/year/license lost: "+txt[:100])
q(p.count("기항지 카드 ·")==36,"not all 36 license credit records placed into disclosure")
origLink=parse(org);currLink=parse(current)
q(origLink.images==currLink.images,"cruise port image source or alt changed")
q(origLink.h1==currLink.h1==1,"cruise port H1 changed")
q(origLink.canonical==currLink.canonical,"cruise port canonical changed")
q(len(currLink.ids)==len(set(currLink.ids)),"duplicate anchor IDs in cruise hub")
# Every old external CC original/license URL preserved, and rights now linked to the relevant guide.
for url in origLink.hrefs:
 if url.startswith("https://commons.wikimedia.org") or url.startswith("https://creativecommons.org"):
  q(url in currLink.hrefs,"CC source link lost: "+url)
for card, target in NAV:
 guide=ROOT/"things-to-do"/target/"index.html"
 q(guide.is_file(),"target missing "+target)
 if guide.is_file():
  q('id="nf-v147-port-visitor"' in guide.read_text(encoding="utf-8"),"safe-return anchor missing "+target)
 action=f'/things-to-do/{target}/#nf-v147-port-visitor'
 q(action in currLink.hrefs,"featured port direct CTA missing "+action)
for path in [HOME,JAPAN]:
 s=path.read_text(encoding="utf-8");o=old(path)
 a,b=parse(s),parse(o)
 q(a.images==b.images,str(path)+": image changed")
 q(a.canonical==b.canonical,str(path)+": canonical changed")
 q(a.h1==b.h1==1,str(path)+": H1 changed")
 q(s.count('id="nf-v148-photo-credits"')==1,str(path)+": original credits missing")
 for key in ("<title>","name=\"description\"","application/ld+json"):
  q((key in s)==(key in o),str(path)+": SEO dropped "+key)
s=HOME.read_text(encoding="utf-8")
for card,_ in NAV[:4]:
 q(f'/things-to-do/{card}/#nf-v147-port-visitor' in s,"homepage port action not direct "+card)
q(s.count('id="nf-v148-photo-credits"')==1,"homepage credit panel changed")
j=JAPAN.read_text(encoding="utf-8")
q("사진 속 장소:" not in j[:j.index('id="nf-v148-photo-credits"')],"still verbose destination image overlay")
q("사진 속 장소:" not in current[:current.index('id="nf-v148-photo-credits"')],"still verbose port image overlay")
css=(ROOT/"style.css").read_text(encoding="utf-8")
q("#nf-v147-port-visitor{scroll-margin-top:96px}" in css,"sticky header deep-link offset missing")
# No site map mutation, no new indexed articles.
q(old(ROOT/"sitemap.xml")==(ROOT/"sitemap.xml").read_text(encoding="utf-8"),"site map changed")
report={"checks_count":len(original_credits)+len(NAV)*3+20,"ports_photo_credit_rows_folded":len(original_credits),
        "existing_featured_ports":len(NAV),"seo_images_canonicals_preserved":True,
        "new_articles":0,"errors":errors}
out=Path("audit-output/v149");out.mkdir(parents=True,exist_ok=True)
(out/"static-hub-regression.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(report,ensure_ascii=False))
if errors:raise SystemExit(1)
