#!/usr/bin/env python3
"""V83 live Chromium desktop/mobile + photo + 45-guide filters/anchor + parent travel info audit."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE="https://www.nipponferry.com"
URL=BASE+"/things-to-do/travel-companions/"
CASES=[
 ("parents","fukuoka-ohori-park.webp","오호리공원"),
 ("family","yokohama-cupnoodles-museum.webp","컵누들"),
 ("couple","kobe-nunobiki-herb-ropeway.webp","누노비키")
]
OUT=Path("audit-output/v83-companions");OUT.mkdir(parents=True,exist_ok=True)
for mode,img,scene in CASES:
    assert (Path("site/images/venues")/img).is_file(), img
assert Path("site/nf-v83-companions-wide.css").is_file()
checks=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
    for device,width,height in [("desktop",1440,900),("mobile",390,844)]:
        page=browser.new_page(viewport={"width":width,"height":height},is_mobile=device=="mobile",has_touch=device=="mobile",device_scale_factor=1)
        record={"device":device,"viewport":width}
        try:
            resp=page.goto(URL,wait_until="domcontentloaded",timeout=50000)
            root=page.locator("#nf-v83-companions")
            root.wait_for(state="visible",timeout=14000)
            cards=root.locator(".nf83-card")
            for i in range(3):
                card=cards.nth(i)
                card.scroll_into_view_if_needed(timeout=15000)
                img=card.locator("img").first
                img.evaluate("(el)=>{el.loading='eager'}")
                img.evaluate("(el)=>el.decode()")
                card.screenshot(path=str(OUT/f"{device}-card-{i+1}.png"),timeout=20000)
            record.update(page.evaluate("""() => {
              const root=document.querySelector('#nf-v83-companions'),vw=document.documentElement.clientWidth;
              return {
                css:[...document.styleSheets].some(x=>(x.href||'').includes('nf-v83-companions-wide.css')),
                overflow:document.documentElement.scrollWidth>vw+2,
                canonical:document.querySelector('link[rel=canonical]')?.href,
                existingGuides:document.querySelectorAll('.guide-section .guide-card').length,
                guideSections:[...document.querySelectorAll('.guide-section')].map(x=>({id:x.id,count:x.querySelectorAll('.guide-card').length})),
                cards:[...root.querySelectorAll('.nf83-card')].map(c=>{
                  const img=c.querySelector('img'),r=c.getBoundingClientRect(),photo=c.querySelector('.nf83-photo').getBoundingClientRect(),
                    h=c.querySelector('h3'),a=c.querySelector('.nf83-action');
                  return {img:img?.getAttribute('src'),naturalW:img?.naturalWidth,naturalH:img?.naturalHeight,alt:img?.alt,
                    href:a?.getAttribute('href'),cardWidth:r.width,cardLeft:r.left,cardRight:r.right,
                    fits:r.left>=-2&&r.right<=vw+2,photoW:photo.width,photoH:photo.height,
                    buttonH:a?.getBoundingClientRect().height,titlePx:parseFloat(getComputedStyle(h).fontSize),
                    caption:c.querySelector('.nf83-credit')?.innerText,
                    links:[...c.querySelectorAll('.nf83-credit a')].map(x=>x.href),
                    scene:c.querySelector('.nf83-scene')?.innerText,
                    parentFactCount:c.querySelectorAll('.nf83-parents-facts>div').length,
                  };
                })
              };
            }"""))
            record["status"]=resp.status if resp else None
            record["pass"]=(record["status"]==200 and record["css"] and
                record["canonical"]==URL and not record["overflow"] and record["existingGuides"]==45 and
                len(record["cards"])==3 and all(sec["count"]==15 for sec in record["guideSections"]) and
                all(c["img"]=="/images/venues/"+filename and c["href"]=="#"+mode and scene in c["scene"] and
                    c["naturalW"]>=450 and c["naturalH"]>=300 and c["fits"] and c["photoW"]>=300 and
                    c["photoH"]>=200 and c["buttonH"]>=48 and c["titlePx"]>=28 and
                    len(c["links"])==2 and "WebP" in c["caption"]
                    for c,(mode,filename,scene) in zip(record["cards"],CASES)) and
                record["cards"][0]["parentFactCount"]==3)
            # Clicking a big card selects the matching 15-guide section; existing filtering must still work.
            record["filterChecks"]=[]
            for mode,_,_ in CASES:
                page.locator(f'#nf-v83-companions .nf83-card .nf83-action[href="#{mode}"]').click()
                page.wait_for_timeout(250)
                active=page.evaluate("""() => [...document.querySelectorAll('.guide-section')].filter(s=>!s.hidden).map(x=>x.id)""")
                record["filterChecks"].append({"clicked":mode,"visible":active,"ok":active==[mode]})
            record["pass"]=record["pass"] and all(x["ok"] for x in record["filterChecks"])
            # Inspect existing 15 parent article cards, not only the three entrance cards.
            page.locator('#nf-v83-companions .nf83-action[href="#parents"]').click()
            guide=page.locator('#parents .guide-card').first
            guide.scroll_into_view_if_needed(timeout=15000)
            guide.locator('img').first.evaluate("(el)=>{el.loading='eager';}")
            guide.locator('img').first.evaluate("(el)=>el.decode()")
            guide.screenshot(path=str(OUT/f"{device}-existing-parent-guide.png"),timeout=15000)
            record["existingCard"]=page.evaluate("""() => {
                const cs=[...document.querySelectorAll('#parents .guide-card')];
                const a=cs[0],b=cs[1],img=a.querySelector('img');
                const r=a.getBoundingClientRect(),s=b.getBoundingClientRect();
                return {width:r.width,secondLeft:s.left,firstLeft:r.left,secondTop:s.top,firstTop:r.top,
                  titlePx:parseFloat(getComputedStyle(a.querySelector('h3')).fontSize),
                  detailPx:parseFloat(getComputedStyle(a.querySelector('p')).fontSize),
                  photoWidth:img.getBoundingClientRect().width,
                  imgLoaded:img.naturalWidth>200,
                  mobileStacked:s.top>r.top+50};
            }""")
            record["pass"]=record["pass"] and record["existingCard"]["titlePx"]>=25 and record["existingCard"]["detailPx"]>=16 and record["existingCard"]["imgLoaded"] and (record["existingCard"]["mobileStacked"] if device=="mobile" else True)
            page.locator("#nf-v83-companions").screenshot(path=str(OUT/f"{device}-section.png"),timeout=30000)
        except Exception as e:
            record["pass"]=False;record["error"]=str(e)[:750]
        print(json.dumps(record,ensure_ascii=False),flush=True)
        checks.append(record);page.close()
    browser.close()
(OUT/"report.json").write_text(json.dumps({"total":2,"passed":sum(bool(x["pass"]) for x in checks),"checks":checks},ensure_ascii=False,indent=2),encoding="utf-8")
if not all(x["pass"] for x in checks):raise SystemExit("V83 companions QA failed")
