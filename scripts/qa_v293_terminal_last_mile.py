#!/usr/bin/env python3
"""V293 offline guard: operator-linked last-mile terminal guidance on existing pages only."""
from html.parser import HTMLParser
from pathlib import Path

DATA = {
    "fukuoka": {
        "canonical": "https://www.nipponferry.com/booking/fukuoka/",
        "official": ["https://hakataport.com/terminal/", "https://www.camellia-line.co.jp/boarding/"],
        "booking": "https://www.koreaferry.kr/",
        "facts": ["하카타항 국제터미널", "88번", "80번", "BRT", "오키하마마치 14-1", "막차 시간"],
    },
    "shimonoseki": {
        "canonical": "https://www.nipponferry.com/booking/shimonoseki/",
        "official": ["https://www.kampuferry.co.jp/passenger_info/t_access/", "https://kanmon.gr.jp/areamap/"],
        "booking": "https://www.kampuferry.co.jp/reserve/",
        "facts": ["시모노세키항 국제터미널", "도보 약 7분", "18:00", "마지막 열차"],
    },
    "osaka": {
        "canonical": "https://www.nipponferry.com/booking/osaka/",
        "official": ["https://www.panstar.jp/embarkation", "https://www.panstarcruise.com/product/osaka/info"],
        "booking": "https://www.panstarcruise.com/",
        "facts": ["코스모스퀘어역", "2번 승강장", "14:10", "14:30", "14:50", "15:10", "당일 운행·막차 보증이 아닙니다"],
    },
    "tsushima": {
        "canonical": "https://www.nipponferry.com/booking/tsushima/",
        "official": ["https://www.panstar.jp/tsushimalink/", "https://www.panstarcruise.com/support/notice"],
        "booking": "https://www.panstarcruise.com/",
        "facts": ["히타카츠항 국제터미널", "신이즈하라항 국제터미널", "341-24", "마지막 버스", "확인되지 않았으므로"],
    },
}
class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids=[]; self.links=[]; self.canonical=[]; self.title=0; self.meta=False
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if "id" in a: self.ids.append(a["id"])
        if tag=="a": self.links.append(a.get("href", ""))
        if tag=="link" and a.get("rel")=="canonical": self.canonical.append(a.get("href", ""))
        if tag=="title": self.title+=1
        if tag=="meta" and a.get("name")=="description" and a.get("content"): self.meta=True

for name, expected in DATA.items():
    raw=(Path("site/booking")/name/"index.html").read_text(encoding="utf-8")
    p=Page();p.feed(raw)
    assert p.title==1 and p.meta, f"{name}: SEO title/description regression"
    assert p.canonical==[expected["canonical"]], f"{name}: canonical regression"
    assert p.ids.count("nf-v293-access")==1, f"{name}: duplicate/missing access section"
    assert p.ids.count("nf-v293-title")==1, f"{name}: missing accessible heading"
    assert p.links.count("#nf-v293-access")==1, f"{name}: missing/duplicate nav link"
    assert expected["booking"] in p.links, f"{name}: booking CTA lost"
    assert "2026년 11월 2일" in raw, f"{name}: source date missing"
    assert "마지막" in raw or "막차" in raw, f"{name}: last-mile caution missing"
    assert "willer" not in raw.lower(), f"{name}: wrong domestic ferry booking regression"
    for url in expected["official"]:
        assert any(link.startswith(url) for link in p.links), f"{name}: missing source {url}"
    for fact in expected["facts"]:
        assert fact in raw, f"{name}: missing source-supported note {fact}"
    print(f"PASS V293 {name}: terminal access, source links, booking, SEO and last-mile cautions")
print("V293 PASS 4/4: static source-linked content only; no live last-bus or booking validation.")
