#!/usr/bin/env python3
"""V309: original photo/SEO/link preservation and real-operator booking/return checks.
No new pages. Frozen operator sources crosschecked 2026-11-02; no live-seat guarantee.
"""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
from hashlib import sha256
import subprocess,json,re
ROOT=Path("site")
SLUGS=["booking","booking/osaka","booking/fukuoka","booking/shimonoseki","booking/tsushima","guide/busan-tsushima-ferry"]
OFFICIAL={
 "booking/osaka":("https://www.panstarcruise.com/","https://www.panstarcruise.com/product/osaka/procedure"),
 "booking/fukuoka":("https://www.koreaferry.co.kr/rs/idv/reservation/calendar_index/1/2?country=2","https://www.camellia-line.co.jp/boarding/"),
 "booking/shimonoseki":("https://www.kampuferry.co.jp/lang_kor/reserve/","https://www.kampuferry.co.jp/lang_kor/passenger_info/t_access/checkin.html"),
 "booking/tsushima":("https://www.panstarcruise.com/","https://www.panstarcruise.com/product/daemado/procedure")
}
class Parse(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.h2=0;self.canon=[];self.desc=[];self.robots=[];self.jsonld=[];self.images=[];self.links=[];self.ids=[];self._is_ld=False;self._lddata=""
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="h1":self.h1+=1
  if tag=="h2":self.h2+=1
  if tag=="link" and a.get("rel")=="canonical":self.canon.append(a.get("href"))
  if tag=="meta" and a.get("name")=="description":self.desc.append(a.get("content"))
  if tag=="meta" and a.get("name")=="robots":self.robots.append(a.get("content"))
  if tag=="a":self.links.append(a.get("href",""))
  if tag=="img":self.images.append(a)
  if "id" in a:self.ids.append(a["id"])
  if tag=="script" and a.get("type")=="application/ld+json":self._is_ld=True;self._lddata=""
 def handle_data(self,data):
  if self._is_ld:self._lddata+=data
 def handle_endtag(self,tag):
  if tag=="script" and self._is_ld:self.jsonld.append(json.loads(self._lddata));self._is_ld=False
def parse(txt):
 p=Parse();p.feed(txt);return p
css=(ROOT/"nf-v309-booking-safe-return.css").read_text(encoding="utf8")
for selector in [".nf309-journey__grid",".nf309-journey__step",".nf309-journey__actions",".nf309-compare",".nf309-route","@media(max-width:720px)"]:
 assert selector in css,("missing scoped selector",selector)
for slug in SLUGS:
 path=ROOT/slug/"index.html"
 s=path.read_text(encoding="utf8")
 before=subprocess.check_output(["git","show","origin/main:"+str(path)],text=True)
 p,o=parse(s),parse(before)
 assert p.h1==o.h1==1,(slug,"H1")
 assert p.canon==o.canon==["https://www.nipponferry.com/"+slug+"/"],(slug,"canonical")
 assert p.desc==o.desc and p.robots==o.robots,(slug,"metadata unexpectedly changed")
 assert p.jsonld==o.jsonld,(slug,"JSON-LD changed")
 assert p.images==o.images,(slug,"image/alt/source modified")
 assert not (Counter(o.links)-Counter(p.links)),(slug,"existing reservation/rights link lost",Counter(o.links)-Counter(p.links))
 assert len(p.ids)==len(set(p.ids)),(slug,"duplicate id")
 for img in p.images:
  src=img.get("src","")
  if src.startswith("/") and not src.startswith("//"):
   assert (ROOT/src.lstrip("/").split("?")[0]).exists(),(slug,"local photo missing",src)
 if slug.startswith("booking"):
  assert "nf-v309-booking-safe-return.css?v=20261102" in s,(slug,"CSS missing")
  assert s.count('id="nf309-booking-return"')== (0 if slug=="booking" else 1),(slug,"route panel missing")
  assert s.count('id="nf309-before-return"')== (1 if slug=="booking" else 0),(slug,"hub panel missing")
  assert "NIPPONFERRY는" in s and "실시간" in s,(slug,"nonbooking disclaimer missing")
  if slug=="booking":
   assert s.count('class="nf309-route"')==4,("all four booking routes")
   for city in ("오사카","하카타","시모노세키","대마도"):assert city in s,city
  else:
   assert s.count('class="nf309-journey__step"')==3,(slug,"three-step guide")
   for source in OFFICIAL[slug]:
    assert source in p.links,(slug,"operator link missing",source)
   assert "마지막" in s,(slug,"actual return transport caveat")
 else:
  assert "2026년 11월 1일 출항분부터" in s
  for amt in ("16,000원","27,000원","1,600엔","2,700엔"):
   assert amt in s,("missing Nov Tsushima fuel",amt)
  assert "15,000원" not in s and "25,000원" not in s,("stale old outgoing surcharge")
  assert "2026년 11월 15일 이후" in s
  assert "출항 90분 전" in s and "30분 전" in s
  assert "https://www.panstarcruise.com/support/notice/309" in p.links
  assert "https://www.panstarcruise.com/product/daemado/procedure" in p.links
  assert "완벽를" not in s,(slug,"templated Korean grammar")
  assert "2026년 10월 20~21일 결항" in s,(slug,"historical service cancellation context missing")
 print("PASS",slug,"factual source, return and SEO/photo preservation")
approved=ROOT/"images/panstar-cruise-clean-2048.webp"
assert approved.is_file(),"blocked: approved original not committed"
assert sha256(approved.read_bytes()).hexdigest()=="bbcfa65a0e670060b5ce6fe79b2a9ea3272874b4d96f96799800ec9ccb631bdd","blocked: PanStar original mismatch"
assert not subprocess.check_output(["git","diff","--name-only","--diff-filter=A","origin/main...HEAD"],text=True).splitlines().__contains__("site/guide/new.html")
print("V309 PASS: six existing pages, no new article, approved original intact")
