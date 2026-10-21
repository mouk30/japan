#!/usr/bin/env python3
"""V82 live browser and factual-disclosure QA for four existing activity categories."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE="https://www.nipponferry.com"
CASES=[
 ("/shopping/","shopping-city-night-guide.webp","도톤보리"),
 ("/food/","local-food-market-guide.webp","니시키시장"),
 ("/things-to-do/onsen/","onsen-first-time.webp","다카노유"),
 ("/things-to-do/culture/","traditional-experience-booking.webp","다도")
]
OUT=Path("audit-output/v82-activities");OUT.mkdir(parents=True,exist_ok=True)
for href,img,scene in CASES:
    assert (Path("site")/href.strip("/")/"index.html").is_file(), href
    assert (Path("site/images/culture-verified")/img).is_file(), img
assert (Path("site/nf-v82-things-to-do-cards.css")).is_file()
reports=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
    for device,w,h in [("desktop",1440,900),("mobile",390,844)]:
        page=browser.new_page(viewport={"width":w,"height":h},device_scale_factor=1,
                              is_mobile=device=="mobile",has_touch=device=="mobile")
        record={"device":device,"viewport":w}
        try:
            resp=page.goto(BASE+"/things-to-do/",wait_until="domcontentloaded",timeout=50000)
            area=page.locator("#nf-v82-showcase")
            area.wait_for(state="visible",timeout=15000)
            cards=page.locator("#nf-v82-showcase .nf-v82-card")
            for i in range(4):
                card=cards.nth(i)
                card.scroll_into_view_if_needed(timeout=12000)
                img=card.locator("img").first
                img.evaluate("(el)=>el.loading='eager'")
                img.evaluate("(el)=>el.decode()")
                card.screenshot(path=str(OUT/f"{device}-card-{i+1}.png"),timeout=15000)
            record.update(page.evaluate("""() => {
              const area=document.querySelector('#nf-v82-showcase'), vw=document.documentElement.clientWidth;
              return {
                css:[...document.styleSheets].some(x=>(x.href||'').includes('nf-v82-things-to-do-cards.css')),
                overflow:document.documentElement.scrollWidth>vw+2,
                canonical:document.querySelector('link[rel=canonical]')?.href,
                old_section:!!document.querySelector('#food-shopping-seasons'),
                existing_topics:document.querySelectorAll('.v60-hub-card').length,
                cards:[...area.querySelectorAll('.nf-v82-card')].map(c=>{
                  const img=c.querySelector('img'), br=c.getBoundingClientRect(), ph=c.querySelector('.nf-v82-media').getBoundingClientRect(),
                    btn=c.querySelector('.nf-v82-action'), heading=c.querySelector('h3');
                  return {href:btn?.getAttribute('href'), img:img?.getAttribute('src'),alt:img?.alt,
                    naturalW:img?.naturalWidth,naturalH:img?.naturalHeight,
                    imageW:ph.width,imageH:ph.height,
                    cardLeft:br.left,cardRight:br.right,cardWidth:br.width,
                    fit:br.left>=-2&&br.right<=vw+2,
                    headingFont:parseFloat(getComputedStyle(heading).fontSize),
                    buttonH:btn.getBoundingClientRect().height,
                    links:[...c.querySelectorAll('.nf-v82-credit a')].map(x=>x.href),
                    caption:c.querySelector('.nf-v82-credit')?.innerText,
                    scene:c.querySelector('.nf-v82-photo-place')?.innerText
                  }
                })
              }
            }"""))
            record["http"]=resp.status if resp else None
            record["pass"]=(record["http"]==200 and record["css"] and not record["overflow"] and
                record["canonical"]==BASE+"/things-to-do/" and record["old_section"] and
                record["existing_topics"]>=4 and len(record["cards"])==4 and all(
                    c["href"]==href and c["img"]=="/images/culture-verified/"+img and c["naturalW"]>=450 and c["naturalH"]>=300 and
                    c["imageW"]>=300 and c["imageH"]>=200 and c["fit"] and c["buttonH"]>=44 and
                    c["headingFont"]>=27 and len(c["links"])==2 and scene in c["scene"] and
                    "WebP" in c["caption"] for c,(href,img,scene) in zip(record["cards"],CASES)))
            area.screenshot(path=str(OUT/f"{device}-section.png"),timeout=26000)
        except Exception as e:
            record["pass"]=False;record["error"]=str(e)[:600]
        reports.append(record)
        print(json.dumps(record,ensure_ascii=False),flush=True)
        page.close()
    browser.close()
(OUT/"report.json").write_text(json.dumps({"total":2,"passed":sum(bool(x["pass"]) for x in reports),"checks":reports},ensure_ascii=False,indent=2),encoding="utf-8")
if not all(x["pass"] for x in reports):raise SystemExit("V82 live browser verification failed")
