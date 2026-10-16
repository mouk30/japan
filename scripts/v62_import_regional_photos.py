#!/usr/bin/env python3
"""Import two location-verified Commons photographs as local WebP and update V61 cards."""
from __future__ import annotations
import io, json, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
PHOTOSET = [
    {
        "id": "shimonoseki",
        "old": "/images/editorial/shimonoseki-cruise-port-day-trip.webp",
        "new": "/images/venues/v62-karato-market-real.webp",
        "source_page": "https://commons.wikimedia.org/wiki/File:Karato_Fish_Market,_Shimonoseki_-_Jun_24,_2023.jpg",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/0/00/Karato_Fish_Market%2C_Shimonoseki_-_Jun_24%2C_2023.jpg",
            "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/00/Karato_Fish_Market%2C_Shimonoseki_-_Jun_24%2C_2023.jpg/1280px-Karato_Fish_Market%2C_Shimonoseki_-_Jun_24%2C_2023.jpg",
        ],
        "author": "bryan...",
        "license": "CC BY-SA 2.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/2.0/",
        "year": "2023",
        "alt_old": "시모노세키 항구 관광과 간몬해협을 표현한 참고 이미지",
        "alt_new": "2023년 실제 촬영된 시모노세키 가라토시장 외관",
        "detail_alt_old": "시모노세키 항구와 간몬해협 여행을 표현한 참고 이미지",
        "detail_alt_new": "시모노세키 가라토시장 건물 및 출입구의 실제 사진",
        "note": "시모노세키 가라토시장은 2023년 사진입니다. 현재 영업 점포와 시간은 공식 사이트로 확인하세요.",
    },
    {
        "id": "tsushima",
        "old": "/images/editorial/tsushima-izuhara-cruise-port-day-trip.webp",
        "new": "/images/venues/v62-izuhara-port-real.webp",
        "source_page": "https://commons.wikimedia.org/wiki/File:Izuhara_port,_terminal.jpg",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/a/a1/Izuhara_port%2C_terminal.jpg",
            "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a1/Izuhara_port%2C_terminal.jpg/960px-Izuhara_port%2C_terminal.jpg",
        ],
        "author": "Saigen Jiro",
        "license": "CC0 1.0",
        "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
        "year": "2017",
        "alt_old": "대마도 이즈하라 항구 여행 주제 참고 이미지",
        "alt_new": "2017년 실제 촬영된 대마도 이즈하라 여객선 항구 터미널",
        "detail_alt_old": "대마도 이즈하라 항구 여행을 표현한 참고 이미지",
        "detail_alt_new": "대마도 이즈하라항의 실제 여객선 터미널 모습",
        "note": "이즈하라항 터미널은 2017년 촬영 사진입니다. 사진은 현재 터미널 운영 상황을 보장하지 않습니다.",
    },
]

def fetch_photo(spec):
    errors = []
    for uri in spec["urls"]:
        for attempt in range(2):
            try:
                req = urllib.request.Request(uri, headers={
                    "User-Agent": "NIPPONFERRY-PhotoCreditImporter/1.0 (https://www.nipponferry.com/; site photo attribution)",
                    "Accept": "image/jpeg,image/*;q=0.8",
                })
                with urllib.request.urlopen(req, timeout=35) as resp:
                    raw = resp.read(12_000_000)
                with Image.open(io.BytesIO(raw)) as source:
                    source.load()
                    image = ImageOps.exif_transpose(source).convert("RGB")
                if min(image.size) < 500:
                    raise ValueError(f"Unexpected small image: {image.size}")
                image.thumbnail((1440, 1440), Image.Resampling.LANCZOS)
                target = ROOT / "site" / spec["new"].lstrip("/")
                target.parent.mkdir(parents=True, exist_ok=True)
                image.save(target, "WEBP", quality=84, method=5)
                if target.stat().st_size < 25000:
                    raise ValueError("Suspiciously small WebP")
                return {"width": image.width, "height": image.height,
                        "bytes": target.stat().st_size, "download": uri}
            except Exception as ex:
                errors.append(f"{uri}: {type(ex).__name__} {str(ex)[:120]}")
                time.sleep(2 + attempt)
    raise RuntimeError("Failed to import actual photograph:\n" + "\n".join(errors))

def replace_one(source, old, new, title):
    if old not in source:
        if new in source:
            return source
        raise AssertionError(f"{title}: missing old and new marker: {old}")
    return source.replace(old, new)

def update_content(spec):
    # The same images are present on homepage and dedicated one-day articles.
    pages = [
        ROOT / "site/index.html",
        ROOT / "site/things-to-do" / ({"shimonoseki": "shimonoseki-one-day",
            "tsushima": "tsushima-one-day"}[spec["id"]]) / "index.html",
    ]
    for path in pages:
        s = path.read_text(encoding="utf-8")
        is_home = path.name == "index.html" and path.parent.name == "site"
        s = replace_one(s, spec["old"], spec["new"], str(path))
        s = s.replace(spec["alt_old"], spec["alt_new"]).replace(spec["detail_alt_old"], spec["detail_alt_new"])
        credit = (f'<a class="d62-source" href="{spec["source_page"]}" target="_blank" '
                  f'rel="noopener noreferrer">실제 사진: {spec["author"]} / Wikimedia Commons · '
                  f'{spec["license"]} · {spec["year"]}년 촬영 (WebP 리사이즈) ↗</a>')
        if is_home:
            # Scope credit to the card containing this specific image.
            marker = f'<img src="{spec["new"]}"'
            at = s.index(marker)
            nxt = s.index("</a><div class=\"d61-home-body\">", at)
            end = s.index("<small>", nxt)
            s = s[:end] + credit + s[end:]
            # The reference-image badge occurs directly after the new image.
            start = s.index(marker)
            badge = s.index("<em>여행 주제 참고 이미지</em>", start)
            s = s[:badge] + f"<em>실제 장소 촬영 · {spec['year']}년</em>" + s[badge+len("<em>여행 주제 참고 이미지</em>"):]
            if '<style id="d62-real-photo-credit">' not in s:
                s = s.replace("</head>", '<style id="d62-real-photo-credit">.d62-source{display:block;margin:4px 0 7px;font-size:10px;line-height:1.5;color:#476e81;text-decoration:underline;text-underline-offset:2px;overflow-wrap:anywhere}.d61-home-body .d62-source{order:10}</style></head>', 1)
        else:
            s = s.replace("<figcaption>여행 주제 참고 이미지 · 현장 사진 아님</figcaption>",
                          f"<figcaption>실제 현장 사진 · {spec['year']}년 촬영</figcaption>", 1)
            marker = f'<img src="{spec["new"]}"'
            at = s.index(marker)
            endfig = s.index("</figure>", at) + len("</figure>")
            s = s[:endfig] + credit + s[endfig:]
            if '<style id="d62-real-photo-credit">' not in s:
                s = s.replace("</head>", '<style id="d62-real-photo-credit">.d62-source{display:block;margin:8px 13px;font-size:11px;color:#33698a;line-height:1.5;text-decoration:underline;overflow-wrap:anywhere}</style></head>', 1)
            s = s.replace('사진은 기존 사이트 자산을 사용했습니다. 일부 이미지는 주제 이해를 위한 참고 이미지로 표시했습니다.',
                          '사진은 실제 장소 사진과 기존 사이트 자산을 사용했습니다. 촬영연도와 현재 운영 내용은 다를 수 있습니다.')
        path.write_text(s, encoding="utf-8")
    return [str(p.relative_to(ROOT)) for p in pages]

def main():
    report = []
    for spec in PHOTOSET:
        downloaded = fetch_photo(spec)
        updated = update_content(spec)
        report.append({
            "place": spec["id"], "photo": spec["new"], "photo_type": "original location photography",
            "author": spec["author"], "license": spec["license"],
            "license_url": spec["license_url"], "source_page": spec["source_page"],
            "captured_year": spec["year"], "conversion": "JPEG to resized 1440px WebP, quality 84",
            "image": downloaded, "pages": updated,
        })
    index = ROOT / "site/index.html"
    s = index.read_text(encoding="utf-8")
    s = s.replace('※ 시모노세키·대마도 일부 이미지는 여행 주제 참고 자료입니다. 실제 현장 촬영 사진으로 표시하지 않았습니다.',
                  '※ 시모노세키 가라토시장과 대마도 이즈하라항에는 출처 확인된 실제 장소 사진을 사용했습니다. 촬영 당시 풍경이므로 현재 영업·항구 운영 현황은 공식 안내에서 재확인하세요.')
    index.write_text(s, encoding="utf-8")
    out = ROOT / "docs/v62-regional-real-photo-sources.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"photos": len(report), "details": report}, ensure_ascii=False, indent=2))
if __name__ == "__main__":
    main()
