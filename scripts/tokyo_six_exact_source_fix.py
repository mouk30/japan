import pathlib,json,urllib.parse,urllib.request,io,html,re,time
from PIL import Image,ImageOps
root=pathlib.Path("site")
mappingfile=root/"tokyo-card-photos.js"
js=mappingfile.read_text(encoding="utf-8")
mapping=json.loads(js.split("const map=",1)[1].split(";document.querySelectorAll",1)[0])
candidates={
 "disneysea-rapunzel-lantern":["File:Rapunzel’s Lantern Festival.jpg","라푼젤 랜턴 페스티벌 어트랙션 표지"],
 "daimaru-tokyo-b1-food":["File:DAIMARU TOKYO Entrance 2019.jpg","다이마루 도쿄점 입구 · B1 식품관 내부 사진 아님"],
 "daimaru-tokyo-12f-taxfree":["File:Daimaru Tokyo and Yaesu exit, Tokyo station - Aug 28, 2025.jpg","도쿄역 야에스 출구 다이마루 도쿄점 외관 · 12층 사진 아님"],
 "daimaru-tokyo-10f-hands":["File:Daimaru tokyo (49750080667).jpg","다이마루 도쿄점 외관 · 10층 핸즈 내부 사진 아님"]
}
# Any unresolved image is deliberately left unchanged; publish honest failure list.
results={};unresolved={}
headers={"User-Agent":"NipponferryCreativeCommonsPhotoCorrection/1.0 (https://www.nipponferry.com)"}
for slug,(title,description) in candidates.items():
 try:
  url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","titles":title,"prop":"imageinfo","iiprop":"url|extmetadata|size","iiurlwidth":1280})
  req=urllib.request.Request(url,headers=headers)
  with urllib.request.urlopen(req,timeout=45) as r: response=json.load(r)
  page=next(iter(response["query"]["pages"].values()))
  info=page["imageinfo"][0]
  def clean(v):return html.unescape(re.sub(r"<[^>]+>","",v)).strip()
  meta=info["extmetadata"]
  lic=clean(meta.get("LicenseShortName",{}).get("value",""))
  if not(lic.startswith("CC BY") or lic=="CC0"):raise ValueError("license mismatch "+lic)
  artist=clean(meta.get("Artist",{}).get("value",""))[:130]
  with urllib.request.urlopen(urllib.request.Request(info.get("thumburl") or info["url"],headers=headers),timeout=60) as r:
   im=Image.open(io.BytesIO(r.read()));im.load()
  if min(im.size)<420:raise ValueError("image too small")
  im=ImageOps.exif_transpose(im).convert("RGB")
  im=ImageOps.fit(im,(1280,720),method=Image.Resampling.LANCZOS)
  target=root/"images/tokyo-verified"/(slug+".webp");target.parent.mkdir(exist_ok=True,parents=True)
  im.save(target,"WEBP",quality=86)
  data={"src":"/images/tokyo-verified/"+slug+".webp","alt":description,"caption":"사진: "+artist+" · "+lic+" · Wikimedia Commons","source":info["descriptionurl"],"license":lic,"author":artist,"source_file":page["title"]}
  mapping[slug]=data
  file=root/"japan/tokyo"/slug/"index.html"
  doc=file.read_text()
  q=lambda v:html.escape(str(v),quote=True)
  figure='<figure class="tokyo-article-photo-v1"><img src="'+q(data["src"])+'" alt="'+q(description)+'" loading="lazy" decoding="async"><figcaption>'+q(description)+' · 촬영: '+q(artist)+' · '+q(lic)+' · <a href="'+q(data["source"])+'" target="_blank" rel="noopener noreferrer">원본·라이선스</a></figcaption></figure>'
  doc,n=re.subn(r'<figure class="tokyo-article-photo-v1">[\s\S]*?</figure>',lambda _:figure,doc,count=1)
  if n!=1:raise ValueError("hero figure missing")
  file.write_text(doc)
  results[slug]={"file":page["title"],"license":lic,"author":artist}
 except Exception as e:unresolved[slug]=str(e)[:180]
 time.sleep(.3)
js=js.split("const map=",1)[0]+"const map="+json.dumps(mapping,ensure_ascii=False,separators=(",",":"))+";document.querySelectorAll"+js.split(";document.querySelectorAll",1)[1]
mappingfile.write_text(js)
for slug in ("disneysea-soaring-flight","disney-fantasy-springs-hotel"):
 unresolved[slug]="No exact, verified site photograph selected; misleading existing photo remains to be removed/replaced."
report={"replaced":results,"unresolved":unresolved,"notes":"Daimaru photographs depict the actual Tokyo store exterior, not the specific B1, 10F, or 12F floor."}
pathlib.Path("audit-reports/tokyo-six-exact-source-photo-fix.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({"replaced":len(results),"pending":len(unresolved)},ensure_ascii=False))
