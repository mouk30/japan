import pathlib,re,json,html,time,io,urllib.parse,urllib.request,urllib.error
from PIL import Image,ImageOps
root=pathlib.Path("site")
jsfile=root/"tokyo-card-photos.js"
js=jsfile.read_text()
mapdata=json.loads(js.split("const map=",1)[1].split(";document.querySelectorAll",1)[0])
targets={
"disneysea-rapunzel-lantern":("Tokyo DisneySea Rapunzel Lantern Festival",["rapunzel","disneysea"]),
"disneysea-soaring-flight":("Tokyo DisneySea Soaring Fantastic Flight",["soaring","disneysea"]),
"disney-fantasy-springs-hotel":("Tokyo DisneySea Fantasy Springs Hotel exterior",["fantasy","springs","hotel"]),
"daimaru-tokyo-b1-food":("Daimaru Tokyo department store Tokyo station",["daimaru","tokyo"]),
"daimaru-tokyo-12f-taxfree":("Daimaru Tokyo Yaesu shopping building",["daimaru","tokyo"]),
"daimaru-tokyo-10f-hands":("Daimaru Tokyo Hands shopping",["daimaru","tokyo"])
}
headers={"User-Agent":"NipponferryEditorialMediaAudit/1.0 (https://www.nipponferry.com)"}
def fetch(url):
 for retry in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=45) as r:return r.read()
  except Exception:
   if retry==2:raise
   time.sleep(6*(retry+1))
def strip(s):return html.unescape(re.sub("<[^>]+>","",s)).strip()
used={x.get("source_file") for key,x in mapdata.items() if key not in targets and x.get("source_file")}
done={};pending={}
for slug,(query,tokens) in targets.items():
 try:
  params=urllib.parse.urlencode({"action":"query","format":"json","generator":"search","gsrsearch":query+" filetype:bitmap","gsrnamespace":6,"gsrlimit":50,"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":1280})
  pages=json.loads(fetch("https://commons.wikimedia.org/w/api.php?"+params)).get("query",{}).get("pages",{})
  options=[]
  for page in pages.values():
   title=page.get("title","");low=title.lower()
   if not all(t in low for t in tokens):continue
   if any(t in low for t in ("map","diagram","logo","poster","gif","drawing","sketch","cover")):continue
   if title in used:continue
   info=(page.get("imageinfo") or [{}])[0];meta=info.get("extmetadata",{})
   license=strip(meta.get("LicenseShortName",{}).get("value",""))
   if not (license.startswith("CC BY") or license=="CC0"):continue
   options.append((title,info,meta,license))
  if not options:raise ValueError("No distinct photo matched the exact site/attraction and license filters")
  options.sort(key=lambda a:len(a[0]))
  title,info,meta,license=options[0]
  img=Image.open(io.BytesIO(fetch(info.get("thumburl") or info["url"]))).convert("RGB")
  if min(img.size)<480:raise ValueError("Image too small")
  img=ImageOps.fit(img,(1280,720),method=Image.Resampling.LANCZOS)
  out=root/"images"/"tokyo-verified"/(slug+".webp");out.parent.mkdir(parents=True,exist_ok=True)
  img.save(out,"WEBP",quality=87)
  artist=strip(meta.get("Artist",{}).get("value",""))[:140] or "Wikimedia Commons"
  record={"src":"/images/tokyo-verified/"+slug+".webp","alt":title.removeprefix("File:")+" 관련 현장 사진","caption":"사진: "+artist+" · "+license+" · Wikimedia Commons","author":artist,"license":license,"source":info.get("descriptionurl"),"source_file":title}
  mapdata[slug]=record;used.add(title);done[slug]=title
  art=root/"japan"/"tokyo"/slug/"index.html"
  doc=art.read_text()
  fig=re.search(r'<figure class="tokyo-article-photo-v1">.*?</figure>',doc,re.S)
  if fig:
   q=lambda s:html.escape(str(s),quote=True)
   repl='<figure class="tokyo-article-photo-v1"><img src="'+q(record["src"])+'" alt="'+q(record["alt"])+'" loading="lazy" decoding="async"><figcaption>관련 실제 현장 사진 · '+q(artist)+' · '+q(license)+' · <a href="'+q(record["source"])+'" target="_blank" rel="noopener noreferrer">사진 원본과 라이선스</a></figcaption></figure>'
   art.write_text(doc[:fig.start()]+repl+doc[fig.end():])
 except Exception as e:pending[slug]=str(e)[:190]
 time.sleep(1)
js=js.split("const map=",1)[0]+"const map="+json.dumps(mapdata,ensure_ascii=False,separators=(",",":"))+";document.querySelectorAll"+js.split(";document.querySelectorAll",1)[1]
jsfile.write_text(js)
pathlib.Path("audit-reports/tokyo-six-photo-corrections.json").write_text(json.dumps({"replaced":done,"unresolved":pending,"note":"Unmatched items remain flagged; do not claim visual accuracy without direct human inspection. Original source, license and artist recorded."},ensure_ascii=False,indent=2))
print(json.dumps({"replaced":len(done),"unresolved":len(pending)}))
