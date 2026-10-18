import pathlib,json,urllib.request,urllib.parse,io,re,html
from PIL import Image,ImageOps
slug="disneysea-rapunzel-lantern"
file_title="File:Rapunzel’s Lantern Festival.jpg"
headers={"User-Agent":"NipponferryPhotoVerification/1.0 (https://www.nipponferry.com)"}
api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","titles":file_title,"prop":"imageinfo","iiprop":"url|extmetadata|size","iiurlwidth":1280})
with urllib.request.urlopen(urllib.request.Request(api,headers=headers),timeout=55) as r: data=json.load(r)
page=next(iter(data["query"]["pages"].values()))
assert "imageinfo" in page,page
info=page["imageinfo"][0]
meta=info["extmetadata"]
clean=lambda s:html.unescape(re.sub(r"<[^>]+>","",s)).strip()
license=clean(meta.get("LicenseShortName",{}).get("value",""))
assert license.startswith("CC BY"),license
assert page["title"]==file_title,page["title"]
artist=clean(meta.get("Artist",{}).get("value",""))[:130]
with urllib.request.urlopen(urllib.request.Request(info.get("thumburl") or info["url"],headers=headers),timeout=60) as r: img=Image.open(io.BytesIO(r.read()));img.load()
assert min(img.size)>=480
img=ImageOps.exif_transpose(img).convert("RGB")
img=ImageOps.fit(img,(1280,720),method=Image.Resampling.LANCZOS)
path=pathlib.Path("site/images/tokyo-verified")/(slug+".webp")
path.parent.mkdir(parents=True,exist_ok=True);img.save(path,"WEBP",quality=86)
jsfile=pathlib.Path("site/tokyo-card-photos.js")
js=jsfile.read_text(encoding="utf8")
registry=json.loads(js.split("const map=",1)[1].split(";document.querySelectorAll",1)[0])
record={"src":"/images/tokyo-verified/"+slug+".webp","alt":"도쿄 디즈니씨 라푼젤 랜턴 페스티벌 어트랙션 표지 실사진","caption":"촬영: "+artist+" · "+license+" · Wikimedia Commons (16:9 WebP 크롭)","source":info["descriptionurl"],"author":artist,"license":license,"source_file":file_title}
registry[slug]=record
js=js.split("const map=",1)[0]+"const map="+json.dumps(registry,ensure_ascii=False,separators=(",",":"))+";document.querySelectorAll"+js.split(";document.querySelectorAll",1)[1]
jsfile.write_text(js,encoding="utf8")
docfile=pathlib.Path("site/japan/tokyo")/slug/"index.html"
doc=docfile.read_text()
esc=lambda s:html.escape(str(s),quote=True)
fig='<figure class="tokyo-article-photo-v1"><img src="'+esc(record["src"])+'" alt="'+esc(record["alt"])+'" loading="lazy" decoding="async"><figcaption>라푼젤 랜턴 페스티벌 어트랙션 표지 · '+esc(artist)+' · '+esc(license)+' · 16:9 크롭 · <a href="'+esc(record["source"])+'" target="_blank" rel="noopener noreferrer">원본 사진·라이선스</a></figcaption></figure>'
pattern=r'<section class="tky-block tokyo-official-photo-pending"[^>]*>.*?</section>'
doc,n=re.subn(pattern,lambda _:fig,doc,count=1,flags=re.S)
assert n==1,n
docfile.write_text(doc)
audit={"updated":slug,"source":file_title,"license":license,"author":artist,"source_url":record["source"],"other_pending":["disneysea-soaring-flight","disney-fantasy-springs-hotel"]}
pathlib.Path("audit-reports/tokyo-disney-three-final-photo-status.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2))
print(json.dumps(audit,ensure_ascii=False))
