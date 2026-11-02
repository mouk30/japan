#!/usr/bin/env python3
"""V307: verified 2023 Karato Market photo replaces a 436x654 sushi thumbnail."""
from pathlib import Path
import subprocess
from qa_v307_food_allowlist import allow_verified_v307_photo
from qa_v308_food_allowlist import allow_verified_v308_photo

page = Path("site/food/index.html").read_text(encoding="utf-8")
before = subprocess.check_output(["git", "show", "origin/main:site/food/index.html"], text=True)
approved = allow_verified_v308_photo(allow_verified_v307_photo(before))
assert page == approved, "Unapproved /food/ change outside V307 verified source, alt, caption and credit"
assert page.count('class="dircard"') == 16
assert page.count('https://upload.wikimedia.org/wikipedia/commons/') == 9
assert 'src="https://upload.wikimedia.org/wikipedia/commons/0/00/Karato_Fish_Market%2C_Shimonoseki_-_Jun_24%2C_2023.jpg"' in page
assert 'alt="시모노세키 가라토시장 외관 · 2023년 6월 촬영"' in page
assert '가라토시장 실사 · 2023년 촬영' in page
assert 'bryan... / Wikimedia Commons · Flickr 원본' in page
assert 'https://creativecommons.org/licenses/by-sa/2.0/' in page
assert '원본 4032×3024px, 4:3 카드 크롭' in page
assert 'Karato_market%2C_Shimonoseki.jpg' not in page
assert '<link rel="canonical" href="https://www.nipponferry.com/food/">' in page
assert '<meta name="robots" content="index,follow,max-image-preview:large">' in page
assert '<script src="/nf-v306-food-images.js" defer></script>' in page
added = subprocess.check_output(["git", "diff", "--name-only", "--diff-filter=A", "origin/main...HEAD"], text=True).splitlines()
assert not any(x.startswith("site/") and x.endswith(".html") for x in added), "New articles forbidden"
print("V307 PASS: one location-verified 4032x3024 Karato image and exact CC BY-SA 2.0 credit; 16 cards, 9 external images, SEO unchanged")
