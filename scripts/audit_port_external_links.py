#!/usr/bin/env python3
"""Check outbound sources of the five flagship cruise port guides.

Reachability != correctness of the facts. 403/429/5xx and network errors are
'inconclusive', NEVER interpreted as broken. Only repeatable GET 404/410 or
malformed URLs are 'broken'. Original location and links are preserved.
"""
import argparse, concurrent.futures, json, re, sys, time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

PORTS=[
 "naha-cruise-terminal-kokusai-dori",
 "ishigaki-cruise-kabira-bay-bus-taxi",
 "hakata-port-hakata-station-access",
 "nagasaki-matsugae-glover-garden-cruise-access",
 "yokohama-red-brick-warehouse",
]
AGENT="Mozilla/5.0 (compatible; NIPPONFERRY-Link-QA/1.0; external link verification)"
class Links(HTMLParser):
    def __init__(self):
        super().__init__();self.out=[]
    def handle_starttag(self,tag,attrs):
        if tag!="a":return
        a=dict(attrs);url=a.get("href","")
        if url.startswith(("https://","http://")) and "nipponferry.com" not in (urlparse(url).hostname or ""):
            self.out.append(url)

def get_links(root):
    owners={}
    for slug in PORTS:
        path=root/"things-to-do"/slug/"index.html"
        if not path.is_file():raise ValueError("Missing guide: "+str(path))
        obj=Links();obj.feed(path.read_text(encoding="utf-8"))
        for url in set(obj.out):
            owners.setdefault(url,[]).append(slug)
    return owners

def probe(url,method):
    req=Request(url,headers={"User-Agent":AGENT},method=method)
    try:
        with urlopen(req,timeout=16) as response:
            if method=="GET":response.read(1024)
            return {"status":response.status,"final_url":response.geturl(),"error":None}
    except HTTPError as err:
        return {"status":err.code,"final_url":err.geturl(),"error":None}
    except (URLError,TimeoutError,OSError,ValueError) as err:
        return {"status":None,"final_url":None,"error":str(err)[:250]}

def classify(url,owners):
    parsed=urlparse(url)
    item={"url":url,"pages":sorted(owners)}
    if parsed.scheme not in ("http","https") or not parsed.hostname:
        item.update({"classification":"broken","reason":"invalid URL"})
        return item
    one=probe(url,"HEAD")
    if one["status"] in (200,206):
        result=one
        reason="HTTP reachable (HEAD)"
        classification="reachable"
    else:
        result=probe(url,"GET")
        if result["status"] in (404,410):
            time.sleep(.5)
            confirm=probe(url,"GET")
            if confirm["status"] in (404,410):
                classification="broken";reason=f"GET {result['status']} confirmed by GET {confirm['status']}"
            else:
                classification="inconclusive";reason="initial 404/410 was not reproduced"
        elif result["status"] is not None and 200<=result["status"]<400:
            classification="reachable";reason="HTTP reachable (GET)"
        else:
            classification="inconclusive";reason=f"GET status {result['status']} or network error"
    item.update({"classification":classification,"reason":reason,"head_status":one["status"],
                 "get_status":result["status"],"final_url":result["final_url"],"error":result["error"]})
    return item

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",default="site")
    p.add_argument("--out",default="audit-output/port-official-links")
    p.add_argument("--allow-broken",action="store_true",
                   help="Diagnostic only: do not fail CI for repeatable 404/410")
    args=p.parse_args()
    owners=get_links(Path(args.root))
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        rows=list(pool.map(lambda kv: classify(*kv), sorted(owners.items())))
    status={name:sum(x["classification"]==name for x in rows)
            for name in ("reachable","broken","inconclusive")}
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    doc={"checked_utc":datetime.now(timezone.utc).isoformat(),
         "scope":"External anchor reachability for five flagship pages; NOT freshness, photo rights or conversion",
         "pages":len(PORTS),"links":len(rows),"summary":status,"results":rows}
    (out/"external-links.json").write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding="utf-8")
    for row in rows:
        print(f'{row["classification"].upper():12} {row["get_status"]!s:>4} {row["url"]}')
        if row["classification"]!="reachable":print("   ",row["reason"],"used by",", ".join(row["pages"]))
    print("SUMMARY",json.dumps({"urls":len(rows),**status}))
    if status["broken"] and not args.allow_broken:sys.exit(1)

if __name__=="__main__":main()
