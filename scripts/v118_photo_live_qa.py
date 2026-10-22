#!/usr/bin/env python3
"""V118 production check: ten deployed new images, visible source credits, original SEO, 2 viewports."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
plan=json.loads((ROOT/"audit-reports/v118/photo-plan.json").read_text("utf8"))["selected"]
prior={x["slug"]:x for x in json.loads((ROOT/"audit-reports/v118/seo-and-ai-candidate-baselines.json").read_text("utf8"))["pages"]}
imported={x["slug"]:x for x in json.loads((ROOT/"audit-reports/v118/import-result.json").read_text("utf8"))["images"]}
out=ROOT/"audit-output/v118"
out.mkdir(parents=True,exist_ok=True)
checks=[];errors=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
 for width,height in ((1440,900),(390,844)):
  context=browser.new_context(viewport={"width":width,"height":height})
  page=context.new_page()
  for entry in plan:
   slug=entry["slug"]
   label=f"{slug}@{width}"
   try:
    url="https://www.nipponferry.com/things-to-do/"+slug+"-cruise-port-day-trip/"
    response=page.goto(url,wait_until="domcontentloaded",timeout=60000)
    if response is None or response.status!=200:raise ValueError("live page HTTP non-200")
    image=page.locator('img.cover[src="'+entry["output"]+'"]')
    if image.count()!=1:raise ValueError("WebP hero not published yet")
    image.scroll_into_view_if_needed(timeout=12000)
    image.evaluate("(i)=>i.complete?true:new Promise((resolve)=>{i.addEventListener('load',()=>resolve(true),{once:true});i.addEventListener('error',()=>resolve(false),{once:true})})",timeout=25000)
    info=image.evaluate("(i)=>({loaded:i.complete&&i.naturalWidth>0,w:i.naturalWidth,h:i.naturalHeight})")
    if not info["loaded"] or (info["w"],info["h"])!=(imported[slug]["pixel_width"],imported[slug]["pixel_height"]):
     raise ValueError("broken or unexpected image pixels")
    if page.locator("figcaption.v118-photo-credit").count()!=1:
     raise ValueError("source credit missing")
    credit=page.locator("figcaption.v118-photo-credit").inner_text()
    if any(value not in credit for value in (entry["author"],entry["license"],entry["taken"])):
     raise ValueError("rights attribution incomplete")
    if page.locator('meta[property="og:image"]').get_attribute("content")!="https://www.nipponferry.com"+entry["output"]:
     raise ValueError("OG mismatch")
    if page.locator('link[rel="canonical"]').get_attribute("href")!=prior[slug]["canonical"]:
     raise ValueError("canonical regression")
    if page.title()!=prior[slug]["title"]:raise ValueError("page title regression")
    if page.evaluate("document.documentElement.scrollWidth")>width+12:raise ValueError("horizontal overflow")
    page.screenshot(path=str(out/f"{slug}-{width}.png"),full_page=False)
    checks.append({"slug":slug,"viewport":width,"decoded":True,"correct_image":entry["output"],"seo_preserved":True})
   except Exception as exc:errors.append(label+" "+str(exc)[:200])
  page.close();context.close()
 browser.close()
result={"passed":len(checks)==20 and not errors,"checked":len(checks),"expected":20,"errors":errors,"checks":checks}
(out/"report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps({k:result[k] for k in ("passed","checked","expected","errors")},ensure_ascii=False))
raise SystemExit(0 if result["passed"] else 1)
