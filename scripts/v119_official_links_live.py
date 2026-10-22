#!/usr/bin/env python3
"""V119: scan all site outbound anchors and test a bounded official-first URL selection.
404/410 is broken only when 2 independent GETs reproduce. Other failures inconclusive.
HTTP success does NOT verify schedules, live bookings, fees or facility operation.
"""
import concurrent.futures,json,re,time,datetime
from collections import defaultdict,Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
ROOT=Path(__file__).resolve().parents[1];SITE=ROOT/"site"
OUT=ROOT/"audit-reports/v119";OUT.mkdir(parents=True,exist_ok=True)
MAX_URLS=900
UA="Mozilla/5.0 (compatible; NIPPONFERRY-Editorial-Link-Audit/1.0)"
PRIORITY=("panstarcruise.com","koreaferry.kr","kampuferry.co.jp","pukwan.co.kr","hakataport.com","mlit.go.jp","japan.travel","city.","pref.","lg.jp")
SKIP=("commons.wikimedia.org","creativecommons.org","wikipedia.org","youtu.be","youtube.com","instagram.com","x.com","facebook.com")
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  if tag=="a":
   x=dict(attrs).get("href","").strip()
   if x.startswith(("http://","https://")):self.links.append(x)
def load():
 owners=defaultdict(set)
 for f in SITE.rglob("*.html"):
  page="/"+f.relative_to(SITE).as_posix()
  if page.endswith("/index.html"):page=page.removesuffix("index.html")
  try:html=f.read_text("utf8")
  except UnicodeDecodeError:continue
  parser=Links();parser.feed(html)
  for url in parser.links:
   host=urlsplit(url).hostname or ""
   if "nipponferry.com" not in host and host:owners[url].add(page)
 return owners
def rank(url):
 host=(urlsplit(url).hostname or "").lower()
 if any(x in host for x in SKIP):return 100
 for i,key in enumerate(PRIORITY):
  if key in host:return i
 if host.endswith(".go.jp") or host.endswith(".lg.jp"):return 12
 if host.endswith(".jp"):return 25
 return 45
def probe(url,method):
 req=Request(url,headers={"User-Agent":UA,"Accept":"text/html,*/*"},method=method)
 try:
  with urlopen(req,timeout=11) as r:
   if method=="GET":r.read(512)
   return {"status":r.status,"final":r.url,"error":None}
 except HTTPError as e:return {"status":e.code,"final":e.url,"error":None}
 except Exception as e:return {"status":None,"final":None,"error":type(e).__name__}
def verify(item):
 url,pages=item
 head=probe(url,"HEAD")
 result=head
 if head["status"] in (404,410,405,None,403,429) or (head["status"] and head["status"]>=500):
  result=probe(url,"GET")
 if result["status"] in (404,410):
  confirm=probe(url,"GET")
  status="confirmed_broken" if confirm["status"] in (404,410) else "unverified"
 elif result["status"] and 200<=result["status"]<400:
  status="reachable"
 else:status="unverified"
 return {"url":url,"pages":sorted(pages)[:15],"classification":status,"head_status":head["status"],"final_status":result["status"],"redirected_to":result["final"] if result["final"]!=url else None,"error":result["error"]}
def main():
 all_=load()
 eligible=sorted((p for p in all_.items() if rank(p[0])<100),key=lambda x:(rank(x[0]),-len(x[1]),x[0]))
 selected=eligible[:MAX_URLS]
 with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:rows=list(pool.map(verify,selected))
 counts=Counter(x["classification"] for x in rows)
 report={"version":"V119","checked_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"total_external_urls":len(all_),"eligible_non_media_urls":len(eligible),"probed":len(rows),"remaining_unprobed":len(all_)-len(rows),"counts":dict(counts),"definition":"HTTP reachable does not prove booking success or valid entrance/fee; 403,429,5xx,tls failure remain unverified.","confirmed_broken":[x for x in rows if x["classification"]=="confirmed_broken"],"unverified":[x for x in rows if x["classification"]=="unverified"],"results":rows}
 (OUT/"official-and-editorial-link-checks.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
 print(json.dumps({k:report[k] for k in ("total_external_urls","eligible_non_media_urls","probed","remaining_unprobed","counts")},ensure_ascii=False))
 print("CONFIRMED_404_410",json.dumps(report["confirmed_broken"][:30],ensure_ascii=False))
 return 0
if __name__=="__main__":raise SystemExit(main())
