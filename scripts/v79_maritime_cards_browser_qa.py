#!/usr/bin/env python3
"""V79 live browser QA for spacious homepage cruise/ferry cards."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE="https://www.nipponferry.com"
OUT=Path("audit-output/v79-maritime");OUT.mkdir(parents=True,exist_ok=True)
EXPECTED=[
 {"url":"/things-to-do/cruise-ports/","photo":"nipponferry-hero-cruise-arrival.webp","label":"일본 크루즈 기항지"},
 {"url":"/booking/japan-cruise/","photo":"v72-shodoshima-tonosho-ferry-2010.webp","label":"일본 연안페리·항로"}
]
rows=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
    for device,width,height in (("desktop",1440,900),("mobile",390,844)):
        page=browser.new_page(viewport={"width":width,"height":height},device_scale_factor=1,
                              is_mobile=device=="mobile",has_touch=device=="mobile")
        item={"device":device}
        try:
            response=page.goto(BASE+"/",wait_until="domcontentloaded",timeout=45000)
            page.locator(".nf-v79-maritime-grid .nf-maritime-card").first.wait_for(state="visible",timeout=13000)
            page.wait_for_timeout(900)
            item["status"]=response.status if response else None
            item["layout"]=page.evaluate("""() => {
              const cards=[...document.querySelectorAll('.nf-v79-maritime-grid .nf-maritime-card')];
              const section=document.querySelector('.nf-maritime-panel');
              return {overflow:document.documentElement.scrollWidth>innerWidth+2,
                section_rect:section?.getBoundingClientRect().toJSON(),
                credits:[...document.querySelectorAll('.nf-v79-photo-credit')].map(c=>({text:c.innerText,links:[...c.querySelectorAll('a')].map(a=>a.href),rect:c.getBoundingClientRect().toJSON()})),
                cards:cards.map(a=>{let r=a.getBoundingClientRect(),css=getComputedStyle(a);
                  return {href:a.getAttribute('href'),text:a.innerText,rect:r.toJSON(),bg:css.backgroundImage,
                    heading_font:getComputedStyle(a.querySelector('strong')).fontSize,
                    image_layer:css.backgroundImage!=='none',
                    onscreen:r.width>200&&r.height>300&&r.left>=-2&&r.right<=innerWidth+2};
                })
              };
            }""")
            cards=item["layout"]["cards"]
            item["asset_checks"]=[]
            for wanted in EXPECTED:
                url=BASE+("/images/" if wanted["photo"].startswith("nipponferry") else "/images/v72-verified/")+wanted["photo"]
                asset=page.request.get(url,timeout=20000)
                item["asset_checks"].append({"url":url,"status":asset.status,"ctype":asset.headers.get("content-type","")})
            item["pass"]=item["status"]==200 and not item["layout"]["overflow"] and len(cards)==2 and len(item["layout"]["credits"])==2 and all(
                c["href"]==w["url"] and w["photo"] in c["bg"] and w["label"] in c["text"] and c["onscreen"]
                for c,w in zip(cards,EXPECTED)
            ) and all(z["status"]==200 and "image" in z["ctype"] for z in item["asset_checks"]) and (
                all(c["rect"]["height"]>=340 for c in cards)
            ) and len(item["layout"]["credits"][1]["links"])==2
            section=page.locator(".nf-maritime-panel")
            section.screenshot(path=str(OUT/(device+".png")),timeout=20000)
        except Exception as exc:
            item["pass"]=False;item["error"]=str(exc)[:500]
        print(json.dumps(item,ensure_ascii=False),flush=True);rows.append(item);page.close()
    browser.close()
(OUT/"report.json").write_text(json.dumps({"passed":sum(x["pass"] for x in rows),"total":len(rows),"checks":rows},ensure_ascii=False,indent=2),encoding="utf-8")
if not all(x["pass"] for x in rows):raise SystemExit("V79 live card QA failed")
