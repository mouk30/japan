#!/usr/bin/env python3
"""V304: source-level gate for existing /explore/ links, SEO and safe map fallback."""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import subprocess

ROOT = Path("site")
PAGE = ROOT / "explore/index.html"
html = PAGE.read_text(encoding="utf-8")
css = (ROOT / "nf-v304-explore-map.css").read_text(encoding="utf-8")
before = subprocess.check_output(["git", "show", "origin/main:site/explore/index.html"], text=True)

class Scan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1 = 0
        self.meta = {}
        self.links = []
        self.images = []
        self.jsonld = []
        self._ld = False
        self._buffer = ""
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "h1":
            self.h1 += 1
        if tag == "meta" and d.get("name") in ("description", "robots"):
            self.meta[d["name"]] = d.get("content")
        if tag == "link" and d.get("rel") == "canonical":
            self.meta["canonical"] = d.get("href")
        if tag == "img":
            self.images.append(d)
        if tag == "a":
            self.links.append(d.get("href", ""))
        if tag == "script" and d.get("type") == "application/ld+json":
            self._ld = True
            self._buffer = ""
    def handle_data(self, data):
        if self._ld:
            self._buffer += data
    def handle_endtag(self, tag):
        if tag == "script" and self._ld:
            self.jsonld.append(self._buffer)
            self._ld = False

def scan(text):
    p = Scan()
    p.feed(text)
    return p

old, new = scan(before), scan(html)
assert old.h1 == new.h1 == 1, "H1 changed"
assert old.meta == new.meta, "canonical/robots/description changed"
assert old.jsonld == new.jsonld, "JSON-LD changed"
assert old.images == new.images, "existing photos or attribution image attributes changed"
assert all(href in new.links for href in old.links), "original visible HTML link removed"
assert new.meta["canonical"] == "https://www.nipponferry.com/explore/"
assert 'nf-v304-explore-map.css' in html and 'nf304-explore' in html
assert 'aria-live="polite"' in html and 'aria-pressed="true"' in html
assert 'typeof L!=="undefined"' in html, "Leaflet fallback guard removed"
assert 'list.replaceChildren()' in html, "accessible link rendering removed"
assert 'locate.disabled=!map' in html, "map fallback buttons must be disabled"
assert html.count('document.body.classList.add("nf304-map-unavailable")') == 2, "blank-map fallback not hidden"
assert 'onclick=' not in html, "inline onclick would bypass accessible event handling"
assert "@media(max-width:900px)" in css and "@media(max-width:600px)" in css
assert "grid-template-columns:minmax(0,1fr)" in css, "mobile single-column cards missing"
assert "min-height:44px" in css, "minimum touch target missing"

match = re.search(r"const E=(\[[^;]+\]);", html)
assert match, "map dataset missing"
items = json.loads(match.group(1))
assert len(items) == 17, "map destination count changed"
assert len({row[0] for row in items}) == 17, "duplicate place names"
assert len({row[5] for row in items}) == 17, "duplicate destination URLs"
for name, lat, lon, region, description, href in items:
    assert -90 <= lat <= 90 and -180 <= lon <= 180, name
    assert href.startswith("/") and href.endswith("/") and not href.startswith("//"), (name, href)
    assert (ROOT / href.strip("/") / "index.html").is_file(), (name, "missing destination", href)
    assert href in new.links, (name, "missing static fallback link", href)
    assert description and region, name
    assert not any(token in description for token in ("마지막 버스 ", "실시간 잔여석", "예약 확정")), name

changed = subprocess.check_output(["git", "diff", "--name-only", "--diff-filter=A", "origin/main...HEAD"], text=True).splitlines()
assert not any(p.startswith("site/") and p.endswith(".html") for p in changed), "new article forbidden"
print("V304 PASS: 17 existing guide targets, static links, safe CDN fallback, SEO/JSON-LD/photo preservation")
