#!/usr/bin/env python3
"""V43 acceptance on published site: 20 genuine originals and photo-spots route.
Production WebP bytes must match the exact repository revision.
"""
import concurrent.futures,hashlib,json,time,urllib.request
from pathlib import Path

SITE="https://www.nipponferry.com"
ROOT=Path("site")
photos=json.loads(Path("docs/v43-deployed-photo-credits.json").read_text("utf-8"))
assert len(photos)==20
checks=[]
REGIONS=["/japan/fukuoka-photo/","/japan/osaka-photo/","/japan/tsushima-photo/","/japan/shimonoseki-photo/"]
items=[("image",r["slug"],r["asset"],r["asset"]) for r in photos]
items.extend(("page",r["slug"],f"/things-to-do/{r['slug']}/",r["asset"]) for r in photos)
items.extend([("hub","directory","/things-to-do/",""),
("home","home","/",""),
("spots","spots","/photo-spots/",""),
("explore","map","/explore/",""),
("sitemap","sitemap","/sitemap.xml","")])
items.extend(("region",str(i),url,"") for i,url in enumerate(REGIONS))
assert len(items)==49,len(items)
def test(entry):
  typ,slug,path,asset=entry
  try:
    request=urllib.request.Request(SITE+path+"?v43="+str(int(time.time())),
      headers={"User-Agent":"Nipponferry-V43-website-audit/1.0 (https://www.nipponferry.com/)",
               "Cache-Control":"no-cache"})
    with urllib.request.urlopen(request,timeout=50) as response:
      status=response.status
      b=response.read()
      mime=response.headers.get("Content-Type","")
    txt=b.decode("utf-8","replace") if typ!="image" else None
    ok=status==200
    detail={}
    if typ=="image":
      expected=hashlib.sha256((ROOT/path.lstrip("/")).read_bytes()).hexdigest()
      actual=hashlib.sha256(b).hexdigest()
      ok&=len(b)>7000 and b[:4]==b"RIFF" and b[8:12]==b"WEBP" and actual==expected
      detail={"bytes":len(b),"sha256_matches_repository":actual==expected}
    elif typ=="page":
      url=SITE+asset
      ok&=(f'src="{asset}"' in txt and
          f'<meta property="og:image" content="{url}">' in txt and
          f'<meta name="twitter:image" content="{url}">' in txt and
          "Wikimedia Commons" in txt)
    elif typ=="hub":
      ok&=all(f'src="{x["asset"]}"' in txt for x in photos)
      ok&="V43 responsive audit" in txt
    elif typ=="home":
      ok&=txt.count('href="/photo-spots/"')>=2
      ok&='<b>포토 스팟</b>' in txt
    elif typ=="spots":
      ok&='class="photo-card"' in txt and txt.count('class="photo-card"')==4
      ok&=all('href="'+url+'"' in txt for url in REGIONS)
      ok&='href="/explore/"' in txt and 'id="exploreMap"' not in txt
      ok&='<link rel="canonical" href="https://www.nipponferry.com/photo-spots/">' in txt
    elif typ=="explore":
      ok&='id="exploreMap"' in txt and 'href="/photo-spots/"' in txt
    elif typ=="sitemap":
      ok&='<loc>https://www.nipponferry.com/photo-spots/</loc>' in txt
      ok&=all(f'<loc>{SITE}/things-to-do/{x["slug"]}/</loc>' in txt for x in photos)
    elif typ=="region":
      ok&=('<h1>' in txt and 'photo' in path)
    return {"type":typ,"slug":slug,"path":path,"status":status,"ok":bool(ok),"mime":mime,**detail}
  except Exception as exc:
    return {"type":typ,"slug":slug,"path":path,"ok":False,"error":str(exc)[:180]}
REPORT=Path("docs/v43-live-qa.json")
result={"site":SITE,"checks":[],"complete":False,"attempts":[]}
for attempt in range(1,6):
  with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    checks=list(executor.map(test,items))
  failed=[x for x in checks if not x["ok"]]
  result.update({"checks":checks,"complete":not failed,"attempt":attempt})
  result["attempts"].append({"attempt":attempt,"ok":len(checks)-len(failed),"total":len(checks),
                             "failed":failed[:5]})
  REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
  print(f"V43 live QA {attempt}: {len(checks)-len(failed)}/{len(checks)}",str(failed[:2])[:500],flush=True)
  if not failed:break
  if attempt<5:time.sleep(18)
if not result["complete"]:raise SystemExit("V43 production mismatch")
print("PASS 49 actual HTTP checks incl 20 WebP byte-perfect SHA256 and photo spot links",flush=True)
