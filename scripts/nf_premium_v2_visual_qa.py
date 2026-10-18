import asyncio,json,pathlib
from playwright.async_api import async_playwright
BASE="http://127.0.0.1:8765"
OUT=pathlib.Path("audit-reports/nf-premium-v2")
OUT.mkdir(parents=True,exist_ok=True)
PAGES={
 "home":"/",
 "cruise_ports":"/things-to-do/cruise-ports/",
 "tokyo_hub":"/japan/tokyo/",
 "tokyo_article":"/japan/tokyo/tokyo-ramen-best-areas/",
 "destination_hub":"/japan/",
 "things_to_do":"/things-to-do/",
 "booking_hub":"/booking/japan-cruise/",
 "cruise_article":"/things-to-do/aomori-cruise-port-day-trip/"
}
async def main():
 reports=[]
 async with async_playwright() as p:
  browser=await p.chromium.launch(args=["--no-sandbox"])
  for w in [390,768,1440]:
   context=await browser.new_context(viewport={"width":w,"height":870},device_scale_factor=1)
   for name,url in PAGES.items():
    page=await context.new_page()
    errs=[]
    page.on("pageerror",lambda e:errs.append(str(e)[:150]))
    data={"name":name,"url":url,"width":w}
    try:
     resp=await page.goto(BASE+url,wait_until="domcontentloaded",timeout=40000)
     await page.wait_for_timeout(180)
     d=await page.evaluate("""() => ({
      title:document.title,canonical:document.querySelector('link[rel="canonical"]')?.href,
      jsonld:document.querySelectorAll('script[type="application/ld+json"]').length,
      header:!!document.querySelector('.site-header'),
      premium:document.body.classList.contains('nf-premium-v2'),
      css:!!document.querySelector('link[href*="nf-premium-v2.css"]'),
      brand:document.querySelector('.site-header .brand strong')?.textContent?.trim(),
      navigation:[...document.querySelectorAll('.desktop-nav a')].length,
      logo:!!document.querySelector('.nf-brand-mark'),
      overflow:document.documentElement.scrollWidth>window.innerWidth+3,
      cta:!!document.querySelector('.nf-v2-cta'),
      headerHeight:Math.round(document.querySelector('.site-header')?.getBoundingClientRect().height||0),
      menuVisible:getComputedStyle(document.querySelector('.menu-toggle')).display!=='none'
     })""")
     data.update(d)
     data["status"]=resp.status if resp else None
     if w==390 and data.get("menuVisible"):
      await page.locator(".site-header .menu-toggle").click()
      data["mobileOpen"]=await page.locator(".site-header .mobile-menu").evaluate("(x)=>x.classList.contains('open')")
      data["expanded"]=await page.locator(".site-header .menu-toggle").get_attribute("aria-expanded")
      await page.keyboard.press("Escape")
      data["escapeClosed"]=not await page.locator(".site-header .mobile-menu").evaluate("(x)=>x.classList.contains('open')")
     if name in ("home","cruise_ports","tokyo_hub","tokyo_article","booking_hub") and w in (390,1440):
      await page.screenshot(path=str(OUT/f"{name}-{w}.png"),full_page=False)
    except Exception as e:data["exception"]=str(e)[:230]
    data["errors"]=errs
    reports.append(data)
    await page.close()
   await context.close()
  await browser.close()
 failures=[]
 for r in reports:
  if r.get("status")!=200 or not r.get("premium") or not r.get("css") or r.get("brand")!="NIPPONFERRY" or r.get("navigation")!=8 or r.get("overflow") or r.get("exception"):
   failures.append({k:r.get(k) for k in ("name","width","status","premium","css","brand","navigation","overflow","exception")})
  if r.get("width")==390 and r.get("menuVisible") and (not r.get("mobileOpen") or not r.get("escapeClosed") or r.get("expanded")!="true"):
   failures.append({"mobileMenu":r["name"],"open":r.get("mobileOpen"),"escape":r.get("escapeClosed"),"aria":r.get("expanded")})
 summary={"pages":len(PAGES),"viewports":[390,768,1440],"checks":len(reports),"failures":failures,"reports":reports,"note":"Static site rendered in real Chromium from exact post-migration files; live deployed site needs separate monitoring."}
 (OUT/"visual-qa.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2))
 print(json.dumps({"checks":len(reports),"failures":failures},ensure_ascii=False))
 assert not failures,"Premium V2 QA failed"
asyncio.run(main())
