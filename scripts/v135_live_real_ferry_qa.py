#!/usr/bin/env python3
"""V135 live image and photo-credit QA for ten newly upgraded Shimonoseki/Osaka ferry guides."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
ROOT=Path(__file__).resolve().parents[1]
PLAN=json.loads((ROOT/"audit-reports/v135/photo-plan.json").read_text("utf8"))
PHOTOS={x["key"]:x for x in PLAN["photos"]}
OUTPUT=ROOT/"audit-output/v135"
BASE="https://www.nipponferry.com"
def run():
 OUTPUT.mkdir(parents=True,exist_ok=True)
 audit={"expected":20,"passed_checks":0,"failures":[],"screenshots":[]}
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
  for width,height in ((1440,900),(390,844)):
   ctx=browser.new_context(viewport={"width":width,"height":height})
   page=ctx.new_page()
   for row in PLAN["entries"]:
    slug=row["slug"]
    source=PHOTOS[row["picture"]]
    url=BASE+"/guide/"+slug+"/"
    try:
     res=page.goto(url,wait_until="domcontentloaded",timeout=60000)
     if not res or res.status!=200:raise ValueError("guide HTTP error")
     if page.locator('link[rel="canonical"]').get_attribute("href")!=url:raise ValueError("canonical changed")
     photo=page.locator('img.article-cover')
     if photo.count()!=1 or photo.get_attribute("src")!=source["output"]:raise ValueError("old or missing article image")
     photo.scroll_into_view_if_needed(timeout=14000)
     if not photo.evaluate("(e)=>new Promise(done=>{if(e.complete)return done(e.naturalWidth>0);e.addEventListener('load',()=>done(e.naturalWidth>0),{once:true});e.addEventListener('error',()=>done(false),{once:true})})",timeout=22000):raise ValueError("hero failed WebP decode")
     credit=page.locator(".nf-v135-photo-credit")
     if credit.count()!=1:raise ValueError("missing image license display")
     caption=credit.inner_text()
     for expected in (source["author"],source["license"],source["date"]):
      if expected not in caption:raise ValueError("missing caption "+expected)
     if credit.locator('a[href="'+source["source"]+'"]').count()!=1:raise ValueError("missing original Commons photo link")
     if credit.locator('a[href="'+source["license_url"]+'"]').count()!=1:raise ValueError("missing valid CC reuse deed")
     og=page.locator('meta[property="og:image"]').get_attribute("content")
     if og!=BASE+source["output"]:raise ValueError("og photo inconsistency")
     if page.evaluate("document.documentElement.scrollWidth")>width+12:raise ValueError("horizontal overflow")
     page.screenshot(path=str(OUTPUT/f"v135-{slug}-{width}.png"),full_page=False)
     audit["screenshots"].append(f"v135-{slug}-{width}.png")
     audit["passed_checks"]+=1
    except Exception as e:audit["failures"].append({"slug":slug,"viewport":width,"issue":str(e)[:220]})
   page.close();ctx.close()
  browser.close()
 audit["passed"]=audit["passed_checks"]==20 and not audit["failures"]
 (OUTPUT/"public-real-photo-qa.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n","utf8")
 print(json.dumps({k:audit[k] for k in ("passed","expected","passed_checks","failures")},ensure_ascii=False))
 return audit["passed"]
if __name__=="__main__":raise SystemExit(0 if run() else 1)
