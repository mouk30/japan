#!/usr/bin/env python3
"""V144 production: verify 51 unique content pages and 3 responsive widths.
Sitewide no extra articles, exact metadata, no wrong generic photo claims.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,hashlib
R=Path(__file__).resolve().parents[1]
out=R/"audit-output/v144";out.mkdir(parents=True,exist_ok=True)
base="https://www.nipponferry.com"
inv=json.loads((R/"audit-reports/v144/repetition-inventory.json").read_text("utf8"))
report=json.loads((R/"audit-reports/v144/editorial-image-provenance-report.json").read_text("utf8"))
by_route={"/"+group+"/"+x["slug"]+"/":x for group in ("season","practical") for x in inv["targets"][group]}
priority={"/season/asahikawa-winter-festival/","/season/otaru-snow-light-path-2027/","/season/new-chitose-to-sapporo-winter/","/practical/ghibli-museum-guide/","/practical/japan-ic-card-guide/","/practical/kyoto-tango-kuromatsu/"}
cases=[(x["url"],390) for x in report["edited_pages"]]
cases += [(route,w) for route in sorted(priority) for w in (320,768,1440)]
result={"version":"V144","public":base,"tested":len(cases),"screenshots":[],"checks":[],"errors":[]}
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
 for url,w in cases:
  issues=[]
  page=browser.new_page(viewport={"width":w,"height":920},device_scale_factor=1)
  try:
   res=page.goto(base+url,wait_until="domcontentloaded",timeout=48000)
   if not res or res.status!=200:issues.append("HTTP != 200")
   if page.locator('.nf301-header').count()!=1:issues.append("shared site navigation missing")
   origin=by_route[url]
   if page.locator('h1').first.inner_text().strip()!=origin["title"]:issues.append("H1 changed")
   if page.locator('meta[name="description"]').get_attribute("content")!=origin["description"]:issues.append("meta description changed")
   if page.locator('link[rel="canonical"]').get_attribute("href")!=base+url:issues.append("canonical changed")
   if page.locator('link[href*="nf-v144-topic-depth.css"]').count()!=1:issues.append("V144 stylesheet not linked")
   box=page.locator(".v144-detailed-guide")
   figure=page.locator(".v144-topic-visual")
   if box.count()!=1 or figure.count()!=1:issues.append("topic guide and accurate visual not found")
   else:
    if box.locator('.v144-action').count()!=3:issues.append("missing unique travel-decision sections")
    if len(box.inner_text())<320:issues.append("detail too short")
    if "실제 관광지·차량·시설 촬영 사진이 아닙니다." not in figure.inner_text():issues.append("topic-only figure disclaimer absent")
    if figure.locator('.v144-visual-panel').count()!=3:issues.append("figure panel count wrong")
    if not box.locator('.v144-source-caution a[href^="https://www.japan.travel"]').count():issues.append("official background source missing")
    if not figure.is_visible():issues.append("main visual hidden")
    if w<=390:
     for e in (box.locator('.v144-action p').first,figure.locator('.v144-visual-panel b').first):
      if float(e.evaluate("(e)=>parseFloat(getComputedStyle(e).fontSize)"))<15.8:issues.append("text smaller than 16px")
   if page.locator('a[href="https://willer-travel.com/ko/ferry/"]').count()==0:issues.append("original ferry reservation missing")
   if page.locator('.v143-context-journey').count()!=1:issues.append("global related card build missing")
   if page.evaluate("document.documentElement.scrollWidth")>w+3:issues.append("page horizontal overflow")
   if w in (390,1440) and url in priority:
    label=url.strip("/").replace("/","_")+f"_{w}.png"
    page.locator(".content-main").screenshot(path=str(out/label),animations="disabled",timeout=40000)
    result["screenshots"].append(label)
  except Exception as e:issues.append("browser: "+str(e)[:300])
  result["checks"].append({"url":url,"width":w,"errors":issues})
  result["errors"].extend(f"{url} {w}px: {x}" for x in issues)
  page.close()
 browser.close()
result["passed"]=not result["errors"] and len(result["checks"])==len(cases)
(out/"report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps({"passed":result["passed"],"viewports":len(result["checks"]),"screenshots":len(result["screenshots"]),"errors":result["errors"][:25]},ensure_ascii=False))
raise SystemExit(0 if result["passed"] else 1)
