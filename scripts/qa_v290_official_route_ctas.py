#!/usr/bin/env python3
"""V290: protect four existing Busan ferry route CTAs from generic, wrong-route booking destinations.

Static regression gate only: verifies markup, not live seats, booking completion or operator site uptime.
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json

ROOT = Path("site/booking")
ROUTES = {
    "fukuoka": ("https://www.koreaferry.kr/", "고려훼리"),
    "osaka": ("https://www.panstarcruise.com/", "팬스타"),
    "shimonoseki": ("https://www.kampuferry.co.jp/reserve/", "관부훼리"),
    "tsushima": ("https://www.panstarcruise.com/", "팬스타"),
}
WRONG_GENERIC = "willer-travel.com/ko/ferry/"
IMAGE = "/images/panstar-cruise-clean-2048.webp"

class Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.active = None
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.active = {"attrs": dict(attrs), "label": ""}
    def handle_data(self, text):
        if self.active is not None:
            self.active["label"] += text
    def handle_endtag(self, tag):
        if tag == "a" and self.active is not None:
            self.links.append(self.active)
            self.active = None

rows, failures = [], []
for route, (official, operator) in ROUTES.items():
    path = ROOT / route / "index.html"
    html = path.read_text(encoding="utf-8")
    parser = Anchors()
    parser.feed(html)
    errors = []
    if WRONG_GENERIC in html:
        errors.append("generic_japan_ferry_aggregator_used_as_route_booking")
    official_ctas = [
        link for link in parser.links
        if link["attrs"].get("href") == official and (
            "공식" in link["label"] or "예약" in link["label"] or "날짜" in link["label"]
        )
    ]
    if len(official_ctas) < 2:
        errors.append("operator_official_booking_ctas_missing_or_wrong")
    if not any(link["attrs"].get("class") == "bk-primary" for link in official_ctas):
        errors.append("primary_booking_cta_not_operator_official")
    if not any("예약" in link["label"] or "날짜" in link["label"] for link in official_ctas):
        errors.append("operator_cta_label_not_actionable")
    for link in official_ctas:
        attrs = link["attrs"]
        if attrs.get("target") == "_blank" and "noopener" not in attrs.get("rel", "").split():
            errors.append("external_tab_missing_noopener")
        if urlsplit(attrs["href"]).scheme != "https":
            errors.append("official_url_not_https")
    if "nf-v290-route-note" not in html or "선사에서 재확인" not in html:
        errors.append("booking_uncertainty_disclaimer_missing")
    if IMAGE not in html or "연출 이미지" not in html:
        errors.append("approved_artwork_or_illustration_disclaimer_missing")
    canonical = f"https://www.nipponferry.com/booking/{route}/"
    if canonical not in html:
        errors.append("canonical_missing")
    if "<h1>" not in html or "</h1>" not in html:
        errors.append("h1_missing")
    row = {"route": route, "operator": operator, "official_booking_guidance": official,
           "official_cta_count": len(official_ctas), "errors": errors}
    rows.append(row)
    failures.extend({"route": route, "error": e} for e in errors)

out = Path("audit-output/v290")
out.mkdir(parents=True, exist_ok=True)
(out / "official-route-cta.json").write_text(json.dumps({
    "scope": "four existing Busan departure route booking pages; no new articles",
    "pages": rows, "failures": failures,
    "limitations": [
        "Static CTA URL and labels only; does not confirm external availability or actual ticket purchase",
        "PanStar artwork still pending exact binary upload and V287/V288 image gates",
        "Operator sailing schedules, port changes and last-return transport must be checked for travel date",
    ]
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"V290: {len(rows)} existing routes checked, {len(failures)} CTA integrity errors")
for failure in failures:
    print("FAIL", failure)
if failures:
    raise SystemExit(1)
