#!/usr/bin/env python3
"""V35: Convert five licensed Commons documentary photos to local WebP and update existing articles.

No synthetic image is represented as photography. All five downloads must validate before
any article is rewritten. Run from repository root with Pillow available.
"""
from __future__ import annotations

import io
import re
import time
import urllib.request
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
HOST = "https://www.nipponferry.com"
LICENSE = "https://creativecommons.org/licenses/by-sa/4.0/"
COMMONS = "https://commons.wikimedia.org/wiki/File:"
ITEMS = [
    {
        "slug": "niigata-tsubame-sanjo-metalwork",
        "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/6/69/Masashi_Kokuen_Kiritsuke_Petty_135mm_%282026%29-104A7479.jpg/1280px-Masashi_Kokuen_Kiritsuke_Petty_135mm_%282026%29-104A7479.jpg",
        "source": COMMONS + "Masashi_Kokuen_Kiritsuke_Petty_135mm_%282026%29-104A7479.jpg",
        "photographer": "Frank Schulenburg",
        "licence": "CC BY-SA 4.0",
        "licence_url": LICENSE,
        "alt": "니가타현 산조의 장인 마사시 야마모토가 제작한 기리쓰케 스타일 일본식 수제 칼 실제 사진",
        "label": "니가타 산조 장인이 만든 칼 제품. 공방 거리나 작업 현장을 촬영한 사진은 아닙니다.",
        "template": "editorial",
    },
    {
        "slug": "kumiko-japanese-wood-joinery",
        "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b9/Kumiko.jpg/1280px-Kumiko.jpg",
        "source": COMMONS + "Kumiko.jpg",
        "photographer": "Sergei Sarin",
        "licence": "CC BY-SA 4.0",
        "licence_url": LICENSE,
        "alt": "일본 전통 구미코 목공예의 정교한 별 모양 격자 결구 실사",
        "label": "구미코 목공예 세공품. 제작 공정 사진은 아닙니다.",
        "template": "hero",
    },
    {
        "slug": "japan-okinawan-bingata-textiles",
        "url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Fragment_from_Okinawa%2C_19th_century%2C_Honolulu_Museum_of_Art_3044.1.JPG",
        "source": COMMONS + "Fragment_from_Okinawa%2C_19th_century%2C_Honolulu_Museum_of_Art_3044.1.JPG",
        "photographer": "Hiart",
        "licence": "CC0 1.0",
        "licence_url": "https://creativecommons.org/publicdomain/zero/1.0/",
        "alt": "호놀룰루 미술관 소장 19세기 오키나와 빈가타 염색 비단 직물 실제 유물 사진",
        "label": "호놀룰루 미술관의 19세기 빈가타 유물 사진. 현대 염색 공방 사진이 아닙니다.",
        "template": "hero",
    },
    {
        "slug": "fukuoka-hakata-ori-textiles",
        "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/6/6e/Former_Miura_Residence_the_workshop_for_hakata-ori_Hakata-ku_Hakata-ku_Fukuoka_20241114_154457.jpg/960px-Former_Miura_Residence_the_workshop_for_hakata-ori_Hakata-ku_Hakata-ku_Fukuoka_20241114_154457.jpg",
        "source": COMMONS + "Former_Miura_Residence_the_workshop_for_hakata-ori_Hakata-ku_Hakata-ku_Fukuoka_20241114_154457.jpg",
        "photographer": "Hirho",
        "licence": "CC BY-SA 4.0",
        "licence_url": LICENSE,
        "alt": "후쿠오카 하카타 구 미우라가 주택의 하카타오리 직기와 전통 직조 작업장 전시 실제 사진",
        "label": "후쿠오카 옛 미우라가 주택의 하카타오리 직기 전시. 현직 장인이 작업하는 순간은 아닙니다.",
        "template": "editorial",
    },
    {
        "slug": "japan-sudare-bamboo-blinds",
        "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/3/38/Facade_of_a_dwelling_with_sudare%2C_wooden_balustrades_and_yellow_lamp%2C_Shinbashi-dori%2C_Gion%2C_Kyoto%2C_Japan.jpg/1280px-Facade_of_a_dwelling_with_sudare%2C_wooden_balustrades_and_yellow_lamp%2C_Shinbashi-dori%2C_Gion%2C_Kyoto%2C_Japan.jpg",
        "source": COMMONS + "Facade_of_a_dwelling_with_sudare%2C_wooden_balustrades_and_yellow_lamp%2C_Shinbashi-dori%2C_Gion%2C_Kyoto%2C_Japan.jpg",
        "photographer": "Basile Morin",
        "licence": "CC BY-SA 4.0",
        "licence_url": LICENSE,
        "alt": "교토 기온 신바시 거리 전통 가옥 창에 걸린 일본식 스다레 발 실제 사진",
        "label": "교토 기온의 실제 건물에 걸린 스다레. 제작 공정 사진은 아닙니다.",
        "template": "hero",
    },
]


def photo_credit(item: dict) -> str:
    # This attribution stays visible next to the photo, including for CC0.
    source = item["source"].replace("&", "&amp;")
    credit = item["photographer"].replace("&", "&amp;")
    return (
        f'{item["label"]} '
        f'사진: <a href="{source}" target="_blank" rel="noopener noreferrer"'
        f' style="color:inherit;text-decoration:underline">{credit} / Wikimedia Commons</a> · '
        f'<a href="{item["licence_url"]}" target="_blank" rel="noopener noreferrer"'
        f' style="color:inherit;text-decoration:underline">{item["licence"]}</a>. '
        "원본을 WebP로 변환·크기 조정했으며 화면 비율에 따라 가장자리가 일부 잘릴 수 있습니다."
    )


def get_webp(item: dict) -> bytes:
    err = None
    for attempt in range(5):
        try:
            request = urllib.request.Request(
                item["url"],
                headers={
                    "User-Agent": "NIPPONFERRY-V35/1.0 (https://www.nipponferry.com; Commons-attributed noncommercial/commerce editorial)",
                    "Accept": "image/jpeg,image/png,image/*;q=0.7",
                },
            )
            with urllib.request.urlopen(request, timeout=55) as response:
                mimetype = response.headers.get("Content-Type", "")
                raw = response.read()
            if not mimetype.lower().startswith("image/") or len(raw) < 9000:
                raise RuntimeError(f"Bad upstream response: {mimetype} {len(raw)} bytes")
            with Image.open(io.BytesIO(raw)) as picture:
                picture.load()
                picture = ImageOps.exif_transpose(picture).convert("RGB")
                picture.thumbnail((1440, 1440), Image.Resampling.LANCZOS)
                encoded = io.BytesIO()
                picture.save(encoded, format="WEBP", quality=85, method=6)
            webp = encoded.getvalue()
            with Image.open(io.BytesIO(webp)) as checked:
                checked.verify()
            if len(webp) < 5000:
                raise RuntimeError("WebP unexpectedly small")
            return webp
        except Exception as exc:
            err = exc
            print(f'Attempt {attempt + 1} failed for {item["slug"]}: {exc}', flush=True)
            time.sleep((attempt + 1) * 3)
    raise RuntimeError(f'Cannot cache {item["slug"]}: {err}')


def rewrite(item: dict, page: str) -> str:
    slug = item["slug"]
    source = f"/images/culture-verified/{slug}.webp"
    alt = item["alt"]
    attribution = photo_credit(item)
    figure_style = (
        'style="margin:0;background:#15373c"'
        if item["template"] == "hero" else ""
    )
    if item["template"] == "hero":
        # Fit portrait textile fully without a misleading 16:9 crop.
        extra = (
            ' style="display:block;width:100%;height:auto;max-height:620px;'
            'aspect-ratio:16/9;object-fit:contain;background:#122e31"'
            if slug == "japan-okinawan-bingata-textiles"
            else ' style="display:block;width:100%"'
        )
        replacement = (
            f'<div class="hero"><figure {figure_style}><img src="{source}" alt="{alt}"'
            f' decoding="async" fetchpriority="high"{extra}>'
            f'<figcaption style="padding:10px 20px;font-size:12px;line-height:1.7;'
            f'color:#f0f4f2">{attribution}</figcaption></figure>'
        )
        page, count = re.subn(r'<div class="hero"><img[^>]*>', lambda _: replacement, page, count=1)
    else:
        replacement = (
            f'<figure class="editorial-hero"><img src="{source}" alt="{alt}"'
            f' decoding="async" fetchpriority="high">'
            f'<figcaption>{attribution}</figcaption></figure>'
        )
        page, count = re.subn(
            r'<figure class="editorial-hero"><img[^>]*><figcaption>'
            r'AI 생성 참고 이미지로 실제 장소와 차이가 있을 수 있습니다\.</figcaption></figure>',
            lambda _: replacement,
            page,
            count=1,
        )
    if count != 1:
        raise RuntimeError(f"Unexpected {item['template']} hero markup for {slug} ({count} matches)")
    og = f'<meta property="og:image" content="{HOST}{source}">'
    page, matchcount = re.subn(
        r'<meta property="og:image" content="[^"]*">',
        lambda _: og,
        page,
        count=1,
    )
    if matchcount != 1:
        raise RuntimeError(f"Failed to replace OG image for {slug}")
    twitter = f'<meta name="twitter:image" content="{HOST}{source}">'
    if 'name="twitter:image"' in page:
        page, twitter_count = re.subn(r'<meta name="twitter:image" content="[^"]*">', lambda _: twitter, page, count=1)
        if twitter_count != 1:
            raise RuntimeError(f"Failed Twitter image for {slug}")
    else:
        page = page.replace(og, og + twitter, 1)
    if 'name="twitter:card"' not in page:
        page = page.replace(og, og + '<meta name="twitter:card" content="summary_large_image">', 1)
    if f'src="{source}"' not in page or og not in page or twitter not in page or item["source"] not in page:
        raise RuntimeError(f"Incomplete image or credit in {slug}")
    return page


def main() -> None:
    blobs = []
    for item in ITEMS:
        payload = get_webp(item)
        print(f'Validated {item["slug"]}: {len(payload)} WebP bytes', flush=True)
        blobs.append((item, payload))
        time.sleep(1.1)
    pages = []
    for item, _ in blobs:
        path = ROOT / "site" / "things-to-do" / item["slug"] / "index.html"
        content = path.read_text(encoding="utf-8")
        pages.append((path, rewrite(item, content)))
    folder = ROOT / "site" / "images" / "culture-verified"
    folder.mkdir(parents=True, exist_ok=True)
    for item, payload in blobs:
        (folder / f'{item["slug"]}.webp').write_bytes(payload)
    for path, content in pages:
        path.write_text(content, encoding="utf-8")
    print("V35: 5/5 local WebP files and 5/5 credited page/social image rewrites completed.", flush=True)


if __name__ == "__main__":
    main()
