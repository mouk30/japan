#!/usr/bin/env python3
"""V168 public HTTP smoke acceptance: four existing guides, four original
licensed real WebP images and sitemap. Checks rendered hrefs, not paid tickets.
"""
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime,timezone
import xml.etree.ElementTree as ET,json,time
HOST="https://www.nipponferry.com"
D={
"amami-naze":{"photo":"/images/venues/nf-v125-amami-naze-cruise-port-day-trip-real.webp",
  "links":["https://www.aline-ferry.com/status/status-route/route-amami/","https://www.aline-ferry.com/amami/reserve/","https://www.aline-ferry.com/kagoshima/access/"],
  "facts":["페리 아마미","페리 기카이","주 3편","10월 23일","귀선"]},
"naha":{"photo":"/images/venues/naha-kokusai-street.webp",
  "links":["https://www.vill.tokashiki.okinawa.jp/","https://www.vill.zamami.okinawa.jp/ship/","https://yoyaku.vill.zamami.okinawa.jp/zamami_web/res0301%21doFormOpenNologSp.action"],
  "facts":["10월 24일","도카시키","12월 3일","귀선"]},
"motobu":{"photo":"/images/venues/nf-v114-motobu-real.webp",
  "links":["https://www.aline-ferry.com/status/status-route/route-kagoshima/","https://www.aline-ferry.com/kagoshima/reserve/","https://www.aline-ferry.com/kagoshima/access/"],
  "facts":["나미노우에","10월 24일","25일","27일","수수료","귀선"]},
"kagoshima":{"photo":"/images/venues/kagoshima-ioworld-aquarium.webp",
  "links":["https://www.tokara.jp/ferryinfo/ferrytoshima/","https://ferry-toshima.sakura.ne.jp/","https://nakagawaunyu.jp/toshima/"],
  "facts":["도시마2","10월 23일","10월 26일","21:00","귀선"]}
}
class P(HTMLParser):
 def __init__(self):
  super().__init__();self.ids=[];self.img=[];self.canon=[];self.h1=0;self.links=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if "id" in a:self.ids.append(a["id"])
  if t=="img":self.img.append((a.get("src",""),a.get("alt","")))
  if t=="a":self.links.append(a.get("href",""))
  if t=="h1":self.h1+=1
  if t=="link" and a.get("rel")=="canonical":self.canon.append(a.get("href",""))
def fetch(path,binary=False):
 e=""
 for n in range(4):
  try:
   with urlopen(Request(HOST+path,headers={"User-Agent":"Mozilla/5.0 (NIPPONFERRY-V168-source-check)","Cache-Control":"no-cache"}),timeout=24) as r:
    x=r.read(5_000_000)
    return r.status,r.headers.get("Content-Type",""),x if binary else x.decode("utf-8","replace")
  except (HTTPError,URLError,TimeoutError) as ex:e=str(ex);time.sleep(n+1)
 raise RuntimeError(path+" "+e)
rows=[]
def add(path,checks,error=None):
 x={"url":HOST+path,"pass":all(checks.values()),"checks":checks}
 if error:x["error"]=error
 rows.append(x)
 print("PASS" if x["pass"] else "FAIL",path,[a for a,b in checks.items() if not b],flush=True)
for slug,cfg in D.items():
 path=f"/things-to-do/{slug}-cruise-port-day-trip/"
 try:
  status,typ,html=fetch(path);p=P();p.feed(html)
  a=html.find(f'id="nf-v168-{slug}"');b=html.find("</section>",a)
  panel=html[a:b] if a>=0 and b>a else ""
  tests={
   "public_200_html":status==200 and "html" in typ.lower(),
   "canonical_original_path":p.canon==[HOST+path],
   "single_H1":p.h1==1,
   "exactly_one_V168_panel":p.ids.count("nf-v168-"+slug)==1,
   "three_useful_cards":panel.count('class="nf-v168-card"')==3,
   "official_real_booking_status_links_in_HTML":all(u in panel and u in p.links for u in cfg["links"]),
   "dated_operator_changes_and_ship_return":all(x in panel for x in cfg["facts"]),
   "authentic_existing_photo_and_alt":any(src==cfg["photo"] and len(alt)>15 for src,alt in p.img),
   "photographer_and_legal_source_link":any("commons.wikimedia.org" in (u or "") for u in p.links),
   "large_mobile_tap_targets":'id="nf-v168-official-css"' in html and "min-height:52px" in html and "@media(max-width:620px)" in html,
   "still_search_indexable":'name="robots" content="index,follow' in html[:9000],
   "avoid_guarantee_of_booked_inventory":"잔여석 확보 완료" not in panel and "승선권 구매 완료" not in panel
  }
  add(path,tests)
 except Exception as e:add(path,{"HTTP_error":False},str(e))
for cfg in D.values():
 path=cfg["photo"]
 try:
  status,typ,body=fetch(path,binary=True)
  add(path,{"WebP_http_200":status==200 and "webp" in typ.lower(),"actual_RIFF_WEBP_image":body[:4]==b"RIFF" and body[8:12]==b"WEBP"})
 except Exception as e:add(path,{"HTTP_error":False},str(e))
try:
 status,typ,s=fetch("/sitemap.xml")
 locs=[u.find("{*}loc").text for u in ET.fromstring(s).findall("{*}url")]
 add("/sitemap.xml",{"xml_200":status==200,"original_four_paths":all(HOST+f"/things-to-do/{slug}-cruise-port-day-trip/" in locs for slug in D),"no_duplicate_urls":len(locs)==len(set(locs))})
except Exception as e:add("/sitemap.xml",{"HTTP_error":False},str(e))
summary={"version":"V168","timestamp_utc":datetime.now(timezone.utc).isoformat(),"new_articles":0,"edited_original_articles":4,
 "checked_public_items":len(rows),"passed":sum(x["pass"] for x in rows),"booking_stock_payment_and_return_gate_not_verified":True,"rows":rows}
out=Path("audit-output/v168-public");out.mkdir(parents=True,exist_ok=True)
(out/"four-original-guides-WebP-and-sitemap.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",summary["passed"],"/",summary["checked_public_items"],flush=True)
if summary["passed"]!=summary["checked_public_items"]:raise SystemExit(1)
