import pathlib,re,json,urllib.parse,urllib.request,urllib.error,collections,concurrent.futures,time,html
SITE=pathlib.Path("site");root=SITE/"japan/tokyo";home=(root/"index.html").read_text()
slugs=re.findall(r'<a\s+class="tky-card"[^>]*href="/japan/tokyo/([^/]+)/"',home)
photo=(SITE/"tokyo-card-photos.js").read_text()
registry=json.loads(photo.split("const map=",1)[1].split(";document.querySelectorAll",1)[0])
urls=collections.defaultdict(list);photos=[]
for i,s in enumerate(slugs,1):
 page=(root/s/"index.html").read_text()
 for url in re.findall(r'<a\b[^>]*href="(https?[^"]+)"',page):
  u=html.unescape(url)
  if "nipponferry.com" not in u:urls[u].append(i)
 entry=registry.get(s,{})
 src=entry.get("src","");source=entry.get("source_file","")
 flags=[]
 if not src:flags.append("missing_card_photo")
 if source and any(x in source.lower() for x in ["kobe","kyoto","nara","gdansk","lithuania","shanghai","romania","cfr","2010"]):flags.append("source_filename_out_of_place_or_historical")
 if src.endswith(".svg"):flags.append("editorial_non_photo")
 if entry.get("license") and entry.get("license")!="Original editorial SVG" and not entry.get("source"):flags.append("photo_source_absent")
 photos.append({"v":i,"slug":s,"source_file":source,"flags":flags})
headers={"User-Agent":"Mozilla/5.0 (compatible; Nipponferry QA Link Check)"}
def check(item):
 url,versions=item
 try:
  req=urllib.request.Request(url,headers=headers,method="HEAD")
  try:
   with urllib.request.urlopen(req,timeout=14) as r: return {"url":url,"status":r.status,"final_url":r.url,"articles":versions[:10]}
  except urllib.error.HTTPError as e:
   if e.code not in (403,405,429,500,503):return {"url":url,"status":e.code,"articles":versions[:10]}
  req=urllib.request.Request(url,headers=headers,method="GET")
  with urllib.request.urlopen(req,timeout=14) as r: return {"url":url,"status":r.status,"final_url":r.url,"articles":versions[:10]}
 except urllib.error.HTTPError as e:return {"url":url,"status":e.code,"articles":versions[:10],"note":"May be anti-bot; verify manually"}
 except Exception as e:return {"url":url,"status":None,"articles":versions[:10],"error":str(e)[:130]}
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
 result=list(pool.map(check,urls.items()))
bad=[r for r in result if r.get("status")!=200]
report={"total_articles":len(slugs),"external_unique_urls":len(urls),"external_success_200":len(result)-len(bad),"external_non_200_or_unreachable":len(bad),"external_issues":bad,"all_external_checks":result,"photo_flag_count":sum(bool(x["flags"]) for x in photos),"photo_flagged":[x for x in photos if x["flags"]],"photo_registry":photos,"limitations":"HTTP status only, anti-bot may cause false positive; no proof of factual freshness or photo semantic match. Source file-name heuristic only."}
out=pathlib.Path("audit-reports/tokyo-final-link-photo-qa.json");out.parent.mkdir(exist_ok=True,parents=True)
out.write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ("all_external_checks","external_issues","photo_registry","photo_flagged")},ensure_ascii=False))
