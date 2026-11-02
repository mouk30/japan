#!/usr/bin/env python3
"""V297: make Busan-bound booking CTAs honest and verify first-timer hero/source."""
from html.parser import HTMLParser
from pathlib import Path
import re
ROOT=Path("site")
PAGES={
  "booking/budget":3,
  "booking/cabin-comparison":1,
  "booking/checkin":3,
  "booking/couple":3,
  "booking/family-cabin":1,
  "booking/family":3,
  "booking/ferry-route-cost":1,
  "booking/first-timer":3,
  "booking/overnight-ferry":1,
  "booking/room":3,
  "booking/solo-cabin":1,
  "booking/trip-cost-calculator":2,
}
class Page(HTMLParser):
 def __init__(self):
  super().__init__();self.links=[];self.h1=0;self.canon=[];self.descriptions=[];self.images=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="a": self.links.append((a.get("href",""),a.get("target")))
  if tag=="h1": self.h1+=1
  if tag=="link" and "canonical" in a.get("rel",""): self.canon.append(a.get("href"))
  if tag=="meta" and a.get("name")=="description":self.descriptions.append(a.get("content"))
  if tag=="img":self.images.append(a)
total=0
for slug,n in PAGES.items():
 file=ROOT/slug/"index.html";s=file.read_text(encoding="utf-8")
 p=Page();p.feed(s)
 guide=[u for u,target in p.links if u=="/booking/japan-cruise/"]
 assert len(guide)>=n,(slug,"missing route-specific booking guide CTAs",len(guide),n)
 assert "willer-travel.com/ko/ferry/" not in s,(slug,"Japanese domestic booking link remains")
 assert p.h1==1,(slug,"heading structure")
 assert p.canon==["https://www.nipponferry.com/"+slug+"/"],(slug,"canonical")
 assert len(p.descriptions)==1 and len(p.descriptions[0])>30,(slug,"meta")
 assert not any(u=="/booking/japan-cruise/" and target=="_blank" for u,target in p.links),(slug,"internal CTA must remain same-tab")
 total+=n
first=(ROOT/"booking/first-timer/index.html").read_text(encoding="utf-8")
assert "/images/ferry.jpg" not in first,"legacy hero image was not removed"
assert "src='/images/venues/nf-v134-new-camellia-busan-2026-real.webp'" in first
assert (ROOT/"images/venues/nf-v134-new-camellia-busan-2026-real.webp").is_file()
assert "object-fit:contain" in first and "flex-direction:column" in first,"full vessel responsive rules missing"
assert "Midnight cadet" in first and "CC BY 4.0" in first
assert "commons.wikimedia.org/wiki/File:" in first and "creativecommons.org/licenses/by/4.0/" in first
assert "팬스타호 사진은 아닙니다" in first
assert (ROOT/"booking/japan-cruise/index.html").exists(),"internal landing missing"
print(f"V297 PASS: {len(PAGES)} existing guides, {total} corrected CTAs, canonical/H1/meta preserved; verified photo provenance and no-crop CSS")
