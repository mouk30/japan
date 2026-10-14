#!/usr/bin/env python3
"""V26 4th batch: license-verified Wikimedia Commons real location images.
Only edits five existing cruise-port pages. Fails closed on downloads/markup.
"""
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from io import BytesIO
import re, json
from PIL import Image, ImageOps

ROOT=Path("site")
entries=[
 {"slug":"akita","file":"Akita Port Tower SELION 20170709.jpg","name":"아키타 셀리온 전망타워","author":"掬茶","license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/","year":"2017"},
 {"slug":"kochi","file":"Katsurahama beach through pine trees, Kochi, March 2014.jpg","name":"고치 가쓰라하마 해변","author":"NevinThompson","license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/","year":"2014"},
 {"slug":"matsuyama","file":"Dogo-onsen Honkan.jpg","name":"마쓰야마 도고온천 본관","author":"Mnd","license":"CC BY-SA 2.1 JP","license_url":"https://creativecommons.org/licenses/by-sa/2.1/jp/","year":"2004"},
 {"slug":"maizuru","file":"Maizuru red brick warehouses05s3200.jpg","name":"마이즈루 아카렌가 창고군","author":"663highland","license":"CC BY-SA 3.0","license_url":"https://creativecommons.org/licenses/by-sa/3.0/","year":"2007"},
 {"slug":"kumamoto","file":"KumamotoCastle.jpg","name":"구마모토성 (복구 전 기록사진)","author":"Fg2 / Immanuel Giel","license":"CC BY-SA 3.0","license_url":"https://creativecommons.org/licenses/by-sa/3.0/","year":"2005"},
]
reports=[]
for d in entries:
 slug=d["slug"]; name=d["name"]
 file_url="https://commons.wikimedia.org/wiki/File:"+quote(d["file"].replace(" ","_"),safe="._()-")
 image_url="https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(d["file"].replace(" ","_"),safe="._()-")+"?width=1440"
 req=Request(image_url,headers={"User-Agent":"NipponFerryImageCompliance/1.0 (site content photo reuse; contact via nipponferry.com)","Accept":"image/avif,image/webp,image/jpeg,image/png,*/*"})
 with urlopen(req,timeout=55) as res: data=res.read()
 if len(data)<12000: raise RuntimeError(f"Suspicious image length: {slug}, {len(data)}")
 img=Image.open(BytesIO(data)); img.load()
 if img.width<700 or img.height<500: raise RuntimeError(f"Photo too small: {slug} {img.size}")
 img=ImageOps.exif_transpose(img).convert("RGB")
 img.thumbnail((1440,1000),Image.Resampling.LANCZOS)
 outname=f"{slug}-v26-real-location.webp"
 outpath=ROOT/"images"/"venues"/outname;outpath.parent.mkdir(parents=True,exist_ok=True)
 img.save(outpath,"WEBP",quality=83,method=6)
 pagepath=ROOT/"things-to-do"/f"{slug}-cruise-port-day-trip"/"index.html"
 html=pagepath.read_text(encoding="utf-8")
 hero=re.search(r'<img[^>]*src="/images/editorial/[^"]+"[^>]*>',html)
 if not hero: raise RuntimeError(f"Expected existing AI hero absent: {slug}")
 orig=hero.group()
 newpath=f"/images/venues/{outname}"
 new=re.sub(r'src="[^"]+"',f'src="{newpath}"',orig)
 new=re.sub(r'alt="[^"]*"',f'alt="{name} 실제 촬영 사진 ({d["year"]}년). 크루즈 접안 부두 모습 아님"',new)
 new=re.sub(r'width="\d+"',f'width="{img.width}"',new)
 new=re.sub(r'height="\d+"',f'height="{img.height}"',new)
 html=html.replace(orig,new,1)
 credit=(f'{name} 현장 촬영 사진 ({d["year"]}년 기록, 현재 시설 모습과 다를 수 있음). '
 f'사진: {d["author"]} · <a href="{file_url}" target="_blank" rel="noopener noreferrer">원본 사진</a> · '
 f'<a href="{d["license_url"]}" target="_blank" rel="noopener noreferrer">{d["license"]}</a> · WebP 형식 변환·크기 조정. '
 '관광명소 사진이며 크루즈 접안 위치나 당일 운항 상태를 나타내지 않습니다.')
 caption=re.search(r'<(?:figcaption|p) class="(?:small|source)">AI 생성[^<]*</(?:figcaption|p)>',html)
 if caption:
  newcap=f'<figcaption class="small">{credit}</figcaption>'
  html=html.replace(caption.group(),newcap,1)
 else:
  html=html.replace(new, new+f'<figcaption class="small">{credit}</figcaption>',1)
 # Canonical and descriptions deliberately unchanged; replace OG/Twitter pointers with real assets.
 html=html.replace(f'/images/editorial/{slug}-cruise-port-day-trip.webp',newpath)
 html=re.sub(r'(<meta property="og:image:width" content=")\d+(")',lambda m:m[1]+str(img.width)+m[2],html)
 html=re.sub(r'(<meta property="og:image:height" content=")\d+(")',lambda m:m[1]+str(img.height)+m[2],html)
 html=html.replace('AI 생성 기항지 참고 이미지,','실제 촬영 관광지 이미지,')
 pagepath.write_text(html,encoding="utf-8")
 reports.append({"slug":slug,"image":newpath,"source":file_url,"author":d["author"],"license":d["license"],"width":img.width,"height":img.height,"bytes":outpath.stat().st_size,"note":"Kumamoto historic photo is before 2016 earthquake" if slug=="kumamoto" else "Historical photograph, not real-time"})
print("V26_BATCH4",json.dumps(reports,ensure_ascii=False))
Path("audit-reports/v26").mkdir(parents=True,exist_ok=True)
Path("audit-reports/v26/batch4.json").write_text(json.dumps(reports,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
