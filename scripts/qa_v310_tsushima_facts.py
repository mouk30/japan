#!/usr/bin/env python3
"""V310: actual outdated price and broken foreign booking link fixes.
Release gate: exact old SEO/JSON-LD/photo rights, 4 × operator-correct route pages.
"""
from html.parser import HTMLParser
from pathlib import Path
from collections import Counter
from hashlib import sha256
import subprocess
ROOT=Path("site")
SLUGS=("busan-tsushima-ferry-price","tsushima-busan-ferry","busan-hitakatsu-ferry","busan-izuhara-ferry")
OLD="https://willer-travel.com/ko/ferry/"
FUEL="https://www.panstarcruise.com/support/notice/309"
SCHEDULE="https://www.panstarcruise.com/product/daemado/info"
CHECKIN="https://www.panstarcruise.com/product/daemado/procedure"
class Reader(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.canon=[];self.desc=[];self.robots=[];self.images=[];self.anchors=[];self.ld=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=="h1":self.h1+=1
  if t=="link" and a.get("rel")=="canonical":self.canon.append(a.get("href"))
  if t=="meta" and a.get("name")=="description":self.desc.append(a.get("content"))
  if t=="meta" and a.get("name")=="robots":self.robots.append(a.get("content"))
  if t=="img":self.images.append(a)
  if t=="a":self.anchors.append(a.get("href",""))
  if t=="script" and a.get("type")=="application/ld+json":self.ld.append(tuple(attrs))
def parse(s):
 r=Reader();r.feed(s);return r
assert (ROOT/"nf-v310-tsushima-facts.css").is_file()
css=(ROOT/"nf-v310-tsushima-facts.css").read_text()
for x in (".nf310-preflight",".nf310-steps",".nf310-links","@media(max-width:540px)"): assert x in css,x
for slug in SLUGS:
 p=ROOT/"guide"/slug/"index.html";html=p.read_text()
 orig=subprocess.check_output(["git","show","origin/main:"+str(p)],text=True)
 a,b=parse(html),parse(orig)
 assert a.h1==b.h1==1,(slug,"h1")
 assert a.canon==b.canon==["https://www.nipponferry.com/guide/"+slug+"/"],(slug,"canonical")
 assert a.desc==b.desc and a.robots==b.robots and a.ld==b.ld,(slug,"SEO changed")
 assert a.images==b.images,(slug,"original image or attribution changed")
 assert Counter(b.anchors)-Counter(a.anchors)==Counter({OLD:2}),(slug,"unexpected old links lost",Counter(b.anchors)-Counter(a.anchors))
 assert OLD not in a.anchors,(slug,"wrong domestic-marketplace link remains")
 assert SCHEDULE in a.anchors and CHECKIN in a.anchors and FUEL in a.anchors,(slug,"operator sources")
 assert "nf-v310-tsushima-facts.css" in html and html.count('id="nf310-travel-check"')==1,(slug,"responsive facts")
 assert html.count('class="nf310-step"')==3,(slug,"three traveler decisions")
 assert "실시간" in html and "NIPPONFERRY" in html,(slug,"false ticketing")
 assert not any(z in html for z in ("15,000원","25,000원","2,500엔","willer-travel.com")),(slug,"old price or unrelated booking site")
 for img in a.images:
  src=img.get("src","")
  if src.startswith("/") and not src.startswith("//"):
   assert (ROOT/src.lstrip("/").split("?")[0]).is_file(),(slug,"local photo missing",src)
 if slug=="busan-tsushima-ferry-price":
  for amount in ("16,000원","27,000원","1,600엔","2,700엔"):assert amount in html,amount
  assert "2026년 11월 15일" in html and "15:30" in html
  assert "10월 결항 공지는 현재 결항을 의미하지" in html
 if slug=="tsushima-busan-ferry":
  assert "15:30" in html and "30분 전" in html,(slug,"return")
 if slug=="busan-hitakatsu-ferry":
  assert "17:10" in html and "1,600엔" in html,(slug,"Hitakatsu")
 if slug=="busan-izuhara-ferry":
  assert "15:30" in html and "2,700엔" in html,(slug,"Izuhara")
 print("PASS",slug,"Nov surcharge, return port, operator links, original SEO/images")
approved=ROOT/"images/panstar-cruise-clean-2048.webp"
assert approved.exists() and sha256(approved.read_bytes()).hexdigest()=="bbcfa65a0e670060b5ce6fe79b2a9ea3272874b4d96f96799800ec9ccb631bdd","approved original WebP missing or changed"
added=subprocess.check_output(["git","diff","--name-only","--diff-filter=A","origin/main...HEAD"],text=True).splitlines()
assert not any(f.startswith("site/") and f.endswith(".html") for f in added),("new article blocked",added)
print("V310 PASS 4 existing guide pages; 8 wrong CTAs repaired; no new articles")
