#!/usr/bin/env python3
"""V297: static regression gate for official November 2026 fuel fees and return details on two existing guides."""
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path("site/guide")
CASES = {
    "busan-osaka-ferry": {
        "official": "https://www.panstarcruise.com/support/notice/310",
        "booking": "/booking/osaka/",
        "facts": ["2026년 11월 1일", "27,000원", "2,700엔", "15:00~16:10", "15:40~16:20", "17:00"],
        "old": ["유류할증료 · 2026년 9월 1일", "9월부터 25,000원"],
    },
    "busan-tsushima-ferry": {
        "official": "https://www.panstarcruise.com/support/notice/309",
        "booking": "/booking/tsushima/",
        "facts": ["2026년 11월 1일", "16,000원", "27,000원", "1,600엔", "2,700엔", "11월 15일", "15:30", "이즈하라", "히타카츠"],
        "old": ["유류할증료 · 2026년 9월 1일", "이후 정상 운항 여부는 확인된 바가 없으므로"],
    },
}

class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.canonicals = []
        self.h1 = 0
        self.images = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a": self.links.append(a.get("href", ""))
        if tag == "link" and a.get("rel") == "canonical": self.canonicals.append(a.get("href", ""))
        if tag == "h1": self.h1 += 1
        if tag == "img": self.images.append(a.get("src", ""))

for slug, case in CASES.items():
    path = ROOT / slug / "index.html"
    html = path.read_text(encoding="utf-8")
    parser = Tags()
    parser.feed(html)
    assert parser.h1 == 1, (slug, "H1")
    assert parser.canonicals == [f"https://www.nipponferry.com/guide/{slug}/"], (slug, "canonical")
    assert case["official"] in parser.links, (slug, "official November notice missing")
    assert case["booking"] in parser.links, (slug, "internal booking checklist missing")
    assert "https://www.panstarcruise.com/" in parser.links, (slug, "official booking site missing")
    assert 'data-verified-on="2026-11-02"' in html, (slug, "review date")
    assert "최종 대조일: 2026-11-02" in html, (slug, "source review date")
    assert "실시간 운항·요금·예약 가능 여부는 선사에서 별도로 확인하세요" in html, (slug, "no live-availability claim")
    assert all(term in html for term in case["facts"]), (slug, "official facts")
    assert all(term not in html for term in case["old"]), (slug, "stale live guidance")
    assert "site/images/panstar-cruise-clean-2048.webp" not in html, (slug, "must not bypass image gate")
    for src in parser.images:
        if src.startswith("/images/"):
            assert (Path("site") / src.lstrip("/").split("?")[0]).is_file(), (slug, "missing image", src)
    print("PASS", slug, "official surcharge, return, canonical, links, image references")
print("V297 PASS: 2 existing guides; no new articles; no image-dependent deployment")
