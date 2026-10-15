#!/usr/bin/env python3
"""V34: archive precisely verified Wikimedia photographs into local WebP assets.

Run from repository root. Each processed article keeps visible source/author/license credit.
No new pages are created. Fails closed if a download, decode or HTML match fails.
"""
from __future__ import annotations

import io
import time
import urllib.request
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = "https://www.nipponferry.com"
ITEMS = {
    "japanese-pottery-kilns": (
        "https://thumb.wikimedia.org/wikipedia/commons/thumb/3/3b/Climbing_kiln_in_Arita_Porcelain_Park_2.JPG/1280px-Climbing_kiln_in_Arita_Porcelain_Park_2.JPG",
    ),
    "japanese-urushi-lacquerware": (
        "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b9/Wajima-nuri_red_rice_bowl.jpg/1280px-Wajima-nuri_red_rice_bowl.jpg",
    ),
    "japanese-woodblock-printmaking": (
        "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/93/Ukiyoe_printmaking_process.jpg/1280px-Ukiyoe_printmaking_process.jpg",
    ),
    "sagano-scenic-railway": (
        "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/5d/Sagano-Scenic-Railway_DE10-1104.jpg/1280px-Sagano-Scenic-Railway_DE10-1104.jpg",
    ),
    "hakone-tozan-switchback-train": (
        "https://upload.wikimedia.org/wikipedia/commons/a/ae/Hakone-Tozan-Kami-ohiradai-Signal-Sta.jpg",
    ),
}

# Download all files before modifying any article; prevents half-complete commits.
assets = []
for slug, (url,) in ITEMS.items():
    error = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "NIPPONFERRY-V34-photo-cache/1.0 (https://www.nipponferry.com/; editorial)",
                "Accept": "image/jpeg,image/png,image/*;q=0.8",
            })
            with urllib.request.urlopen(req, timeout=35) as res:
                raw = res.read()
                mime = res.headers.get("Content-Type", "")
            if not raw or len(raw) < 3000 or "image" not in mime.lower():
                raise RuntimeError(f"Invalid image response for {slug}: {mime}, {len(raw)} bytes")
            with Image.open(io.BytesIO(raw)) as image:
                image.load()
                image = ImageOps.exif_transpose(image).convert("RGB")
                image.thumbnail((1440, 1080), Image.Resampling.LANCZOS)
                output = io.BytesIO()
                image.save(output, "WEBP", quality=84, method=6)
                webp = output.getvalue()
            with Image.open(io.BytesIO(webp)) as check:
                check.verify()
            assets.append((slug, url, webp))
            print(f"Verified {slug}: {len(raw)} original bytes -> {len(webp)} WebP bytes")
            break
        except Exception as exc:
            error = exc
            if attempt < 3:
                time.sleep((attempt + 1) * 3)
    else:
        raise RuntimeError(f"Could not cache {slug}: {error}")
    time.sleep(1.3)

articles = []
for slug, url, binary in assets:
    path = ROOT / "site" / "things-to-do" / slug / "index.html"
    content = path.read_text(encoding="utf-8")
    local = f"/images/culture-verified/{slug}.webp"
    if f'src="{url}"' not in content:
        raise RuntimeError(f"Expected verified photo src missing from {path}")
    if f'content="{url}"' not in content:
        raise RuntimeError(f"Expected verified social image missing from {path}")
    content = content.replace(f'src="{url}"', f'src="{local}"')
    content = content.replace(f'content="{url}"', f'content="{PUBLIC}{local}"')
    if f'src="{local}"' not in content or f'content="{PUBLIC}{local}"' not in content:
        raise RuntimeError(f"Image rewrite failed for {slug}")
    articles.append((path, content))

directory = ROOT / "site" / "images" / "culture-verified"
directory.mkdir(parents=True, exist_ok=True)
for slug, url, binary in assets:
    (directory / f"{slug}.webp").write_bytes(binary)
for path, content in articles:
    path.write_text(content, encoding="utf-8")
print("V34 local WebP conversions and 5 article/social-image rewrites complete.")
