#!/usr/bin/env python3
"""V301 responsive Shikoku food feature: no missing credits, photos or SEO."""
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path("site")
path=ROOT/"things-to-do/food-experience/index.html"
s=path.read_text(encoding="utf-8")
class Scan(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.canonical=[];self.img=[];self.links=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="h1":self.h1+=1
  if tag=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href"))
  if tag=="img":self.img.append(a)
  if tag=="a":self.links.append(a.get("href",""))
a=Scan();a.feed(s)
assert a.h1==1
assert a.canonical==["https://www.nipponferry.com/things-to-do/food-experience/"]
assert s.count('class="nf-v153-pilot-card"')==1
assert "id=\"nf-v301-food-editorial\"" in s
assert "max-width:none!important" in s
assert "grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr)" in s
assert "grid-template-columns:minmax(0,1fr)" in s
assert "https://commons.wikimedia.org/wiki/File:Kama-age_sanuki_udon_by_sekido_in_Takamatsu%2C_Kagawa.jpg" in a.links
assert "https://creativecommons.org/licenses/by/2.0" in a.links
assert "/things-to-do/takamatsu-cruise-udon-market-return/" in a.links
assert "도쿠시마·고치 음식 사진은 아님" in s
assert sum(x.get("src")=="/images/culture-verified/japan-kagawa-udon-pilgrimage.webp" for x in a.img)==1
assert (ROOT/"images/culture-verified/japan-kagawa-udon-pilgrimage.webp").is_file()
print("V301 PASS: full-width single card, original photo/license, SEO and landing URL preserved")
