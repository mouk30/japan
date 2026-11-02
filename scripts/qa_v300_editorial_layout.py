#!/usr/bin/env python3
"""V300: existing-page only responsive editorial + route-photo/source regression."""
from pathlib import Path
from hashlib import sha256
from html.parser import HTMLParser
import re
ROOT=Path("site")
PANSTAR=ROOT/"images/panstar-cruise-clean-2048.webp"
assert PANSTAR.is_file(),"Approved PanStar original missing: do not merge or deploy"
assert sha256(PANSTAR.read_bytes()).hexdigest()=="bbcfa65a0e670060b5ce6fe79b2a9ea3272874b4d96f96799800ec9ccb631bdd","Approved original PanStar SHA-256 differs: DO NOT MERGE"
PAGES=[
    "", "booking", "booking/osaka", "booking/fukuoka", "booking/shimonoseki",
    "booking/tsushima", "booking/japan-cruise", "japan-cruise",
    "things-to-do/travel-companions",
]
PHOTO_MAP={
    "/images/panstar-cruise-clean-2048.webp":"AI",
    "/images/venues/nf-v134-new-camellia-busan-2026-real.webp":"real",
    "/images/venues/nf-v135-shimonoseki-international-terminal-2021-real.webp":"real",
    "/images/venues/nf-v124-tsushima-harbor-real.webp":"real",
    "/images/venues/nf-v85-osaka-dotonbori-licensed.webp":"real",
    "/images/venues/fukuoka-ohori-park.webp":"real",
    "/images/venues/v62-karato-market-real.webp":"real",
}
class Tags(HTMLParser):
    def __init__(self):
        super().__init__();self.h1=0;self.canonicals=[];self.links=[];self.images=[];self.styles=[]
    def handle_starttag(self,t,attrs):
        a=dict(attrs)
        if t=="h1":self.h1+=1
        if t=="link" and a.get("rel")=="canonical":self.canonicals.append(a.get("href"))
        if t=="a":self.links.append(a.get("href",""))
        if t=="img":self.images.append(a)
        if t=="link" and a.get("rel")=="stylesheet":self.styles.append(a.get("href",""))
css=(ROOT/"nf-v300-editorial-rebalance.css").read_text()
for token in [".bk-case-grid",".companion-main .guide-grid",".nf247-route-photo",".nf298-banner-img","@media(max-width:720px)"]:
    assert token in css,("missing responsive selector",token)
for slug in PAGES:
    p=ROOT/slug/"index.html" if slug else ROOT/"index.html"
    html=p.read_text(encoding="utf-8")
    parsed=Tags();parsed.feed(html)
    url=f"https://www.nipponferry.com/{slug + '/' if slug else ''}"
    assert parsed.canonicals==[url],(slug,"canonical")
    assert parsed.h1==1,(slug,"h1")
    assert "nf300-editorial" in html,(slug,"opt in")
    assert any("nf-v300-editorial-rebalance.css" in x for x in parsed.styles),(slug,"CSS")
    assert "<meta name=" in html or "<meta " in html,(slug,"SEO header")
    assert "nf298-banner-img" in html if slug in ["booking","booking/osaka","booking/fukuoka","booking/shimonoseki","booking/tsushima","booking/japan-cruise","japan-cruise"] else True
    if slug.startswith("booking") or slug=="japan-cruise":
        assert "willer-travel.com/ko/ferry/" not in html or slug not in ["booking","booking/osaka","booking/fukuoka","booking/shimonoseki","booking/tsushima"],(slug,"obsolete booking")
    for img in parsed.images:
        src=img.get("src","")
        if src in PHOTO_MAP:
            assert (ROOT/src.lstrip("/")).is_file(),(slug,"asset missing",src)
            assert img.get("alt"),(slug,"missing alt",src)
    if slug=="booking":
        assert html.count('class="bk-case-card"')==4
        for link in ["/booking/osaka/","/booking/fukuoka/","/booking/shimonoseki/","/booking/tsushima/"]:
            assert link in parsed.links,(slug,"missing route link",link)
        assert "AI 제작 연출 이미지" in html,("approved banner illustration disclosure lost")
        assert "시모노세키 가라토시장 실사" in html,("destination thumbnail missing")
        assert "이 사이트는 실시간 좌석 검색" in html,("false booking capability implication")
        assert html.count('class="bk-case-photo"')==4,("booking photo count")
        assert "/ferry/#nf-v148-photo-credits" in parsed.links,("license/source link lost")
    if not slug:
        assert html.count('class="nf247-route-photo"')==4
        assert html.count('class="nf305-photo-rights"')==4,("route photo rights")
        assert 'data-nf247-finder' in html,("route chooser JS contract changed")
        assert "https://www.kampuferry.co.jp/reserve/" in parsed.links,("official Shimonoseki reservation method")
        assert "www.koreaferry.co.kr/rs/idv/reservation/" in "\n".join(parsed.links),("official New Camellia search")
    if slug=="things-to-do/travel-companions":
        assert html.count('class="guide-card"')>=45,("guides dropped")
        assert all('href="/things-to-do/' in html for _ in [0])
    print("PASS",slug or "/", "H1 canonical CSS images/links retained")
print("V300 static PASS: 9 existing pages, new articles 0")
