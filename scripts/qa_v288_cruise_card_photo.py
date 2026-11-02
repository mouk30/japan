#!/usr/bin/env python3
"""V288 ensure the ferry-booking thumbnail is route-labelled, credited and not the generic image."""
from pathlib import Path
from html.parser import HTMLParser
f=Path('site/japan-cruise/index.html')
s=f.read_text(encoding='utf-8')
asset=Path('site/images/venues/nf-v134-new-camellia-busan-2026-real.webp')
assert asset.is_file(), 'verified existing ferry photo missing'
assert 'src="/images/ferry.jpg"' not in s, 'low-information generic ferry card remains'
assert s.count('src="/images/venues/nf-v134-new-camellia-busan-2026-real.webp"')==1
assert '뉴카멜리아 국제여객선' in s and '팬스타호가 아닌' in s
assert 'Midnight cadet' in s and 'creativecommons.org/licenses/by/4.0/' in s
assert 'commons.wikimedia.org/wiki/File:' in s
assert 'object-fit:contain' in s
assert '<link rel="canonical" href="https://www.nipponferry.com/japan-cruise/">' in s
for url in ['/booking/japan-cruise/','/booking/room/','/things-to-do/']:
 assert 'href="'+url+'"' in s,url
print('V288 PASS: source-credited route-correct booking image, canonical and internal CTAs preserved')
