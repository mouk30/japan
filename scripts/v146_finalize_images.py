#!/usr/bin/env python3
"""V146: download licensed real Wikimedia photographs, convert to 4:3 WebP and connect
two art-island pilot articles. Run only on dedicated review branch; no AI stock images.
All credits and derivatives remain CC-licensed per original sources."""
import json, os, re, time, hashlib
from html import escape
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image, ImageOps, UnidentifiedImageError

ROOT = Path("site")
CONFIG = [
 dict(slug="naoshima-art-ferry-return", filename="v146-naoshima-miyanoura-ferry-terminal-2025.webp",
   jpg="Naoshima_Ferry_Terminal.jpg", hash="e/e3", year="2025", photographer="Bea Phi",
   license="CC BY-SA 4.0", license_url="https://creativecommons.org/licenses/by-sa/4.0/",
   original="https://commons.wikimedia.org/wiki/File:Naoshima_Ferry_Terminal.jpg",
   alt="2025년 촬영된 일본 나오시마 미야노우라 페리터미널 실경. 넓은 지붕 아래 승객 대기 구역과 선박",
   caption="2025년 9월 촬영 · 실제 나오시마 미야노우라 페리터미널. 사진은 촬영 당시 시설 모습이며 현재 운항 선박·시간표를 보증하지 않습니다."),
 dict(slug="teshima-art-ferry-return", filename="v146-teshima-art-museum-exterior-2013.webp",
   jpg="Teshima_Art_Museum_exterior_view_201310.jpg", hash="1/1d", year="2013",
   photographer="Kentaro Ohno", license="CC BY 2.0",
   license_url="https://creativecommons.org/licenses/by/2.0/",
   original="https://commons.wikimedia.org/wiki/File:Teshima_Art_Museum_exterior_view_201310.jpg",
   alt="2013년 촬영된 일본 데시마미술관의 실제 외관과 주변 자연 풍경",
   caption="2013년 10월 촬영 · 실제 데시마미술관 외관. 과거 촬영 사진으로 현재 시설의 운영상태를 뜻하지 않습니다."),
]
UA = "Mozilla/5.0 (compatible; NIPPONFERRY editorial-photo/1.0; Wikimedia attribution)"

def get_jpeg(item):
    slug=item["jpg"]
    urlset=[
      "https://upload.wikimedia.org/wikipedia/commons/thumb/"+item["hash"]+"/"+slug+"/1920px-"+slug,
      "https://thumb.wikimedia.org/wikipedia/commons/thumb/"+item["hash"]+"/"+slug+"/1280px-"+slug,
      "https://upload.wikimedia.org/wikipedia/commons/"+item["hash"]+"/"+slug,
    ]
    errors=[]
    for url in urlset:
      for attempt in range(3):
       try:
        with urlopen(Request(url,headers={"User-Agent":UA,"Referer":"https://commons.wikimedia.org/"}), timeout=35) as response:
         blob=response.read(16_000_000)
         if response.status!=200 or not blob.startswith(b"\xff\xd8\xff"): raise ValueError("not JPEG")
         img=Image.open(BytesIO(blob));img.verify()
         return blob,url
       except Exception as err:
        errors.append(f"{url} attempt {attempt+1}: {err}");time.sleep(2+attempt)
    raise RuntimeError("Photo download failed: "+"; ".join(errors[-7:]))

def render_webp(blob, destination):
    image=Image.open(BytesIO(blob))
    image=ImageOps.exif_transpose(image).convert("RGB")
    # Center 4:3 crop; photographed scene stays unaltered (no AI retouching).
    width,height=image.size
    crop_ratio=4/3
    if width/height>crop_ratio:
       new_width=int(height*crop_ratio);left=(width-new_width)//2
       image=image.crop((left,0,left+new_width,height))
    else:
       new_height=int(width/crop_ratio);top=(height-new_height)//2
       image=image.crop((0,top,width,top+new_height))
    image=image.resize((1200,900),Image.Resampling.LANCZOS)
    destination.parent.mkdir(parents=True,exist_ok=True)
    image.save(destination, "WEBP", quality=85, method=6)
    with Image.open(destination) as check: assert check.size==(1200,900) and check.format=="WEBP"
    return hashlib.sha256(destination.read_bytes()).hexdigest(),destination.stat().st_size

def patch_html(path,item):
    html=path.read_text(encoding="utf-8")
    if "<figure class=\"v146-hero\"" in html: return False
    if html.count("</header>")!=1:raise ValueError(f"{path}: unexpected header")
    image_path="/images/editorial/"+item["filename"]
    license_html=f'<a href="{item["license_url"]}" target="_blank" rel="noopener noreferrer">{item["license"]}</a>'
    credit=(f'{item["caption"]} 사진: {item["photographer"]} · '
           f'<a href="{item["original"]}" target="_blank" rel="noopener noreferrer">Wikimedia Commons 원본</a> · '
           f'{license_html} · 원본 실사에서 4:3 크롭 후 WebP 변환 (색상·장소의 AI 변경 없음). '
           '저작권 라이선스의 저작자표시·동일조건변경허락 조항을 확인하세요.')
    markup=(f'<figure class="v146-hero" aria-label="실제 장소 사진">'
       f'<img src="{image_path}" alt="{escape(item["alt"],quote=True)}" width="1200" height="900" '
       'fetchpriority="high" decoding="async" loading="eager">'
       f'<figcaption>{credit}</figcaption></figure>')
    html=html.replace('</header>','</header>\n'+markup,1)
    css='''<style id="v146-hero-photo">
.v146-hero{margin:0 0 24px;background:#fff;border:1px solid #cfdee8;border-radius:17px;overflow:hidden;box-shadow:0 8px 27px #0a385414}
.v146-hero img{width:100%;display:block;aspect-ratio:4 / 3;object-fit:cover;height:auto}
.v146-hero figcaption{font-size:13px;line-height:1.85;padding:14px 19px 17px;color:#426276;overflow-wrap:anywhere}
.v146-hero figcaption a{color:#096083;text-decoration:underline;text-underline-offset:3px}
@media(max-width:600px){.v146-hero{border-radius:12px}.v146-hero figcaption{padding:14px;font-size:12px}}
</style>'''
    html=html.replace('</head>',css+'</head>',1)
    absolute="https://www.nipponferry.com"+image_path
    html=html.replace('<meta name="twitter:card" content="summary">',f'<meta property="og:image" content="{absolute}"><meta property="og:image:alt" content="{escape(item["alt"],quote=True)}">\n<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{absolute}">')
    def add_image_to_schema(match):
      obj=json.loads(match.group(1))
      for x in (obj if isinstance(obj,list) else [obj]):
        if x.get("@type")=="Article":x["image"]=[absolute]
      return '<script type="application/ld+json">'+json.dumps(obj,ensure_ascii=False).replace("<","\\u003c")+'</script>'
    html,n=re.subn(r'<script type="application/ld\+json">([\s\S]*?)</script>',add_image_to_schema,html,count=1)
    if n!=1:raise ValueError("No JSON-LD")
    path.write_text(html,encoding="utf-8")
    assert html.count('class="v146-hero"')==1
    return True

def main():
  manifest=[]
  for item in CONFIG:
    dest=ROOT/"images"/"editorial"/item["filename"]
    if not dest.exists():
      blob,download_url=get_jpeg(item)
      sha,bytes_count=render_webp(blob,dest)
    else:
      download_url="existing local image"
      with Image.open(dest) as check:assert check.format=="WEBP" and check.size==(1200,900)
      sha=hashlib.sha256(dest.read_bytes()).hexdigest(); bytes_count=dest.stat().st_size
    page=ROOT/"things-to-do"/item["slug"]/"index.html"
    changed=patch_html(page,item)
    manifest.append(dict(slug=item["slug"],relative_webp=str(dest),source=item["original"],
      retrieved_url=download_url,photographer=item["photographer"],license=item["license"],year=item["year"],
      cropped_4_by_3=True,size_bytes=bytes_count,sha256=sha,page_changed=changed))
  out=Path("audit-output/v146");out.mkdir(parents=True,exist_ok=True)
  (out/"media-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
  print(json.dumps(manifest,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
