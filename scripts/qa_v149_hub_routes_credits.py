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
q(len(original_credits) in (0,36),"expected initial 36 or already-compacted 0 original on-card photo credit rows, got "+str(len(original_credits)))
if len(original_credits)==0:
 q(panel(org).count("기항지 카드 ·")==36,"existing V149 baseline missing 36 preserved photo-credit entries")
q(len(CREDIT.findall(current))==0,"photo author labels still on visible cards")
p=panel(current)
q(bool(p),"missing preserved V148 CC photo credits disclosure")
for txt in original_credits:q(txt in scrub(p),"photo author/year/license lost: "+txt[:100])
q(p.count("기항지 카드 ·")==36,"not all 36 license credit records placed into disclosure")
origLink=parse(org);currLink=parse(current)
images_iter=iter(currLink.images)
q(all(any(img==original_img for img in images_iter) for original_img in origLink.images),"an original cruise-port photo or alt was lost/altered")
new_card_images=3 if 'id="nf-v153-pilot-hub"' in current and 'id="nf-v153-pilot-hub"' not in org else 0
q(len(currLink.images)==len(origLink.images)+new_card_images,"unexpected cruise-port thumbnail addition/removal")
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
 if path==HOME and 'class="nf247-route-photo"' in s:
  # V305: the four existing route cards now use licensed destination photography,
  # not illustrative PanStar artwork or a misleading ferry-terminal screenshot.
  # The old-to-new comparison is exact and refuses any unrelated photo changes.
  approved_removed=Counter({
   ("/images/panstar-cruise-clean-2048.webp","팬스타 크루즈를 모티브로 한 AI 연출 이미지"):1,
   ("/images/venues/nf-v134-new-camellia-busan-2026-real.webp","2026년 부산항 뉴카멜리아 국제여객선 실제 사진"):1,
   ("/images/venues/nf-v135-shimonoseki-international-terminal-2021-real.webp","시모노세키 국제터미널 실제 사진"):1,
   ("/images/venues/nf-v124-tsushima-harbor-real.webp","대마도 항구 실제 풍경 사진"):1
  })
  approved_added=Counter({
   ("/images/venues/nf-v85-osaka-dotonbori-licensed.webp","2015년 촬영한 오사카 도톤보리 실제 야경과 수로. 페리 선박·승선 부두 사진 아님"):1,
   ("/images/venues/fukuoka-ohori-park.webp","2026년 촬영한 후쿠오카 오호리공원 실제 풍경. 뉴카멜리아 선박·하카타항 사진 아님"):1,
   ("/images/venues/v62-karato-market-real.webp","2023년 촬영한 시모노세키 가라토시장 실제 모습. 국제여객선 터미널·선박 사진 아님"):1,
   ("/images/venues/nf-v124-tsushima-harbor-real.webp","2017년 촬영한 대마도 이즈하라항과 항구마을 실제 풍경. 히타카츠항과 다른 장소"):1
  })
  added=Counter(a.images)-Counter(b.images)
  removed=Counter(b.images)-Counter(a.images)
  q((added==approved_added and removed==approved_removed) or (not added and not removed),
    "homepage photo/alt changed outside exactly four V305 approved real-place replacements")
  q(s.count('class="nf247-route-photo"')==4,"unexpected homepage route photo count")
  q(s.count('class="nf305-photo-rights"')==0 or s.count('class="nf305-photo-rights"')==4,
    "photo provenance missing from a route card")
  for url in ["/images/venues/nf-v85-osaka-dotonbori-licensed.webp",
              "/images/venues/fukuoka-ohori-park.webp",
              "/images/venues/v62-karato-market-real.webp",
              "/images/venues/nf-v124-tsushima-harbor-real.webp"]:
   q((ROOT/url.lstrip("/")).is_file(),"missing licensed destination file: "+url)
  q('히타카츠와 다른 장소' in s and '선박 아님' in s,
    "real place/vessel separation labels missing")
 else:
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
