#!/usr/bin/env python3
"""Read-only NIPPONFERRY template, photo and booking CTA inventory.

Usage: python3 scripts/audit_legacy_templates.py --root site --out-dir audit-output
This is a TRIAGE report, not proof that external assets or links are live.
"""
import argparse
import csv
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

class Scan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.links = []
        self.images = []
        self.structured = 0
        self.canonical = False
        self.description = False
        self.headers = []
        self.main = False
        self.og_image = False

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "header":
            self.headers.append(attrs.get("class", ""))
        if tag == "main":
            self.main = True
        if tag == "a":
            self.links.append((attrs.get("href", ""), attrs.get("class", "")))
        if tag == "img":
            self.images.append(attrs)
        if tag == "script" and attrs.get("type", "").lower() == "application/ld+json":
            self.structured += 1
        if tag == "link" and "canonical" in attrs.get("rel", "").lower():
            self.canonical = bool(attrs.get("href"))
        if tag == "meta":
            if attrs.get("name", "").lower() == "description":
                self.description = bool(attrs.get("content"))
            if attrs.get("property", "").lower() == "og:image":
                self.og_image = bool(attrs.get("content"))

def media_status(src, html_path, root):
    if not src or src.startswith(("data:", "blob:")):
        return "dynamic_or_empty"
    u = urlsplit(src.strip())
    if u.scheme in ("http", "https") or src.startswith("//"):
        return "external_unverified"
    if u.scheme or src.startswith("#") or "{" in src or "${" in src:
        return "dynamic_or_empty"
    rel = unquote(u.path)
    if not rel:
        return "dynamic_or_empty"
    target = root / rel.lstrip("/") if rel.startswith("/") else html_path.parent / rel
    try:
        target.resolve().relative_to(root.resolve())
    except ValueError:
        return "outside_site"
    return "local_exists" if target.is_file() else "local_missing"

def classify(path, root):
    relative = path.relative_to(root).as_posix()
    if relative == "index.html":
        return "home"
    bits = relative.split("/")
    if "cruise-ports" in bits:
        return "cruise_ports"
    if "tokyo" in bits:
        return "tokyo"
    if "booking" in bits:
        return "booking"
    if "things-to-do" in bits:
        return "things_to_do"
    if "practical" in bits:
        return "practical"
    return "other"

def audit(root):
    rows = []
    for path in sorted(root.rglob("*.html")):
        try:
            html = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            rows.append({"path": path.relative_to(root).as_posix(), "error": "unreadable"})
            continue
        parser = Scan()
        try:
            parser.feed(html)
        except Exception:
            rows.append({"path": path.relative_to(root).as_posix(), "error": "html_parse_review"})
            continue
        local_missing = []
        unverified = 0
        for image in parser.images:
            src = image.get("src", "")
            status = media_status(src, path, root)
            if status == "local_missing":
                local_missing.append(src)
            elif status != "local_exists":
                unverified += 1
        booking_links = [(href, cls) for href, cls in parser.links
                         if "/booking/" in href or "reservation" in href.lower()
                         or "reserve" in cls.lower()]
        premium = 'nf-premium-v2' in html or 'nf-premium-v1.css' in html
        common_header = any("site-header" in h for h in parser.headers)
        legacy = not common_header
        rows.append({
            "path": path.relative_to(root).as_posix(),
            "group": classify(path, root),
            "legacy_header_review": int(legacy),
            "premium_theme_marker": int(premium),
            "header_count": len(parser.headers),
            "main_present": int(parser.main),
            "canonical": int(parser.canonical),
            "description": int(parser.description),
            "json_ld_count": parser.structured,
            "og_image": int(parser.og_image),
            "image_count": len(parser.images),
            "local_missing_image_count": len(local_missing),
            "local_missing_image_examples": " | ".join(local_missing[:3]),
            "unverified_image_count": unverified,
            "booking_link_count": len(booking_links),
            "booking_link_examples": " | ".join(h for h, _ in booking_links[:3]),
            "error": ""
        })
    return rows

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", default="site")
    p.add_argument("--out-dir", default="audit-output")
    args = p.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        p.error("site root not found: " + str(root))
    rows = audit(root)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    keys = ["path","group","legacy_header_review","premium_theme_marker","header_count",
            "main_present","canonical","description","json_ld_count","og_image",
            "image_count","local_missing_image_count","local_missing_image_examples",
            "unverified_image_count","booking_link_count","booking_link_examples","error"]
    with (out / "template-audit.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)
    legacy = [r for r in rows if r.get("legacy_header_review") == 1]
    missing = [r for r in rows if r.get("local_missing_image_count", 0) > 0]
    no_booking = [r for r in rows if r.get("booking_link_count") == 0 and not r.get("error")]
    lines = [
        "# NIPPONFERRY read-only template audit",
        "",
        "Generated from local HTML and media paths. External URLs, dynamic images,",
        "visual appearance, current booking availability and deployed HTTP are NOT checked.",
        "A legacy marker means no `header.site-header` was found; manual review required.",
        "",
        f"- HTML scanned: {len(rows)}",
        f"- Header review candidates: {len(legacy)}",
        f"- HTML with missing local <img src> targets: {len(missing)}",
        f"- HTML without booking-related <a> links: {len(no_booking)}",
        "",
        "## Review candidates by section",
    ]
    lines += [f"- {key}: {count}" for key, count in sorted(Counter(r.get("group", "unknown") for r in legacy).items())]
    lines += ["", "## First 80 header review candidates"]
    lines += [f"- `{r['path']}`" for r in legacy[:80]]
    lines += ["", "## First 50 pages with missing local images"]
    lines += [f"- `{r['path']}`: {r['local_missing_image_examples']}" for r in missing[:50]]
    (out / "template-audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:12]))
    print("Full CSV and Markdown reports:", out.resolve())

if __name__ == "__main__":
    main()
