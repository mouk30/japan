#!/usr/bin/env python3
"""V80: browser-check five source-attributed cruise hub cards, PC and mobile."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE="https://www.nipponferry.com"
HUB="/things-to-do/cruise-ports/"
DATA=[
 ("naha-cruise-terminal-kokusai-dori","naha-shureimon.webp"),
 ("hakata-port-hakata-station-access","fukuoka-ohori-park.webp"),
 ("nagasaki-matsugae-glover-garden-cruise-access","nagasaki-glover-garden.webp"),
 ("ishigaki-cruise-kabira-bay-bus-taxi","ishigaki-kabira-bay.webp"),
 ("yokohama-cruise-port-day-trip","yokohama-redbrick-waterfront.webp")
]
OUT=Path("audit-output/v80-featured-ports");OUT.mkdir(parents=True,exist_ok=True)
for slug,filename in DATA:
    assert (Path("site/things-to-do")/slug/"index.html").is_file(),slug
    assert (Path("site/images/venues")/filename).is_file(),filename
assert (Path("site/nf-v80-featured-ports.css")).is_file()
checks=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
    for viewport,width,height in [("desktop",1440,900),("mobile",390,844)]:
        page=browser.new_page(viewport={"width":width,"height":height},is_mobile=(viewport=="mobile"),has_touch=(viewport=="mobile"),device_scale_factor=1)
        item={"viewport":viewport,"width":width}
        try:
            response=page.goto(BASE+HUB,wait_until="domcontentloaded",timeout=45000)
            page.locator("#nf-v80-featured-ports .nf-v80-card").first.wait_for(state="visible",timeout=15000)
            # Real-user scroll: load/decode each lazy photograph before capturing.
            photo_cards=page.locator("#nf-v80-featured-ports .nf-v80-card")
            for i in range(5):
                card=photo_cards.nth(i)
                card.scroll_into_view_if_needed(timeout=15000)
                img=card.locator("img").first
                img.evaluate("(el) => { el.loading='eager'; }")
                img.evaluate("(el) => el.decode()")
                page.wait_for_timeout(180)
                card.screenshot(path=str(OUT/(viewport+"-card-"+str(i+1)+".png")),timeout=15000)
            page.wait_for_timeout(500)
            item.update(page.evaluate("""() => {
              const root=document.querySelector('#nf-v80-featured-ports');
              const cards=[...root.querySelectorAll('.nf-v80-card')], vw=document.documentElement.clientWidth;
              return {
               css_loaded:[...document.styleSheets].some(s => (s.href||'').includes('nf-v80-featured-ports.css')),
               heading:root.querySelector('h2')?.innerText,
               document_overflow:document.documentElement.scrollWidth>vw+2,
               cards:cards.map(c=>{
                 const r=c.getBoundingClientRect(), im=c.querySelector('img'), ir=im.getBoundingClientRect();
                 const credits=c.querySelector('.nf-v80-credit');
                 const h=c.querySelector('h3'), a=c.querySelector('.nf-v80-action');
                 return {
                   href:a?.getAttribute('href'), photo:im?.getAttribute('src'), alt:im?.alt,
                   natural_width:im?.naturalWidth,natural_height:im?.naturalHeight,
                   img_box:ir.toJSON(),card_box:r.toJSON(),caption_links:[...credits.querySelectorAll('a')].map(x=>x.href),
                   caption_text:credits.innerText, title:h?.innerText,
                   h3_px:parseFloat(getComputedStyle(h).fontSize),
                   button_height:a.getBoundingClientRect().height,
                   fits:r.left>=-2&&r.right<=vw+2,
                   card_visibility:ir.width>260&&ir.height>180,
                   caption_fits:credits.getBoundingClientRect().right<=vw+2
                 }
               })
              };
            }"""))
            item["status"]=response.status if response else None
            item["pass"]=item["status"]==200 and item["css_loaded"] and not item["document_overflow"] and len(item["cards"])==5 and all(
                c["photo"]=="/images/venues/"+fname and
                c["href"]=="/things-to-do/"+slug+"/" and
                c["natural_width"]>=800 and c["natural_height"]>=600 and
                c["fits"] and c["card_visibility"] and c["caption_fits"] and
                len(c["caption_links"])==2 and
                c["button_height"]>=44 and c["h3_px"]>=26 and
                ("부두" in c["alt"] or "터미널" in c["alt"])
                for c,(slug,fname) in zip(item["cards"],DATA)
            )
            # All five pictures explicitly disclose that they do not depict the berth.
            item["photo_site_disclosure"]=all("사진" in c["caption_text"] and "항만" in c["caption_text"] for c in item["cards"])
            item["pass"]=item["pass"] and item["photo_site_disclosure"]
            page.locator("#nf-v80-featured-ports").screenshot(path=str(OUT/(viewport+".png")),timeout=30000)
        except Exception as exc:
            item["pass"]=False;item["error"]=str(exc)[:500]
        print(json.dumps(item,ensure_ascii=False),flush=True)
        checks.append(item)
        page.close()
    browser.close()
(OUT/"report.json").write_text(json.dumps({"passed":sum(c["pass"] for c in checks),"total":len(checks),"checks":checks},ensure_ascii=False,indent=2),encoding="utf-8")
if not all(x["pass"] for x in checks):raise SystemExit("V80 displayed cruise port card QA failed")
