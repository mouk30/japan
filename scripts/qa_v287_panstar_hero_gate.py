#!/usr/bin/env python3
"""V287 approved PanStar hero deployment gate: never ship an absent or text-baked image."""
from pathlib import Path
from hashlib import sha256
from html.parser import HTMLParser
import struct
ROOT=Path('site')
asset=ROOT/'images/panstar-cruise-clean-2048.webp'
pages=['japan-cruise','booking','booking/japan-cruise','booking/fukuoka','booking/osaka','booking/shimonoseki','booking/tsushima']
assert asset.is_file(), 'BLOCK DEPLOY: upload the approved clean PanStar image to site/images/panstar-cruise-clean-2048.webp'
assert asset.stat().st_size>40000, 'BLOCK DEPLOY: asset is suspiciously small'
assert sha256(asset.read_bytes()).hexdigest() == 'bbcfa65a0e670060b5ce6fe79b2a9ea3272874b4d96f96799800ec9ccb631bdd', 'BLOCK DEPLOY: image differs from user-approved PanStar WebP (do not substitute another ship)'
for p in pages:
 text=(ROOT/p/'index.html').read_text(encoding='utf-8')
 assert "/images/panstar-cruise-clean-2048.webp" in text,p+' missing approved asset'
 assert 'aspect-ratio:3 / 1' in text,p+' missing complete-ship desktop aspect ratio'
 assert 'aspect-ratio:2.2 / 1' in text,p+' missing mobile aspect ratio'
 assert 'overflow-wrap:break-word' in text,p+' missing title wrap protection'
 assert '<link rel="canonical"' in text or "rel='canonical'" in text,p+' canonical lost'
print('V287 PASS: all seven pages reference uploaded approved image with responsive separate text')
