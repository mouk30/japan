#!/usr/bin/env python3
"""V146 public-domain release QA: GET deployed articles, 2 WebP assets, sitemap and links.
This is not a substitute for trip-date availability checks at ferry/museum providers."""
import json, re, time
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError,URLError
ROOT="https://www.nipponferry.com"
PAGES={
 "naoshima-art-ferry-return":{
   "image":"/images/editorial/v146-naoshima-miyanoura-ferry-terminal-2025.webp",
   "checkout":"https://benesse-artsite.eventos.tokyo/web/portal/797/event/8483/module/booth/239565/176695?language=eng"},
 "teshima-art-ferry-return":{
   "image":"/images/editorial/v146-teshima-art-museum-exterior-2013.webp",
   "checkout":"https://benesse-artsite.eventos.tokyo/web/portal/797/event/8483/module/booth/239565/185773?language=eng"}
}
UA="Mozilla/5.0 (compatible; NIPPONFERRY-Public-Release-QA/1.0)"
results=[]
def download(path):
  last=None
  for attempt in range(4):
    try:
      with urlopen(Request(ROOT+path,headers={"User-Agent":UA,"Cache-Control":"no-cache"}),timeout=28) as r:
        body=r.read(3_000_000);return r.status,r.url,r.headers.get("Content-Type",""),body
    except (HTTPError,URLError,TimeoutError) as e:
      last=str(e);time.sleep(6)
  raise RuntimeError(f"GET {path} unavailable: {last}")
def check(name,path,fn):
  try:
    status,url,ctype,blob=download(path)
    checks=fn(status,url,ctype,blob)
    ok=(status==200 and all(checks.values()))
    result=dict(name=name,path=path,status=status,final_url=url,content_type=ctype,bytes=len(blob),checks=checks,passed=ok)
  except Exception as e:
    result=dict(name=name,path=path,passed=False,error=str(e))
  print(("PASS" if result["passed"] else "FAIL"),name,result)
  results.append(result)
def page_conditions(slug,conf):
  path=f"/things-to-do/{slug}/"
  def validate(status,url,ctype,blob):
    html=blob.decode("utf-8","replace")
    return {
     "html_type":"html" in ctype,
     "h1_single":len(re.findall(r"<h1(?:\\s|>)",html,re.I))==1,
     "canonical":f'<link rel="canonical" href="{ROOT}{path}">' in html,
     "image_local":f'src="{conf["image"]}"' in html,
     "official_checkout":conf["checkout"] in html,
     "real_credit":"Wikimedia Commons" in html and "WebP" in html,
     "checklist":'id="checklist"' in html,
     "jsonld":'application/ld+json' in html,
     "robots_no_noindex":'content="noindex' not in html,
     "return_instruction":"귀항" in html and "선착장" in html
    }
  check(slug,path,validate)
  def image_validation(status,url,ctype,blob):
    return {"webp_format":blob[:4]==b"RIFF" and blob[8:12]==b"WEBP",
       "image_mime":"image/" in ctype.lower(),
       "image_not_placeholder":len(blob)>20000}
  check("image-"+slug,conf["image"],image_validation)
for slug,conf in PAGES.items():page_conditions(slug,conf)
def sitemap_validation(status,url,ctype,blob):
  txt=blob.decode("utf-8","replace")
  return {"naoshima_in_sitemap":ROOT+"/things-to-do/naoshima-art-ferry-return/" in txt,
    "teshima_in_sitemap":ROOT+"/things-to-do/teshima-art-ferry-return/" in txt,
    "looks_like_sitemap":"<urlset" in txt}
check("sitemap","/sitemap.xml",sitemap_validation)
for old in ("shodoshima-ferry-island-access","takamatsu-cruise-port-day-trip"):
  def old_links_validation(status,url,ctype,blob):
    txt=blob.decode("utf-8","replace")
    return {"naoshima_link":"/things-to-do/naoshima-art-ferry-return/" in txt,
     "teshima_link":"/things-to-do/teshima-art-ferry-return/" in txt}
  check("related-"+old,"/things-to-do/"+old+"/",old_links_validation)
out=Path("audit-output/v146-public");out.mkdir(parents=True,exist_ok=True)
report={"checked_at_utc":datetime.now(timezone.utc).isoformat(),"origin":ROOT,"results":results,
 "passed":sum(r["passed"] for r in results),"total":len(results)}
(out/"public-release.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",report["passed"],"/",report["total"])
if report["passed"]!=report["total"]:raise SystemExit(1)
