import asyncio,json,pathlib,re,urllib.parse,collections,datetime
from playwright.async_api import async_playwright
BASE="https://www.nipponferry.com"
OUT=pathlib.Path("audit-reports/tokyo-final-live-qa");OUT.mkdir(parents=True,exist_ok=True)
home=pathlib.Path("site/japan/tokyo/index.html").read_text()
slugs=re.findall(r'<a\s+class="tky-card"[^>]*href="/japan/tokyo/([^/]+)/"',home)
assert len(slugs)==220
sema=asyncio.Semaphore(7)
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(args=["--no-sandbox"])
  context=await browser.new_context(viewport={"width":390,"height":844},device_scale_factor=1)
  results=[None]*len(slugs)
  async def check(i,slug):
   async with sema:
    page=await context.new_page()
    errs=[]
    page.on("pageerror",lambda e:errs.append(str(e)[:180]))
    status=None;data={}
    try:
     resp=await page.goto(BASE+"/japan/tokyo/"+slug+"/",wait_until="domcontentloaded",timeout=45000)
     status=resp.status if resp else None
     await page.locator("figure.tokyo-article-photo-v1 img").first.wait_for(timeout=12000)
     data=await page.evaluate("""async () => {
       const imgs=[...document.querySelectorAll('figure.tokyo-article-photo-v1 img')];
       await Promise.all(imgs.map(i=>{i.loading='eager';return i.complete?null:new Promise(r=>{i.addEventListener('load',r,{once:true});i.addEventListener('error',r,{once:true});setTimeout(r,9000)})}));
       const links=[...document.querySelectorAll('a[href^="https://"]')].map(a=>a.href);
       return {title:document.title,h1:!!document.querySelector('h1'),hero_count:imgs.length,hero_broken:imgs.some(i=>!i.complete||i.naturalWidth===0),hero_src:imgs[0]?.getAttribute('src'),horizontal_overflow:document.documentElement.scrollWidth>innerWidth+2,jsonld_count:document.querySelectorAll('script[type="application/ld+json"]').length,official_links:links.filter(x=>!x.includes('nipponferry.com')).slice(0,12),canonical:document.querySelector('link[rel="canonical"]')?.href}
     }""")
     if i in [0,21,41,80,100,119,140,160,180,199,200,219]:
      await page.screenshot(path=str(OUT/("mobile-"+str(i+1)+".png")),full_page=False)
    except Exception as e:errs.append(str(e)[:250])
    finally:await page.close()
    results[i]={"v":i+1,"slug":slug,"http":status,**data,"errors":errs}
  await asyncio.gather(*(check(i,s) for i,s in enumerate(slugs)))
  await context.close()
  desktop=await browser.new_context(viewport={"width":1440,"height":900})
  checks={}
  for i in [0,40,100,160,200,219]:
   pg=await desktop.new_page()
   try:
    resp=await pg.goto(BASE+"/japan/tokyo/"+slugs[i]+"/",wait_until="domcontentloaded",timeout=45000)
    checks[str(i+1)]={"status":resp.status if resp else None,"overflow":await pg.evaluate("document.documentElement.scrollWidth>innerWidth+2")}
    await pg.screenshot(path=str(OUT/("desktop-"+str(i+1)+".png")),full_page=False)
   except Exception as e:checks[str(i+1)]={"error":str(e)[:200]}
   finally:await pg.close()
  await desktop.close()
  await browser.close()
  issues=[{"v":x["v"],"slug":x["slug"],"status":x.get("http"),"errors":x.get("errors"),"broken":x.get("hero_broken"),"overflow":x.get("horizontal_overflow"),"hero_count":x.get("hero_count")} for x in results if x.get("http")!=200 or x.get("errors") or x.get("hero_broken") or x.get("horizontal_overflow") or x.get("hero_count")!=1]
  links=sorted({u for x in results for u in x.get("official_links",[])})
  report={"checked":len(results),"http_200":sum(x.get("http")==200 for x in results),"hero_broken":sum(bool(x.get("hero_broken")) for x in results),"mobile_horizontal_overflow":sum(bool(x.get("horizontal_overflow")) for x in results),"issues":issues,"desktop_samples":checks,"external_links_discovered":len(links),"external_links":links,"entries":results,"notes":"Actual live website checked in Playwright Chromium at 390px for all 220 pages; 1440px desktop sampled on 6 pages. Photo semantic correctness and link content not established by browser loading."}
  (OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
  print(json.dumps({k:v for k,v in report.items() if k not in ("entries","issues","external_links")},ensure_ascii=False))
asyncio.run(main())
