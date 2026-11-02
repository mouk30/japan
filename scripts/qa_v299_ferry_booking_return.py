#!/usr/bin/env python3
"""V299: guard two existing Busan ferry guides and the official Shimonoseki booking CTA."""
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path("site")
GUIDES = {
    "busan-fukuoka-ferry": {
        "photo": "/images/venues/nf-v134-new-camellia-busan-2026-real.webp",
        "official": "https://www.koreaferry.kr/",
    },
    "busan-shimonoseki-ferry": {
        "photo": "/images/venues/nf-v135-shimonoseki-international-terminal-2021-real.webp",
        "official": "https://www.kampuferry.co.jp/reserve/",
    },
}
NOTICE = "https://www.kampuferry.co.jp/news/20261027systemmaintenance.html"


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.canonicals = []
        self.images = []
        self.h1 = 0
        self.primary = []
        self.secondary = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a":
            self.links.append(a.get("href", ""))
            classes = a.get("class", "").split()
            if "nf86-action-primary" in classes:
                self.primary.append(a.get("href", ""))
            if "nf86-action-secondary" in classes:
                self.secondary.append(a.get("href", ""))
        elif tag == "img":
            self.images.append(a.get("src", ""))
        elif tag == "h1":
            self.h1 += 1
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonicals.append(a.get("href", ""))


for slug, expected in GUIDES.items():
    html = (ROOT / "guide" / slug / "index.html").read_text(encoding="utf-8")
    page = Page()
    page.feed(html)
    assert page.h1 == 1, (slug, "H1 count")
    assert page.canonicals == [f"https://www.nipponferry.com/guide/{slug}/"], (slug, "canonical")
    assert expected["photo"] in page.images, (slug, "operator/terminal photo")
    assert (ROOT / expected["photo"].lstrip("/")).is_file(), (slug, "missing photo")
    assert expected["official"] in page.links, (slug, "official operator link")
    assert "페리 완벽를" not in html, (slug, "broken Korean introduction")
    assert all((ROOT / img.lstrip("/").split("?")[0]).is_file()
               for img in page.images if img.startswith("/images/")), (slug, "broken local image")
    assert "nf-v148-photo-credits" in html, (slug, "photo attribution missing")
    assert "site/images/panstar-cruise-clean-2048.webp" not in html, (slug, "unrelated PanStar image")
    if slug == "busan-shimonoseki-ferry":
        assert page.primary == [expected["official"]], (slug, "primary CTA must lead to official reservation method")
        assert page.secondary == [NOTICE], (slug, "secondary CTA must lead to dated resumption notice")
        assert "2026년 10월 27일 인터넷 예약 재개" in html, (slug, "official resumption context")
        assert "실시간 예약 조회가 아닙니다" in html, (slug, "live availability disclaimer")
        assert "https://www.kampuferry.co.jp/lang_kor/passenger_info/t_access/checkin.html" in page.links, (slug, "check-in source")
    print("PASS", slug, "canonical, photo, source, official booking and safe return")

print("V299 PASS: 2 existing guides; no new articles or guessed last-transport times")
