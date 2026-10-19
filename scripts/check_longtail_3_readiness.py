#!/usr/bin/env python3
"""Conservative SEO and launch checks for ONLY the three live long-tail trial pages.
This checks technical availability; it DOES NOT measure search traffic or bookings.
"""
import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
from xml.etree import ElementTree

ORIGIN = "https://www.nipponferry.com"
SLUGS = [
    "busan-hakata-ferry-reservation",
    "bukan-ferry-shimonoseki-price",
    "panstar-miracle-osaka-cabin-types",
]
PATHS = ["/japan-cruise/" + slug + "/" for slug in SLUGS]
USER_AGENT = "NIPPONFERRY-LaunchQA/1.0 (site operation verification)"

class HTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1 = 0
        self.description = []
        self.canonical = []
        self.robots = []
        self.links = []
        self.scripts = []
        self.ld_json = []
        self._in_ld = False
        self._ld = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "h1":
            self.h1 += 1
        if tag == "meta" and a.get("name", "").lower() == "description":
            self.description.append(a.get("content", ""))
        if tag == "meta" and a.get("name", "").lower() == "robots":
            self.robots.append(a.get("content", "").lower())
        if tag == "link" and "canonical" in a.get("rel", "").lower():
            self.canonical.append(a.get("href", ""))
        if tag == "a":
            self.links.append(a.get("href", ""))
        if tag == "script":
            self.scripts.append(a.get("src", ""))
            if a.get("type") == "application/ld+json":
                self._in_ld = True
                self._ld = []
    def handle_data(self, data):
        if self._in_ld:
            self._ld.append(data)
    def handle_endtag(self, tag):
        if tag == "script" and self._in_ld:
            try:
                self.ld_json.append(json.loads("".join(self._ld)))
            except ValueError:
                self.ld_json.append(None)
            self._ld = []
            self._in_ld = False

def fetch(url):
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=18) as response:
        return response.status, response.geturl(), response.read().decode("utf-8", "replace")

def read(mode, path):
    if mode == "static":
        f = Path("site") / path.lstrip("/")
        if path.endswith("/"):
            f = f / "index.html"
        return 200, ORIGIN + path, f.read_text(encoding="utf-8")
    last_error = None
    for attempt in range(2):
        try:
            return fetch(ORIGIN + path)
        except Exception as error:
            last_error = error
            if attempt == 0:
                time.sleep(2)
    raise last_error

def check_page(mode, path):
    row = {"path": path, "checks": {}, "errors": []}
    try:
        status, final_url, body = read(mode, path)
        p = HTML()
        p.feed(body)
        expected = ORIGIN + path
        row["checks"] = {
            "http_200": status == 200,
            "not_redirected_off_page": final_url.rstrip("/") == expected.rstrip("/"),
            "one_h1": p.h1 == 1,
            "has_description": any(p.description),
            "canonical_exact": p.canonical == [expected],
            "no_noindex": all("noindex" not in value for value in p.robots),
            "parseable_json_ld": len(p.ld_json) > 0 and all(x is not None for x in p.ld_json),
            "internal_booking_guide": "/booking/japan-cruise/" in p.links,
            "has_official_outbound": any(x.startswith("https://") and "nipponferry.com" not in x for x in p.links),
            "click_script_linked": "/nf-longtail-clicks.js" in p.scripts,
        }
        row["analytic_collector_detected"] = bool(re.search(
            r"googletagmanager\.com/(?:gtag/js|gtm\.js)|GTM-[A-Z0-9]{5,}|G-[A-Z0-9]{7,}|vercel/analytics",
            body, flags=re.I))
        row["notes"] = "Analytics collection is NOT proven by a loaded event script."
    except Exception as error:
        row["errors"].append(str(error))
        row["checks"]["page_accessible"] = False
    row["pass"] = not row["errors"] and all(row["checks"].values())
    return row

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["static", "live"], required=True)
    args = ap.parse_args()
    mode = args.mode
    rows = [check_page(mode, path) for path in PATHS]
    sitewide = {}
    try:
        _, _, sm = read(mode, "/sitemap.xml")
        tree = ElementTree.fromstring(sm)
        locations = {x.text for x in tree.findall(".//{*}loc")}
        sitewide["three_urls_in_sitemap"] = all(ORIGIN + p in locations for p in PATHS)
    except Exception as error:
        sitewide["three_urls_in_sitemap"] = False
        sitewide["sitemap_error"] = str(error)
    try:
        _, _, robots = read(mode, "/robots.txt")
        sitewide["robots_has_sitemap"] = ORIGIN + "/sitemap.xml" in robots
        sitewide["robots_no_global_disallow"] = not bool(re.search(
            r"(?im)^\s*Disallow:\s*/\s*$", robots))
    except Exception as error:
        sitewide["robots_has_sitemap"] = False
        sitewide["robots_no_global_disallow"] = False
        sitewide["robots_error"] = str(error)
    try:
        if mode == "static":
            data = Path("site/nf-longtail-clicks.js").read_text(encoding="utf-8")
            status = 200
        else:
            status, _, data = read(mode, "/nf-longtail-clicks.js")
        sitewide["click_script_accessible"] = status == 200 and "nf_travel_link_click" in data
    except Exception as error:
        sitewide["click_script_accessible"] = False
        sitewide["click_script_error"] = str(error)
    valid = all(x["pass"] for x in rows) and all(
        value is True for key, value in sitewide.items() if not key.endswith("_error"))
    report = {
        "date_utc": datetime.now(timezone.utc).isoformat(),
        "mode": mode, "status": "PASS" if valid else "FAIL",
        "pages_checked": len(rows), "pages_passed": sum(x["pass"] for x in rows),
        "sitewide": sitewide, "pages": rows,
        "scope": "Availability, metadata, indexability prerequisites and click-script delivery only.",
        "not_measured": ["Google impressions", "Naver impressions", "real clicks", "bookings", "sales"]
    }
    out = Path("audit-output/longtail-3")
    out.mkdir(parents=True, exist_ok=True)
    (out / (mode + "-readiness.json")).write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not valid:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
