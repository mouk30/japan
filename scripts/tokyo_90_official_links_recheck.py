import json,pathlib,re,urllib.request,urllib.error,urllib.parse,concurrent.futures,time,collections
old=json.loads(pathlib.Path("audit-reports/tokyo-final-link-photo-qa.json").read_text())
issues=old["external_issues"]
headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/125.0 Safari/537.36","Accept-Language":"en-US,en;q=0.9"}
def check(x):
 url=x["url"];domain=urllib.parse.urlsplit(url).hostname
 statuses=[]
 for mode in ["HEAD","GET"]:
  try:
   req=urllib.request.Request(url,headers=headers,method=mode)
   with urllib.request.urlopen(req,timeout=22) as r:
    statuses.append({"method":mode,"status":r.status,"final":r.url})
    if r.status==200:break
  except urllib.error.HTTPError as e:
   statuses.append({"method":mode,"status":e.code})
   if e.code in [404,410]:break
  except Exception as e:statuses.append({"method":mode,"error":type(e).__name__})
 codes=[z.get("status") for z in statuses]
 if 200 in codes:status="confirmed_200"
 elif 404 in codes or 410 in codes:status="probable_broken_404_410"
 elif any(c in (403,429) for c in codes):status="access_blocked_unverified"
 else:status="timeout_or_network_unverified"
 return {"url":url,"articles":x.get("articles",[]),"initial_status":x.get("status"),"recheck":statuses,"classification":status,"domain":domain}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as e: results=list(e.map(check,issues))
by=collections.Counter(x["classification"] for x in results)
report={"original_unverified":len(issues),"rechecked":len(results),"classification_counts":dict(by),"probable_broken":[x for x in results if x["classification"]=="probable_broken_404_410"],"unresolved":[x for x in results if x["classification"] not in ("confirmed_200","probable_broken_404_410")],"all_results":results,"note":"HTTP-only retries; access blocks do not imply dead pages; even HTTP 200 does not prove on-page facts are current."}
p=pathlib.Path("audit-reports/tokyo-90-official-links-recheck.json");p.write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({"rechecked":len(results),"outcomes":dict(by)},ensure_ascii=False))
