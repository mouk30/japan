#!/usr/bin/env python3
"""V147 release test: verify eight UPDATED EXISTING pages on the public domain, no new articles.
Checks publication and explanatory links; does not assert real-time bookings or departures."""
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from html.parser import HTMLParser
from datetime import datetime,timezone
from pathlib import Path
import json,time,re
ORIGIN="https://www.nipponferry.com"
NOTICE="https://kampuferry.co.jp/news/20261023systemmaintenance.html"
BOOKING=["booking/japan-cruise","ferry","guide/busan-shimonoseki-ferry"]
PORTS={
 "things-to-do/naha-cruise-terminal-kokusai-dori":"https://cruise.visitokinawa.jp/en/nahaport/",
 "things-to-do/ishigaki-cruise-kabira-bay-bus-taxi":"https://www.azumabus.co.jp/localbus/",
 "things-to-do/hakata-port-hakata-station-access":"https://hakataport.com/center/",
 "things-to-do/nagasaki-matsugae-glover-garden-cruise-access":"https://glover-garden.jp/guide/",
 "things-to-do/yokohama-red-brick-warehouse":"https://www.yokohama-akarenga.jp/"
}
UA="Mozilla/5.0 (compatible; NIPPONFERRY-V147-LiveQuality/1.0)"
class Page(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.links=[];self.canonical=[];self.ids=[];self.img=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="h1":self.h1+=1
  if tag=="a":self.links.append(a.get("href",""))
  if tag=="img":self.img.append(a.get("src",""))
  if "id" in a:self.ids.append(a["id"])
  if tag=="link" and "canonical" in a.get("rel",""):self.canonical.append(a.get("href",""))
def fetch(url):
 error=None
 for i in range(4):
  try:
   with urlopen(Request(url,headers={"User-Agent":UA,"Cache-Control":"no-cache"}),timeout=28) as f:
    return f.status,f.geturl(),f.headers.get("content-type",""),f.read(2_000_000)
  except (HTTPError,URLError,TimeoutError) as err:
   error=str(err);time.sleep(4+i)
 raise RuntimeError(f"{url}: {error}")
reports=[]
for item in BOOKING+list(PORTS):
 url=ORIGIN+"/"+item+"/"
 row={"url":url,"existing_article":True}
 try:
  status,dest,ctype,blob=fetch(url)
  text=blob.decode("utf-8","replace");page=Page();page.feed(text)
  tests={"HTTP_200":status==200,"HTML_type":"html" in ctype,
    "canonical_exact":page.canonical==[url],"one_h1":page.h1==1,
    "has_local_image":any(src.startswith("/") for src in page.img),
    "noindex_absent":not ("content=\"noindex" in text.lower() or "content=\'noindex" in text.lower())}
  if item in BOOKING:
   tests.update({"Kampu_official_notice":NOTICE in page.links,
     "notice_one":page.ids.count("nf-v147-kampu-20261023")==1,
     "international_email":"mailto:support@kampuferry.co.jp" in page.links,
     "not_present_as_online_checkout":'href="https://kampuferry.co.jp/reserve/"' not in text,
     "reserve_not_confirmed":"발송만으로 예약 확정이 아닙니다" in text})
  else:
   tests.update({"local_port_return_block":page.ids.count("nf-v147-port-visitor")==1,
     "official_source_link":PORTS[item] in page.links,
     "return_time_fields":"귀선 시각 작성" in text or "여행자가 채울 시간" in text})
  row.update({"checks":tests,"passed":all(tests.values()),"bytes":len(blob)})
 except Exception as err:
  row.update({"passed":False,"error":str(err)})
 print("PASS" if row["passed"] else "FAIL",item,row.get("checks",row.get("error")))
 reports.append(row)
# Check the sitemap still resolves; this release changed no sitemap URLs.
try:
 status,_,ctype,body=fetch(ORIGIN+"/sitemap.xml")
 sitemap_ok=status==200 and b"<urlset" in body
except Exception as err:
 sitemap_ok=False;print("FAIL sitemap",err)
out=Path("audit-output/v147-public");out.mkdir(parents=True,exist_ok=True)
report={"checked_utc":datetime.now(timezone.utc).isoformat(),"pass":sum(p["passed"] for p in reports),
    "total":len(reports),"sitemap_accessible":sitemap_ok,"pages":reports}
(out/"published-existing-guides.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",report["pass"],"/",report["total"],"sitemap",sitemap_ok)
if report["pass"]!=len(reports) or not sitemap_ok:raise SystemExit(1)
