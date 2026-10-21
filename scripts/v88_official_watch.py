#!/usr/bin/env python3
"""V88: check official ferry sources, dated baselines and stale on-site copy.

Scheduled in GitHub Actions. Never changes public fares, schedules or inventory.
A failed source fetch is 'unverified', not evidence of a fare change.
"""
import argparse
import datetime as dt
import hashlib
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "scripts/v88_official_baseline.json"
OUTPUT = ROOT / "audit-reports/v88/current"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; NIPPONFERRY Editorial Quality Audit/1.0)",
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.7",
}
TIMEOUT = (12, 30)
NOTICE_WORDS = (
    "유류", "할증", "운임", "결항", "운항", "스케줄", "일정", "예약",
    "변경", "중단", "위탁수하물", "접수", "안전", "지연", "임시", "점검",
    "surcharge", "cancel", "sailing", "fare", "schedule", "maintenance", "baggage",
)
def tidy(value):
    return re.sub(r"\s+", " ", html.unescape(str(value))).strip()

def fetch(session, url):
    try:
        r = session.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        if r.status_code >= 400:
            return None, {"url": url, "status": r.status_code, "error": "http_error"}
        if not r.content or len(r.content) < 180:
            return None, {"url": url, "status": r.status_code, "error": "empty_or_small"}
        r.encoding = r.apparent_encoding or r.encoding
        soup = BeautifulSoup(r.text, "html.parser")
        for e in soup.select("script,style,noscript,footer,header,nav"):
            e.decompose()
        text = tidy(soup.get_text(" ", strip=True))
        return soup, {"url": url, "status": r.status_code, "length": len(text)}
    except requests.RequestException as exc:
        return None, {"url": url, "error": type(exc).__name__, "detail": str(exc)[:180]}

def notice_index(soup, kind):
    """Take semantic article href and title, not timestamps, view counters or raw page hash."""
    observed = {}
    if soup is None:
        return observed
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        pattern = r"/support/notice/(\d+)" if kind == "panstar" else r"[?&]wr_id=(\d+)"
        match = re.search(pattern, href)
        if not match:
            continue
        if kind == "koreaferry" and "ferry_notice" not in urljoin("https://koreaferry.kr/eng/bbs/board.php?bo_table=ferry_notice", href):
            continue
        title = tidy(a.get_text(" ", strip=True))
        if len(title) < 4:
            title = tidy(a.parent.get_text(" ", strip=True))[:170] if a.parent else ""
        if len(title) > 200:
            title = title[:200]
        key = int(match.group(1))
        observed[key] = {"title": title, "url": urljoin(
            "https://www.panstarcruise.com/support/notice" if kind == "panstar"
            else "https://koreaferry.kr/eng/bbs/board.php?bo_table=ferry_notice",
            href,
        )}
    return observed

def fuel_fee_row(soup):
    """Read the actual table row, never aggregate unrelated facility taxes or fares."""
    if soup is None:
        return None
    for tr in soup.find_all("tr"):
        cells = [tidy(x.get_text(" ", strip=True)) for x in tr.find_all(["th", "td"])]
        if not any("유류할증료" in c for c in cells):
            continue
        row = " | ".join(cells)
        krw = [int(n.replace(",", "")) for n in re.findall(r"(\d[\d,]*)\s*원", row)]
        jpy = [int(n.replace(",", "")) for n in re.findall(r"(\d[\d,]*)\s*엔", row)]
        if krw and jpy:
            return {"busan_krw": krw[-1], "shimonoseki_jpy": jpy[-1], "row": row[:350]}
    return None

def official_signature(item):
    return hashlib.sha256(json.dumps(item, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:14]

def semantic_document(soup, provider):
    """Hash stable article content and referenced image URLs, excluding visitor counters."""
    if soup is None:
        return None
    if provider == "koreaferry":
        node = soup.select_one("#bo_v_con") or soup.select_one("#bo_v_atc") or soup.select_one("article")
    else:
        node = soup.select_one("main") or soup.select_one("article")
    node = node or soup.body or soup
    for unwanted in node.select("script,style,footer,nav,.comments,#bo_vc,.bo_vc,button"):
        unwanted.decompose()
    words = tidy(node.get_text(" ", strip=True))
    photos = sorted(img.get("src", "") for img in node.select("img[src]"))
    return official_signature({"text": words, "images": photos}) if words or photos else None

def korea_ferry_tax_images(session, soup, source_url, max_images=3, max_bytes=4_000_000):
    """Hash current bytes of official TAX notice images, never infer price values."""
    if soup is None:
        return {}
    node = soup.select_one("#bo_v_con") or soup.select_one("#bo_v_atc") or soup.select_one("article")
    node = node or soup
    allowed_host = urlparse(source_url).hostname or ""
    results = {}
    for img in node.select("img[src]"):
        if len(results) >= max_images:
            break
        url = urljoin(source_url, img.get("src", ""))
        host = urlparse(url).hostname or ""
        if urlparse(url).scheme != "https" or (host != allowed_host and not host.endswith("." + allowed_host)):
            continue
        if url in results:
            continue
        try:
            with session.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True, allow_redirects=True) as response:
                final_host = urlparse(response.url).hostname or ""
                if final_host != allowed_host and not final_host.endswith("." + allowed_host):
                    results[url] = {"status": "redirected_offsite"}
                    continue
                if response.status_code != 200:
                    results[url] = {"status": "http_error", "code": response.status_code}
                    continue
                if not response.headers.get("Content-Type", "").lower().startswith("image/"):
                    results[url] = {"status": "not_an_image"}
                    continue
                digest = hashlib.sha256()
                total = 0
                for chunk in response.iter_content(chunk_size=65536):
                    if chunk:
                        total += len(chunk)
                        if total > max_bytes:
                            break
                        digest.update(chunk)
                if total == 0:
                    results[url] = {"status": "empty"}
                elif total > max_bytes:
                    results[url] = {"status": "too_large"}
                else:
                    results[url] = {"status": "ok", "sha256": digest.hexdigest(), "bytes": total}
        except requests.RequestException as exc:
            results[url] = {"status": "fetch_failed", "error": type(exc).__name__}
    return results

def scan_existing_site(cfg):
    scans = []
    current_age = (dt.date.today() - dt.date.fromisoformat(cfg["verified_as_of"])).days
    missing = []
    for route in cfg["routes"]:
        for suffix in cfg["existing_guide_suffixes"]:
            path = ROOT / "site/guide" / f"busan-{route}-{suffix}" / "index.html"
            rel = str(path.relative_to(ROOT))
            if not path.is_file():
                missing.append(rel)
                continue
            content = path.read_text("utf-8", errors="replace")
            problems = []
            if content.count('id="nf87-verified-operations"') != 1:
                problems.append("source verification section missing or duplicated")
            if "nf-v87-verified-operations.css" not in content:
                problems.append("verification display stylesheet missing")
            expected = {
                "osaka": "25,000원", "fukuoka": "14,000원",
                "shimonoseki": "19,000원", "tsushima": "15,000원"
            }[route]
            if expected not in content:
                problems.append(f"verified fare {expected} not found")
            obsolete = {
                "osaka": [r"유류할증료는\s*29,000원"],
                "fukuoka": [],
                "shimonoseki": [],
                "tsushima": [r"유류할증료는\s*16,000원", r"부산→이즈하라\s*유류할증료는\s*27,000원"],
            }[route]
            for rx in obsolete:
                if re.search(rx, content):
                    problems.append("obsolete surcharge presented as current: " + rx)
            if current_age >= 45:
                problems.append(f"official verification date aged {current_age} days; recheck required")
            if problems:
                scans.append({"path": rel, "problems": problems})
    # Expand beyond the 12 V87 guides, but report suspected historic numbers for human review.
    legacy = []
    patterns = [
        ("Osaka legacy 29,000", re.compile(r"(?:부산.{0,90}오사카|오사카.{0,90}부산).{0,170}(?:유류할증료.{0,30}29,000원|29,000원.{0,30}유류할증료)", re.S)),
        ("Tsushima legacy 16,000", re.compile(r"(?:히타카츠|대마도|쓰시마).{0,145}유류할증료(?:는|가|:)\s*16,000원", re.S)),
        ("Tsushima legacy 27,000", re.compile(r"(?:이즈하라|대마도|쓰시마).{0,145}유류할증료(?:는|가|:)\s*27,000원", re.S)),
    ]
    for path in (ROOT / "site").rglob("*.html"):
        if "guide/busan-" in str(path):
            continue  # the active authoritative guides are covered above
        if path.stat().st_size > 1000000:
            continue
        data = path.read_text("utf-8", errors="replace")
        if "유류할증료" not in data:
            continue
        # Avoid matching embedded structured data and raw stylesheet.
        doc = BeautifulSoup(data, "html.parser")
        for e in doc.select("script,style"):
            e.decompose()
        plain = tidy(doc.get_text(" ", strip=True))
        for label, rx in patterns:
            found = rx.search(plain)
            if found:
                context = found.group(0)
                if any(phrase in context for phrase in ("구 공지", "종전", "과거", "변경 전", "기존 금액")):
                    continue
                legacy.append({"path": str(path.relative_to(ROOT)), "reason": label, "excerpt": context[:250]})
    return {"guides_checked": 12, "guides_with_problems": scans,
            "suspected_legacy_other_pages": legacy[:75],
            "suspected_legacy_total": len(legacy), "missing": missing}

def run(today=None, offline=False):
    cfg = json.loads(BASELINE.read_text("utf-8"))
    today = today or dt.date.today()
    report = {
        "version": "V88", "checked_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "baseline_date": cfg["verified_as_of"], "mode": "offline-test" if offline else "production",
        "sources": {}, "new_official_notices": [], "review_items": [],
        "site_audit": {}, "status": "clean"
    }
    if offline:
        return report
    session = requests.Session()
    old_report_file = OUTPUT.parent / "previous" / "report.json"
    try:
        previous = json.loads(old_report_file.read_text("utf-8")) if old_report_file.is_file() else {}
    except (OSError, ValueError):
        previous = {}
    for kind, key, floor in [
        ("panstar", "panstar_notice_index", cfg["panstar_last_reviewed_id"]),
        ("koreaferry", "koreaferry_notice_index", cfg["koreaferry_last_reviewed_id"])
    ]:
        url = cfg[key]
        soup, source = fetch(session, url)
        observed = notice_index(soup, kind)
        recent = sorted(observed.keys(), reverse=True)
        source.update({"parsed_notice_count": len(observed), "highest_id": max(recent, default=None)})
        source["notice_titles_by_id"] = {str(k): v["title"] for k, v in sorted(observed.items(), reverse=True)[:30]}
        report["sources"][kind + "_index"] = source
        older = previous.get("sources", {}).get(kind + "_index", {}).get("notice_titles_by_id", {})
        for notice_id, title in source["notice_titles_by_id"].items():
            if notice_id in older and older[notice_id] != title:
                report["review_items"].append({"kind": "notice_edited", "route": kind,
                    "message": f"Official notice #{notice_id} changed its title; verify before publishing", "url": url})
        if soup is None:
            report["review_items"].append({"kind": "source_unavailable", "route": kind,
                                            "message": "Could not verify official notice board (NOT a confirmed operational change)", "url": url})
        elif not observed:
            report["review_items"].append({"kind": "parsing_gap", "route": kind,
                                            "message": "Official notice titles could not be extracted: review parser or JS rendering", "url": url})
        else:
            for idx, item in sorted(observed.items(), reverse=True):
                if idx > floor and any(word in item["title"].lower() for word in NOTICE_WORDS):
                    report["new_official_notices"].append({"provider": kind, "id": idx, **item})
    # Data-driven price change from current tariff (not from dated historic notices).
    url = cfg["kampu_fare_url"]
    soup, source = fetch(session, url)
    parsed = fuel_fee_row(soup)
    source["parsed_fuel_row"] = parsed
    report["sources"]["kampu_fuel"] = source
    if soup is None or not parsed:
        report["review_items"].append({"kind": "source_unavailable" if soup is None else "parsing_gap",
                                        "route": "shimonoseki", "message": "Unable to parse current operator fuel fee; do not infer a new price", "url": url})
    elif (parsed["busan_krw"], parsed["shimonoseki_jpy"]) != (cfg["kampu_busan_fuel_krw"], cfg["kampu_shimonoseki_fuel_jpy"]):
        report["review_items"].append({"kind": "official_fare_mismatch", "route": "shimonoseki",
                                        "message": f"Current official table {parsed['busan_krw']} KRW / {parsed['shimonoseki_jpy']} JPY differs from reviewed reference",
                                        "url": url, "operator_values": parsed})
    # Reference docs are dated: check accessibility, not treat historic changes as live changes.
    for entry in cfg["panstar_verified_notices"]:
        url = entry["url"]
        soup, src = fetch(session, url)
        name = "panstar_" + entry["route"]
        text_body = tidy(soup.get_text(" ", strip=True)) if soup else ""
        src["text_available"] = len(text_body) > 80
        src["semantic_fingerprint"] = semantic_document(soup, "panstar")
        report["sources"][name] = src
        old_fingerprint = previous.get("sources", {}).get(name, {}).get("semantic_fingerprint")
        if old_fingerprint and src["semantic_fingerprint"] and old_fingerprint != src["semantic_fingerprint"]:
            report["review_items"].append({"kind": "existing_notice_edited", "route": entry["route"],
                "message": "Previously reviewed PanStar notice text changed in place; reverify effective date and rate", "url": url})
        if soup is None or not src["text_available"]:
            report["review_items"].append({"kind": "source_unavailable", "route": entry["route"],
                                            "message": "Dated official reference cannot be read", "url": url})
    k_url = cfg["koreaferry_tax_notice"]
    soup, source = fetch(session, k_url)
    source["semantic_fingerprint"] = semantic_document(soup, "koreaferry")
    source["image_digests"] = korea_ferry_tax_images(session, soup, k_url)
    report["sources"]["koreaferry_tax_notice"] = source
    previous_images = previous.get("sources", {}).get("koreaferry_tax_notice", {}).get("image_digests", {})
    for image_url, info in source["image_digests"].items():
        old_image = previous_images.get(image_url, {})
        if old_image.get("status") == "ok" and info.get("status") == "ok" and old_image.get("sha256") != info.get("sha256"):
            report["review_items"].append({"kind": "quarterly_tax_image_changed", "route": "fukuoka",
                "message": "Official TAX image at the same URL has changed: manually verify the amount and date", "url": image_url})
        elif info.get("status") != "ok":
            report["review_items"].append({"kind": "quarterly_tax_image_unverified", "route": "fukuoka",
                "message": "Cannot safely compare current official TAX image", "url": image_url})
    old_fingerprint = previous.get("sources", {}).get("koreaferry_tax_notice", {}).get("semantic_fingerprint")
    if old_fingerprint and source["semantic_fingerprint"] and old_fingerprint != source["semantic_fingerprint"]:
        report["review_items"].append({"kind": "quarterly_tax_notice_edited", "route": "fukuoka",
            "message": "Previously reviewed quarterly TAX body or linked graphic changed in place; inspect official image table", "url": k_url})
    if soup is None:
        report["review_items"].append({"kind": "source_unavailable", "route": "fukuoka",
                                        "message": "Quarterly TAX notice cannot be read", "url": k_url})
    due = dt.date.fromisoformat(cfg["koreaferry_tax_applies_through"])
    remaining = (due - today).days
    report["sources"]["fukuoka_tax_validity"] = {"expires": due.isoformat(), "days_remaining": remaining}
    if remaining <= 21:
        report["review_items"].append({"kind": "quarterly_expiry", "route": "fukuoka",
                                        "message": "Fukuoka quarterly TAX table expires in <=21 days or has expired; seek next official quarter",
                                        "url": k_url})
    report["site_audit"] = scan_existing_site(cfg)
    for item in report["site_audit"]["guides_with_problems"]:
        report["review_items"].append({"kind": "stale_article", **item})
    for item in report["site_audit"]["missing"]:
        report["review_items"].append({"kind": "missing_guide", "path": item})
    for item in report["site_audit"]["suspected_legacy_other_pages"]:
        report["review_items"].append({"kind": "possible_legacy_copy", **item})
    report["status"] = "needs_review" if report["review_items"] or report["new_official_notices"] else "clean"
    report["attention"] = report["status"] != "clean"
    # Fingerprint enables deduplication of identical recurring GitHub issue notifications.
    signals = [{"kind": i["kind"], "route": i.get("route"), "path": i.get("path"),
                "message": i.get("message"), "url": i.get("url")} for i in report["review_items"]]
    signals += [{"new_notice": v["provider"], "id": v["id"]} for v in report["new_official_notices"]]
    report["fingerprint"] = official_signature(signals)
    return report

def output(report):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
    lines = [
        "# V88 official-source monitor — " + report["status"],
        "", f"Checked (UTC): {report['checked_at_utc']}",
        f"Baseline: {report['baseline_date']}",
        f"New official matching notices: {len(report['new_official_notices'])}",
        f"Review items: {len(report['review_items'])}",
        "Do not auto-publish or assume confirmed sailings, live prices or seat inventory.",
        ""
    ]
    for n in report["new_official_notices"]:
        lines.append(f"- **New notice** [{n['provider']} #{n['id']}]({n['url']}): {n['title']}")
    for n in report["review_items"]:
        lines.append(f"- **Review {n['kind']}** {n.get('route', '')} {n.get('path', '')}: {n.get('message', n.get('reason', ''))} {n.get('url', '')}")
    (OUTPUT / "summary.md").write_text("\n".join(lines) + "\n", "utf-8")
    github_output = __import__("os").environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as fp:
            fp.write(f"attention={'true' if report['attention'] else 'false'}\n")
            fp.write(f"fingerprint={report['fingerprint']}\n")
    print(json.dumps({"status": report["status"], "new_notices": len(report["new_official_notices"]),
                      "review_items": len(report["review_items"]),
                      "suspected_legacy": report["site_audit"]["suspected_legacy_total"],
                      "fingerprint": report["fingerprint"]}, ensure_ascii=False))
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="No network; for fixture/procedure checks")
    args = parser.parse_args()
    output(run(offline=args.offline))
