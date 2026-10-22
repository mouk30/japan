#!/usr/bin/env python3
"""V124 replace exactly three homepage day-trip card pictures with sourced real scenic WebPs.
Atomic conversion and protected SEO; never modify other card photos or indexed articles.
"""
import hashlib, io, json, re, time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from html import escape
from PIL import Image,ImageOps,ImageEnhance,ImageFilter
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"
HOME=SITE/"index.html"
PLAN=ROOT/"audit-reports/v124/photo-plan.json"
OUT=ROOT/"audit-reports/v124/import-result.json"
PROTECTED=[
 r"<title>[\s\S]*?</title>",
 r'<meta name="description"[^>]*>',
 r'<link rel="canonical"[^>]*>',
 r"<h1\b[^>]*>[\s\S]*?</h1>",
 r'<script type="application/ld\+json">[\s\S]*?</script>',
 r'<meta property="og:title"[^>]*>',
 r'<meta property="og:url"[^>]*>'
]
def protected(x):
 return [[m.group(0) for m in re.finditer(p,x,re.I)] for p in PROTECTED]
def fetch(filename):
 url="https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(filename,safe="")+"?width=1400"
 errors=[]
 for k in range(3):
  try:
   req=Request(url,headers={"User-Agent":"NipponFerry/1.0 (https://www.nipponferry.com/)","Accept":"image/jpeg,image/png,image/webp,*/*"})
   with urlopen(req,timeout=45) as r:
    if r.status!=200 or not r.headers.get("Content-Type","").startswith("image/"):raise ValueError("not HTTP 200 image")
    data=r.read(13000001)
    if len(data)<12000 or len(data)>13000000:raise ValueError("invalid source bytes")
    return data,r.url
  except Exception as e:
   errors.append(repr(e))
   if k<2:time.sleep(3+k*3)
 raise RuntimeError(filename+" download failed "+str(errors)[:260])
def webp(data):
 with Image.open(io.BytesIO(data)) as src:
  src=ImageOps.exif_transpose(src).convert("RGB")
  if src.width<900 or src.height<600:raise ValueError("low resolution")
  # Crop from center to 16:10. Existing homepage card remains 4:3 via CSS,
  # but 16:10 source provides breathing room for responsive object-fit.
  w,h=src.size
  ar=1.5
  if w/h>ar:
   w2=round(h*ar)
   src=src.crop(((w-w2)//2,0,(w+w2)//2,h))
  else:
   h2=round(w/ar)
   src=src.crop((0,(h-h2)//2,w,(h+h2)//2))
  src=src.resize((1200,800),Image.Resampling.LANCZOS)
  src=ImageEnhance.Color(src).enhance(1.085)
  src=ImageEnhance.Contrast(src).enhance(1.065)
  src=ImageEnhance.Sharpness(src).enhance(1.12)
  o=io.BytesIO();src.save(o,format="WEBP",quality=83,method=6)
  ans=o.getvalue()
  if len(ans)<10000 or ans[:4]!=b"RIFF" or ans[8:12]!=b"WEBP":raise ValueError("invalid conversion")
  return ans
def run():
 p=json.loads(PLAN.read_text("utf8"))["photos"]
 if len(p)!=3 or {x["slug"] for x in p}!={"osaka","shimonoseki","tsushima"}:
  raise ValueError("Expected exact 3-card photo plan")
 html=HOME.read_text("utf8");before=html
 photos=[]
 for x in p:
  raw,final_url=fetch(x["filename"])
  dest=SITE/x["output"].lstrip("/")
  data=webp(raw)
  # A unique corresponding card href is required; do not alter unrelated photos.
  pattern=(
   r'(<article class="d61-home-card"><a class="d61-home-photo" href="'
   +re.escape(x["href"])
   +r'"[\s\S]*?<img )src="'+re.escape(x["old"])+r'"([^>]*>)'
  )
  m=re.search(pattern,html)
  if not m:raise ValueError(x["slug"]+" original exact card img not found")
  alt=f'{x["subject"]} (실제 촬영 {x["taken"]}, 당시 풍경)'
  old=m.group(0);new=old.replace('src="'+x["old"]+'"','src="'+x["output"]+'"',1)
  new=re.sub(r'alt="[^"]*"',f'alt="{escape(alt,quote=True)}"',new,count=1)
  new=re.sub(r'width="\d+"', 'width="1200"',new,count=1)
  new=re.sub(r'height="\d+"','height="800"',new,count=1)
  html=html[:m.start()]+new+html[m.end():]
  photos.append({"slug":x["slug"],"output":x["output"],"data":data,
   "sha256":hashlib.sha256(data).hexdigest(),"source_sha256":hashlib.sha256(raw).hexdigest(),
   "bytes":len(data),"width":1200,"height":800,"download_url":final_url,
   "source":x["source"],"date":x["taken"],"license":x["license"],"author":x["author"]})
  print("PREPARED",x["slug"],len(data),flush=True)
 # Only the hero trio source note changes; other photo notes and full on-page SEO stay.
 i=html.index('<p class="d61-home-note">');j=html.index("</p>",i)+len("</p>")
 oldnote=html[i:j]
 if not all(sub in oldnote for sub in ("Kaiy%C5%ABkan.jpg","Karato_Fish_Market","Izuhara_port")):
  raise ValueError("Existing rights attribution note unexpectedly changed")
 anchor=[]
 for x in p:
  anchor.append(f'<a href="{escape(x["source"],quote=True)}" rel="noopener noreferrer" target="_blank">'
   f'{escape(x["slug"].capitalize())} · {escape(x["author"])} · {escape(x["taken"])} · '
   f'{escape(x["license"])}</a> (<a href="{x["license_url"]}" rel="noopener noreferrer" target="_blank">사용조건</a>)')
 note=(
  '<p class="d61-home-note">'
  '※ 여행지 사진은 실제 장소의 과거 촬영본을 선별해 색감 보정·화면비 조정·WebP 변환한 것입니다. '
  '오사카는 덴포잔 대관람차 노을, 시모노세키는 가라토시장 인근 간몬해협의 황혼, '
  '대마도는 이즈하라항 해안 풍경입니다. 실시간 부두·영업상황을 의미하지 않습니다. '
  '이즈하라항과 히타카츠항은 서로 다른 도착항이며, 모지코는 시모노세키 반대편의 별도 여행지입니다. '
  '사진 원본·촬영자·촬영일·라이선스: '+', '.join(anchor)+'. '
  '오사카·시모노세키 변경 이미지는 CC BY-SA 4.0 조건을 유지합니다. '
  '후쿠오카 카드의 연출 이미지는 별도 표기돼 있습니다.'
  '</p>'
 )
 html=html[:i]+note+html[j:]
 if protected(before)!=protected(html):raise ValueError("Original home SEO changed")
 if len(re.findall('class="d61-home-card"',html))!=len(re.findall('class="d61-home-card"',before)):
  raise ValueError("Card count changed")
 for x in p:
  target=f'src="{x["output"]}"'
  if html.count(target)!=1:raise ValueError("New card reference missing "+x["slug"])
 if any(html.count('src="'+x["old"]+'"')!=0 for x in p):
  raise ValueError("Previous bland home image still used in targeted card")
 # Stage first and publish only if every original photo was retrieved and converted.
 for x in photos:
  output=SITE/x["output"].lstrip("/")
  output.parent.mkdir(parents=True,exist_ok=True)
  output.write_bytes(x["data"])
 HOME.write_text(html,"utf8")
 OUT.write_text(json.dumps({"version":"V124","converted":3,"card_updates":3,
  "home_seo_preserved":True,"photographs_not_ai_generated":True,
  "note":"Original generated three mood studies are independent concept art; deployed images are sourced actual photos.",
  "images":[{k:v for k,v in x.items() if k!="data"} for x in photos]},
  ensure_ascii=False,indent=2)+"\n","utf8")
 print("DONE: 3 source-backed photo replacements, unchanged home SEO",flush=True)
if __name__=="__main__":run()
