#!/usr/bin/env python3
"""V306: preserve existing food URLs, captions, photo credits, SEO and route links."""
from pathlib import Path
import re
import subprocess

html = Path("site/food/index.html").read_text(encoding="utf-8")
css = Path("site/nf-v305-food.css").read_text(encoding="utf-8")
js = Path("site/nf-v306-food-images.js").read_text(encoding="utf-8")
before = subprocess.check_output(["git", "show", "origin/main:site/food/index.html"], text=True)
tag = '<script src="/nf-v306-food-images.js" defer></script>'
assert html.count(tag) == 1
assert html.replace(tag, "") == before, "V306 may not change photos, SEO, credits or booking links"
assert html.count('class="dircard"') == 16
assert html.count('https://upload.wikimedia.org/wikipedia/commons/') == 9
assert '<link rel="canonical" href="https://www.nipponferry.com/food/">' in html
assert '<meta name="robots" content="index,follow,max-image-preview:large">' in html
assert "사진 출처 보기" in html and "CC BY" in html
assert "nf-v306-photo-failed" in css and "aspect-ratio:4/3" in css
assert 'img.addEventListener("error"' in js
assert 'img.complete && img.naturalWidth === 0' in js
assert "https://upload.wikimedia.org/" in js
assert "fetch(" not in js, "No hotlink retry or unverified replacement allowed"
added = subprocess.check_output(["git", "diff", "--name-only", "--diff-filter=A", "origin/main...HEAD"], text=True).splitlines()
assert not any(p.startswith("site/") and p.endswith(".html") for p in added), "New articles forbidden"
print("V306 PASS: 9 external sources, 16 existing cards, original image URLs/credits/SEO/links preserved")
