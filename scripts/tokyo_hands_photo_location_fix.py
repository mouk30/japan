import io,json,pathlib,requests,re
from PIL import Image,ImageOps
source="File:Tokyu-Hands-Shibuya-2022-11-04 06.jpg"
api="https://commons.wikimedia.org/w/api.php"
headers={"User-Agent":"NipponferryEditorialQA/1.0 (source attribution audit)"}
j=requests.get(api,params={"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","titles":source},headers=headers,timeout=35).json()
p=next(iter(j["query"]["pages"].values()))
assert "missing" not in p,p
meta=p["imageinfo"][0]
u=meta["url"]
resp=requests.get(u,headers=headers,timeout=65);resp.raise_for_status()
im=Image.open(io.BytesIO(resp.content)).convert("RGB")
im=ImageOps.fit(im,(1280,720),method=Image.Resampling.LANCZOS,centering=(.5,.42))
dest=pathlib.Path("site/images/tokyo-verified/tokyo-hands-diy-gifts-shibuya.webp");im.save(dest,"WEBP",quality=83,method=5)
f=pathlib.Path("site/tokyo-card-photos.js");s=f.read_text();map=json.loads(s.split("const map=",1)[1].split(";document.querySelectorAll",1)[0])
name="tokyo-hands-diy-gifts"
map[name]={"src":"/images/tokyo-verified/tokyo-hands-diy-gifts-shibuya.webp","alt":"2022년 촬영된 도쿄 시부야 핸즈 매장 외관 · 매장 내부 사진 아님","caption":"도쿄 시부야 핸즈 매장 외관(2022년) · Wikimedia Commons · 촬영자·라이선스 원본 확인","source":"https://commons.wikimedia.org/wiki/File:Tokyu-Hands-Shibuya-2022-11-04_06.jpg","license":"See Commons source metadata","author":"See Commons source metadata","source_file":source}
f.write_text(s.split("const map=",1)[0]+"const map="+json.dumps(map,ensure_ascii=False,separators=(",",":"))+";document.querySelectorAll"+s.split(";document.querySelectorAll",1)[1])
p=pathlib.Path("site/japan/tokyo/tokyo-hands-diy-gifts/index.html")
doc=p.read_text();fig='<figure class="tokyo-article-photo-v1"><img src="/images/tokyo-verified/tokyo-hands-diy-gifts-shibuya.webp" alt="도쿄 시부야 핸즈 매장 외관, 2022년 촬영" loading="lazy" decoding="async" width="1280" height="720"><figcaption>도쿄 시부야 핸즈 매장 외관(2022년 촬영, 내부·현재 진열 아님). <a href="https://commons.wikimedia.org/wiki/File:Tokyu-Hands-Shibuya-2022-11-04_06.jpg" target="_blank" rel="noopener noreferrer">원본·촬영자·라이선스 확인</a></figcaption></figure>'
doc,n=re.subn(r'<figure class="tokyo-article-photo-v1">.*?</figure>',lambda _:fig,doc,count=1,flags=re.S);assert n==1
p.write_text(doc)
print("correct Tokyo Hands photo",dest,len(resp.content))
