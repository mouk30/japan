import asyncio,json,pathlib,re
from playwright.async_api import async_playwright
URL="https://www.nipponferry.com/japan/tokyo/"
OUT=pathlib.Path("audit-reports/tokyo-mobile-ui");OUT.mkdir(parents=True,exist_ok=True)
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch()
  findings={}
  for width in [375,390,768,1440]:
   page=await browser.new_page(viewport={"width":width,"height":844},device_scale_factor=1)
   failures=[]
   page.on("pageerror",lambda err:failures.append(str(err)))
   await page.goto(URL,wait_until="domcontentloaded",timeout=90000)
   try:await page.wait_for_selector(".tky-card-photo img",timeout=25000)
   except Exception:pass
   await page.evaluate("""async () => {
      for (const img of document.querySelectorAll('.tky-card-photo img')) {
        img.loading='eager';
      }
      await Promise.all([...document.querySelectorAll('.tky-card-photo img')].map(img => img.complete?Promise.resolve():new Promise(resolve=>{img.onload=resolve;img.onerror=resolve;setTimeout(resolve,10000)})));
    }""")
   result=await page.evaluate("""() => {
      const cards=[...document.querySelectorAll('.tky-card')];
      const out={cards:cards.length,svg:0,broken:[],aspectErrors:[],hiddenCredits:[],horizontalOverflow:document.documentElement.scrollWidth>innerWidth+2};
      cards.forEach((card,i)=>{
        const img=card.querySelector('.tky-card-photo img');
        if (!img){out.broken.push(i+1);return;}
        if (/\.svg(?:\?|$)/.test(img.currentSrc||img.src))out.svg++;
        if (!img.naturalWidth||!img.naturalHeight)out.broken.push(i+1);
        const b=img.getBoundingClientRect();
        if (Math.abs(b.width/b.height-16/9)>.15)out.aspectErrors.push({v:i+1,ratio:Math.round(b.width/b.height*100)/100});
        const label=card.querySelector('.tky-photo-label');
        if(label){const r=label.getBoundingClientRect(),cr=card.getBoundingClientRect();if(r.bottom>cr.bottom+2||r.height===0)out.hiddenCredits.push(i+1);}
      });
      return out;
    }""")
   result["pageErrors"]=failures
   findings[str(width)]=result
   await page.screenshot(path=str(OUT/f"tokyo-{width}.png"),full_page=True,timeout=120000)
   await page.close()
  await browser.close()
  (OUT/"report.json").write_text(json.dumps(findings,ensure_ascii=False,indent=2),encoding="utf8")
  print(json.dumps(findings,ensure_ascii=False))
asyncio.run(main())
