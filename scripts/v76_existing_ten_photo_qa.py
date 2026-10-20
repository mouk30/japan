#!/usr/bin/env python3
"""V76 existing 10 pages: live desktop/mobile hero integrity, disclosure, provenance, URLs."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
SAMPLES={
"naha-cruise-terminal-kokusai-dori":"reference",
"hakata-port-hakata-station-access":"reference",
"nagasaki-matsugae-glover-garden-cruise-access":"real",
"ishigaki-cruise-kabira-bay-bus-taxi":"real",
"okinawa-churaumi-aquarium":"unverified",
"taketomi-water-buffalo-cart":"reference",
"nagasaki-glover-garden":"reference",
"ishigaki-kabira-bay":"reference",
"okinawa-kokusai-dori":"unverified",
"hakodate-goryokaku-fort":"reference",
}
OUT=Path("audit-output/v76-existing-ten");OUT.mkdir(parents=True,exist_ok=True)
rows=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
    for slug,kind in SAMPLES.items():
        for device,width in (("desktop",1440),("mobile",390)):
            page=browser.new_page(viewport={"width":width,"height":844},is_mobile=device=="mobile",has_touch=device=="mobile")
            row={"slug":slug,"kind":kind,"device":device}
            try:
                resp=page.goto("https://www.nipponferry.com/things-to-do/"+slug+"/",wait_until="domcontentloaded",timeout=40000)
                page.locator("main img").first.wait_for(state="visible",timeout=12000)
                row.update(page.evaluate("""() => {
                    let i=document.querySelector('main img'), b=i.getBoundingClientRect();
                    let text=document.querySelector('main').innerText;
                    let urls=[...document.querySelectorAll('main a[href]')].map(x=>x.href);
                    return {hero:i.getAttribute('src'),image_w:i.naturalWidth,image_h:i.naturalHeight,
                      on_screen:b.left>=-2&&b.right<=innerWidth+2,overflow:document.documentElement.scrollWidth>innerWidth+2,
                      real_source:urls.some(x=>x.startsWith('https://commons.wikimedia.org/wiki/File:')),
                      ai_disclosure:text.includes('AI 생성')||i.alt.includes('AI 생성'),
                      credit: /CC BY|CC0|퍼블릭 도메인|Public domain/.test(text),
                      external_source:urls.find(x=>x.startsWith('https://commons.wikimedia.org/wiki/File:'))||null };
                }"""))
                row["status"]=resp.status
                row["pass"]=resp.status==200 and row["image_w"]>200 and row["on_screen"] and not row["overflow"] and (row["real_source"] and row["credit"] if kind=="real" else True)
                if device=="mobile":page.screenshot(path=str(OUT/(slug+"-mobile.png")),full_page=False)
            except Exception as e:row["pass"]=False;row["error"]=str(e)[:350]
            rows.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
            page.close()
    browser.close()
summary={"total":len(rows),"passed":sum(r["pass"] for r in rows),"results":rows,"limitations":"A visible reference image does not prove actual site/rights. Real-source link confirms placement, not independent license legality."}
(OUT/"report.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
if summary["passed"]!=summary["total"]:raise SystemExit("Visual/source QA failed")
