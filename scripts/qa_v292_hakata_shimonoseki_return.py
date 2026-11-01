#!/usr/bin/env python3
"""V292: offline regression checks for verified Hakata and Shimonoseki return check-in."""
from html.parser import HTMLParser
from pathlib import Path

DATA = {
    "fukuoka": {
        "canonical": "https://www.nipponferry.com/booking/fukuoka/",
        "sources": [
            "https://www.camellia-line.co.jp/boarding/",
            "https://www.camellia-line.co.jp/guide/",
        ],
        "facts": [
            "10:30~11:30", "18:00~19:00", "하카타항 국제터미널",
            "1층", "2층 출발 게이트", "오키하마마치 14-1",
        ],
        "booking": "https://www.koreaferry.kr/",
    },
    "shimonoseki": {
        "canonical": "https://www.nipponferry.com/booking/shimonoseki/",
        "sources": [
            "https://www.kampuferry.co.jp/lang_kor/passenger_info/t_access/checkin.html",
            "https://www.kampuferry.co.jp/lang_kor/passenger_info/schedule/",
            "https://www.kampuferry.co.jp/lang_kor/passenger_info/t_access/",
        ],
        "facts": [
            "15:00~18:00", "19:45", "08:00", "시모노세키 국제터미널",
            "히가시야마토마치 1-10-60", "18:00은",
        ],
        "booking": "https://www.kampuferry.co.jp/reserve/",
    },
}

class Tags(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.canonicals = []
        self.meta = set()
        self.title = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "a":
            self.links.append(a.get("href", ""))
        if tag == "link" and a.get("rel") == "canonical":
            self.canonicals.append(a.get("href", ""))
        if tag == "meta" and a.get("name") == "description" and a.get("content"):
            self.meta.add("description")
        if tag == "title":
            self.title += 1

for name, expected in DATA.items():
    path = Path("site/booking") / name / "index.html"
    raw = path.read_text(encoding="utf-8")
    parsed = Tags()
    parsed.feed(raw)
    assert parsed.title == 1 and "description" in parsed.meta, f"{name}: SEO metadata lost"
    assert parsed.canonicals == [expected["canonical"]], f"{name}: canonical changed"
    assert parsed.ids.count("nf-v292-return") == 1, f"{name}: return section missing/duplicate"
    assert "#nf-v292-return" in parsed.links, f"{name}: nav anchor missing"
    assert expected["booking"] in parsed.links, f"{name}: original booking CTA lost"
    assert "2026년 11월 2일" in raw, f"{name}: source check date missing"
    assert "마지막" in raw and "확인" in raw, f"{name}: unverified transport disclaimer missing"
    assert "실시간 좌석" in raw, f"{name}: false live-booking claim protection missing"
    assert "willer" not in raw.lower(), f"{name}: unrelated Japanese domestic booking regression"
    for url in expected["sources"]:
        assert url in parsed.links, f"{name}: official source missing: {url}"
    for phrase in expected["facts"]:
        assert phrase in raw, f"{name}: verified fact missing: {phrase}"
    print(f"PASS V292 {name}: return check-in, terminal, official sources, SEO and booking CTA")
print("V292 PASS 2/2. Static content checks only: no live ticket, timetable or last-bus verification.")
