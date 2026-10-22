#!/usr/bin/env python3
"""V112 10 historic-photo cruise articles x PC and mobile, production browser QA."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
items=json.loads((ROOT/"audit-reports/v112/ten-port-photo-provenance.json").read_text("utf8"))["items"]
out=Path("audit-output/v112");out.mkdir(parents=True,exist_ok=True)
errors=[];results=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
    for width,height in ((1440,900),(390,844)):
        context=browser.new_context(viewport={"width":width,"height":height})
        page=context.new_page()
        for item in items:
            label=f'{item["slug"]}@{width}'
            try:
                url="https://www.nipponferry.com"+item["article"]
                response=page.goto(url,wait_until="domcontentloaded",timeout=60000)
                if response is None or response.status>=400:
                    raise ValueError("public article HTTP error")
                locator=page.locator(f'img[src="{item["asset"]}"]')
                if locator.count()!=1:raise ValueError("documentary WebP image missing")
                locator.scroll_into_view_if_needed(timeout=12000)
                locator.evaluate("(i)=>i.complete?true:new Promise((r)=>{i.addEventListener('load',()=>r(true),{once:true});i.addEventListener('error',()=>r(false),{once:true})})",timeout=20000)
                photo=locator.evaluate("(i)=>({done:i.complete,width:i.naturalWidth,height:i.naturalHeight})")
                if photo["width"]!=item["width"] or photo["height"]!=item["height"]:
                    raise ValueError("photo failed to decode expected WebP at full intrinsic dimensions")
                cap=page.locator(".v112-photo-credit")
                if cap.count()!=1 or item["author"] not in cap.inner_text():
                    raise ValueError("photo ownership source not displayed")
                if cap.get_attribute("data-photo-year")!=str(item["year"]):
                    raise ValueError("historical photo year not disclosed")
                if page.locator('meta[property="og:image"]').get_attribute("content")!="https://www.nipponferry.com"+item["asset"]:
                    raise ValueError("photo/OG thumbnail mismatch")
                if page.locator('link[rel="canonical"]').get_attribute("href")!=url:
                    raise ValueError("canonical changed")
                if item["slug"] in ("otaru","tokyo") and locator.get_attribute("onerror") is not None:
                    raise ValueError("generic ferry fallback still silently replacing real place photo")
                overflow=page.evaluate("document.documentElement.scrollWidth")
                if overflow>width+12:
                    raise ValueError("horizontal content overflow: "+str(overflow))
                if item["slug"] in ("otaru","tokyo","maizuru"):
                    page.screenshot(path=str(out/f'{item["slug"]}-{width}.png'),full_page=False)
                results.append({"id":label,"img":item["asset"],"year":item["year"],"credit":True,"og":True,"canonical":True,"decoded":True})
            except Exception as exc:
                errors.append(label+": "+str(exc)[:250])
        page.close();context.close()
    browser.close()
passed=not errors and len(results)==20
result={"passed":passed,"checked":len(results),"expected":20,"errors":errors,"records":results}
(out/"report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps({k:result[k] for k in ("passed","checked","expected","errors")},ensure_ascii=False))
raise SystemExit(0 if passed else 1)
