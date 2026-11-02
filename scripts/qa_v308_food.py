#!/usr/bin/env python3
"""V308: verified Yamaguchi fugu photo replacing only one 500x375 card."""
from pathlib import Path
import subprocess
from qa_v307_food_allowlist import allow_verified_v307_photo
from qa_v308_food_allowlist import allow_verified_v308_photo

page = Path("site/food/index.html").read_text(encoding="utf-8")
before = subprocess.check_output(["git", "show", "origin/main:site/food/index.html"], text=True)
assert page == allow_verified_v308_photo(allow_verified_v307_photo(before)), "Unapproved food/SEO/photo modification"
assert page.count('class="dircard"') == 16
assert page.count('https://upload.wikimedia.org/wikipedia/commons/') == 9
assert 'src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Fugu_sashimi_%2832738795990%29.jpg/1280px-Fugu_sashimi_%2832738795990%29.jpg"' in page
assert 'alt="야마구치현에서 촬영된 복어회 · 시모노세키 현지 촬영 아님"' in page
assert '야마구치현 복어회 · 2016년 촬영' in page
assert 'Raita Futo / Wikimedia Commons · Flickr 원본' in page
assert '원본 5739×3826px, 1280px 축소·4:3 카드 크롭' in page
assert 'https://commons.wikimedia.org/wiki/File:Fugu_sashimi_%2832738795990%29.jpg' in page
assert 'https://creativecommons.org/licenses/by/2.0/' in page
assert 'Fugo-sashimi.jpg' not in page
assert '<link rel="canonical" href="https://www.nipponferry.com/food/">' in page
assert '<meta name="robots" content="index,follow,max-image-preview:large">' in page
assert '<script src="/nf-v306-food-images.js" defer></script>' in page
assert Path("site/nf-v305-food.css").is_file()
assert Path("site/nf-v306-food-images.js").is_file()
added = subprocess.check_output(["git", "diff", "--name-only", "--diff-filter=A", "origin/main...HEAD"], text=True).splitlines()
assert not any(p.startswith("site/") and p.endswith(".html") for p in added), "New article forbidden"
print("V308 PASS: one 500px to 1280px source-verified Yamaguchi fugu photo, exact CC BY 2.0 credit, 16 cards and SEO unchanged")
