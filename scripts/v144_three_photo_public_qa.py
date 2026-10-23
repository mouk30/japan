#!/usr/bin/env python3
"""V144 photo follow-up: verify production photo bytes / documentary attribution
and mobile/desktop crop. Original information diagrams remain available.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
from hashlib import sha256
import json
root=Path(__file__).resolve().parents[1]
d=json.loads((root/"audit-reports/v144/editorial-image-provenance-report.json").read_text("utf8"))
photos=d.get("verified_documentary_photo_additions",[])
assert len(photos)==3, "No verified 3 photo import present"
out=root/"audit-output/v144-three-photos";out.mkdir(parents=True,exist_ok=True)
BASE="https://www.nipponferry.com"
report={"photos":3,"widths":[390,1440],"results":[],"errors":[],"screenshots":[]}
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
 api=p.request.new_context()
 for photo in photos:
  src=BASE+photo["image"]
  res=api.get(src,timeout=50000)
  if res.status!=200 or sha256(res.body()).hexdigest()!=photo["sha256"]:
   report["errors"].append(photo["page"]+": uploaded WebP not same as licensed derivative")
  for width in (390,1440):
   page=browser.new_page(viewport={"width":width,"height":920},device_scale_factor=1)
   errors=[]
   try:
    res=page.goto(BASE+photo["page"],wait_until="domcontentloaded",timeout=60000)
    if not res or res.status!=200:errors.append("page not 200")
    fig=page.locator("figure.v144-real-photo")
    if fig.count()!=1:errors.append("licensed image figure missing")
    else:
     image=fig.locator("img")
     image.scroll_into_view_if_needed()
     if image.get_attribute("src")!=photo["image"]:errors.append("wrong WebP")
     if not image.evaluate("(e)=>e.complete && e.naturalWidth>0"):errors.append("image did not decode")
     caption=fig.locator("figcaption")
     if not caption.is_visible():errors.append("license caption hidden")
     text=caption.inner_text()
     for token in (photo["author"],photo["capture_date"],photo["license"]):
      if token not in text:errors.append("photographer/date/license missing "+token)
     if fig.locator('a[href="'+photo["source"]+'"]').count()!=1:errors.append("original source link missing")
     if fig.locator('a[href="'+photo["license_url"]+'"]').count()!=1:errors.append("CC license link missing")
     if fig.locator(".v144-topic-visual").count()>0:errors.append("infographic nested wrongly")
     if not page.locator(".v144-topic-visual").is_visible():errors.append("informational visual missing")
     r=image.bounding_box()
     if r["width"]<250 or r["height"]<170:errors.append("image too small")
     if not errors:
      name=photo["page"].strip("/").replace("/","_")+f"_{width}.png"
      page.locator(".content-main").screenshot(path=str(out/name),animations="disabled",timeout=45000)
      report["screenshots"].append(name)
    if page.evaluate("document.documentElement.scrollWidth")>width+3:
     errors.append("page horizontal overflow")
   except Exception as e:errors.append("browser "+str(e)[:170])
   report["results"].append({"page":photo["page"],"width":width,"problems":errors})
   report["errors"] += [photo["page"]+" "+str(width)+": "+e for e in errors]
   page.close()
 api.dispose();browser.close()
report["passed"]=not report["errors"] and len(report["results"])==6 and len(report["screenshots"])==6
(out/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps({"passed":report["passed"],"photos":3,"views":len(report["results"]),"screens":len(report["screenshots"]),"errors":report["errors"]},ensure_ascii=False))
raise SystemExit(0 if report["passed"] else 1)
