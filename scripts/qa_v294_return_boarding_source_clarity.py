#!/usr/bin/env python3
"""V294 offline regression: official return check-in and shuttle direction clarity.

This checks page content and SEO structure only; it does not certify live operations.
The separate V287 image gate remains mandatory and intentionally blocks deployment
until the approved PanStar WebP is committed.
"""
from pathlib import Path
from html.parser import HTMLParser
from html import unescape
import re

DATA = {
    "fukuoka": {
        "section": "nf-v292-return",
        "facts": ["출발 시각 60분 전까지 수속 완료", "여권과 예약내역", "10:30~11:30", "18:00~19:00", "마지막 운행 시각은 확인되지"],
        "sources": ["https://www.camellia-line.co.jp/boarding/"],
        "booking": "https://www.koreaferry.kr/",
    },
    "shimonoseki": {
        "section": "nf-v292-return",
        "facts": ["현금만 가능(신용카드 불가)", "시설사용료", "유가할증료", "국제관광여객세", "15:00~18:00"],
        "sources": ["https://www.kampuferry.co.jp/lang_kor/passenger_info/t_access/checkin.html"],
        "booking": "https://www.kampuferry.co.jp/reserve/",
    },
    "osaka": {
        "section": "nf-v293-access",
        "facts": ["코스모스퀘어역 → 국제페리터미널 출발편", "터미널 → 코스모스퀘어역 셔틀", "입국심사 중 터미널 방송", "14:10~15:10", "당일 운행·막차 보증이 아닙니다"],
        "sources": ["https://www.panstar.jp/embarkation"],
        "booking": "https://www.panstarcruise.com/",
    },
}
class Tags(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[]; self.ids=[]; self.canonical=[]; self.description=0; self.titles=0
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if "id" in a: self.ids.append(a["id"])
        if tag=="a": self.links.append(a.get("href", ""))
        if tag=="link" and a.get("rel")=="canonical": self.canonical.append(a.get("href"))
        if tag=="meta" and a.get("name")=="description" and a.get("content"): self.description+=1
        if tag=="title": self.titles+=1

for name, cfg in DATA.items():
    path=Path("site/booking")/name/"index.html"
    raw=path.read_text(encoding="utf-8")
    parsed=Tags(); parsed.feed(raw)
    assert parsed.titles==1 and parsed.description==1, f"{name}: SEO title/description regression"
    assert parsed.canonical==[f"https://www.nipponferry.com/booking/{name}/"], f"{name}: canonical regression"
    assert cfg["booking"] in parsed.links, f"{name}: booking CTA lost"
    assert parsed.ids.count(cfg["section"])==1, f"{name}: target section missing/duplicated"
    match=re.search(r"<section\b[^>]*\bid=['\"]"+re.escape(cfg["section"])+r"['\"][^>]*>(.*?)</section>", raw, re.S)
    assert match, f"{name}: section HTML not found"
    html=match.group(1)
    visible=unescape(re.sub(r"<[^>]*>", "", html))
    for fact in cfg["facts"]:
        assert fact in visible, f"{name}: missing verified detail: {fact}"
    for url in cfg["sources"]:
        assert url in html and url in parsed.links, f"{name}: source link lost: {url}"
    assert html.count("<strong>")==html.count("</strong>"), f"{name}: strong markup mismatch"
    assert "willer" not in raw.lower(), f"{name}: incorrect Japan domestic booking provider"
    assert "/images/panstar-cruise-clean-2048.webp" in raw, f"{name}: approved hero reference lost"
    print(f"PASS V294 {name}: check-in/payment/shuttle details, official source, SEO, booking link")
print("V294 PASS 3/3 static page checks. Not a live timetable, availability, photo license or image decode verification.")
