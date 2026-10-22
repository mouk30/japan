#!/usr/bin/env python3
"""V111 source/SEO regression for ten existing Japanese cruise-port articles."""
import hashlib
import json
import re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "audit-reports/v111/ten-ports-photo-provenance.json"
SEO = "audit-reports/v111/seo-baselines.json"

PATTERNS = {
    "title": r"<title>([^<]+)</title>",
    "description": r'<meta name="description" content="([^"]+)"',
    "canonical": r'<link rel="canonical" href="([^"]+)"',
    "h1": r"<h1[^>]*>([\s\S]*?)</h1>",
    "json_ld": r'<script type="application/ld\+json">([\s\S]*?)</script>',
}
def capture(html, regex, field):
    matched = re.search(regex, html, flags=re.S)
    if not matched:
        raise AssertionError("missing " + field)
    return matched.group(1)

def audit(root=ROOT):
    root = Path(root)
    items = json.loads((root / MANIFEST).read_text("utf8"))["items"]
    baselines = json.loads((root / SEO).read_text("utf8"))["pages"]
    seo = {item["slug"]: item for item in baselines}
    errors = []
    inspected = 0
    if len(items) != 10 or len(seo) != 10:
        errors.append("Expected ten distinct entries and protected SEO snapshots")
    for item in items:
        slug = item["slug"]
        try:
            path = root / "site" / item["page"].lstrip("/") / "index.html"
            html = path.read_text("utf8")
            old = seo[slug]
            for name, regex in PATTERNS.items():
                if capture(html, regex, name) != old[name]:
                    errors.append(slug + " SEO drift: " + name)
            target = "https://www.nipponferry.com" + item["asset"]
            if capture(html, r'<meta property="og:image" content="([^"]+)"', "OG") != target:
                errors.append(slug + " OG image differs from featured image")
            covers = re.findall(r'<img class="cover"[^>]*>', html)
            if len(covers) != 1:
                errors.append(slug + " expected exactly one hero photo")
            else:
                cover = covers[0]
                for attr, value in (
                    ("src", item["asset"]),
                    ("width", str(item["width"])),
                    ("height", str(item["height"])),
                ):
                    if f'{attr}="{value}"' not in cover:
                        errors.append(slug + " hero " + attr + " mismatch")
                alt = capture(cover, r'alt="([^"]+)"', "alt")
                if "접안" not in alt or len(alt) < 25:
                    errors.append(slug + " inaccurate or unhelpful tourism photo alt")
            if html.count('class="v111-photo-credit"') != 1:
                errors.append(slug + " visible author credit not exactly once")
            for field in ("source", "license", "photographer"):
                if item[field] not in html:
                    errors.append(slug + " missing " + field + " credit")
            if not "WebP 변환·크기 조정" in html:
                errors.append(slug + " edited photo disclosure missing")
            if item["stale_caption_removed"] and "현재는 공통 크루즈 참고 이미지입니다." in html:
                errors.append(slug + " obsolete placeholder note still on site")
            if item["historical_photo_note"] and slug == "kumamoto":
                if "2016년 구마모토 지진 이전" not in html:
                    errors.append(slug + " historic castle image lacks pre-earthquake note")
            if item["historical_photo_note"] and slug == "kobe":
                if "2005년" not in html:
                    errors.append(slug + " historic port tower image lacks year")
            asset = root / "site" / item["asset"].lstrip("/")
            binary = asset.read_bytes()
            actual = hashlib.sha1(b"blob " + str(len(binary)).encode() + b"\0" + binary).hexdigest()
            if actual != item["blob_sha"]:
                errors.append(slug + " WebP changed since verified image review")
            with Image.open(asset) as image:
                if image.format != "WEBP" or image.size != (item["width"], item["height"]):
                    errors.append(slug + " WebP dimensions/format mismatch")
            inspected += 1
        except Exception as exc:
            errors.append(slug + " audit exception: " + str(exc))
    result = {
        "passed": not errors,
        "verified_pages": inspected,
        "expected": 10,
        "representative_images_replaced": sum(x["changed_cover"] for x in items),
        "og_images_corrected": sum(x["og_changed"] for x in items),
        "errors": errors,
    }
    return result

if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] and result["verified_pages"] == 10 else 1)
