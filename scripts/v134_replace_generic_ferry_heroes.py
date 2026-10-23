#!/usr/bin/env python3
"""V134 replace five generic ferry-route hero images with three actual reusable Commons photographs.

All five existing paths and original SEO title/description/canonical remain exactly.
Three unique photos are sufficient because the three Fukuoka articles share the
same real New Camellia route vessel; two Tsushima ports receive their own terminal.
Photo captions disclose original date, site, author, CC license and conversion.
Do not infer current operations, route availability or exact embarkation gate.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import quote
from html import escape
from PIL import Image,ImageOps
import json,io,hashlib,re,time
ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/"audit-reports/v134/photo-plan.json"
BASE=ROOT/"audit-reports/v134/original-protected-metadata.json"
RESULT=ROOT/"audit-reports/v134/photo-import-result.json"
def fetch_image(name):
 url="https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(name,safe="")+"?width=1400"
 errors=[]
 for attempt in range(4):
  try:
   req=Request(url,headers={"User-Agent":"NipponFerryResearch/1.0 (https://www.nipponferry.com/)","Accept":"image/*"})
   with urlopen(req,timeout=65) as res:
    if res.status!=200 or "image/" not in res.headers.get("Content-Type",""):
     raise ValueError("not direct image")
    if "wikimedia.org" not in res.url:raise ValueError("unexpected origin: "+res.url)
    raw=res.read(14000001)
    if len(raw)<10000 or len(raw)>14000000:raise ValueError("not expected image bytes")
    return raw,res.url
  except Exception as ex:
   errors.append(str(ex)[:150])
   if attempt<3:time.sleep((attempt+1)*3)
 raise RuntimeError(name+": "+"; ".join(errors))
def one(html,pattern,name):
 match=re.search(pattern,html,re.S)
 if not match:raise RuntimeError("Missing protected "+name)
 return match.group(1)
def run():
 spec=json.loads(PLAN.read_text("utf8"))
 sources={x["key"]:x for x in spec["photos"]}
 pages=json.loads(BASE.read_text("utf8"))["pages"]
 if len(pages)!=5 or len(sources)!=3 or len({x["slug"] for x in pages})!=5:raise RuntimeError("V134 expected 5 pages/3 photos")
 converted={}
 for key,item in sources.items():
  raw,download=fetch_image(item["filename"])
  with Image.open(io.BytesIO(raw)) as photo:
   photo=ImageOps.exif_transpose(photo).convert("RGB")
   if photo.width<800 or photo.height<450:raise ValueError(key+" source resolution insufficient")
   photo.thumbnail((1400,1000),Image.Resampling.LANCZOS)
   width,height=photo.size
   b=io.BytesIO();photo.save(b,format="WEBP",quality=85,method=6)
   blob=b.getvalue()
  if len(blob)<7000 or blob[:4]!=b"RIFF" or blob[8:12]!=b"WEBP":raise RuntimeError(key+" invalid webp")
  converted[key]={"width":width,"height":height,"blob":blob,"download":download,"raw_sha256":hashlib.sha256(raw).hexdigest(),"webp_sha256":hashlib.sha256(blob).hexdigest(),"bytes":len(blob)}
  print("SOURCE VERIFIED",key,width,height,len(blob),flush=True)
 staged=[]
 for pg in pages:
  slug=pg["slug"]
  source=sources[pg["picture"]]
  bininfo=converted[pg["picture"]]
  file=ROOT/"site/guide"/slug/"index.html"
  old=file.read_text("utf8")
  for label,rx in (
    ("title",r"<title>([^<]*)</title>"),
    ("description",r'<meta name="description" content="([^"]*)"'),
    ("canonical",r'<link rel="canonical" href="([^"]*)"')):
   if one(old,rx,label)!=pg[label]:raise RuntimeError(slug+" protected SEO drift "+label)
  tag=re.search(r'<img class="article-cover" src="'+re.escape(pg["old_cover"])+r'"[^>]*>',old)
  if not tag:raise RuntimeError(slug+" expected generic hero missing")
  if "nf-v134-photo-credit" in old:raise RuntimeError(slug+" already converted")
  alt=(f'{source["subject"]} 사진 촬영일 {source["date"]}, 촬영자 {source["author"]}.')
  replacement=(f'<img class="article-cover" src="{source["output"]}" width="{bininfo["width"]}" height="{bininfo["height"]}" alt="{escape(alt,quote=True)}" decoding="async" fetchpriority="high">')
  credit=(f'<p class="nf-v134-photo-credit" style="font-size:12px;line-height:1.8;color:#496779;max-width:850px;margin:9px 0 20px;padding:8px 12px;border-left:3px solid #2585a2;background:#f5f9fb">'
   f'실제 촬영 사진 · {escape(source["subject"])} 촬영일 {source["date"]} · 촬영자 {escape(source["author"])} · '
   f'<a href="{escape(source["source"],quote=True)}" target="_blank" rel="noopener noreferrer">원본 사진·촬영 장소</a> · '
   f'<a href="{escape(source["license_url"],quote=True)}" target="_blank" rel="noopener noreferrer">{escape(source["license"])}</a> · '
   f'원본 사진을 크기 조정·WebP 변환했습니다. '
   f'{"CC BY-SA 동일조건 재사용에 유의하세요. " if "BY-SA" in source["license"] else ""}'
   f'현재 운항·시설 개방·접안 게이트의 실시간 증빙은 아닙니다.</p>')
  new=old[:tag.start()]+replacement+credit+old[tag.end():]
  og="https://www.nipponferry.com"+source["output"]
  if '<meta property="og:image"' in new or '<meta name="twitter:image"' in new:
   raise RuntimeError(slug+" untracked OG/Twitter existing")
  meta=f'<meta property="og:image" content="{og}"><meta name="twitter:image" content="{og}">'
  if new.count("</head>")!=1:raise RuntimeError("head not unique "+slug)
  new=new.replace("</head>",meta+"</head>",1)
  for label,rx in (
    ("title",r"<title>([^<]*)</title>"),
    ("description",r'<meta name="description" content="([^"]*)"'),
    ("canonical",r'<link rel="canonical" href="([^"]*)"')):
   if one(new,rx,label)!=pg[label]:raise RuntimeError(slug+" SEO changed after replacement "+label)
  if new.count('class="article-cover"')!=1 or new.count('class="nf-v134-photo-credit"')!=1:
   raise RuntimeError(slug+" duplicate photo elements")
  staged.append({"slug":slug,"path":file,"html":new,"output":source["output"],"author":source["author"],"license":source["license"],"original":source["source"]})
 if len(staged)!=5:raise RuntimeError("partial batch refused")
 for key,photoinfo in converted.items():
  path=ROOT/"site"/sources[key]["output"].lstrip("/")
  path.parent.mkdir(parents=True,exist_ok=True)
  path.write_bytes(photoinfo["blob"])
 for x in staged:x["path"].write_text(x["html"],"utf8")
 data={"version":"V134","status":"webp created and five source pages updated","photos": [{**{k:x[k] for k in ("key","source","author","date","license","license_url","output","subject")},**{k:converted[x["key"]][k] for k in ("raw_sha256","webp_sha256","width","height","bytes","download")}} for x in spec["photos"]],"pages":[{k:v for k,v in x.items() if k not in ("path","html")} for x in staged],"updated_pages":5,"distinct_real_source_photos":3,"preserved_existing_seo":5}
 RESULT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n","utf8")
 print(json.dumps({"updated_pages":5,"distinct_photos":3,"seo_preserved":5},ensure_ascii=False))
if __name__=="__main__":run()
