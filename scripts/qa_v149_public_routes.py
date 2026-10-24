#!/usr/bin/env python3
"""V149 publication test for existing homepage, destination and cruise-port hubs.
Tests actual public NIPPONFERRY HTML, never asserts seat inventory or cruise ETA."""
import json,re,time
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError
ORIGIN="https://www.nipponferry.com"
HUBS=["/","/japan/","/things-to-do/cruise-ports/"]
PORTS=[
 "naha-cruise-terminal-kokusai-dori",
 "hakata-port-hakata-station-access",
 "nagasaki-matsugae-glover-garden-cruise-access",
 "ishigaki-cruise-kabira-bay-bus-taxi",
 "yokohama-red-brick-warehouse"
]
UA="Mozilla/5.0 (compatible; NIPPONFERRY-V149-PublicRouteQA/1.0)"
def read(path):
  last=None
  for i in range(4):
    try:
      with urlopen(Request(ORIGIN+path,headers={"User-Agent":UA,"Cache-Control":"no-cache"}),timeout=27) as response:
        return response.status,response.headers.get("content-type",""),response.read(3_000_000).decode("utf-8","replace")
    except (URLError,HTTPError,TimeoutError) as e:last=str(e);time.sleep(i+2)
  raise RuntimeError(str(last))
rows=[]
for path in HUBS+["/things-to-do/"+x+"/" for x in PORTS]:
  rec={"url":ORIGIN+path}
  try:
    status,mime,html=read(path)
    checks={"http200":status==200,"html":"html" in mime.lower(),
      "canonical":'href="'+ORIGIN+path+'"' in html or "href='"+ORIGIN+path+"'" in html,
      "one_h1":len(re.findall(r"<h1(?:\s|>)",html,re.I))==1,
      "indexable":"noindex" not in html[:5000].lower()}
    if path in HUBS:
      checks["single_photo_source_disclosure"]=html.count('id="nf-v148-photo-credits"')==1
      checks["source_one_line"]='<summary>사진 출처 보기</summary>' in html
    if path=="/things-to-do/cruise-ports/":
      p=html.split('id="nf-v148-photo-credits"')
      visible=p[0] if p else html
      credits=p[1] if len(p)>1 else ""
      checks.update({
        "no_verbose_36_card_labels":'class="nf-v130-photo-credit"' not in visible,
        "folded_36_card_licenses":credits.count("기항지 카드 ·")==36,
        "preserve_source_author":"Kiyok" in credits and "CC BY-SA 3.0" in credits,
        "five_verified_return_buttons":all(
            'href="/things-to-do/'+slug+'/#nf-v147-port-visitor"' in html for slug in PORTS),
        "photo_original_links":'commons.wikimedia.org' in credits and 'creativecommons.org' in credits,
      })
    if path=="/":
      checks["four_home_arrival_return_buttons"]=all(
          'href="/things-to-do/'+slug+'/#nf-v147-port-visitor"' in html for slug in PORTS[:4])
      checks["return_process_copy"]="현지 교통" in html and "승선 마감" in html
    if path=="/japan/":
      checks["short_photo_overlay"]= "사진 속 장소:" not in html.split('id="nf-v148-photo-credits"')[0]
    if path.startswith("/things-to-do/") and path!="/things-to-do/cruise-ports/":
      checks["actual_return_anchor"]='id="nf-v147-port-visitor"' in html
    rec.update({"checks":checks,"passed":all(checks.values()),"bytes":len(html)})
  except Exception as e:rec.update({"passed":False,"error":str(e)})
  print("PASS" if rec["passed"] else "FAIL",path,rec.get("checks",rec.get("error")),flush=True)
  rows.append(rec)
report={"checked_utc":datetime.now(timezone.utc).isoformat(),
 "passed":sum(x["passed"] for x in rows),"total":len(rows),"results":rows}
out=Path("audit-output/v149-public");out.mkdir(parents=True,exist_ok=True)
(out/"published-hub-journeys.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",report["passed"],"/",report["total"])
if report["passed"]!=report["total"]:raise SystemExit(1)
