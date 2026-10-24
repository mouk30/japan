#!/usr/bin/env python3
"""JNTO original plan: actual public-domain HTTP quality check.
21 article pages (20 improved existing, one food pilot) and sitemap.
Checks published HTML/SEO/required links, not GA4 conversion or seat inventory.
"""
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from html.parser import HTMLParser
from datetime import datetime,timezone
from pathlib import Path
import xml.etree.ElementTree as ET,json,time,re
ORIGIN="https://www.nipponferry.com"
CORE="naoshima-art-ferry-return teshima-art-ferry-return shodoshima-ferry-island-access takamatsu-cruise-port-day-trip amami-naze-cruise-port-day-trip goto-fukue-cruise-port-day-trip nagasaki-cruise-4-6-8-hour-itinerary matsuyama-cruise-port-day-trip sado-ogi-cruise-port-day-trip japan-amami-oshima-tsumugi".split()
RELATED="japan-kagawa-udon-pilgrimage kagawa-marugame-uchiwa-fans nagasaki-dejima-island-trade nagasaki-cruise-parents-guide hakata-cruise-parents-guide ishigaki-cruise-parents-guide nagasaki-glover-garden nagasaki-cruise-family-guide local-food-market-guide udon-japanese-regional-noodles".split()
PILOT="takamatsu-cruise-udon-market-return"
class Tags(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.canonical=[];self.images=[];self.ids=[];self.hrefs=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="h1":self.h1+=1
  if tag=="img":self.images.append(a.get("src",""))
  if tag=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href",""))
  if tag=="a":self.hrefs.append(a.get("href",""))
  if "id" in a:self.ids.append(a["id"])
def read(url):
 error=None
 for k in range(4):
  try:
   with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0 (NIPPONFERRY original JNTO-plan quality; +https://www.nipponferry.com)","Cache-Control":"no-cache"}),timeout=24) as r:
    return r.status,r.headers.get("content-type",""),r.read(5_000_000)
  except (HTTPError,URLError,TimeoutError) as e:error=str(e);time.sleep(2+k)
 raise RuntimeError(str(error))
result=[]
for kind,names in [("core",CORE),("related",RELATED),("pilot",[PILOT])]:
 for slug in names:
  route="/things-to-do/"+slug+"/";record={"type":kind,"path":route}
  try:
   status,ctype,data=read(ORIGIN+route);s=data.decode("utf-8","replace");t=Tags();t.feed(s)
   marker={"core":"nf-jnto-journey-20261024","related":"nf-jnto-experience-links-20261024","pilot":"nf-v148-photo-credits"}[kind]
   checks={
    "http_200":status==200,
    "html":"html" in ctype.lower(),
    "canonical":t.canonical==[ORIGIN+route],
    "one_h1":t.h1==1,
    "indexable":"noindex" not in s[:6000].lower(),
    "relevant_panel":t.ids.count(marker)==1,
    "images_present":len(t.images)>0,
   }
   if kind=="core":
    checks.update({"official_destination_links":len([a for a in t.hrefs if a.startswith("https") and "nipponferry.com" not in a and "creativecommons" not in a and "wikimedia" not in a])>=2,
      "return_book_transport":"귀선" in s and "예약" in s and "이동" in s})
   if kind=="related":
    checks.update({"at_least_three_updated_links":len([x for x in t.hrefs if x.startswith("/things-to-do/")])>=3,
      "post_update_text":"2026-10-24" in s})
   if kind=="pilot":
    checks.update({
      "3_shikoku_areas":all(x in s for x in ("다카마쓰","도쿠시마","고치")),
      "booking_transport_return":all(x in s for x in ("미식","귀선","하선","__:__")),
      "original_photo":"/images/culture-verified/japan-kagawa-udon-pilgrimage.webp" in t.images,
      "licensed_source":"https://commons.wikimedia.org/wiki/File:Kama-age_sanuki_udon_by_sekido_in_Takamatsu%2C_Kagawa.jpg" in t.hrefs,
      "cc_by_2":"https://creativecommons.org/licenses/by/2.0" in t.hrefs,
      "official_3_regions":all(x in t.hrefs for x in ["https://www.my-kagawa.jp/en/see-and-do/10132","https://discovertokushima.net/ko/cuisines/","https://visitkochijapan.com/ko/see-and-do/10024"]),
    })
   record.update({"checks":checks,"pass":all(checks.values()),"bytes":len(data)})
  except Exception as e:record.update({"pass":False,"error":str(e)})
  print("PASS" if record["pass"] else "FAIL",kind,route,[x for x,v in record.get("checks",{}).items() if not v],record.get("error",""),flush=True)
  result.append(record)
route="/sitemap.xml";rec={"type":"sitemap","path":route}
try:
 st,ct,b=read(ORIGIN+route);root=ET.fromstring(b)
 url_nodes=root.findall("{*}url")
 listed={x.find("{*}loc").text:(x.find("{*}lastmod").text if x.find("{*}lastmod") is not None else None) for x in url_nodes}
 checks={"http_200":st==200,
    "pilot_present":listed.get(ORIGIN+"/things-to-do/"+PILOT+"/")=="2026-10-24",
    "updated_20_lastmod":all(listed.get(ORIGIN+"/things-to-do/"+slug+"/")=="2026-10-24" for slug in CORE+RELATED),
    "no_duplicates":len(url_nodes)==len(listed)}
 rec.update({"checks":checks,"pass":all(checks.values()),"listed":len(url_nodes)})
except Exception as e:rec.update({"pass":False,"error":str(e)})
print("PASS" if rec["pass"] else "FAIL",route,rec.get("checks",rec.get("error")),flush=True)
result.append(rec)
report={"checked_utc":datetime.now(timezone.utc).isoformat(),
 "existing_core_pages":10,"related_pages":10,"new_pilot_pages":1,
 "existing_other_two_pilots":"Naoshima & Teshima maintained, not duplicated",
 "checked":len(result),"passed":sum(x["pass"] for x in result),
 "booking_GA4_conversion":"not measured - access missing",
 "Search_Console_impressions":"not measured - access missing",
 "results":result}
out=Path("audit-output/jnto-plan-public");out.mkdir(parents=True,exist_ok=True)
(out/"public-21-pages-and-sitemap.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",report["passed"],"/",report["checked"])
if report["passed"]!=report["checked"]:raise SystemExit(1)
