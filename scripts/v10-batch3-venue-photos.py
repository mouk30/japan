#!/usr/bin/env python3
"""V10 batch3: download source-credited location photos; only replace cards if download succeeded."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import quote
from PIL import Image,ImageOps
import io,json,re
root=Path("site")
folder=root/"images"/"venues";folder.mkdir(parents=True,exist_ok=True)
targets=[
 ("aomori","A-FACTORY·ASPAM","A-factory.JPG","aomori-a-factory","Angaurits","CC0 1.0","https://creativecommons.org/publicdomain/zero/1.0/"),
 ("beppu","기지마 고원 파크","Jupiter_roller_coaster_at_Kijima_Kogen.jpg","beppu-kijima-jupiter","Martin Lewison","CC BY-SA 2.0","https://creativecommons.org/licenses/by-sa/2.0/"),
 ("aomori","아사무시 수족관","Asamushi_Aquarium_Aomori_Japan03n.jpg","aomori-asamushi-aquarium","663highland","CC BY-SA 3.0","https://creativecommons.org/licenses/by-sa/3.0/"),
 ("beppu","우미타마고 수족관","Umitamago.jpg","beppu-umitamago-aquarium","OitaKiseichu","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/"),
 ("aomori","네부타 와랏세","Nebuta_house_Warasse_Aomori_Japan10n.jpg","aomori-nebuta-warasse","663highland","CC BY-SA 3.0","https://creativecommons.org/licenses/by-sa/3.0/"),
 ("beppu","벳푸 지옥 순례","Umi_Jigoku_(Sea_Hell)_in_Beppu.jpg","beppu-umi-jigoku","Bpcon98","CC0 1.0","https://creativecommons.org/publicdomain/zero/1.0/"),
 ("hakodate","고료카쿠 타워","Goryokaku_Tower_Hakodate_Hokkaido_Japan01n.jpg","hakodate-goryokaku-tower","663highland","CC BY 2.5","https://creativecommons.org/licenses/by/2.5/")
]
results=[]
for port,venue,name,slug,author,lic,licurl in targets:
 source="https://commons.wikimedia.org/wiki/File:"+quote(name)
 try:
  url="https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(name)+"?width=1200"
  with urlopen(Request(url,headers={"User-Agent":"NipponFerryTravelEditorial/1.0 (https://www.nipponferry.com)"}),timeout=35) as r:b=r.read(14_000_000)
  img=ImageOps.exif_transpose(Image.open(io.BytesIO(b))).convert("RGB");img.thumbnail((1200,900),Image.Resampling.LANCZOS)
  file=folder/(slug+".webp");img.save(file,"WEBP",quality=83,method=6)
  if file.stat().st_size<3000:raise ValueError("image too small")
  page=root/"things-to-do"/(port+"-cruise-family-guide")/"index.html"
  c=page.read_text(encoding="utf-8")
  marker='<h3>'+venue+'</h3>';start=c.index('id="ct-topic-dashboard"');i=c.index(marker,start);j=c.index("</article>",i)
  seg=c[i:j]
  seg=re.sub(r'<figure class="ct-photo"[^>]*>.*?</figure>',"",seg,flags=re.S)
  fig='<figure class="ct-photo"><img src="/images/venues/'+slug+'.webp" width="960" height="640" alt="'+venue+' 실제 장소 현장 사진" loading="lazy" decoding="async"><figcaption>사진: '+author+' · '+lic+' · <a href="'+source+'" target="_blank" rel="noopener noreferrer">원본·저작자</a> · <a href="'+licurl+'" target="_blank" rel="noopener noreferrer">라이선스</a> · WebP 변환·리사이즈</figcaption></figure>'
  seg=seg.replace(marker,marker+fig,1);c=c[:i]+seg+c[j:];page.write_text(c,encoding="utf-8")
  results.append({"port":port,"venue":venue,"status":"ok","webp":str(file),"size_bytes":file.stat().st_size})
 except Exception as e:results.append({"port":port,"venue":venue,"status":"failed","error":str(e)})
(folder/"v10-batch3-manifest.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(results,ensure_ascii=False,indent=2))
if not any(x["status"]=="ok" for x in results):raise SystemExit(1)\n# Failed images remain unchanged; publish each successful image independently.
