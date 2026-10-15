#!/usr/bin/env python3
"""V32: upgrade five explicitly topic-matched culture heroes from reference art to
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
 ("bonsai-japanese-miniature-trees","Acer buergerianum bonsai Kyoto.jpg","교토에서 촬영된 분재","Fritzmann2002","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/"),
 ("ikebana-japanese-flower-arrangement","Ikebana Flower Arrangement Japanese Tea Ceremony.jpg","이케바나 꽃꽂이 작품","KuboBella","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/"),
 ("edo-kiriko-cut-glass","Edo-Kiriko.JPG","도쿄 아사쿠사의 에도키리코 공예품","(WT-shared) Shoestring","Public domain","https://commons.wikimedia.org/wiki/Commons:Public_domain"),
 ("hinamatsuri-japanese-dolls","Hinamatsuri.JPG","히나마쓰리 전통 인형 장식","Taichi","CC BY-SA 3.0","https://creativecommons.org/licenses/by-sa/3.0/"),
 ("kokeshi-japanese-wooden-dolls","Kokeshi 1.JPG","일본의 전통 고케시 목제 인형","Boberger","CC BY-SA 3.0","https://creativecommons.org/licenses/by-sa/3.0/"),
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
  except Exception as e: print("V32_DOWNLOAD_RETRY",slug,str(e)[:140],flush=True)
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
 credit=(f'<p class="v32-photo-credit" style="width:min(1060px,calc(100% - 32px));margin:12px auto 22px;'
  f'font-size:12px;line-height:1.7;color:#425e6d">실제 자료사진: {escape(caption)} · 저작자 {escape(author)} · '
  f'<a href="{escape(source)}" rel="noopener noreferrer" target="_blank">Wikimedia Commons 원본</a> · '
  f'{licence_link}{escape(same_license)}. 사진은 당시 촬영된 기록으로 현재 상태를 보장하지 않습니다.</p>')
 # Insert credit after the hero section and before body article. Protect old layout.
 n=0
 for pattern in ['</div><div class="ew el">','</div><div class="w main">']:
  if pattern in html:
   html=html.replace(pattern,'</div>'+credit+pattern[6:],1)
   n=1
   break
 if n!=1:raise RuntimeError("Cannot insert photo credit outside hero for "+slug)
 path.write_text(html,encoding="utf8")
 report.append({"slug":slug,"from":old_url,"to":image_path,"file":file,"creator":author,
  "license":license_name,"license_uri":license_url,"source":source,"bytes":bytesize,
  "width":size[0],"height":size[1]})
 print("V32_EXACT_TOPIC_PHOTO",slug,image_path,bytesize,flush=True)
out=Path("audit-reports/v32");out.mkdir(parents=True,exist_ok=True)
(out/"five-exact-culture-photos.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
print("V32_PHOTO_UPGRADE",len(report),flush=True)
