#!/usr/bin/env python3
"""V148 production QA: ensure verbose licensed-photo provenance is collapsed on public pages."""
import json,re,time
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from datetime import datetime,timezone
ORIGIN="https://www.nipponferry.com"
URLS=[
  "/","/ferry/","/japan/","/food/",
  "/things-to-do/naoshima-art-ferry-return/",
  "/things-to-do/teshima-art-ferry-return/",
  "/things-to-do/cruise-ports/",
  "/things-to-do/okinawa-shuri-castle/"
]
TOKYO="/japan/tokyo/photo-review/"
UA="Mozilla/5.0 (compatible; NIPPONFERRY-V148-PhotoCredits-Release/1.0)"
def fetch(path):
  last=None
  for attempt in range(4):
    try:
      with urlopen(Request(ORIGIN+path,headers={"User-Agent":UA,"Cache-Control":"no-cache"}),timeout=25) as r:
        return r.status,r.geturl(),r.headers.get("content-type",""),r.read(3_000_000).decode("utf-8","replace")
    except (URLError,HTTPError,TimeoutError) as exc:
      last=str(exc);time.sleep(2+attempt)
  raise RuntimeError(last)
R=[]
for p in URLS:
  info={"url":ORIGIN+p}
  try:
    st,final,ctype,html=fetch(p)
    matches=re.findall(r'<details\b[^>]*id="nf-v148-photo-credits"[^>]*>(.*?)</details>',html,re.S|re.I)
    body_without=re.sub(r'<details\b[^>]*id="nf-v148-photo-credits"[^>]*>.*?</details>',"",
       html,flags=re.S|re.I)
    tests={
      "http200":st==200,
      "html":"html" in ctype,
      "folded_credit_panel_one":len(matches)==1,
      "closed_by_default":not bool(re.search(r'<details[^>]*id="nf-v148-photo-credits"[^>]*\sopen\b',html,re.I)),
      "one_line_summary":'<summary>사진 출처 보기</summary>' in html,
      "license_accessible":bool(matches) and "creativecommons.org" in matches[0] and "commons.wikimedia.org" in matches[0],
      "no_long_main_credit":'class="v140-credit"' not in body_without and
           'class="nf-v81-credit"' not in body_without and
           'class="nf84-route__caption"' not in body_without,
      "canonical_intact":('rel="canonical"' in html or "rel='canonical'" in html),
      "image_intact":"<img" in html,
    }
    if p=="/":
      # build.js strips internal V140 prefixes; it is only important that the
      # old verbose source note no longer appears in the visible reading flow.
      tests["v140_not_visible"]=bool(matches) and "V140 실사 출처" not in body_without
    if p=="/things-to-do/okinawa-shuri-castle/":
      tests["v72_photo_anchor_intact"]='id="nf-v72-verified-photo"' in html
    info.update({"checks":tests,"passed":all(tests.values()),"bytes":len(html)})
  except Exception as exc:info.update({"passed":False,"error":str(exc)})
  print("PASS" if info["passed"] else "FAIL",p,info.get("checks",info.get("error")),flush=True)
  R.append(info)
try:
  st,final,ctype,tokyo=fetch(TOKYO)
  review=dict(url=ORIGIN+TOKYO,
    checks={"http200":st==200,"navigation_20":tokyo.count("게시글 보기 ↗")>=20,
      "unmodified_review":'id="nf-v148-photo-credits"' not in tokyo})
  review["passed"]=all(review["checks"].values())
except Exception as exc:review=dict(url=ORIGIN+TOKYO,passed=False,error=str(exc))
R.append(review);print("PASS" if review["passed"] else "FAIL",TOKYO,review,flush=True)
out=Path("audit-output/v148-public");out.mkdir(parents=True,exist_ok=True)
report={"checked_utc":datetime.now(timezone.utc).isoformat(),"checked":len(R),
   "passed":sum(x["passed"] for x in R),"results":R}
(out/"live-photo-credits.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",report["passed"],"/",report["checked"])
if report["passed"]!=report["checked"]:raise SystemExit(1)
