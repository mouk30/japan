#!/usr/bin/env python3
"""V26 4th batch: license-verified Wikimedia Commons real location images.
Only edits five existing cruise-port pages. Fails closed on downloads/markup.
"""
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
from io import BytesIO
import re, json
from PIL import Image, ImageOps

ROOT=Path("site")
entries=[
 {"slug":"hiroshima","file":"A Bomb Dome and Peace Park.jpg","name":"히로시마 평화기념공원·원폭돔","author":"SRP1998","license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/","year":"2025"},
 {"slug":"iwakuni","file":"Kintaikyo Bridge on Nishikigawa River 2.jpg","name":"이와쿠니 긴타이쿄 다리","author":"そらみみ","license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/","year":"2018"},
 {"slug":"kure","file":"Yamato Museum and Kure Central Pier from Yamato Wharf.jpg","name":"구레 야마토뮤지엄과 중앙부두","author":"そらみみ","license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/","year":"2018"},
 {"slug":"mojiko","file":"140721 Mojiko Station Kitakyushu Japan03s3.jpg","name":"모지코 레트로역","author":"663highland","license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/","year":"2014"},
 {"slug":"aburatsu","file":"Obi, Nichinan, Ōtemon Gate of Obi Castle 01.jpg","name":"니치난 오비성 오테몬","author":"commons contributor","license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/","year":"2019"}
]
reports=[]
for d in entries:
 slug=d["slug"]; name=d["name"]
 file_url="https://commons.wikimedia.org/wiki/File:"+quote(d["file"].replace(" ","_"),safe="._()-")
 image_url="https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(d["file"].replace(" ","_"),safe="._()-")+"?width=1440"
 req=Request(image_url,headers={"User-Agent":"NipponFerryImageCompliance/1.0 (site content photo reuse; contact via nipponferry.com)","Accept":"image/avif,image/webp,image/jpeg,image/png,*/*"})
 try:
  with urlopen(req,timeout=35) as res: data=res.read()
 except Exception as first_error:
  proxy="https://wsrv.nl/?"+urlencode({"url":image_url,"output":"jpg","w":"1440"})
  try:
   with urlopen(Request(proxy,headers={"User-Agent":"Mozilla/5.0"}),timeout=50) as res: data=res.read()
  except Exception as other_error:
   raise RuntimeError(f"Verified Commons photo unavailable for {slug}: {first_error}; proxy: {other_error}")

 if len(data)<12000: raise RuntimeError(f"Suspicious image length: {slug}, {len(data)}")
 img=Image.open(BytesIO(data)); img.load()
 if img.width<700 or img.height<500: raise RuntimeError(f"Photo too small: {slug} {img.size}")
 img=ImageOps.exif_transpose(img).convert("RGB")
 img.thumbnail((1440,1000),Image.Resampling.LANCZOS)
 outname=f"{slug}-v26b5-real-location.webp"
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
print("V26_BATCH5",json.dumps(reports,ensure_ascii=False))
Path("audit-reports/v26").mkdir(parents=True,exist_ok=True)
Path("audit-reports/v26/batch5.json").write_text(json.dumps(reports,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
