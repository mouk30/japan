#!/usr/bin/env python3
"""V29 supplemental accuracy pass: replace non-Hokkaido fallbacks and rebuild photo credit list."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import quote,urlencode
from io import BytesIO
from html import escape
import json,re
from PIL import Image,ImageOps

additional={
 3:("Sidewalk Snow, Susukino, Sapporo - Jan 23, 2014.jpg","daita saru","CC BY 2.0","https://creativecommons.org/licenses/by/2.0/"),
 13:("JR Chitose-Line New Chitose Airport Station Platform.jpg","Mister0124","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/"),
 21:("Noboribetsu Onsen hot spring.jpg","Lawsonstu","CC0 1.0","https://creativecommons.org/publicdomain/zero/1.0/"),
 23:("Snow roads in Hokkaido (53370261279).jpg","Raita Futo","CC BY 2.0","https://creativecommons.org/licenses/by/2.0/"),
 25:("Mount Hokkaido Komagatake in winter 202601.jpg","掬茶","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/")
}
root=Path("site");manifest=Path("audit-reports/v29/seasons.json")
data=json.loads(manifest.read_text())
s=(root/"seasons/index.html").read_text()
def acquire(i,name):
 src="https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(name.replace(" ","_"),safe="._()-")+"?width=1200"
 proxy="https://wsrv.nl/?"+urlencode({"url":src,"w":"1200","output":"jpg"})
 for url in [proxy,src]:
  try:
   with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=48) as resp:raw=resp.read()
   image=Image.open(BytesIO(raw));image.load()
   if image.width<560 or image.height<400:raise ValueError("source too small")
   image=ImageOps.exif_transpose(image).convert("RGB")
   image.thumbnail((1200,800),Image.Resampling.LANCZOS)
   out=root/"images/seasons"/f"v29-season-{i:02d}.webp"
   image.save(out,"WEBP",quality=83,method=5)
   if out.stat().st_size<10000:raise ValueError("invalid WebP")
   return ("/"+str(out.relative_to(root)),image.size,out.stat().st_size)
  except Exception as e: print("V29_SUPPLEMENT_RETRY",i,str(e)[:100],flush=True)
 return None
for i,(name,author,lic,licurl) in additional.items():
 found=acquire(i,name)
 if not found:continue
 img,dim,nbytes=found
 fileurl="https://commons.wikimedia.org/wiki/File:"+quote(name.replace(" ","_"),safe="._()-")
 card=data["cards_manifest"][i-1]
 needle=re.compile(r'(<a class="dircard" href="'+re.escape(card["href"])+r'">)(<img[^>]*>)(<span class="season-photo-note">[^<]*</span>)')
 m=needle.search(s)
 if not m:raise RuntimeError("card missing: "+str(i))
 im=re.sub(r'src="[^"]+"','src="'+img+'"',m[2])
 im=re.sub(r'alt="[^"]+"','alt="'+escape(card["title"],quote=True)+' 관련 관광·계절 현장 자료사진"',im)
 result=m[1]+im+'<span class="season-photo-note">과거 촬영 실사 · 출처 하단</span>'
 s=s[:m.start()]+result+s[m.end():]
 data["cards_manifest"][i-1]["image"]=img
 data["cards_manifest"][i-1]["real_photo"]=True
 data["photo_sources"][str(i)]={"src":img,"author":author,"license":lic,"license_url":licurl,"url":fileurl,"width":dim[0],"height":dim[1],"bytes":nbytes}
 print("V29_SUPPLEMENT_OK",i,card["title"],nbytes,flush=True)
data["photos"]=len(data["photo_sources"])
# Earlier automatic license labels used region tags; replace with precise card titles.
credits=[]
for key,d in sorted(data["photo_sources"].items(),key=lambda x:int(x[0])):
 i=int(key)
 title=data["cards_manifest"][i-1]["title"]
 license_link=(f'<a href="{escape(d["license_url"])}" rel="noopener noreferrer" target="_blank">{escape(d["license"])}</a>'
               if d.get("license_url") else escape(d["license"]))
 credits.append(f'<li>{escape(title)} — 사진: {escape(d["author"])} · {license_link} · '
                f'<a href="{escape(d["url"])}" rel="noopener noreferrer" target="_blank">Commons 원본 사진</a> · '
                'WebP 크기·형식 변환. 행사·관광시설의 현재 모습을 보장하지 않는 과거 촬영 자료사진입니다.</li>')
creditSection='<section class="wrap seasons-image-credits"><details><summary>대표사진 원본·저작자·라이선스 확인 ('+str(len(credits))+'건)</summary><ol>'+''.join(credits)+'</ol></details></section>'
s,n=re.subn(r'<section class="wrap seasons-image-credits">.*?</section>',lambda m:creditSection,s,count=1,flags=re.S)
if n!=1:raise RuntimeError("credit section not found")
s=s.replace('https://www.nipponferry.com/seasons/','https://www.nipponferry.com/seasons/')
if 'property="og:image"' not in s:
 url='https://www.nipponferry.com/images/seasons/v29-season-01.webp'
 s=s.replace('<meta name="twitter:card"',f'<meta property="og:image" content="{url}"><meta name="twitter:image" content="{url}"><meta name="twitter:card"',1)
if len(set(x["image"] for x in data["cards_manifest"]))!=34:raise RuntimeError("duplicate images")
data["allUnique"]=True
(root/"seasons/index.html").write_text(s)
manifest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
print("V29_SUPPLEMENT_RESULT",json.dumps({"sources":data["photos"],"cards":34,"unique":data["allUnique"]}),flush=True)
