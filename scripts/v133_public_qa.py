#!/usr/bin/env python3
"""V133 live desktop/mobile visit to four changed pages, no ticket purchases."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
ROOT=Path(__file__).resolve().parents[1]
BASE="https://www.nipponferry.com"
OUT=ROOT/"audit-output/v133"
CASES=[
 ("okinawa-shuri-castle","nf-v133-shuri-official-20261023","おにく","Shuri_Castle_Reconstruction.jpg"),
 ("naha-shuri-castle-cruise-sightseeing","nf-v133-shuri-official-20261023","슈리성","oki-park.jp/shurijo/ticket_guide/"),
 ("nanao-cruise-port-day-trip","nf-v133-nanao-earthquake-market-check","nanaoshimin","Nanao"),
 ("nagasaki-cruise-port-day-trip",None,"Fg2","Ringer House"),
]
def run():
 OUT.mkdir(parents=True,exist_ok=True)
 audit={"version":"V133","checked":0,"expected":8,"errors":[],"screenshots":[]}
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
  for width,height in ((1440,900),(390,844)):
   ctx=browser.new_context(viewport={"width":width,"height":height})
   page=ctx.new_page()
   for slug,card,author,source in CASES:
    uri=BASE+"/things-to-do/"+slug+"/"
    try:
     resp=page.goto(uri,wait_until="domcontentloaded",timeout=60000)
     if not resp or resp.status!=200:raise ValueError("HTTP not 200")
     if page.locator('link[rel="canonical"]').count()!=1 or page.locator('link[rel="canonical"]').get_attribute("href")!=uri:
      raise ValueError("canonical URL incorrect")
     if page.locator("h1").count()!=1:raise ValueError("H1 mismatch")
     img=page.locator("img.cover, img.hero").first
     if img.count()!=1:raise ValueError("hero photo not found")
     img.scroll_into_view_if_needed(timeout=12000)
     isloaded=img.evaluate("(i)=>new Promise(done=>{if(i.complete)return done(i.naturalWidth>0);i.addEventListener('load',()=>done(true),{once:true});i.addEventListener('error',()=>done(false),{once:true})})",timeout=22000)
     if not isloaded:raise ValueError("hero photo decode error")
     if card and page.locator("#"+card).count()!=1:raise ValueError("official condition card missing")
     content=page.locator("body").inner_text()
     if author not in content or source not in page.content():raise ValueError("verified source or attribution missing")
     if page.evaluate("document.documentElement.scrollWidth")>width+12:raise ValueError("mobile horizontal overflow")
     if card:page.locator("#"+card).scroll_into_view_if_needed(timeout=12000)
     target=OUT/f"v133-{slug}-{width}.png"
     page.screenshot(path=str(target),full_page=False)
     audit["screenshots"].append(target.name)
     audit["checked"]+=1
    except Exception as e:audit["errors"].append({"slug":slug,"width":width,"reason":str(e)[:260]})
   page.close();ctx.close()
  browser.close()
 audit["passed"]=audit["checked"]==audit["expected"] and not audit["errors"]
 (OUT/"live-qa.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n","utf8")
 print(json.dumps({k:audit[k] for k in ("passed","checked","expected","errors")},ensure_ascii=False))
 return audit["passed"]
if __name__=="__main__":raise SystemExit(0 if run() else 1)
