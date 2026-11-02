#!/usr/bin/env python3
"""V305: only the existing food hub presentation changes; preserve all original content."""
from pathlib import Path
from html.parser import HTMLParser
import re
import subprocess
from qa_v307_food_allowlist import allow_verified_v307_photo

page = Path("site/food/index.html").read_text(encoding="utf-8")
css = Path("site/nf-v305-food.css").read_text(encoding="utf-8")
before = subprocess.check_output(["git", "show", "origin/main:site/food/index.html"], text=True)
link = '<link rel="stylesheet" href="/nf-v305-food.css">'
assert page.count(link) == 1, "scoped CSS must be loaded exactly once"
# V305 is already merged into main; only V306's scoped script tag may be added.
v306_script = '<script src="/nf-v306-food-images.js" defer></script>'
approved = allow_verified_v307_photo(before)
assert page == approved or page.replace(v306_script, "") == approved, "Unexpected food content, SEO, image or license change"
assert len(re.findall(r'<a class="dircard" href="(/[^"]+/)"', page)) == 16, "food cards changed"
assert len(set(re.findall(r'<a class="dircard" href="(/[^"]+/)"', page))) == 16, "duplicate food destinations"
assert page.count('<h1>') == 1
assert '<link rel="canonical" href="https://www.nipponferry.com/food/">' in page
assert '<meta name="robots" content="index,follow,max-image-preview:large">' in page
assert "https://commons.wikimedia.org/wiki/File:Kama-age_sanuki_udon_by_sekido_in_Takamatsu%2C_Kagawa.jpg" in page
assert "https://creativecommons.org/licenses/by/2.0" in page
assert "도쿠시마·고치 음식 사진은 아님" in page
assert 'href="/things-to-do/takamatsu-cruise-udon-market-return/"' in page
assert "body.nf-premium-v2 .hub-main .dircard>img" in css
assert "aspect-ratio:4/3" in css
assert "grid-template-columns:repeat(3,minmax(0,1fr))" in css
assert "grid-template-columns:repeat(2,minmax(0,1fr))" in css
assert "grid-template-columns:minmax(0,1fr)" in css
assert "max-width:none" in css and "1.1fr" in css
assert "min-height:52px" in css
added = subprocess.check_output(["git", "diff", "--name-only", "--diff-filter=A", "origin/main...HEAD"], text=True).splitlines()
assert not any(x.startswith("site/") and x.endswith(".html") for x in added), "new article forbidden"
print("V305 PASS: 16 existing food cards, Shikoku photo and rights, all SEO and original links unchanged")
