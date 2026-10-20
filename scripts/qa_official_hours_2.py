#!/usr/bin/env python3
"""Check two existing guides' official hours/ticket links in built and live HTML.
Does not claim ticket availability, live boarding, or search ranking.
"""
import argparse, json, sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import urlparse

ROOT="https://www.nipponferry.com"
TARGETS={
"nagasaki-matsugae-glover-garden-cruise-access":{
 "must":["2026년 10월 12~31일","10월 21일","10월 23·24·30·31일","1,300엔","650엔","19:40","21:10"],
 "must_not":["통상 08:00~18:00, 최종 입장 20분 전"],
 "links":["https://glover-garden.jp/event-and-news/26532/","https://glover-garden.jp/guide/"],
},
"okinawa-churaumi-aquarium":{
 "must":["AI 생성 참고 이미지","마지막 입장 시각","임시 휴관","08:30~18:30"],
 "must_not":["여행 가이드은(는)","휴무을(를)","공식 지역 관광포털에서 시설명 찾기"],
 "links":["https://oki-churaumi.jp/kr/guide/info/","https://www.churaumi.okinawa/sp/kr/guide/hour/"],
}}
class Tags(HTMLParser):
 def __init__(self):super().__init__();self.h1=0;self.links=[];self.canonical=[];self.ld_count=0;self._ld=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="h1":self.h1+=1
  if tag=="a":self.links.append(a.get("href",""))
  if tag=="link" and "canonical" in a.get("rel",""):self.canonical.append(a.get("href",""))
  if tag=="script" and a.get("type")=="application/ld+json":self._ld=[]
 def handle_data(self,data):
  if self._ld is not None:self._ld.append(data)
 def handle_endtag(self,tag):
  if tag=="script" and self._ld is not None:
   try:json.loads("".join(self._ld));self.ld_count+=1
   except ValueError:pass
   self._ld=None

def fetch(route,mode,local):
 if mode=="static":return (local/route.lstrip("/")/"index.html").read_text(encoding="utf-8")
 req=Request(ROOT+route,headers={"User-Agent":"Mozilla/5.0 (NIPPONFERRY Quality QA)"})
 with urlopen(req,timeout=20) as resp:
  if resp.status!=200 or "html" not in resp.headers.get("Content-Type","").lower():raise ValueError(f"HTTP/content type: {resp.status}")
  if resp.geturl().rstrip("/")!=(ROOT+route).rstrip("/"):raise ValueError("unexpected redirect")
  return resp.read().decode("utf-8","replace")
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--mode",choices=["static","live"],required=True)
 p.add_argument("--root",default="dist")
 args=p.parse_args();data=[]
 for slug,expected in TARGETS.items():
  route="/things-to-do/"+slug+"/"
  result={"page":route,"checks":{},"errors":[]}
  try:
   html=fetch(route,args.mode,Path(args.root));tags=Tags();tags.feed(html)
   result["checks"]={
    "exact_canonical":tags.canonical==[ROOT+route],
    "one_h1":tags.h1==1,
    "article_json_ld":tags.ld_count>0,
    "required_copy":all(x in html for x in expected["must"]),
    "old_misleading_copy_gone":not any(x in html for x in expected["must_not"]),
    "official_links_in_anchor":all(x in tags.links for x in expected["links"]),
    "booking_navigation":"/booking/japan-cruise/" in tags.links,
   }
  except Exception as error:result["errors"].append(str(error))
  result["pass"]=bool(result["checks"]) and all(result["checks"].values()) and not result["errors"]
  data.append(result)
  print(("PASS" if result["pass"] else "FAIL"),route,"failed checks", [k for k,v in result["checks"].items() if not v],result["errors"])
 summary={"mode":args.mode,"checked_at_utc":datetime.now(timezone.utc).isoformat(),"passed":sum(x["pass"] for x in data),"total":len(data),"results":data}
 out=Path("audit-output/official-hours-2")
 out.mkdir(parents=True,exist_ok=True);(out/(args.mode+".json")).write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
 print("SUMMARY",json.dumps({"mode":args.mode,"passed":summary["passed"],"total":summary["total"]}))
 if summary["passed"]!=len(data):sys.exit(1)
if __name__=="__main__":main()
