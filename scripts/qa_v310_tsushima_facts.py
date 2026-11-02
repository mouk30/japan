#!/usr/bin/env python3
"""V310: old Tsushima price guide only — verified PanStar fare, return, links.
Do not overlap parallel PR #121 for other 6 return guides.
"""
from html.parser import HTMLParser
from pathlib import Path
from collections import Counter
from hashlib import sha256
import subprocess
ROOT=Path("site")
P=ROOT/"guide/busan-tsushima-ferry-price/index.html"
WILLER="https://willer-travel.com/ko/ferry/"
FUEL="https://www.panstarcruise.com/support/notice/309"
INFO="https://www.panstarcruise.com/product/daemado/info"
PROCEDURE="https://www.panstarcruise.com/product/daemado/procedure"
class Tags(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.canon=[];self.meta=[];self.images=[];self.anchors=[];self.ld=0
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if tag=="h1":self.h1+=1
  if tag=="link" and d.get("rel")=="canonical":self.canon.append(d.get("href"))
  if tag=="meta" and d.get("name") in ("description","robots"):self.meta.append((d.get("name"),d.get("content")))
  if tag=="img":self.images.append(d)
  if tag=="a":self.anchors.append(d.get("href",""))
  if tag=="script" and d.get("type")=="application/ld+json":self.ld+=1
def parse(html):
 p=Tags();p.feed(html);return p
html=P.read_text()
old=subprocess.check_output(["git","show","origin/main:"+str(P)],text=True)
a,b=parse(html),parse(old)
assert a.h1==b.h1==1,"original H1 must stay"
assert a.canon==b.canon==["https://www.nipponferry.com/guide/busan-tsushima-ferry-price/"],"canonical changed"
assert a.meta==b.meta and a.ld==b.ld,"SEO/JSON-LD changed"
assert a.images==b.images,"image, original credits or ALT changed"
assert Counter(b.anchors)-Counter(a.anchors)==Counter({WILLER:2}),"unexpected link removals"
assert WILLER not in a.anchors and "willer-travel.com" not in html,"wrong domestic booking site still used"
assert a.anchors.count(INFO)>=2 and a.anchors.count(PROCEDURE)>=1 and FUEL in a.anchors,"operator sources missing"
assert html.count('id="nf310-travel-check"')==1 and html.count('class="nf310-step"')==3,"3-part real booking/return check missing"
assert "nf-v310-tsushima-facts.css" in html,"CSS absent"
for amount in ("16,000원","27,000원","1,600엔","2,700엔"):
 assert amount in html,("November fuel fee missing",amount)
for oldfee in ("15,000원","25,000원","2,500엔"):
 assert oldfee not in html,("obsolete September fee",oldfee)
assert "2026년 11월 1일" in html and "2026년 11월 15일" in html
assert "15:30" in html and "30분 전" in html and "90분 전" in html
assert "과거 10월 결항 공지는 현재 결항을 의미하지" in html
assert "실시간" in html and "발권" in html and "NIPPONFERRY" in html,"no fake checkout"
assert (ROOT/"nf-v310-tsushima-facts.css").is_file()
css=(ROOT/"nf-v310-tsushima-facts.css").read_text()
for key in (".nf310-preflight",".nf310-links","@media(max-width:540px)"):assert key in css,key
for img in a.images:
 src=img.get("src","")
 if src.startswith("/") and not src.startswith("//"):
  assert (ROOT/src.split("?")[0].lstrip("/")).is_file(),("original image missing",src)
approved=ROOT/"images/panstar-cruise-clean-2048.webp"
assert approved.is_file()
assert sha256(approved.read_bytes()).hexdigest()=="bbcfa65a0e670060b5ce6fe79b2a9ea3272874b4d96f96799800ec9ccb631bdd","approved PanStar original SHA mismatch"
added=subprocess.check_output(["git","diff","--name-only","--diff-filter=A","origin/main...HEAD"],text=True).splitlines()
assert not any(x.startswith("site/") and x.endswith(".html") for x in added),("new article blocked",added)
print("V310 PASS: 1 old price guide, 2 wrong CTAs corrected; rights SEO PanStar source retained")
