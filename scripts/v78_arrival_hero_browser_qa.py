#!/usr/bin/env python3
"""Verify uploaded arrival image, public hero composition and readable CTA at PC/mobile."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ASSET=Path("site/images/nipponferry-hero-cruise-arrival.webp")
if not ASSET.exists() or ASSET.stat().st_size < 20000:
    raise SystemExit("Required cruise-arrival image missing or too small. Upload WebP before claiming deployment.")
OUT=Path("audit-output/v78-arrival-hero");OUT.mkdir(parents=True,exist_ok=True)
checks=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
    for device,width,height in [("desktop",1440,900),("mobile",390,844)]:
        page=browser.new_page(viewport={"width":width,"height":height},is_mobile=device=="mobile",has_touch=device=="mobile",device_scale_factor=1)
        row={"device":device}
        try:
            response=page.goto("https://www.nipponferry.com/",wait_until="domcontentloaded",timeout=45000)
            page.locator(".nf-premium-hero").wait_for(state="visible",timeout=12000)
            row.update(page.evaluate("""() => {
              let h=document.querySelector('.nf-premium-hero'), r=h.getBoundingClientRect();
              let css=getComputedStyle(h), links=[...h.querySelectorAll('.nf-hero-actions a')];
              return {hero_background:css.backgroundImage,heading:!!h.querySelector('h1')?.innerText.trim(),
                hero_width:r.width,viewport_width:innerWidth,horizontal_overflow:document.documentElement.scrollWidth>innerWidth+2,
                ctas:links.map(a=>({label:a.innerText.trim(),width:a.getBoundingClientRect().width,height:a.getBoundingClientRect().height})),
                css_loaded:css.backgroundImage.includes('nipponferry-hero-cruise-arrival.webp')};
            }"""))
            img=page.request.get("https://www.nipponferry.com/images/nipponferry-hero-cruise-arrival.webp",timeout=20000)
            row["image_status"]=img.status
            row["image_type"]=img.headers.get("content-type","")
            row["status"]=response.status if response else None
            row["pass"]=row["status"]==200 and row["image_status"]==200 and "image" in row["image_type"] and row["css_loaded"] and row["heading"] and not row["horizontal_overflow"] and all(x["height"]>=44 for x in row["ctas"])
            page.screenshot(path=str(OUT/(device+".png")),full_page=False)
        except Exception as e:
            row["pass"]=False;row["error"]=str(e)[:400]
        print(json.dumps(row,ensure_ascii=False),flush=True);checks.append(row)
        page.close()
    browser.close()
(OUT/"report.json").write_text(json.dumps({"passed":sum(x["pass"] for x in checks),"total":2,"checks":checks},ensure_ascii=False,indent=2))
if not all(x["pass"] for x in checks):raise SystemExit("V78 hero QA failed: published image or display needs review")
