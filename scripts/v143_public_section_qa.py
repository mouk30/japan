#!/usr/bin/env python3
"""V143 production QA: 15 existing guides, actual photo/infographic, links and mobile."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"audit-output/v143";OUT.mkdir(parents=True,exist_ok=True)
r=json.loads((ROOT/"audit-reports/v143/sitewide-content-and-image-audit.json").read_text("utf8"))
BASE=os.environ.get("NF_V143_BASE","https://www.nipponferry.com").rstrip("/")
cases=[(x['page'],w) for x in r["modified_pages"] for w in [390,1440]]
cases+= [(x,w) for x in ['/season/sapporo-snow-festival-2027/','/practical/japan-esim-vs-sim-wifi/','/practical/japan-data-usage/'] for w in [320,768]]
report={"version":"V143","base":BASE,"tested_routes":len(r["modified_pages"]),"cases":len(cases),"checks":[],"errors":[],"screenshots":[]}
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
 for route,width in cases:
  p=browser.new_page(viewport={"width":width,"height":900},device_scale_factor=1)
  issue=[];kind='season' if '/season/' in route else 'practical'
  try:
   res=p.goto(BASE+route,wait_until="domcontentloaded",timeout=60000)
   if res.status!=200:issue.append(f"HTTP {res.status}")
   if p.locator("h1").count()!=1:issue.append("not one H1")
   if p.locator("link[rel=canonical]").get_attribute("href")!=BASE+route:issue.append("canonical changed")
   if p.locator('link[href*="nf-v143-topic-guides.css"]').count()!=1:issue.append("CSS missing")
   if p.locator('.nf301-header').count()!=1:issue.append("navigation header missing")
   body=p.locator('.v143-topic')
   if body.count()!=1:issue.append("specialized topic content missing")
   if body.locator(".v143-guide-step").count()<4:issue.append("missing detailed steps")
   guide_text=body.inner_text() if body.count() else ""
   if len(guide_text)<520:issue.append("article text still thin")
   if body.locator(".v143-verified-links a").count()<1:issue.append("official reference missing")
   if p.locator(".v143-next a").count()<2:issue.append("next-step links missing")
   if kind=='season':
    fig=p.locator("figure.v143-snow-photo")
    if fig.count()!=1:issue.append("verified actual festival photo missing")
    else:
     im=fig.locator("img")
     im.scroll_into_view_if_needed()
     if not im.evaluate("(e)=>e.complete&&e.naturalWidth>0"):issue.append("image decode failed")
     if not fig.locator("figcaption").is_visible():issue.append("source caption hidden")
     if "2014" not in fig.locator("figcaption").inner_text():issue.append("original photo year absent")
     if fig.locator('a[href*="commons.wikimedia.org"]').count()!=1:issue.append("Wikimedia author/source missing")
   else:
    fig=p.locator("figure.v143-explainer")
    if fig.count()!=1:issue.append("page-specific information diagram missing")
    elif not fig.is_visible():issue.append("diagram hidden")
    else:
     cols=fig.locator(".v143-visual-cols>div")
     if cols.count()!=3:issue.append("visual has missing comparison elements")
     if "자체 제작" not in fig.locator("figcaption").inner_text():issue.append("diagram type not disclosed")
   p.locator(".v143-topic").scroll_into_view_if_needed()
   box=body.bounding_box() if body.count() else None
   if box and box["width"]<width*.42:issue.append("body too narrow")
   scroll=p.evaluate("document.documentElement.scrollWidth")
   if scroll>width+4:issue.append(f"horizontal overflow {scroll} vs {width}")
   if route in ['/season/sapporo-snow-festival-2027/','/practical/japan-esim-vs-sim-wifi/','/practical/japan-data-usage/'] and width in (390,1440):
    name=route.strip('/').replace('/','-')+f"-{width}.png"
    p.locator(".content-main").screenshot(path=str(OUT/name),animations="disabled",timeout=45000)
    report["screenshots"].append(name)
  except Exception as e:issue.append("browser: "+str(e)[:230])
  report["checks"].append({"path":route,"viewport":width,"issues":issue})
  report["errors"].extend(f"{route} at {width}px: {e}" for e in issue)
  p.close()
 browser.close()
# Independently verify that published WebP is byte-identical to verified source derivative.
with sync_playwright() as pw:
 request=pw.request.new_context()
 uri=BASE+r["image_original"]["local_path"]
 resp=request.get(uri,timeout=60000)
 if resp.status!=200:report["errors"].append("verified photo public HTTP "+str(resp.status))
 elif hashlib.sha256(resp.body()).hexdigest()!=r["image_original"]["sha256"]:
  report["errors"].append("published photo SHA-256 differs from stored verified original")
 request.dispose()
report["passed"]=not report["errors"] and len(report["checks"])==len(cases)
(OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps({"passed":report["passed"],"views":len(report["checks"]),"screenshots":len(report["screenshots"]),"errors":report["errors"]},ensure_ascii=False))
raise SystemExit(0 if report["passed"] else 1)
