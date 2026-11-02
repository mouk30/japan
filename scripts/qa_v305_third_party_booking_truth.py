#!/usr/bin/env python3
"""V305 external-user audit: accurate Nov 2026 fuel, source-matched visual cards,
direct official booking handoff and original metadata. New articles: ZERO.
"""
from html.parser import HTMLParser
from pathlib import Path
from hashlib import sha256
import re
ROOT=Path("site")
HOME=ROOT/"index.html"
BOOK=ROOT/"booking/index.html"
GUIDE=ROOT/"guide/busan-osaka-ferry/index.html"
FERRY=ROOT/"ferry/index.html"
PHOTO=[
 ("/images/venues/nf-v85-osaka-dotonbori-licensed.webp","오사카"),
 ("/images/venues/fukuoka-ohori-park.webp","후쿠오카"),
 ("/images/venues/v62-karato-market-real.webp","시모노세키"),
 ("/images/venues/nf-v124-tsushima-harbor-real.webp","대마도")
]
class Tags(HTMLParser):
 def __init__(self):
  super().__init__();self.images=[];self.links=[];self.h1=0;self.canonical=[];self.robots=[];self.descriptions=[];self.jsonld=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="img":self.images.append(a)
  if tag=="a":self.links.append(a.get("href",""))
  if tag=="h1":self.h1+=1
  if tag=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href",""))
  if tag=="meta" and a.get("name")=="robots":self.robots.append(a.get("content",""))
  if tag=="meta" and a.get("name")=="description":self.descriptions.append(a.get("content",""))
  if tag=="script" and a.get("type")=="application/ld+json":self.jsonld+=1
def parse(s):
 a=Tags();a.feed(s);return a
home=HOME.read_text(encoding="utf-8");booking=BOOK.read_text(encoding="utf-8")
guide=GUIDE.read_text(encoding="utf-8");ferry=FERRY.read_text(encoding="utf-8")
for slug,s in [("",home),("booking/",booking),("guide/busan-osaka-ferry/",guide)]:
 a=parse(s)
 assert a.h1==1,(slug,"lost main title")
 assert a.canonical==["https://www.nipponferry.com/"+slug],(slug,"canonical changed")
 assert len(a.descriptions)==1 and a.descriptions[0],(slug,"SEO description lost")
 assert not any("noindex" in v for v in a.robots),(slug,"noindexed")
 assert a.jsonld>=1,(slug,"structured data lost")
 assert 'id="nf-v148-photo-credits"' in s,(slug,"photo provenance panel lost")
 for src in (x.get("src","") for x in a.images):
  if src.startswith("/") and not src.startswith("//"):
   assert (ROOT/src.lstrip("/").split("?")[0]).is_file(),(slug,"broken image",src)
for label,html,cls in [("home",home,"nf247-route-photo"),("booking",booking,"bk-case-photo")]:
 cards=re.findall(r'<figure class="'+cls+r'">([\s\S]*?)</figure>',html)
 assert len(cards)==4,(label,"not four photo cards")
 for i,((src,city),card) in enumerate(zip(PHOTO,cards)):
  assert src in card,(label,"wrong city/place for card",i,city)
  assert city in card,(label,"place identification missing",i)
  assert "실사" in card or "실제" in card,(label,"real image caption missing",i)
  assert "선박" in card or i==3,(label,"actual boat/landmark distinction missing",i)
  assert "panstar-cruise-clean-2048.webp" not in card,(label,"AI stock image still leads booking cards")
  assert (ROOT/src.lstrip("/")).is_file(),(label,"photo physically missing",src)
 assert 'site.com' not in html,(label,"unexpected placeholder domain")
assert home.count('class="nf305-photo-rights"')==4,"homepage card source rights must be visible"
assert "/ferry/#nf-v148-photo-credits" in parse(home).links
assert "/#nf-v148-photo-credits" in parse(home).links
for url in ("https://www.kampuferry.co.jp/reserve/",
 "https://www.koreaferry.co.kr/rs/idv/reservation/calendar_index/1/2?country=2"):
 assert url in parse(home).links,("missing direct official link",url)
assert "https://www.kampuferry.co.jp/news/20261027systemmaintenance.html" in parse(home).links,"official notice must be preserved"
assert "이 사이트는 실시간 좌석 검색" in booking,"do not imply checkout capability"
assert "사진 원본·라이선스" in booking,"booking photo license guide missing"
for link in ["https://commons.wikimedia.org/wiki/File:D%C5%8Dtonbori_at_night%2C_Osaka_%2819551420339%29.jpg",
"https://commons.wikimedia.org/wiki/File:%C5%8Chori_Park_The_view_NNE_from_Ukimid%C5%8D_%C5%8Chorik%C5%8Den_Ch%C5%AB%C5%8D-ku_Fukuoka_20260609_154008.jpg",
"https://commons.wikimedia.org/wiki/File:Karato_Fish_Market,_Shimonoseki_-_Jun_24,_2023.jpg"]:
 assert link in parse(ferry).links,("missing photographer original",link)
assert "2026년 11월 1일 출항분부터" in guide
assert "부산 → 오사카 27,000원" in guide and "오사카 → 부산 2,700엔" in guide
assert "https://www.panstarcruise.com/support/notice/310" in parse(guide).links
assert "2026년 9월 적용 25,000원" in guide,"past surcharge needs explicit dated context"
assert "부산 오사카 페리 완벽를" not in guide,"template grammar error persists"
approved=ROOT/"images/panstar-cruise-clean-2048.webp"
assert approved.is_file()
assert sha256(approved.read_bytes()).hexdigest()=="bbcfa65a0e670060b5ce6fe79b2a9ea3272874b4d96f96799800ec9ccb631bdd","approved image hash changed"
print("V305 PASS: exact four licensed destination images, honest booking handoff, Nov 2026 surcharge, SEO and original rights")
