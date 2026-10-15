#!/usr/bin/env python3
"""Remove only the redundant WebP conversion sentence from published HTML credits.

Leave photographers, source URLs, licensing details and descriptions unchanged.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = "원본 사진을 축소하여 WebP로 변환했습니다."
# Remove the divider that belongs to this sentence, avoiding a dangling ' · '.
PATTERN = re.compile(r"(?:[ 	]*·[ 	]*|[ 	]+)?" + re.escape(TARGET))
REPORT = ROOT / "docs" / "v50-webp-credit-sentence-cleanup.json"


def main() -> None:
    changed = []
    scanned = 0
    for file in sorted(ROOT.rglob("*.html")):
        if any(part in {".git", "node_modules", ".next", ".vercel"} for part in file.parts):
            continue
        scanned += 1
        old = file.read_text(encoding="utf-8")
        if TARGET not in old:
            continue
        # All external credit/licensing URLs must remain byte-for-byte identical.
        credit_links = re.findall(
            r'https?://(?:commons\.wikimedia\.org|creativecommons\.org)/[^\s"<>]+',
            old,
        )
        new, removed = PATTERN.subn("", old)
        assert removed > 0 and TARGET not in new
        assert credit_links == re.findall(
            r'https?://(?:commons\.wikimedia\.org|creativecommons\.org)/[^\s"<>]+',
            new,
        ), f"Attribution altered in {file}"
        file.write_text(new, encoding="utf-8")
        changed.append({"file": file.relative_to(ROOT).as_posix(), "removed": removed})

    # Independent post-run scan: no exact sentence may survive in HTML.
    leftovers = []
    for file in ROOT.rglob("*.html"):
        if TARGET in file.read_text(encoding="utf-8"):
            leftovers.append(file.relative_to(ROOT).as_posix())
    assert not leftovers, f"Unremoved sentence in: {leftovers[:10]}"
    report = {
        "removed_sentence": TARGET,
        "html_files_scanned": scanned,
        "html_files_changed": len(changed),
        "sentences_removed": sum(r["removed"] for r in changed),
        "unremoved_html_files": leftovers,
        "attribution_and_license_urls_preserved": True,
        "changed_files": changed,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("V50 cleanup:", json.dumps({k: v for k, v in report.items() if k != "changed_files"}, ensure_ascii=False))
    assert changed, "No HTML contained the target sentence; check deployment source."


if __name__ == "__main__":
    main()
