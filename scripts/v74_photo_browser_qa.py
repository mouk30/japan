#!/usr/bin/env python3
"""V74 real browser QA: four real-photo articles, desktop and mobile."""
import json, os
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE="https://www.nipponferry.com"
SLUGS=["yokohama-red-brick-warehouse","hiroshima-miyajima-ferry-crossing","shodoshima-ferry-island-access","okinawa-shuri-castle"]
OUT=Path("audit-output/v74-photo-browser");OUT.mkdir(parents=True,exist_ok=True)
results=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
    for slug in SLUGS:
        for device,width,height in [("desktop",1440,900),("mobile",390,844)]:
            page=browser.new_page(viewport={"width":width,"height":height},device_scale_factor=1,is_mobile=(device=="mobile"),has_touch=(device=="mobile"))
            url=f"{BASE}/things-to-do/{slug}/"
            record={"slug":slug,"device":device,"url":url}
            try:
                response=page.goto(url,wait_until="domcontentloaded",timeout=45000)
                page.locator("main img").first.wait_for(state="visible",timeout=15000)
                page.wait_for_timeout(700)
                record["http_status"]=response.status if response else None
                record.update(page.evaluate("""() => {
                 const img=document.querySelector('main img');
                 const cap=document.querySelector('.editorial-hero figcaption,#nf-v72-verified-photo');
                 const main=document.querySelector('main');
                 const a=cap?.querySelectorAll('a')||[];
                 const ir=img?.getBoundingClientRect(), cr=cap?.getBoundingClientRect();
                 return {
                   title:document.title,
                   img_src:img?.getAttribute('src'), natural_width:img?.naturalWidth,natural_height:img?.naturalHeight,
                   img_box:ir?{x:ir.x,y:ir.y,width:ir.width,height:ir.height}:null,
                   caption_present:!!cap,caption_box:cr?{x:cr.x,width:cr.width}:null,
                   link_count:a.length,links:[...a].map(x=>({href:x.href,width:x.getBoundingClientRect().width,left:x.getBoundingClientRect().left,right:x.getBoundingClientRect().right})),
                   horizontal_overflow:document.documentElement.scrollWidth>innerWidth+2,
                   image_fits_viewport:!!ir && ir.left>=-2 && ir.right<=innerWidth+2,
                   caption_fits_viewport:!cr || (cr.left>=-2&&cr.right<=innerWidth+2),
                   content_max_width:main?.getBoundingClientRect().width
                 };
                }"""))
                record["pass"]=record["http_status"]==200 and record["natural_width"]>500 and record["image_fits_viewport"] and record["caption_present"] and record["caption_fits_viewport"] and record["link_count"]>=2 and not record["horizontal_overflow"]
                page.screenshot(path=str(OUT/f"{slug}-{device}.png"),full_page=True)
            except Exception as e:
                record["pass"]=False;record["error"]=str(e)
                try:page.screenshot(path=str(OUT/f"{slug}-{device}-error.png"),full_page=True)
                except:pass
            finally:
                print(json.dumps(record,ensure_ascii=False),flush=True)
                results.append(record);page.close()
    browser.close()
(OUT/"report.json").write_text(json.dumps({"passed":sum(x["pass"] for x in results),"total":len(results),"results":results},ensure_ascii=False,indent=2))
if not all(x["pass"] for x in results):raise SystemExit("V74 browser QA failure")
