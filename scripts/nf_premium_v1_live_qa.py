import asyncio,json,pathlib
from playwright.async_api import async_playwright
URL="https://www.nipponferry.com/"
OUT=pathlib.Path("audit-reports/nf-premium-v1");OUT.mkdir(parents=True,exist_ok=True)
async def main():
 results={}
 async with async_playwright() as p:
  browser=await p.chromium.launch(args=["--no-sandbox"])
  for w in [390,768,1440]:
   page=await browser.new_page(viewport={"width":w,"height":900},device_scale_factor=1)
   errors=[];page.on("pageerror",lambda e:errors.append(str(e)))
   r=await page.goto(URL,wait_until="domcontentloaded",timeout=90000)
   await page.locator(".nf-maritime-card").first.wait_for(timeout=25000)
   d=await page.evaluate("""() => ({canonical:document.querySelector('link[rel="canonical"]')?.href,title:document.title,meta:document.querySelector('meta[name="description"]')?.content,hasJsonld:!!document.querySelector('script[type="application/ld+json"]'),hasCruise:!!document.querySelector('.nf-cruise-card'),hasFerry:!!document.querySelector('.nf-ferry-card'),hero:!!document.querySelector('.nf-premium-hero'),cssLoaded:[...document.styleSheets].some(x=>x.href?.includes('nf-premium-v1.css')),overflow:document.documentElement.scrollWidth>innerWidth+2,maritimeLinks:[...document.querySelectorAll('.nf-maritime-card')].map(a=>a.getAttribute('href'))})""")
   d.update({"status":r.status if r else None,"errors":errors})
   await page.screenshot(path=str(OUT/("homepage-"+str(w)+".png")),full_page=False)
   results[str(w)]=d
   await page.close()
  await browser.close()
 report={"page":URL,"widths":results,"notes":"Homepage live browser structural and screenshot smoke test, not exhaustive visual design audit."}
 (OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
 assert all(x["status"]==200 and x["hasCruise"] and x["hasFerry"] and x["hasJsonld"] and x["cssLoaded"] and not x["overflow"] for x in results.values()),report
 print(json.dumps(results,ensure_ascii=False))
asyncio.run(main())
