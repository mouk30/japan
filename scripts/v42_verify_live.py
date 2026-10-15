#!/usr/bin/env python3
"""V42 public-site acceptance: 52 local WebPs, 52 article OG/Twitter previews, 1 hub."""
import concurrent.futures,json,time,urllib.request
from pathlib import Path

HOST="https://www.nipponferry.com"
items=json.loads(Path("docs/v42-image-audit/finalized-52.json").read_text("utf-8"))["rows"]
assert len(items)==52
RESULT=Path("docs/v42-live-qa.json")
UA="Nipponferry-V42-qa/1.0 (https://www.nipponferry.com/)"
def fetch(url):
 req=urllib.request.Request(url,headers={"User-Agent":UA,"Cache-Control":"no-cache"})
 with urllib.request.urlopen(req,timeout=45) as resp:
   return resp.status,resp.headers.get("Content-Type",""),resp.read()
def check(spec,attempt):
 kind,slug,path,asset=spec
 url=HOST+path+f"?v42={attempt}"
 try:
   status,mime,content=fetch(url)
   if kind=="webp":
      valid=status==200 and content[:4]==b"RIFF" and content[8:12]==b"WEBP"
   elif kind=="article":
      expected=f'content="{HOST}{asset}"'.encode()
      valid=(status==200 and f'src="{asset}"'.encode() in content and
             f'<meta property="og:image" {expected.decode()}>'.encode() in content and
             f'<meta name="twitter:image" {expected.decode()}>'.encode() in content)
   else:
      valid=(status==200 and all(f'src="{a["image"]}"'.encode() in content for a in items))
   return {"kind":kind,"slug":slug,"path":path,"status":status,"mime":mime,"bytes":len(content),"ok":valid}
 except Exception as e:return {"kind":kind,"slug":slug,"path":path,"ok":False,"error":str(e)[:170]}
specs=[]
for item in items:
 specs.extend([
  ("webp",item["slug"],item["image"],item["image"]),
  ("article",item["slug"],item["article"],item["image"])
 ])
specs.append(("hub","all52","/things-to-do/",""))
assert len(specs)==105
final={"host":HOST,"complete":False,"attempts":[]}
for attempt in range(1,6):
 with concurrent.futures.ThreadPoolExecutor(max_workers=7) as pool:
  items_result=list(pool.map(lambda x:check(x,attempt),specs))
 failed=[x for x in items_result if not x["ok"]]
 final["attempts"].append({"number":attempt,"ok":len(items_result)-len(failed),"failed":len(failed)})
 final.update({"complete":not failed,"checks":items_result,"attempt":attempt})
 RESULT.write_text(json.dumps(final,ensure_ascii=False,indent=2),encoding="utf-8")
 print("V42 HTTP",attempt,len(items_result)-len(failed),"/",len(items_result), "failed",str(failed[:2])[:400],flush=True)
 if not failed:break
 if attempt<5:time.sleep(22)
if not final["complete"]:raise SystemExit("V42 website QA failed: "+str([x for x in final["checks"] if not x["ok"]][:5]))
print("PASSED all 105 live checks",flush=True)
