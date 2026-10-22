#!/usr/bin/env python3
"""V124 verify public homepage day-trip cards on desktop and narrow mobile.
A source commit alone is not proof the CDN deployed correctly.
"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
photos=json.loads((ROOT/"audit-reports/v124/photo-plan.json").read_text("utf8"))["photos"]
OUT=ROOT/"audit-output/v124"
OUT.mkdir(parents=True,exist_ok=True)
all_checks=[];errors=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
 for width,height in ((1440,900),(390,844)):
  context=browser.new_context(viewport={"width":width,"height":height},device_scale_factor=1)
  page=context.new_page()
  try:
   response=page.goto("https://www.nipponferry.com/",wait_until="domcontentloaded",timeout=60000)
   if not response or response.status!=200:raise ValueError("homepage http status not 200")
   sec=page.locator(".d61-home-card")
   if sec.count()!=4:raise ValueError("Expected 4 day-trip cards, got "+str(sec.count()))
   for x in photos:
    root=page.locator(".d61-home-card").filter(has=page.locator(f'a.d61-home-photo[href="{x["href"]}"]'))
    if root.count()!=1:raise ValueError("Wrong card identity "+x["slug"])
    img=root.locator(f'img[src="{x["output"]}"]')
    if img.count()!=1:raise ValueError("Production image not yet published "+x["slug"])
    img.scroll_into_view_if_needed()
    img.evaluate("""i=>i.complete?true:new Promise(resolve=>{i.addEventListener('load',()=>resolve(true),{once:true});i.addEventListener('error',()=>resolve(false),{once:true})})""",timeout=22000)
    info=img.evaluate("i=>({ok:i.complete&&i.naturalWidth>0,w:i.naturalWidth,h:i.naturalHeight})")
    if not info["ok"] or (info["w"],info["h"])!=(1200,800):
     raise ValueError(x["slug"]+" image decode/dimensions wrong "+str(info))
    if page.locator(f'p.d61-home-note a[href="{x["source"]}"]').count()!=1:
     raise ValueError(x["slug"]+" photo author link not visible")
    all_checks.append({"slug":x["slug"],"screen_width":width,"decoded":True,"photo_credit":True})
   if page.title()!="일본크루즈 여행 | 가격·일정·기항지 | 일본페리":
    raise ValueError("Home title SEO regression")
   if page.locator('link[rel="canonical"]').get_attribute("href")!="https://www.nipponferry.com/":
    raise ValueError("Home canonical SEO regression")
   scroll=page.evaluate("document.documentElement.scrollWidth")
   if scroll>width+12:raise ValueError(f"Viewport horizontal overflow {scroll}>{width}")
   home=page.locator(".d61-home-card").first
   home.scroll_into_view_if_needed()
   page.screenshot(path=str(OUT/f"home-day-trip-{width}.png"),full_page=True)
  except Exception as e:
   errors.append(f"viewport={width}: {str(e)[:230]}")
  finally:
   context.close()
 browser.close()
output={"version":"V124","passed":len(all_checks)==6 and not errors,"checks":all_checks,"expected":6,"errors":errors}
(OUT/"report.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps({"passed":output["passed"],"checked":len(all_checks),"expected":6,"errors":errors},ensure_ascii=False))
raise SystemExit(0 if output["passed"] else 1)
