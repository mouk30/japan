#!/usr/bin/env python3
"""V289: cruise booking entry-page link/SEO and operator-image transparency audit.
Static evidence only; does not prove third-party booking availability, photography rights, or real-world timetables.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json

ROOT = Path("site")
ROUTES = (
    "/japan-cruise/", "/booking/", "/booking/japan-cruise/",
    "/booking/fukuoka/", "/booking/osaka/", "/booking/shimonoseki/", "/booking/tsushima/",
)
DOMAIN = "www.nipponferry.com"
OUT = Path("audit-output/v289")
OUT.mkdir(parents=True, exist_ok=True)

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.in_title = False
        self.links = []
        self.meta = []
        self.images = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "a":
            self.links.append({"href": a.get("href", ""), "text": ""})
        elif tag == "meta":
            self.meta.append(a)
        elif tag == "link":
            self.meta.append(a)
        elif tag == "img":
            self.images.append(a)
    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
    def handle_data(self, data):
        if self.in_title:
            self.title += data

def target_for(href):
    """Return a local target path, or None for third-party/fragment-only links."""
    if not href or href.startswith("#"):
        return None
    u = urlsplit(href)
    if u.scheme and u.scheme not in ("http", "https"):
        return None
    if u.netloc and u.netloc.lower() not in (DOMAIN, "nipponferry.com"):
        return None
    path = unquote(u.path)
    if not path.startswith("/"):
        return None
    if path.endswith("/"):
        return ROOT / path.lstrip("/") / "index.html"
    target = ROOT / path.lstrip("/")
    if target.is_dir():
        return target / "index.html"
    return target

reports = []
failures = []
for route in ROUTES:
    filename = ROOT / route.lstrip("/") / "index.html"
    raw = filename.read_text(encoding="utf-8")
    parser = Page()
    parser.feed(raw)
    canonical = [m.get("href") for m in parser.meta if m.get("rel", "").lower() == "canonical"]
    description = [m.get("content", "") for m in parser.meta if m.get("name", "").lower() == "description"]
    robots = " ".join(m.get("content", "") for m in parser.meta if m.get("name", "").lower() == "robots")
    errors = []
    if len(canonical) != 1 or canonical[0] != "https://" + DOMAIN + route:
        errors.append("canonical_missing_or_mismatched")
    if not parser.title.strip() or len(parser.title.strip()) < 12:
        errors.append("title_missing_or_short")
    if not description or len(description[0].strip()) < 30:
        errors.append("meta_description_missing_or_short")
    if "noindex" in robots.lower():
        errors.append("accidental_noindex")
    if "nf-v289-hero-caption" not in raw or "연출 이미지" not in raw:
        errors.append("illustrative_image_not_labeled")
    missing = []
    for a in parser.links:
        target = target_for(a["href"])
        if target is not None and not target.is_file():
            missing.append({"href": a["href"], "expected": str(target)})
    for image in parser.images:
        target = target_for(image.get("src", ""))
        if target is not None and not target.is_file():
            missing.append({"href": image.get("src"), "expected": str(target), "kind": "img"})
    if missing:
        errors.append("broken_local_links_or_images")
    operator_warning = None
    if route in ("/booking/fukuoka/", "/booking/shimonoseki/"):
        operator_warning = "PanStar illustration does not depict the actual vessel of this operator/route; route-specific verified photo remains pending"
        if "실제 운항 선박 사진이 아니며" not in raw:
            errors.append("route_operator_mismatch_disclaimer_missing")
    row = {
        "route": route, "canonical": canonical, "title": parser.title.strip(),
        "description": description[:1], "local_link_count": sum(target_for(a["href"]) is not None for a in parser.links),
        "missing_local": missing, "errors": errors, "operator_image_review": operator_warning,
    }
    reports.append(row)
    failures.extend({"route": route, "error": err} for err in errors)

report = {
    "scope": "V289 existing seven cruise/booking entry pages; no new content",
    "checked": len(reports), "failed": len(failures), "failures": failures, "pages": reports,
    "limitations": [
        "External URLs were inventoried but not confirmed live",
        "Official booking conditions, port changes, and last return transport require operator-source review",
        "PanStar image is illustrative; photo licensing and real vessel identity not independently verified",
        "Approved image SHA/decode and responsive screenshots are enforced by V287/V288, not this test",
    ],
}
(OUT / "booking-seo-links.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"V289: {len(reports)} entry pages, {len(failures)} static SEO/local-link/caption errors")
for failure in failures:
    print("FAIL", failure)
if failures:
    raise SystemExit(1)
