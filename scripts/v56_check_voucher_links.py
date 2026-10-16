#!/usr/bin/env python3
"""V56: monitor 13 cruise-port issuance links and 11 shopping-coupon links.

This checks technical HTTP reachability, NOT inventory, price, validity, or voucher issuance.
HTTP 403/429 anti-bot responses are 'restricted', not 'broken'.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PORT_PAGE = SITE / "voucher/cruise-ports/index.html"
COUPON_PAGE = SITE / "voucher/index.html"
REPORT_PATH = ROOT / "audit-reports/v56/link-health.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; NIPPONFERRY-link-audit/1.0; +https://www.nipponferry.com/voucher/)",
    "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
    "Accept-Language": "ja,en;q=0.8,ko;q=0.7",
}


def attr(text: str, key: str) -> str | None:
    found = re.search(r'\b' + re.escape(key) + r'="([^"]*)"', text)
    return found.group(1) if found else None


def collect() -> tuple[list[dict], list[dict], list[dict]]:
    port_html = PORT_PAGE.read_text(encoding="utf-8")
    coupon_html = COUPON_PAGE.read_text(encoding="utf-8")
    ports: list[dict] = []
    external: list[dict] = []
    internal: list[dict] = []

    blocks = re.findall(r'<article class="v52-port-card"([^>]*)>(.*?)</article>', port_html, re.S)
    assert len(blocks) == 13, f"Expected 13 port cards, got {len(blocks)}"
    for attrs, body in blocks:
        port_id = attr(attrs, "id")
        assert port_id, "Port card has no ID"
        primary = re.search(r'<a\b[^>]*class="v52-primary"[^>]*>', body)
        assert primary, f"Missing purchase/issuance CTA: {port_id}"
        url = attr(primary.group(0), "href")
        assert url, f"CTA has no href: {port_id}"
        url = url.replace("&amp;", "&")
        assert url.startswith("https://"), f"Non-HTTPS primary URL: {port_id}: {url}"
        ports.append({"id": port_id, "primary_url": url})
        external.append({"kind": "port_primary", "id": port_id, "url": url})
        for u in re.findall(r'<a[^>]+href="(https?://[^"]+)"', body):
            u = u.replace("&amp;", "&")
            if u != url:
                external.append({"kind": "port_official_reference", "id": port_id, "url": u})
        for u in re.findall(r'<a[^>]+href="(/[^"]+)"', body):
            internal.append({"source": f"port_{port_id}", "href": u})

    coupon_blocks = re.findall(r'<article class="v51-card"([^>]*)>(.*?)</article>', coupon_html, re.S)
    assert len(coupon_blocks) == 11, f"Expected 11 coupons, got {len(coupon_blocks)}"
    for i, (attrs, body) in enumerate(coupon_blocks, 1):
        url = re.search(r'<a class="v51-cta" href="([^"]+)"', body)
        assert url, f"Missing coupon CTA #{i}"
        external.append({"kind": "shopping_coupon", "id": f"coupon-{i}", "url": url.group(1).replace("&amp;", "&")})

    assert len({x["id"] for x in ports}) == 13, "Duplicate port IDs"
    for row in external:
        assert row["url"].startswith("https://"), f"External URL must use HTTPS: {row}"
    return ports, external, internal


def local_target(u: str) -> Path:
    parsed = urllib.parse.urlsplit(u)
    rel = urllib.parse.unquote(parsed.path).lstrip("/")
    if ".." in Path(rel).parts:
        raise ValueError(f"Invalid internal target {u}")
    dest = SITE / rel
    return dest / "index.html" if rel.endswith("/") else dest


def check_url(url: str) -> dict:
    begin = time.monotonic()
    final_url = None
    http_code = None
    err = None
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers=HEADERS, method="GET")
            with urllib.request.urlopen(req, timeout=12) as response:
                final_url = response.geturl()
                http_code = response.status
                response.read(1024)
            break
        except urllib.error.HTTPError as e:
            http_code = int(e.code)
            final_url = e.geturl()
            err = str(e.reason)[:130]
            if http_code not in (500, 502, 503, 504):
                break
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            err = str(e)[:160]
        if attempt == 0:
            time.sleep(0.3)

    if http_code is not None and 200 <= http_code < 400:
        status = "reachable"
    elif http_code in (401, 403, 429, 451):
        status = "restricted_or_rate_limited"
    elif http_code in (404, 410):
        status = "possible_missing"
    else:
        status = "uncertain_or_server_error"
    return {
        "url": url,
        "status": status,
        "http_status": http_code,
        "final_url": final_url,
        "error": err,
        "duration_s": round(time.monotonic()-begin, 2),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true", help="Check source references without external requests")
    args = parser.parse_args()
    ports, external, internal = collect()
    local_bad = []
    for entry in internal:
        if not local_target(entry["href"]).is_file():
            local_bad.append(entry)
    if local_bad:
        print("ERROR: missing internal paths", json.dumps(local_bad, ensure_ascii=False))
    unique = list(dict.fromkeys(row["url"] for row in external))
    if args.validate_only:
        print(json.dumps({
            "ports": len(ports), "shopping_coupon_cards": 11, "external_references": len(external),
            "unique_external_urls": len(unique), "internal_links_checked": len(internal),
            "missing_internal": local_bad,
        }, ensure_ascii=False, indent=2))
        return 1 if local_bad else 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        checked = list(pool.map(check_url, unique))
    results = {x["url"]: x for x in checked}
    report = {
        "checked_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "scope": "13 port primary + official reference links; 11 MATCHA coupon cards",
        "note": "Technical reachability only. A 2xx response never guarantees purchaseability, ticket stock, validity or correct sailing. 403/429 restrictions are not broken-link proof.",
        "ports": len(ports),
        "coupon_cards": 11,
        "unique_external_urls": len(unique),
        "internal_links_checked": len(internal),
        "missing_internal": local_bad,
        "status_counts": dict(Counter(x["status"] for x in checked)),
        "results": checked,
        "references": [
            {"kind": x["kind"], "id": x["id"], "url": x["url"], "status": results[x["url"]]["status"]}
            for x in external
        ],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("V56 link audit:", json.dumps({
        "ports": report["ports"],
        "coupon_cards": report["coupon_cards"],
        "unique_external_urls": len(unique),
        "internal_links_checked": len(internal),
        "missing_internal": len(local_bad),
        "http_statuses": report["status_counts"],
    }, ensure_ascii=False))
    for row in checked:
        if row["status"] != "reachable":
            print(f"{row['status']}: HTTP {row['http_status']} {row['url']} -> {row['final_url'] or ''} {row['error'] or ''}")

    missing = sum(x["status"] == "possible_missing" for x in checked)
    if local_bad or missing:
        print(f"V56 ATTENTION: {len(local_bad)} local paths missing, {missing} possible 404/410 URLs. Confirm manually before replacing.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
