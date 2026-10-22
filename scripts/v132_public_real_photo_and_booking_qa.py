#!/usr/bin/env python3
"""V132 production smoke tests of 83 repaired previews and 3 verified booking information panels.
PC 1440 and mobile 390; 83 pages x 2 plus booking 3 x 2 = 172 page checks.
This does not make live ferry bookings or prove photo provenance or actual ticket stock.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
ROOT=Path(__file__).resolve().parents[1]
BASE="https://www.nipponferry.com"
BEFORE=ROOT/"audit-reports/v132/sitewide-inventory-before-photo-repair.json"
OUT=ROOT/"audit-output/v132"
BOOKS=("/booking/japan-cruise/","/ferry/","/guide/busan-shimonoseki-ferry/")
INFO_LINKS=("https://kampuferry.co.jp/reserve/","https://www.kampuferry.co.jp/yoyaku/jp/reservation.html","https://kampuferry.co.jp/qa/")
def scan():
 baseline=json.loads(BEFORE.read_text("utf8"))
 issues=baseline["findings"]["image_meta_mismatch"]
 covers={}
 for item in issues:
  covers[item["page"]]=item["cover"]
 assert len(covers)==83,"Expected 83 previously mismatched pages"
 OUT.mkdir(parents=True,exist_ok=True)
 rows=[];problems=[];booking=[]
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
  for width,height in ((1440,900),(390,844)):
   ctx=browser.new_context(viewport={"width":width,"height":height})
   pg=ctx.new_page()
   for n,(uri,source) in enumerate(sorted(covers.items())):
    key=uri+"@"+str(width)
    try:
     result=pg.goto(BASE+uri,wait_until="domcontentloaded",timeout=60000)
     if not result or result.status!=200:raise ValueError("HTTP response is not 200")
     if pg.locator('link[rel="canonical"]').count()!=1:raise ValueError("canonical missing")
     cover=pg.locator("img.cover")
     if cover.count()!=1 or cover.get_attribute("src")!=source:raise ValueError("cover file changed")
     og=pg.locator('meta[property="og:image"]').get_attribute("content")
     if og!=BASE+source:raise ValueError("OG not aligned with visible cover")
     scripts=pg.locator('script[type="application/ld+json"]').all_text_contents()
     articles=[]
     for script in scripts:
      try:obj=json.loads(script)
      except (TypeError,ValueError):continue
      for entity in (obj if isinstance(obj,list) else [obj]):
       if isinstance(entity,dict) and entity.get("@type")=="Article":articles.append(entity)
     if len(articles)!=1:raise ValueError("expected one Article schema")
     image=articles[0].get("image")
     if image not in ([og],og):raise ValueError("Article structured image mismatch")
     cover.scroll_into_view_if_needed(timeout=12000)
     loaded=cover.evaluate("(i)=>new Promise(done=>{if(i.complete)return done(i.naturalWidth>0);i.addEventListener('load',()=>done(true),{once:true});i.addEventListener('error',()=>done(false),{once:true})})",timeout=22000)
     if not loaded:raise ValueError("hero image failed decode")
     if pg.evaluate("document.documentElement.scrollWidth")>width+12:
      raise ValueError("horizontal viewport overflow")
     rows.append({"page":uri,"viewport":width,"cover":source,"pass":True})
     if n in (0,22,53,82):pg.screenshot(path=str(OUT/f"metadata-page-{n}-{width}.png"),full_page=False)
    except Exception as ex:
     problems.append({"page":uri,"viewport":width,"error":str(ex)[:200]})
   for uri in BOOKS:
    try:
     response=pg.goto(BASE+uri,wait_until="domcontentloaded",timeout=60000)
     if not response or response.status!=200:raise ValueError("page HTTP error")
     section=pg.locator("#nf-v132-kampu-booking-verified")
     if section.count()!=1:raise ValueError("booking conditions panel absent")
     for link in INFO_LINKS:
      if section.locator('a[href="'+link+'"]').count()!=1:
       raise ValueError("official booking or terms link missing "+link)
     copy=section.inner_text()
     for term in ("2개월","오후 1시","취소","신용카드","예약 안내"):
      if term not in copy:raise ValueError("missing operative official condition: "+term)
     if pg.evaluate("document.documentElement.scrollWidth")>width+12:
      raise ValueError("booking page horizontal overflow")
     section.screenshot(path=str(OUT/f"booking-{uri.strip('/').replace('/','-')}-{width}.png"))
     booking.append({"page":uri,"viewport":width,"passed":True})
    except Exception as ex:problems.append({"page":uri,"viewport":width,"error":str(ex)[:200]})
   pg.close();ctx.close()
  browser.close()
 report={"version":"V132","expected_image_checks":166,"passed_image_checks":len(rows),"expected_booking_checks":6,"passed_booking_checks":len(booking),"errors":problems,"passed":len(rows)==166 and len(booking)==6 and not problems,"image_checks":rows,"booking_checks":booking}
 (OUT/"public-live-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
 print(json.dumps({k:report[k] for k in ("passed","passed_image_checks","expected_image_checks","passed_booking_checks","expected_booking_checks","errors")},ensure_ascii=False))
 return report["passed"]
if __name__=="__main__":raise SystemExit(0 if scan() else 1)
