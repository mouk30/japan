#!/usr/bin/env python3
"""V297 image loading stability checks. No article, image, route, link or SEO changes."""
from pathlib import Path
from html.parser import HTMLParser
import json

ROOT = Path("site")
PAGES = [
    "index.html",
    "booking/index.html", "booking/japan-cruise/index.html",
    "booking/fukuoka/index.html", "booking/osaka/index.html",
    "booking/shimonoseki/index.html", "booking/tsushima/index.html",
    "guide/busan-fukuoka-ferry/index.html",
    "guide/busan-osaka-ferry/index.html",
    "guide/busan-shimonoseki-ferry/index.html",
    "things-to-do/cruise-ports/index.html",
]
class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.canonical = []
        self.links = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "img":
            self.images.append(a)
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical.append(a.get("href"))
        if tag == "a":
            self.links.append(a.get("href"))

results = []
for page in PAGES:
    path = ROOT / page
    html = path.read_text(encoding="utf-8")
    doc = Images()
    doc.feed(html)
    assert len(doc.canonical) == 1, (page, "canonical missing/duplicate")
    assert doc.canonical[0] == "https://www.nipponferry.com/" + ("" if page == "index.html" else page.removesuffix("index.html")), (page, "canonical changed")
    if page.endswith("cruise-ports/index.html"):
        assert len(doc.images) >= 140, "expected existing cruise-port cards"
        assert all(x.get("decoding") == "async" for x in doc.images), "decode flag missing"
        assert all(x.get("alt") for x in doc.images), "cruise port alt missing"
        assert all(x.get("width") and x.get("height") for x in doc.images), "cruise port size missing"
    else:
        kakao = [x for x in doc.images if x.get("src") == "/images/kakao-talk.jpg"]
        assert len(kakao) <= 1, (page, "duplicate Kakao image")
        for img in kakao:
            assert img.get("width") == "512" and img.get("height") == "512", (page, "Kakao dimensions")
            assert img.get("loading") == "lazy" and img.get("decoding") == "async", (page, "Kakao loading")
    if page == "index.html":
        for source, size in (
            ("/images/kimono.jpg", ("1600", "1000")),
            ("/images/culture-verified/family-with-kids.webp", ("1000", "671")),
        ):
            items = [i for i in doc.images if i.get("src") == source]
            assert len(items) == 1 and (items[0].get("width"), items[0].get("height")) == size, (page, source)
        assert "/booking/japan-cruise/" in doc.links, "homepage booking CTA lost"
    assert all(
        (ROOT / i["src"].lstrip("/").split("?")[0]).exists()
        for i in doc.images
        if i.get("src", "").startswith("/")
    ), (page, "missing local image file")
    results.append({"page": page, "images": len(doc.images), "canonical": doc.canonical[0], "pass": True})
    print("PASS", page, len(doc.images), "images")
out = Path("audit-output/v297")
out.mkdir(parents=True, exist_ok=True)
(out / "image-stability-report.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
print("V297 PASS", len(results), "pages; no new URLs")
