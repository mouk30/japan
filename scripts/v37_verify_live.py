#!/usr/bin/env python3
"""V37 real deployment photo QA. Run in GitHub Actions with public internet access."""
import json,time,urllib.request
from pathlib import Path
SITE="https://www.nipponferry.com"
rows=json.loads(Path("docs/v37-deployed-photo-credits.json").read_text("utf-8"))
assert len(rows)==22
report={"site":SITE,"checks":[],"passed":False}
UA="Nipponferry-qa/1.0 (https://www.nipponferry.com/)"
def request(url):
 req=urllib.request.Request(url,headers={"User-Agent":UA,"Cache-Control":"no-cache"})
 with urllib.request.urlopen(req,timeout=28) as response:
    return response.status, response.headers.get("Content-Type",""),response.read()
for attempt in range(9):
 checks=[]
 try:
    for pagepath,key,section in [("/food/","food-verified/tsushima-food.webp","food"),("/food/","food-verified/tsushima-dessert.webp","food"),("/things-to-do/","culture-verified/takoyaki-osaka-street-food.webp","things")]:
        status,mime,body=request(SITE+pagepath+"?qa=v37-"+str(attempt))
        ok=status==200 and key.encode() in body
        checks.append({"kind":"hub","path":pagepath,"key":key,"ok":ok,"status":status})
    for entry in rows:
        url=SITE+entry["asset"]
        try:
            status,mime,body=request(url+"?qa=v37-"+str(attempt))
            good=status==200 and ("webp" in mime.lower() or (body[:4]==b"RIFF" and body[8:12]==b"WEBP"))
            checks.append({"kind":"photo","asset":entry["asset"],"ok":good,"status":status,"mime":mime,"bytes":len(body)})
        except Exception as exc:
            checks.append({"kind":"photo","asset":entry["asset"],"ok":False,"error":str(exc)[:160]})
    print(f"Attempt {attempt+1}: {sum(x['ok'] for x in checks)}/{len(checks)} live HTTP probes passed",flush=True)
    if all(item["ok"] for item in checks):
        report.update({"passed":True,"attempt":attempt+1,"checks":checks})
        break
    report.update({"passed":False,"attempt":attempt+1,"checks":checks})
 except Exception as exc:
    report.update({"passed":False,"attempt":attempt+1,"error":str(exc)[:180],"checks":checks})
 if attempt<8:time.sleep(25)
path=Path("docs/v37-live-qa.json")
path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("Saved",path,"PASS" if report["passed"] else "FAIL",flush=True)
if not report["passed"]:
    raise SystemExit(1)
