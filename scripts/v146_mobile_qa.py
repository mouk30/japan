#!/usr/bin/env python3
"""V146 responsive browser smoke test (real Chromium, 320/390/768/1440)."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
SLUGS=("naoshima-art-ferry-return","teshima-art-ferry-return")
WIDTHS=(320,390,768,1440)
OUT=Path("audit-output/v146/mobile")
OUT.mkdir(parents=True,exist_ok=True)
results=[]
with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
  for slug in SLUGS:
    for width in WIDTHS:
      page=browser.new_page(viewport={"width":width,"height":850},device_scale_factor=1)
      url=f"http://127.0.0.1:8800/things-to-do/{slug}/"
      response=page.goto(url,wait_until="load",timeout=30000)
      page.locator(".v146-hero img").scroll_into_view_if_needed()
      report=page.evaluate("""() => {
        const img=document.querySelector('.v146-hero img');
        const box=img?.getBoundingClientRect();
        return { title:document.title, h1:document.querySelectorAll('h1').length,
          canonical:document.querySelector('link[rel=canonical]')?.href,
          imageSrc:img?.getAttribute('src'),
          imageLoaded:!!img&&img.complete&&img.naturalWidth===1200&&img.naturalHeight===900,
          imageAlt:img?.getAttribute('alt')?.length||0,
          imageAspect:box?(box.width/box.height):0,
          scrollWidth:document.documentElement.scrollWidth,
          windowWidth:window.innerWidth,
          jsonld:document.querySelectorAll('script[type="application/ld+json"]').length,
          checklist:!!document.getElementById('checklist'),
          officialLinks:[...document.querySelectorAll('#official a[href]')].length,
          brokenLocal:[...document.querySelectorAll('a[href^="/"]')].filter(a=>!a.getAttribute('href')).length
        };
      }""")
      ok=(response is not None and response.status==200 and report["h1"]==1
          and report["imageLoaded"] and report["imageAlt"]>20
          and abs(report["imageAspect"]-4/3)<.035
          and report["scrollWidth"]<=report["windowWidth"]+2
          and report["checklist"] and report["officialLinks"]>=5 and report["jsonld"]==1)
      shot=OUT/f"{slug}-{width}.png"
      page.screenshot(path=str(shot),full_page=True,animations="disabled")
      results.append(dict(slug=slug,width=width,pass_=ok,screenshot=str(shot),**report))
      print("PASS" if ok else "FAIL",slug,width,report)
      page.close()
  browser.close()
p=Path("audit-output/v146/mobile-results.json")
p.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8")
if not all(row["pass_"] for row in results):raise SystemExit("V146 mobile browser QA failed")
