import asyncio,json,pathlib,re,collections,time,urllib.parse
from playwright.async_api import async_playwright
ROOT=pathlib.Path("site")
OUT=pathlib.Path("audit-reports/tokyo-live-220");OUT.mkdir(parents=True,exist_ok=True)
HUB="https://www.nipponferry.com/japan/tokyo/"
slugs=re.findall(r'<a\s+class="tky-card"[^>]*href="/japan/tokyo/([^/]+)/"',(ROOT/"japan/tokyo/index.html").read_text())
assert len(slugs)==220,len(slugs)
async def main():
 records=[];external=set();semaphore=asyncio.Semaphore(5)
 async with async_playwright() as p:
  browser=await p.chromium.launch(args=["--no-sandbox"])
  async def test(i,slug):
   async with semaphore:
    page=await browser.new_page(viewport={"width":390,"height":844},device_scale_factor=1)
    response=None;error=None;page_errors=[]
    page.on("pageerror",lambda e:page_errors.append(str(e)[:200]))
    try:
     response=await page.goto(HUB+slug+"/",wait_until="domcontentloaded",timeout=45000)
     await page.wait_for_timeout(450)
     data=await page.evaluate("""() => {
       const imgs=[...document.querySelectorAll('article img,main img')];
       const figures=[...document.querySelectorAll('figure.tokyo-article-photo-v1 img')];
       const links=[...document.querySelectorAll('article a[href],main a[href]')].map(a=>a.href);
       const bad=imgs.filter(x=>!x.complete||(x.complete&&x.naturalWidth===0)).map(x=>x.getAttribute('src'));
       const titles=[...document.querySelectorAll('h1')].map(x=>x.textContent.trim());
       return {title:document.title,h1:titles,images:imgs.length,brokenImages:bad,heroImages:figures.length,
        missingAlt:imgs.filter(x=>!x.getAttribute('alt')?.trim()).length,
        overflow:document.documentElement.scrollWidth>window.innerWidth+3,
        canonical:document.querySelector('link[rel=canonical]')?.href||'',
        metaDescription:document.querySelector('meta[name=description]')?.content||'',
        external:links.filter(x=>/^https?:/.test(x)&&new URL(x).hostname!==location.hostname)};
      }""")
     for u in data.pop("external"):external.add(u)
     data.update({"v":i,"slug":slug,"http":response.status if response else None,"pageErrors":page_errors})
     if i in [1,20,40,60,80,100,120,140,160,180,200,213,220]:
      await page.screenshot(path=str(OUT/f"mobile-v{i:03}.png"),full_page=True,timeout=45000)
     records.append(data)
    except Exception as e:records.append({"v":i,"slug":slug,"http":response.status if response else None,"loadError":str(e)[:300]})
    finally:await page.close()
  await asyncio.gather(*(test(i,s) for i,s in enumerate(slugs,1)))
  desktops={}
  for i in [1,22,41,81,110,120,141,161,181,201,220]:
   page=await browser.new_page(viewport={"width":1440,"height":900})
   try:
    res=await page.goto(HUB+slugs[i-1]+"/",wait_until="domcontentloaded",timeout=45000)
    desktops[str(i)]={"http":res.status if res else None,"overflow":await page.evaluate("document.documentElement.scrollWidth>window.innerWidth+3")}
    await page.screenshot(path=str(OUT/f"desktop-v{i:03}.png"),full_page=True,timeout=45000)
   except Exception as e:desktops[str(i)]={"error":str(e)[:230]}
   finally:await page.close()
  await browser.close()
 records.sort(key=lambda x:x["v"])
 summary={"checked":len(records),"ok_http":sum(1 for r in records if r.get("http")==200),"non_200":[{"v":r["v"],"status":r.get("http"),"error":r.get("loadError")} for r in records if r.get("http")!=200],
 "broken_image_pages":[{"v":r["v"],"items":r.get("brokenImages")} for r in records if r.get("brokenImages")],
 "missing_hero":[r["v"] for r in records if r.get("heroImages")==0],"overflow_pages":[r["v"] for r in records if r.get("overflow")],
 "pageerror_pages":[{"v":r["v"],"errors":r.get("pageErrors")} for r in records if r.get("pageErrors")],
 "missing_alt_pages":[{"v":r["v"],"count":r.get("missingAlt")} for r in records if r.get("missingAlt",0)>0],
 "unique_external_links":len(external),"desktop":desktops,"disclaimer":"Playwright DOM/loading QA. Screenshot samples not human visual inspection; HTTP status not external link validation. Some lazy images may not load until scrolled."}
 (OUT/"report.json").write_text(json.dumps({"summary":summary,"pages":records,"external_urls":sorted(external)},ensure_ascii=False,indent=2))
 print(json.dumps(summary,ensure_ascii=False))
asyncio.run(main())
