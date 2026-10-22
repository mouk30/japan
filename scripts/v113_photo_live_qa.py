#!/usr/bin/env python3
"""V113 real public desktop/mobile tests of ten license-credited port photographs."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
planned=json.loads((ROOT/"audit-reports/v113/photo-import-plan.json").read_text("utf8"))["items"]
results=json.loads((ROOT/"audit-reports/v113/import-result.json").read_text("utf8"))
done={item["slug"]:item for item in results["items"]}
out=Path("audit-output/v113");out.mkdir(parents=True,exist_ok=True)
errors=[];checked=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
    for width,height in [(1440,900),(390,844)]:
        context=browser.new_context(viewport={"width":width,"height":height})
        page=context.new_page()
        for item in planned:
            slug=item["slug"];label=f"{slug}@{width}";meta=done[slug]
            try:
                url="https://www.nipponferry.com/things-to-do/"+slug+"-cruise-port-day-trip/"
                res=page.goto(url,wait_until="domcontentloaded",timeout=60000)
                if res is None or res.status>=400:raise ValueError("page request invalid")
                img=page.locator('img[src="'+item["output"]+'"]')
                if img.count()!=1:raise ValueError("new licensed site image absent or duplicated")
                img.scroll_into_view_if_needed(timeout=10000)
                img.evaluate("(i)=>i.complete?true:new Promise(resolve=>{i.addEventListener('load',()=>resolve(true),{once:true});i.addEventListener('error',()=>resolve(false),{once:true})})",timeout=20000)
                decoded=img.evaluate("(i)=>({ok:i.complete,width:i.naturalWidth,height:i.naturalHeight})")
                if not decoded["ok"] or (decoded["width"],decoded["height"])!=(meta["width"],meta["height"]):
                    raise ValueError("WebP was not loaded or intrinsic sizes incorrect")
                if page.locator('meta[property="og:image"]').get_attribute("content")!="https://www.nipponferry.com"+item["output"]:
                    raise ValueError("OG still shows AI artwork")
                if page.locator('link[rel="canonical"]').get_attribute("href")!=url:raise ValueError("canonical changed")
                caps=page.locator(".v113-photo-credit")
                if caps.count()!=1:raise ValueError("visible source credit missing")
                credit=caps.inner_text()
                if meta["author"] not in credit or meta["taken"] not in credit or meta["license"] not in credit:
                    raise ValueError("original photograph author, year or license missing")
                if page.evaluate("document.documentElement.scrollWidth")>width+12:
                    raise ValueError("horizontal scrollbar on published page")
                if width==390 or slug in ("shiraoi","sendai","tottori"):
                    page.screenshot(path=str(out/f"{slug}-{width}.png"),full_page=False)
                checked.append(label)
            except Exception as e:errors.append(label+" "+str(e)[:240])
        page.close();context.close()
    browser.close()
report={"passed":len(checked)==20 and not errors,"checked":len(checked),"expected":20,
        "errors":errors,"rendered_scenes":checked}
(out/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps({k:report[k] for k in ("passed","checked","expected","errors")},ensure_ascii=False))
raise SystemExit(0 if report["passed"] else 1)
