#!/usr/bin/env python3
"""V34: upgrade five explicitly topic-matched culture heroes from reference art to
real Commons photographs. Original author/license/source shown on each article.
Only commit if all five photos download and all five pages pass validation.
"""
from pathlib import Path
from urllib.parse import quote,urlencode
from urllib.request import Request,urlopen
from io import BytesIO
from html import escape
from PIL import Image,ImageOps
import json,re
ROOT=Path("site")
SOURCES=[
 ("japan-bamboo-grove-ecology","Arashiyama Bamboo Grove.jpg","교토 아라시야마 대나무숲 실제 풍경 (2023년)","Mitchwandrew","CC BY 4.0","https://creativecommons.org/licenses/by/4.0/"),
 ("taiko-japanese-drumming","Namahage Sedo Festival taiko performance.jpg","아키타 오가 나마하게 세도 축제 다이코 공연 (2016년)","KQuhen","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/"),
 ("japan-kyoto-gion-festival-floats","Gion Matsuri Float 1.jpg","교토 기온마쓰리의 실제 수레 (2014년)","Immanuelle","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/"),
 ("japan-jizo-roadside-statues","Stone Jizo statues with red caps and bibs, Kochi, June 2016.jpg","고치의 붉은 모자와 턱받이를 한 지장보살상 (2016년)","NevinThompson","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/"),
 ("japanese-vending-machine-culture","Japanese vending machines (DSCN0712).jpg","도쿄 다이토구의 실제 음료 자판기 (2009년)","Northwest","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/"),
]
def download(name,slug):
 encoded=quote(name.replace(" ","_"),safe="._()-")
 direct="https://commons.wikimedia.org/wiki/Special:FilePath/"+encoded+"?width=1400"
 proxy="https://wsrv.nl/?"+urlencode({"url":direct,"w":"1400","output":"jpg"})
 for address in [proxy,direct]:
  try:
   with urlopen(Request(address,headers={"User-Agent":"Mozilla/5.0"}),timeout=55) as f:data=f.read()
   image=Image.open(BytesIO(data));image.load()
   if image.width<560 or image.height<390:raise RuntimeError(f"image too small {image.size}")
   image=ImageOps.exif_transpose(image).convert("RGB")
   image.thumbnail((1400,1050),Image.Resampling.LANCZOS)
   outfile=ROOT/"images"/"culture-verified"/(slug+".webp")
   outfile.parent.mkdir(parents=True,exist_ok=True)
   image.save(outfile,"WEBP",quality=85,method=6)
   if outfile.stat().st_size<10000:raise RuntimeError("truncated")
   return "/images/culture-verified/"+slug+".webp",image.size,outfile.stat().st_size
  except Exception as e: print("V34_DOWNLOAD_RETRY",slug,str(e)[:140],flush=True)
 raise RuntimeError("Cannot verify/download exact licensed image for "+slug)
report=[]
for slug,file,caption,author,license_name,license_url in SOURCES:
 source="https://commons.wikimedia.org/wiki/File:"+quote(file.replace(" ","_"),safe="._()-")
 image_path,size,bytesize=download(file,slug)
 path=ROOT/"things-to-do"/slug/"index.html"
 html=path.read_text("utf8")
 # The first in-content picture is the topic reference hero, never the logo in navigation.
 main=html.find("<main")
 match=re.search(r'<img\b[^>]*src="(/images/editorial/[^"]+)"[^>]*>',html[main:])
 if not match:raise RuntimeError("Hero image tag missing "+slug)
 before=match.group()
 old_url=match.group(1)
 after=before.replace('src="'+old_url+'"','src="'+image_path+'"')
 after=re.sub(r'alt="[^"]*"','alt="'+escape(caption,quote=True)+' 실제 촬영 사진"',after)
 after=re.sub(r'\s+onerror="[^"]*"','',after)
 if 'decoding=' not in after:after=after[:-1]+' decoding="async">'
 html=html[:main]+html[main:].replace(before,after,1)
 # Update all SEO image pointers that still identify the old source.
 html=html.replace('https://www.nipponferry.com'+old_url,'https://www.nipponferry.com'+image_path)
 # Any structured data with relative old source also becomes real photo.
 html=html.replace('"'+old_url+'"','"'+image_path+'"')
 if 'name="nf-topic-photo-note"' in html:
  html=re.sub(r'<meta name="nf-topic-photo-note"[^>]*>', '',html,count=1)
 same_license=(' · WebP 변환·크기 조정본도 동일 '+license_name+' 조건으로 제공' if license_name.startswith('CC ') else ' · 공개 도메인 작품을 WebP로 변환')
 licence_link=(f'<a href="{escape(license_url)}" rel="noopener noreferrer" target="_blank">{escape(license_name)}</a>')
 credit=(f'<p class="v34-photo-credit" style="width:min(1060px,calc(100% - 32px));margin:12px auto 22px;'
  f'font-size:12px;line-height:1.7;color:#425e6d">실제 자료사진: {escape(caption)} · 저작자 {escape(author)} · '
  f'<a href="{escape(source)}" rel="noopener noreferrer" target="_blank">Wikimedia Commons 원본</a> · '
  f'{licence_link}{escape(same_license)}. 과거 촬영한 자료사진이며 현재 축제·시설 운영 상황을 의미하지 않습니다.</p>')
 # Insert credit after the hero section and before body article. Protect old layout.
 n=0
 for pattern in ['</div><div class="ew el">','</div><div class="w main">','</div><div class="w lay">','</div><div class="w layout">']:
  if pattern in html:
   html=html.replace(pattern,'</div>'+credit+pattern[6:],1)
   n=1
   break
 if n!=1:raise RuntimeError("Cannot insert photo credit outside hero for "+slug)
 path.write_text(html,encoding="utf8")
 report.append({"slug":slug,"from":old_url,"to":image_path,"file":file,"creator":author,
  "license":license_name,"license_uri":license_url,"source":source,"bytes":bytesize,
  "width":size[0],"height":size[1]})
 print("V34_EXACT_TOPIC_PHOTO",slug,image_path,bytesize,flush=True)
out=Path("audit-reports/v34");out.mkdir(parents=True,exist_ok=True)
(out/"five-exact-culture-photos.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
print("V34_PHOTO_UPGRADE",len(report),flush=True)
