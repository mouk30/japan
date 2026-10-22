#!/usr/bin/env python3
"""V123 live verification for 56 fixed existing canonical routes.
Source-code correctness and public-server delivery are distinct. Report both honestly.
"""
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.error import HTTPError, URLError
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
import json, re, datetime
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/"audit-reports/v122/canonical-repair.json"
OUT=ROOT/"audit-reports/v123";OUT.mkdir(parents=True,exist_ok=True)
class Tags(HTMLParser):
 def __init__(self):super().__init__();self.canon=[]
 def handle_starttag(self,t,attrs):
  if t=="link":
   a=dict(attrs)
   if a.get("rel")=="canonical":self.canon.append(a.get("href"))
def fetch(row):
 url=row["corrected_self"]
 try:
  req=Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; NipponFerryPublicQA/1.0)","Accept":"text/html"})
  with urlopen(req,timeout=18) as resp:
   h=resp.read(1200000).decode("utf8","replace")
   tags=Tags();tags.feed(h)
   actual=tags.canon[0] if len(tags.canon)==1 else None
   status="correct" if resp.status==200 and actual==url else "mismatch"
   return {"url":url,"status":status,"http":resp.status,"actual_canonical":actual,"redirected":resp.url!=url}
 except HTTPError as e:return {"url":url,"status":"unverified_http","http":e.code}
 except Exception as e:return {"url":url,"status":"unverified_network","error":type(e).__name__}
def main():
 rows=json.loads(EVIDENCE.read_text("utf8"))["pages"]
 with ThreadPoolExecutor(max_workers=10) as pool:results=list(pool.map(fetch,rows))
 counts={name:sum(x["status"]==name for x in results) for name in sorted({x["status"] for x in results})}
 report={"version":"V123","checked_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
         "pages_checked":len(results),"counts":counts,"results":results,
         "notes":"HTTP/TLS/bot denial is not proof of a broken public page; 200 plus exact canonical is a verified result."}
 (OUT/"live-canonical-56.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
 print(json.dumps({"pages_checked":len(results),"counts":counts},ensure_ascii=False))
 return 1 if any(r["status"]=="mismatch" for r in results) else 0
if __name__=="__main__":raise SystemExit(main())
