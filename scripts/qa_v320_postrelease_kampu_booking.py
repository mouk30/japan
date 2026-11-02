#!/usr/bin/env python3
"""Post-V320 fix: official Shimonoseki booking click must not land on a historical notice."""
from html.parser import HTMLParser
from pathlib import Path
import subprocess, re
p=Path("site/booking/japan-cruise/index.html")
html=p.read_text(encoding="utf8")
baseline=subprocess.check_output(["git","show","origin/main:"+str(p)],text=True)
class Page(HTMLParser):
 def __init__(self):
  super().__init__();self.links=[];self.images=[];self.h1=0;self.canonical=[];self.meta=[];self.jsonld=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="a":self.links.append(a)
  if tag=="img":self.images.append(a)
  if tag=="h1":self.h1+=1
  if tag=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href"))
  if tag=="meta" and a.get("name") in ("description","robots"):self.meta.append((a["name"],a.get("content")))
  if tag=="script" and a.get("type")=="application/ld+json":self.jsonld.append(a)
def parse(t):
 a=Page();a.feed(t);return a
a,b=parse(html),parse(baseline)
assert a.h1==b.h1==1
assert a.canonical==b.canonical==["https://www.nipponferry.com/booking/japan-cruise/"]
assert a.images==b.images and a.meta==b.meta and a.jsonld==b.jsonld
assert Path("site/images/panstar-cruise-clean-2048.webp").is_file()
import hashlib
assert hashlib.sha256(Path("site/images/panstar-cruise-clean-2048.webp").read_bytes()).hexdigest()=="bbcfa65a0e670060b5ce6fe79b2a9ea3272874b4d96f96799800ec9ccb631bdd"
def official(t):
 m=re.search(r'<div class="nf91-direct-item" data-route="shimonoseki">([\s\S]*?)</div>',t)
 assert m,"route card missing"
 n=re.search(r'<a class="nf91-direct-primary" href="([^"]+)"',m.group(1))
 assert n,"official action missing"
 return n.group(1)
assert official(baseline)=="https://www.kampuferry.co.jp/news/20261027systemmaintenance.html"
assert official(html)=="https://www.kampuferry.co.jp/reserve/"
assert "https://www.kampuferry.co.jp/news/20261027systemmaintenance.html" in [z.get("href") for z in a.links]
assert "NIPPONFERRY" in html and "실시간" in html
assert "공식 예약 방법" in html
print("PASS official booking action vs old historical notice, existing photos/SEO/rights, approved source")
