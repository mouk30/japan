#!/usr/bin/env python3
"""V147: verify existing guides' booking notice, source links, and return-to-ship quality.
No new article pages or sitemap URLs are allowed by this change.
Does not claim real-time ferry seat availability, sailings or bus timetables."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import json
import re
ROOT=Path("site")
BOOKING=["booking/japan-cruise","ferry","guide/busan-shimonoseki-ferry"]
PORT=["naha-cruise-terminal-kokusai-dori","ishigaki-cruise-kabira-bay-bus-taxi",
      "hakata-port-hakata-station-access","nagasaki-matsugae-glover-garden-cruise-access",
      "yokohama-red-brick-warehouse"]
notice="https://kampuferry.co.jp/news/20261023systemmaintenance.html"
source={"naha-cruise-terminal-kokusai-dori":"https://cruise.visitokinawa.jp/en/nahaport/",
 "ishigaki-cruise-kabira-bay-bus-taxi":"https://www.azumabus.co.jp/localbus/",
 "hakata-port-hakata-station-access":"https://hakataport.com/center/",
 "nagasaki-matsugae-glover-garden-cruise-access":"https://glover-garden.jp/guide/",
 "yokohama-red-brick-warehouse":"https://www.yokohama-akarenga.jp/"}
class Analyzer(HTMLParser):
 def __init__(self):
  super().__init__();self.titles=[];self.headings=0;self.canonicals=[];self.links=[];self.images=[];self.meta=[];self.ids=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="h1":self.headings+=1
  if tag=="link" and "canonical" in a.get("rel",""):self.canonicals.append(a.get("href"))
  if tag=="a":self.links.append(a.get("href",""))
  if tag=="img":self.images.append(a.get("src",""))
  if "id" in a:self.ids.append(a["id"])
  if tag=="meta" and a.get("name")=="description":self.meta.append(a.get("content",""))
rows=[]
for item in BOOKING+["things-to-do/"+x for x in PORT]:
 p=ROOT/item/"index.html";txt=p.read_text(encoding="utf-8");a=Analyzer();a.feed(txt)
 expected="https://www.nipponferry.com/"+item+"/"
 checks={"one_h1":a.headings==1,"canonical":a.canonicals==[expected],
    "meta_description":len(a.meta)==1 and len(a.meta[0])>30,
    "image_present":bool(a.images) and all((ROOT/x.lstrip("/").split("?")[0]).is_file() for x in a.images if x.startswith("/")),
    "no_duplicate_ids":len(a.ids)==len(set(a.ids))}
 if item in BOOKING:
  checks.update({"official_suspension_notice":notice in a.links,
    "emergency_notice_once":a.ids.count("nf-v147-kampu-20261023")==1,
    "official_email":any("support@kampuferry.co.jp" in x for x in a.links),
    "retired_online_booking_links":not re.search(r'href=["\\\']https?://(?:www\\.)?kampuferry\\.co\\.jp/(?:reserve/|yoyaku/)',txt),
    "international_booking_copy":"해외(국제) 고객" in txt and "발송만으로 예약 확정이 아닙니다" in txt,
    "safe_return_copy":"귀국편" in txt and "수속 마감" in txt})
 else:
  slug=item.rsplit("/",1)[1]
  checks.update({"specific_port_card_once":a.ids.count("nf-v147-port-visitor")==1,
    "official_transport_or_ticket_link":source[slug] in a.links,
    "return_time_fields":"___" in txt or "__:__" in txt,
    "no_bookability_claim":"귀선" in txt and "기항" in txt})
 rows.append({"path":str(p),"pass":all(checks.values()),"checks":checks})
 for k,v in checks.items():
  if not v:print("FAIL",p,k)
 print("PASS" if rows[-1]["pass"] else "FAIL",p)
out=Path("audit-output/v147");out.mkdir(parents=True,exist_ok=True)
(out/"existing-guide-qa.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",sum(x["pass"] for x in rows),"/",len(rows))
if not all(x["pass"] for x in rows):raise SystemExit(1)
