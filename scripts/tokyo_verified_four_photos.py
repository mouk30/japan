#!/usr/bin/env python3
"""Four location-specific Commons photos; fail closed on license and downloads."""
import io,json,html,re,pathlib,urllib.request,urllib.parse,time
from PIL import Image,ImageOps
root=pathlib.Path("site")
items=[
("tokyo-asakusa-sensoji-kaminarimon","Senso-ji.jpg","Felix Filnkössl","CC BY-SA 3.0"),
("tokyo-shibuya-crossing-hachiko","Shibuya Crossing in July 2026.jpg","Gatorfan252525","CC BY-SA 4.0"),
("tokyo-shinjuku-night-sightseeing","Shinjuku Kabukicho Entrance.jpg","Ray Tsang","CC BY-SA 2.0"),
("tokyo-akihabara-anime-shopping","Akihabara Electric Town Street - 31-5-2026.jpg","BWard 1997","CC BY 4.0")
]
headers={"User-Agent":"NipponferryTokyoPhotoEditorial/1.0 (https://www.nipponferry.com)","Accept":"application/json,image/*"}
result=[]
for slug,file,author,license_name in items:
 params=urllib.parse.urlencode({"action":"query","format":"json","titles":"File:"+file,"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"1100"})
 req=urllib.request.Request("https://commons.wikimedia.org/w/api.php?"+params,headers=headers)
 with urllib.request.urlopen(req,timeout=35) as res:data=json.load(res)
 page=next(iter(data["query"]["pages"].values()))
 if "missing" in page:raise RuntimeError("Commons file missing "+file)
 info=page["imageinfo"][0];meta=info.get("extmetadata",{})
 lic=html.unescape(re.sub("<[^>]+>","",meta.get("LicenseShortName",{}).get("value",""))).strip()
 if lic.lower().replace(" ","").replace("-","")!=license_name.lower().replace(" ","").replace("-",""):
  raise RuntimeError("License mismatch "+file+" actual "+lic+" expected "+license_name)
 url=info.get("thumburl") or info["url"]
 raw=None
 for retry in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=50) as res:raw=res.read(18*1024*1024)
   break
  except Exception as error:
   if retry==3:raise
   time.sleep(4*(retry+1))
 im=Image.open(io.BytesIO(raw));im.load()
 if im.width<650 or im.height<400:raise RuntimeError("too small "+file)
 im=ImageOps.exif_transpose(im).convert("RGB")
 im.thumbnail((1100,800))
 out=root/"images"/"tokyo-verified"/(slug+".webp");out.parent.mkdir(parents=True,exist_ok=True)
 im.save(out,"WEBP",quality=82,method=6)
 result.append({"slug":slug,"src":"/images/tokyo-verified/"+slug+".webp","title":file,"credit":author,"license":lic,"source":"https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(file.replace(" ","_")),"size":out.stat().st_size})
src='''/* Each named photo downloaded from Commons and checked for licensing. */\n(()=>{const exact=__DATA__;exact["tokyo-odaiba-waterfront-yurikamome"]={src:"/images/editorial/tokyo-yurikamome-automated-train.webp",title:"도쿄 유리카모메",credit:"",license:"",source:""};exact["tokyo-cruise-odaiba-3hours"]={src:"/images/editorial/tokyo-cruise-port-day-trip.webp",title:"도쿄항",credit:"",license:"",source:""};document.querySelectorAll(".tky-card").forEach((card)=>{const slug=(card.getAttribute("href")||"").split("/").filter(Boolean).pop(),p=exact[slug];if(!p||card.querySelector("img"))return;const figure=document.createElement("span");figure.className="tky-card-photo";figure.style.position="relative";const img=document.createElement("img");img.src=p.src;img.alt=p.title+" 실제 현장 사진";img.loading="lazy";img.decoding="async";const credit=document.createElement("span");credit.className="tky-photo-credit";const a=document.createElement("a");a.href=p.source;a.textContent="사진: "+p.credit+" · "+p.license;a.target="_blank";a.rel="noopener noreferrer";a.addEventListener("click",e=>e.stopPropagation());credit.append(a);figure.append(img,credit);img.addEventListener("error",()=>figure.remove(),{once:true});card.insertBefore(figure,card.firstChild)})})();'''.replace("__DATA__",json.dumps({x["slug"]:x for x in result},ensure_ascii=False))
(root/"tokyo-card-photos.js").write_text(src,encoding="utf-8")
(root/"tokyo-photo-credits.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"created":len(result),"assets":[x["src"] for x in result]},ensure_ascii=False))
