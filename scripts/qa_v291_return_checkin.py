#!/usr/bin/env python3
"""V291: source-backed return departure/check-in details; existing SEO and booking URLs stay intact."""
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path("site/booking")
DATA = {
    "osaka": {
        "canonical": "https://www.nipponferry.com/booking/osaka/",
        "official": [
            "https://www.panstarcruise.com/product/osaka/info",
            "https://www.panstarcruise.com/product/osaka/procedure",
            "https://www.panstarcruise.com/support/notice",
        ],
        "facts": ["15:00~16:10", "15:40~16:20", "17:00 (일본 현지시간)", "오사카 국제페리터미널", "1층 매표소"],
    },
    "tsushima": {
        "canonical": "https://www.nipponferry.com/booking/tsushima/",
        "official": [
            "https://www.panstarcruise.com/product/daemado/info",
            "https://www.panstarcruise.com/product/daemado/procedure",
            "https://www.panstarcruise.com/support/notice",
        ],
        "facts": ["2026년 11월 15일 이후 15:30", "출항 1시간 30분 전부터", "출항 30분 전 마감", "히타카츠", "이즈하라"],
    },
}

class Check(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = []
        self.canonical = []
        self.title = False
        self.description = False
        self.section = False
        self.table = False
        self.table_headers = 0
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if "id" in d:
            self.ids.append(d["id"])
            if d["id"] == "nf-v291-return":
                self.section = True
        if tag == "a":
            self.links.append(d.get("href", ""))
        if tag == "link" and d.get("rel") == "canonical":
            self.canonical.append(d.get("href"))
        if tag == "title":
            self.title = True
        if tag == "meta" and d.get("name") == "description" and d.get("content"):
            self.description = True
        if tag == "table":
            self.table = True
        if tag == "th":
            self.table_headers += 1

for name, expected in DATA.items():
    path = ROOT / name / "index.html"
    raw = path.read_text(encoding="utf-8")
    parsed = Check()
    parsed.feed(raw)
    assert parsed.title and parsed.description, f"{name}: SEO metadata missing"
    assert parsed.canonical == [expected["canonical"]], f"{name}: canonical changed"
    assert parsed.ids.count("nf-v291-return") == 1, f"{name}: missing or duplicated return panel"
    assert parsed.ids.count("nf-v291-return-title") == 1, f"{name}: missing return heading"
    assert parsed.table and parsed.table_headers >= 3, f"{name}: accessible return table missing"
    assert "aria-labelledby='nf-v291-return-title'" in raw, f"{name}: section label missing"
    assert "nf-v291-scroll" in raw and "overflow-x:auto" in raw, f"{name}: mobile table scroll missing"
    assert "2026년 11월 2일" in raw, f"{name}: source check date missing"
    assert "실시간 운항" in raw, f"{name}: live availability disclaimer missing"
    assert "마지막" in raw and "별도" in raw, f"{name}: unverified last transport not disclosed"
    assert "willer" not in raw.lower(), f"{name}: domestic ferry booking URL regression"
    assert "https://www.panstarcruise.com/" in parsed.links, f"{name}: booking CTA lost"
    for url in expected["official"]:
        assert url in parsed.links, f"{name}: missing source {url}"
    for phrase in expected["facts"]:
        assert phrase in raw, f"{name}: missing verified detail {phrase}"
    print(f"PASS V291 {path}: official return schedule, sources, SEO and booking CTA")
print("V291 PASS 2 / 2. This does not establish real-time sailing, seat availability, or last ground transport.")
