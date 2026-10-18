import pathlib,re,json,urllib.parse,urllib.request,urllib.error,concurrent.futures,collections
root=pathlib.Path("site/japan/tokyo");links=collections.defaultdict(set);base="https://www.nipponferry.com"
for p in root.glob("*/index.html"):
 s=p.read_text(encoding="utf8")
 for u in re.findall(r'<a\b[^>]*href="(https?://[^"]+)"',s,re.I):
  domain=urllib.parse.urlsplit(u).hostname or ""
  if domain not in ["www.nipponferry.com","nipponferry.com"]:
   links[u].add(p.parent.name)
urls=sorted(links)
heads={"User-Agent":"Mozilla/5.0 (compatible; NIPPONFERRY-LinkAudit/1.0)"}
def check(u):
 try:
  req=urllib.request.Request(u,headers=heads,method="HEAD")
  try:
   with urllib.request.urlopen(req,timeout=12) as r:return {"url":u,"status":r.status,"final":r.url}
  except urllib.error.HTTPError as e:
   if e.code not in (403,405,429):return {"url":u,"status":e.code}
  req=urllib.request.Request(u,headers=heads)
  with urllib.request.urlopen(req,timeout=12) as r:return {"url":u,"status":r.status,"final":r.url}
 except urllib.error.HTTPError as e:return {"url":u,"status":e.code}
 except Exception as e:return {"url":u,"status":None,"error":str(e)[:140]}
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:result=list(pool.map(check,urls))
for r in result:r["pages_count"]=len(links[r["url"]]);r["sample_pages"]=sorted(links[r["url"]])[:8]
issues=[r for r in result if r.get("status") is None or (r["status"]>=400)]
out={"total_unique_external_urls":len(urls),"checked":len(result),"http_2xx":sum(200<=r["status"]<300 for r in result if r.get("status") is not None),"restricted_or_failed":len(issues),"issues":issues,"all_results":result,"warning":"403/429 or connection failure can reflect anti-bot protection; does not necessarily indicate broken for humans. HTTP 200 does not guarantee the page describes the referenced service or updated policy."}
dest=pathlib.Path("audit-reports/tokyo-220-external-links.json");dest.write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in out.items() if k not in ("issues","all_results")},ensure_ascii=False))
