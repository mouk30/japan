#!/usr/bin/env python3
"""V38 live production smoke test: 20 local WebP URLs and 20 article render URLs."""
import json,time,urllib.request
from pathlib import Path
HOST="https://www.nipponferry.com"
rows=json.loads(Path("docs/v38-deployed-photo-credits.json").read_text(encoding="utf-8"))
if len(rows)!=20:raise RuntimeError("Expected 20 V38 completed articles")
result={"site":HOST,"complete":False,"checks":[],"images":20,"articles":20}
def load(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Nipponferry-V38-production-QA/1.0 (https://www.nipponferry.com/)", "Cache-Control":"no-cache"})
    with urllib.request.urlopen(req,timeout=35) as res:
        return res.status,res.headers.get("Content-Type",""),res.read()
for attempt in range(8):
    logs=[]
    for row in rows:
        slug=row["slug"]; asset=row["asset"]
        try:
            status,mime,body=load(HOST+asset+f"?v38qa={attempt}")
            ok=status==200 and body[:4]==b"RIFF" and body[8:12]==b"WEBP"
            logs.append({"item":"image","slug":slug,"path":asset,"status":status,"mime":mime,"bytes":len(body),"ok":ok})
        except Exception as exc:logs.append({"item":"image","slug":slug,"path":asset,"ok":False,"error":str(exc)[:180]})
        try:
            page=f"/things-to-do/{slug}/"
            status,mime,body=load(HOST+page+f"?v38qa={attempt}")
            ok=(status==200 and asset.encode() in body and
                f'property="og:image" content="{HOST}{asset}"'.encode() in body and
                f'name="twitter:image" content="{HOST}{asset}"'.encode() in body)
            logs.append({"item":"page","slug":slug,"path":page,"status":status,"ok":ok})
        except Exception as exc:logs.append({"item":"page","slug":slug,"ok":False,"error":str(exc)[:180]})
    try:
        status,mime,body=load(HOST+"/things-to-do/"+f"?v38qa={attempt}")
        ok=status==200 and all(r["asset"].encode() in body for r in rows)
        logs.append({"item":"hub","path":"/things-to-do/","status":status,"ok":ok})
    except Exception as exc:logs.append({"item":"hub","path":"/things-to-do/","ok":False,"error":str(exc)[:180]})
    result.update({"attempt":attempt+1,"complete":all(x["ok"] for x in logs),"checks":logs})
    print("V38 live verification",attempt+1,sum(x["ok"] for x in logs),"/",len(logs),flush=True)
    if result["complete"]:break
    if attempt!=7:time.sleep(17)
out=Path("docs/v38-live-qa.json")
out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print("Saved",out, "PASS" if result["complete"] else "FAIL",flush=True)
if not result["complete"]:raise SystemExit(1)
