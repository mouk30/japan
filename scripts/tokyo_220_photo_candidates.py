#!/usr/bin/env python3
"""Tokyo 220 exhaustive per-article image candidate audit. Candidate != approved.
Searches Commons for exact article-specific named subjects; preserves existing photos.
Does not publish unreviewed images. Never adds generic substitutes."""
import concurrent.futures,datetime,html,json,pathlib,re,time,urllib.parse,urllib.request,urllib.error
ROOT=pathlib.Path("site")
pages=sorted((ROOT/"japan/tokyo").glob("*/index.html"))
assert len(pages)==220,len(pages)
existing=json.loads((ROOT/"tokyo-photo-credits.json").read_text(encoding="utf8"))
approved={x["slug"]:x for x in existing}
headers={"User-Agent":"NipponferryEditorialAudit/1.0 (https://www.nipponferry.com)","Accept":"application/json"}
def text_only(s):return html.unescape(re.sub("<[^>]+>","",s)).strip()
def search_one(path):
 slug=path.parent.name
 source=path.read_text(encoding="utf8")
 title=text_only(re.search(r"<h1[^>]*>(.*?)</h1>",source,re.S).group(1))
 external=list(dict.fromkeys(re.findall(r'<a[^>]+href="(https://[^"]+)"',source)))
 external=[x for x in external if "nipponferry.com" not in x]
 item={"slug":slug,"title":title,"official_references":external[:5],"image_status":"already_recorded" if slug in approved else "candidate_only","candidates":[]}
 if slug in approved:return item
 # Search via title instead of generic place categories.
 terms=re.sub(r"(가격|예약|가는 법|비교|안내|가이드|운영시간|교통|방법|조건|코스|동선|주의사항|여행|선택|실전|도쿄)"," ",title)
 terms=re.sub(r"[^\w\s가-힣·]"," ",terms).strip()
 terms=" ".join(terms.split()[:5]) or title
 stop={"tokyo","guide","best","tickets","ticket","prices","price","booking","reservation","hours","access","travel","day","trip","how","to","in","from","free","for","and","of","the","route","routes","tips","family","with","station","exit","exits","compare","comparison"}
 tokens=[t for t in slug.split("-") if len(t)>2 and t not in stop and not t.isdigit()]
 terms="Tokyo "+" ".join(tokens[:4]) if tokens else "Tokyo "+title
 params=urllib.parse.urlencode({"action":"query","format":"json","generator":"search","gsrsearch":terms+" filetype:bitmap","gsrnamespace":6,"gsrlimit":8,"prop":"imageinfo","iiprop":"extmetadata|url"})
 try:
  raw=None
  for attempt in range(4):
   try:
    with urllib.request.urlopen(urllib.request.Request("https://commons.wikimedia.org/w/api.php?"+params,headers=headers),timeout=30) as response:raw=json.load(response)
    break
   except urllib.error.HTTPError as e:
    if e.code not in (429,500,502,503,504) or attempt==3:raise
    time.sleep(10*(attempt+1))
   except urllib.error.URLError:
    if attempt==3:raise
    time.sleep(10*(attempt+1))
  for page in raw.get("query",{}).get("pages",{}).values():
   info=(page.get("imageinfo") or [{}])[0]
   m=info.get("extmetadata",{})
   license_name=text_only(m.get("LicenseShortName",{}).get("value",""))
   if not (license_name.startswith("CC BY") or license_name=="CC0"):continue
   name=page.get("title","")
   item["candidates"].append({"commons_title":name,"commons_file_url":info.get("descriptionurl"),"license":license_name,"creator_html":m.get("Artist",{}).get("value","")[:500],"assessment":"NOT REVIEWED — no site publish"})
 except Exception as exc:item["search_error"]=str(exc)[:120]
 return item
# Commons imposes rate limits. A one-at-a-time search respects API capacity.
results=[]
for i,path in enumerate(pages):
 results.append(search_one(path))
 if i<len(pages)-1:time.sleep(1.5)
report={"generated_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"total":len(results),
"approved_photos_before_this_job":len(approved),
"candidate_search_attempts":len(results)-len(approved),
"with_candidates":sum(bool(x["candidates"]) for x in results),
"search_errors":sum(bool(x.get("search_error")) for x in results),
"warning":"Candidate file name, license and search result do NOT prove actual location/subject. Human/photo inspection and live browser confirmation are required.",
"items":results}
out=pathlib.Path("audit-reports/tokyo-220-photo-candidates.json")
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
print(json.dumps({k:v for k,v in report.items() if k!="items"},ensure_ascii=False))
