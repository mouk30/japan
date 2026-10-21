#!/usr/bin/env python3
"""V81 live desktop/mobile QA for four source-attributed Japan destination cards."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE="https://www.nipponferry.com"
EXPECT=[
("/japan/tokyo/","tokyo-city-night-real.webp"),
("/okinawa/","naha-shureimon.webp"),
("/japan/fukuoka/","fukuoka-ohori-park.webp"),
("/things-to-do/nagasaki-matsugae-glover-garden-cruise-access/","nagasaki-glover-garden.webp")
]
for href,img in EXPECT:
    assert (Path("site")/href.strip("/")/"index.html").is_file(),href
    assert (Path("site/images/venues")/img).is_file(),img
assert (Path("site/nf-v81-destination-hub.css")).exists()
OUT=Path("audit-output/v81-destination-hub");OUT.mkdir(parents=True,exist_ok=True)
reports=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
    for device,width,height in [("desktop",1440,900),("mobile",390,844)]:
        page=browser.new_page(viewport={"width":width,"height":height},device_scale_factor=1,is_mobile=(device=="mobile"),has_touch=(device=="mobile"))
        row={"device":device,"viewport_width":width}
        try:
            response=page.goto(BASE+"/japan/",wait_until="domcontentloaded",timeout=50000)
            page.locator("#nf-v81-japan-featured .nf-v81-card").first.wait_for(state="visible",timeout=16000)
            cards=page.locator("#nf-v81-japan-featured .nf-v81-card")
            for i in range(4):
                card=cards.nth(i)
                card.scroll_into_view_if_needed(timeout=12000)
                card.locator("img").first.evaluate("(el) => {el.loading='eager'}")
                card.locator("img").first.evaluate("(el) => el.decode()")
                card.screenshot(path=str(OUT/f"{device}-card-{i+1}.png"),timeout=16000)
            row.update(page.evaluate("""() => {
              const root=document.getElementById('nf-v81-japan-featured');
              const vw=document.documentElement.clientWidth;
              const cards=[...root.querySelectorAll('.nf-v81-card')];
              return {css_loaded:[...document.styleSheets].some(x=>(x.href||'').includes('nf-v81-destination-hub.css')),
                overflow:document.documentElement.scrollWidth>vw+2,
                canonical:document.querySelector('link[rel=canonical]')?.href,
                cards:cards.map(c=>{
                  const im=c.querySelector('img'),r=c.getBoundingClientRect(),p=c.querySelector('.nf-v81-photo').getBoundingClientRect();
                  const btn=c.querySelector('.nf-v81-action');
                  return {href:btn?.getAttribute('href'),img:im?.getAttribute('src'),alt:im?.alt,
                    naturalW:im?.naturalWidth,naturalH:im?.naturalHeight,
                    cardRight:r.right,cardLeft:r.left,photoW:p.width,photoH:p.height,
                    btnH:btn.getBoundingClientRect().height,headPx:parseFloat(getComputedStyle(c.querySelector('h3')).fontSize),
                    sourceLinks:[...c.querySelectorAll('.nf-v81-credit a')].map(a=>a.href),
                    caption:c.querySelector('.nf-v81-credit')?.innerText,
                    fits:r.left>=-2&&r.right<=vw+2
                  }
                })
              };
            }"""))
            row["status"]=response.status if response else None
            row["pass"]=(row["status"]==200 and row["css_loaded"] and len(row["cards"])==4 and not row["overflow"] and
              row["canonical"]==BASE+"/japan/" and all(
                c["href"]==want_url and c["img"]=="/images/venues/"+filename and c["naturalW"]>=450 and c["naturalH"]>=280
                and c["fits"] and c["photoW"]>=300 and c["photoH"]>=200 and c["btnH"]>=44 and c["headPx"]>=27 and len(c["sourceLinks"])==2
                and c["caption"] and "WebP" in c["caption"]
                for c,(want_url,filename) in zip(row["cards"],EXPECT)))
            page.locator("#nf-v81-japan-featured").screenshot(path=str(OUT/f"{device}-section.png"),timeout=25000)
        except Exception as exc:
            row["pass"]=False;row["error"]=str(exc)[:650]
        print(json.dumps(row,ensure_ascii=False),flush=True)
        reports.append(row);page.close()
    browser.close()
(OUT/"report.json").write_text(json.dumps({"total":2,"passed":sum(x["pass"] for x in reports),"checks":reports},ensure_ascii=False,indent=2),encoding="utf-8")
if not all(x["pass"] for x in reports):raise SystemExit("V81 destination PC/mobile QA failed")
