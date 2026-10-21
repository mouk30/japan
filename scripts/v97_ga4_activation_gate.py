#!/usr/bin/env python3
"""V97: read-only GA4 activation gate for NIPPONFERRY production.

No Vercel credentials, no fabricated Measurement IDs, no outbound GA4 events.
This verifies deployment *installation* and current asset health, NOT that
Google Analytics has received actual visitors or booked tickets.

Use --require-active only AFTER the owner has configured GA4_MEASUREMENT_ID
in the Production environment and redeployed on Vercel.
"""
import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

BASE = "https://www.nipponferry.com"
PAGES = [
    "/", "/ferry/", "/booking/japan-cruise/",
    "/guide/busan-fukuoka-ferry/",
]
OUTPUT = Path("audit-output/v97-ga4-activation")
MEASUREMENT = re.compile(r"^G-[A-Z0-9]{7,15}$")


class TagParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.analytics_scripts = []
        self.styles = []
        self.canonical = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script" and "data-nf-ga4" in a:
            self.analytics_scripts.append({
                "id": a.get("data-nf-ga4") or "",
                "src": a.get("src") or "",
                "defer": "defer" in a,
            })
        if tag == "link":
            href = a.get("href") or ""
            if "nf-v93-booking-clicks.css" in href:
                self.styles.append(href)
            if a.get("rel") == "canonical":
                self.canonical.append(href)

def inspect_html(raw, path):
    parsed = TagParser()
    parsed.feed(raw)
    scripts = parsed.analytics_scripts
    valid = len(scripts) == 1 and bool(MEASUREMENT.fullmatch(scripts[0]["id"]))
    source = scripts[0]["src"] if scripts else None
    expected_canonical = BASE + path
    return {
        "path": path,
        "tag_count": len(scripts),
        "configured": valid,
        "has_valid_id_format": valid,
        # Display only an irreversible anonymous signal of stream consistency.
        "stream_fingerprint": hashlib.sha256(scripts[0]["id"].encode()).hexdigest()[:10] if valid else None,
        "has_consent_script": bool(source and source.startswith("/nf-v93-booking-clicks.js")),
        "has_consent_stylesheet": len(parsed.styles) == 1,
        "asset_path": source,
        "canonical_unchanged": expected_canonical in parsed.canonical,
        "has_defer": bool(scripts and scripts[0]["defer"]),
    }

def fetch(url, timeout=16):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; NIPPONFERRY-analytics-activation-quality/1.0)",
        "Accept": "text/html,application/javascript,*/*",
        "Cache-Control": "no-cache",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read(1100000).decode("utf-8", "replace")
            return {"ok": 200 <= r.status < 400, "status": r.status,
                    "body": data, "final_host": urlparse(r.url).hostname}
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as e:
        return {"ok": False, "error": type(e).__name__,
                "status": e.code if isinstance(e, urllib.error.HTTPError) else None}

def production_report(fetcher=fetch):
    report = {
        "version": "V97",
        "checked_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "site": BASE, "status": "unverified",
        "pages": [], "assets": [], "actual_event_counts": None,
        "actual_booking_completions": None,
    }
    for path in PAGES:
        result = fetcher(BASE + path)
        if not result["ok"]:
            report["pages"].append({"path": path, "status": "source_unavailable",
                                    "http": result.get("status"),
                                    "error": result.get("error")})
            continue
        doc = inspect_html(result["body"], path)
        doc["status"] = "fetched"
        doc["http"] = result["status"]
        doc["source_host_matches"] = result.get("final_host") == "www.nipponferry.com"
        report["pages"].append(doc)
    all_reachable = len(report["pages"]) == len(PAGES) and all(
        p.get("status") == "fetched" and p.get("source_host_matches") for p in report["pages"])
    if not all_reachable:
        report["status"] = "source_unavailable_or_misdirected"
        return report
    tags = [p["configured"] for p in report["pages"]]
    if not any(tags):
        if any(p["tag_count"] or p["has_consent_stylesheet"] for p in report["pages"]):
            report["status"] = "inconsistent_partial_deployment"
        else:
            report["status"] = "not_connected"
        return report
    all_valid = all(tags) and all(p["tag_count"] == 1 and p["has_consent_script"] and
                                   p["has_consent_stylesheet"] and p["canonical_unchanged"] and
                                   p["has_defer"] for p in report["pages"])
    stream_set = {p.get("stream_fingerprint") for p in report["pages"]}
    if not all_valid or len(stream_set) != 1:
        report["status"] = "inconsistent_partial_deployment"
        return report
    source_path = report["pages"][0]["asset_path"]
    if not source_path or not source_path.startswith("/"):
        report["status"] = "inconsistent_partial_deployment"
        return report
    for asset in (source_path, "/nf-v93-booking-clicks.css"):
        target = urljoin(BASE, asset)
        response = fetcher(target)
        asset_ok = response["ok"] and response.get("final_host") == "www.nipponferry.com"
        if asset.endswith(".css"):
            asset_ok = asset_ok and ".nf93-consent" in response.get("body", "")
        else:
            asset_ok = (asset_ok and "ferry_operator_click" in response.get("body","")
                        and "analytics_storage" in response.get("body",""))
        report["assets"].append({
            "asset": asset.split("?")[0],
            "ok": bool(asset_ok),
            "http": response.get("status"),
        })
    report["status"] = "installed_ready_for_owner_realtime_test" if all(
        x["ok"] for x in report["assets"]) else "installed_but_missing_or_wrong_asset"
    return report

def write_report(report, output):
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
    labels = {
        "not_connected": "GA4 measurement stream not connected: add Production env var & redeploy.",
        "installed_ready_for_owner_realtime_test": "GA4 tag and consent assets installed. Owner must verify an opt-in click in GA4 Realtime/DebugView.",
        "inconsistent_partial_deployment": "GA4 tag missing or inconsistent on some pages; inspect Vercel deployment.",
        "source_unavailable_or_misdirected": "Production page unavailable or redirected to unexpected host; cannot judge analytics connection.",
        "installed_but_missing_or_wrong_asset": "GA4 tag present but consent JavaScript or CSS broken.",
    }
    lines = [
        "# V97 — GA4 production installation status",
        "", f"Status: **{report['status']}**", "",
        labels.get(report["status"], "Verification incomplete"), "",
        f"Checked (UTC): {report['checked_at_utc']}", "",
        "| Page | HTTP | Configured | JS | CSS | Canonical |",
        "|---|---|---|---|---|---|",
    ]
    for page in report["pages"]:
        lines.append("| " + page["path"] + " | " + str(page.get("http","n/a")) + " | " +
                     str(page.get("configured","unverified")) + " | " +
                     str(page.get("has_consent_script","unverified")) + " | " +
                     str(page.get("has_consent_stylesheet","unverified")) + " | " +
                     str(page.get("canonical_unchanged","unverified")) + " |")
    lines += ["", "**Do not claim GA4 received events until a consented production test is visible in the owner's GA4 property.**",
              "No personal data, secret API keys or actual measurement ID is included in this report."]
    (out / "summary.md").write_text("\n".join(lines) + "\n", "utf-8")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--require-active", action="store_true",
                   help="Fail when owner expects a configured Production GA4 stream.")
    p.add_argument("--output", default=str(OUTPUT))
    args = p.parse_args()
    report = production_report()
    write_report(report, args.output)
    print(json.dumps({
        "status": report["status"], "checked_pages": len(report["pages"]),
        "installed": report["status"] == "installed_ready_for_owner_realtime_test",
        "actual_event_counts": None,
    }, ensure_ascii=False))
    if report["status"] in ("inconsistent_partial_deployment", "source_unavailable_or_misdirected",
                            "installed_but_missing_or_wrong_asset"):
        return 1
    if args.require_active and report["status"] != "installed_ready_for_owner_realtime_test":
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
