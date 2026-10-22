#!/usr/bin/env python3
"""V130 narrow official-source HTTP probe, 2026-10-22.
Reachable HTTP != active schedule, ticket validity, pricing, or confirmed cruise berth.
2 GETs are needed to classify 404/410 as confirmed broken; 403/429/5xx/timeouts are unverified.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from urllib.parse import urlsplit
import json,datetime
ROOT=Path(__file__).resolve().parents[1]
CASES=[
 ("booking/japan-cruise","https://www.panstarcruise.com/","operator"),
 ("booking/japan-cruise","https://www.koreaferry.co.kr/rs/idv/reservation/calendar_index/1/2?country=2","operator_booking"),
 ("booking/japan-cruise","https://kampuferry.co.jp/reserve/","operator_information"),
 ("things-to-do/naha-cruise-terminal-kokusai-dori","https://www.mlit.go.jp/kankocho/cruise/jp/detail/074/index.html","port_official"),
 ("things-to-do/naha-cruise-terminal-kokusai-dori","https://nahaport.jp/english/users/guide/","port_official"),
 ("things-to-do/ishigaki-cruise-kabira-bay-bus-taxi","https://www.city.ishigaki.okinawa.jp/soshiki/kowan/kuruzusenn/370.html","port_schedule"),
 ("things-to-do/ishigaki-cruise-kabira-bay-bus-taxi","https://www.azumabus.co.jp/localbus/","transit_operator"),
 ("things-to-do/hakata-port-hakata-station-access","https://hakataport.com/center/","terminal_official"),
 ("things-to-do/hakata-port-hakata-station-access","https://hakataport.com/access/","terminal_official"),
 ("things-to-do/nagasaki-matsugae-glover-garden-cruise-access","https://nagasaki-p.com/access/","terminal_official"),
 ("things-to-do/nagasaki-matsugae-glover-garden-cruise-access","https://www.discover-nagasaki.com/en/transit/100790","destination_official"),
 ("things-to-do/yokohama-red-brick-warehouse","https://www.city.yokohama.lg.jp/lang/overseas/port/cruise/terminal_info.html","port_official"),
 ("things-to-do/yokohama-red-brick-warehouse","https://www.yokohama-akarenga.jp/","venue_official")
]
UA="Mozilla/5.0 NIPPONFERRY-SourceReview/1.0 (https://www.nipponferry.com)"
def probe(url,method):
 try:
  req=Request(url,method=method,headers={"User-Agent":UA,"Accept":"text/html,*/*"})
  with urlopen(req,timeout=12) as r:
   if method=="GET":r.read(1000)
   return r.status,r.url,None
 except HTTPError as e:return e.code,e.url,None
 except Exception as e:return None,None,type(e).__name__
def one(item):
 slug,url,typ=item
 html=(ROOT/"site"/slug/"index.html").read_text("utf8")
 found=url in html
 status,landed,error=probe(url,"HEAD")
 if status in (None,403,404,405,410,429) or status and status>=500:
  status,landed,error=probe(url,"GET")
 if status in (404,410):
  second,_,_=probe(url,"GET")
  verdict="confirmed_broken" if second in (404,410) else "unverified"
 elif status is not None and 200<=status<400:verdict="reachable"
 else:verdict="unverified"
 return {"page":"/"+slug+"/","url":url,"type":typ,"linked_in_article":found,"http_status":status,"classification":verdict,"error_type":error,"redirect_to":landed if landed!=url else None,"note":"HTTP checks do not validate live tickets, cruise return times, berth or vehicle operations"}
def run():
 with ThreadPoolExecutor(max_workers=8) as ex:rows=list(ex.map(one,CASES))
 from collections import Counter
 counts=dict(Counter(x["classification"] for x in rows))
 issues=[x for x in rows if x["classification"]=="confirmed_broken" or not x["linked_in_article"]]
 out={"version":"V130","checked_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"sources":len(rows),"counts":counts,"confirmed_404_or_missing_anchors":issues,"requires_manual_review":[x for x in rows if x["classification"]=="unverified"],"rows":rows}
 target=ROOT/"audit-output/v130/official-source-link-review.json";target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n","utf8")
 print(json.dumps({"checked":len(rows),"counts":counts,"requires_review":len(out["requires_manual_review"]),"confirmed_404_or_missing_anchors":len(issues),"url_review_not_operations_confirmation":True},ensure_ascii=False))
 for row in out["requires_manual_review"]:
  print("UNVERIFIED",row["url"],"HTTP",row["http_status"],"ERROR",row["error_type"])
 for row in issues:
  print("CONFIRMED_ISSUE",row["url"],row["classification"])
 return not issues
if __name__=="__main__":raise SystemExit(0 if run() else 1)
