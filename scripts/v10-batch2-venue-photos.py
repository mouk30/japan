#!/usr/bin/env python3
"""V10 batch2: fetch verified Commons source, convert to local WebP, attach only on success."""
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.parse import quote
from PIL import Image,ImageOps
import io,json,re
root=Path("site"); dest=root/"images/venues";dest.mkdir(parents=True,exist_ok=True)
items=[
 {"port":"kobe","venue":"고베 애니멀킹덤","file":"Animal Kingdom Kobe Port Island hdsr S5 04.jpg","slug":"kobe-animal-kingdom","by":"Hyppolyte de Saint-Rambert","license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/"},
 {"port":"yokohama","venue":"컵누들 뮤지엄","file":"Cupnoodles museum yokohama.jpg","slug":"yokohama-cupnoodles-museum","by":"Keeezawa","license":"CC0 1.0","license_url":"https://creativecommons.org/publicdomain/zero/1.0/"},
 {"port":"nagasaki","venue":"글로버정원","file":"Nagasaki-Glover-Garden-5384.jpg","slug":"nagasaki-glover-garden","by":"Fg2","license":"Public domain","license_url":"https://commons.wikimedia.org/wiki/File:Nagasaki-Glover-Garden-5384.jpg"},
 {"port":"hakata","venue":"마린월드 우미노나카미치","file":"Marine World Uminonakamichi.jpg","slug":"fukuoka-marine-world","by":"STA3816","license":"CC BY-SA (원본 조건 확인)","license_url":"https://commons.wikimedia.org/wiki/File:Marine_World_Uminonakamichi.jpg"},
 {"port":"ishigaki","venue":"가비라만 글라스보트","file":"Kabira Bay Ishigaki Island23n4500.jpg","slug":"ishigaki-kabira-bay","by":"663highland","license":"CC BY-SA 3.0","license_url":"https://creativecommons.org/licenses/by-sa/3.0/"}
]
report=[]
for a in items:
 file=a["file"];source="https://commons.wikimedia.org/wiki/File:"+quote(file, safe="");url="https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(file,safe="")+"?width=1200"
 try:
  req=Request(url,headers={"User-Agent":"NipponFerryVenueEditorial/1.0 (https://www.nipponferry.com)"})
  with urlopen(req,timeout=45) as response: payload=response.read(14_000_000)
  im=Image.open(io.BytesIO(payload));im=ImageOps.exif_transpose(im).convert("RGB");im.thumbnail((1200,900),Image.Resampling.LANCZOS)
  output=dest/(a["slug"]+".webp");im.save(output,"WEBP",quality=83,method=6)
  if output.stat().st_size<3000:raise ValueError("Converted photo too small")
  page=root/"things-to-do"/(a["port"]+"-cruise-family-guide")/"index.html"
  html=page.read_text(encoding="utf8")
  # Within the TOP-3 card only; never insert photo into an unrelated booking list
  start=html.index('id="ct-topic-dashboard"');title="<h3>"+a["venue"]+"</h3>";p=html.find(title,start)
  if p<0:raise ValueError("Matching venue TOP-3 card not found")
  e=html.find("</article>",p)
  segment=html[p:e]
  local="/images/venues/"+a["slug"]+".webp"
  fig='<figure class="ct-photo v10-local-photo"><img src="'+local+'" width="800" height="533" loading="lazy" decoding="async" alt="'+a["venue"]+' 실제 시설·장소 모습 (촬영 당시)"><figcaption>사진: '+a["by"]+' · '+a["license"]+' · <a href="'+source+'" target="_blank" rel="noopener noreferrer">사진 출처·저작자</a> · <a href="'+a["license_url"]+'" target="_blank" rel="noopener noreferrer">라이선스</a> · WebP 변환·크기 조정</figcaption></figure>'
  # Remove legacy externally hosted photo only for this venue card
  segment=re.sub(r'<figure class="ct-photo"[^>]*>.*?</figure>',"",segment,flags=re.S)
  segment=segment.replace(title,title+fig,1)
  html=html[:p]+segment+html[e:]
  page.write_text(html,encoding="utf8")
  report.append({"venue":a["venue"],"image":str(output),"page":str(page),"status":"published","bytes":output.stat().st_size,"source":source,"license":a["license"]})
 except Exception as exc:
  report.append({"venue":a["venue"],"status":"not_published","error":str(exc)[:400],"source":source})
(dest/"v10-batch2-manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(report,ensure_ascii=False,indent=2))
if any(r["status"]!="published" for r in report):raise SystemExit(1)
