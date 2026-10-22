#!/usr/bin/env python3
"""V114 public site smoke/visual QA: ten images x desktop/mobile, no false AI or berth."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
plan=json.loads((ROOT/"audit-reports/v114/photo-plan.json").read_text("utf8"))["selected"]
meta={x["slug"]:x for x in json.loads((ROOT/"audit-reports/v114/import-result.json").read_text("utf8"))["images"]}
out=Path("audit-output/v114")
out.mkdir(parents=True,exist_ok=True)
done=[];errors=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
    for width,height in ((1440,900),(390,844)):
        ctx=browser.new_context(viewport={"width":width,"height":height})
        page=ctx.new_page()
        for entry in plan:
            slug=entry["slug"];label=f"{slug}@{width}"
            try:
                url=f"https://www.nipponferry.com/things-to-do/{slug}-cruise-port-day-trip/"
                response=page.goto(url,wait_until="domcontentloaded",timeout=60000)
                if response is None or response.status>=400:
                    raise ValueError("article HTTP error")
                photo=page.locator('img[src="'+entry["output"]+'"]')
                if photo.count()!=1:raise ValueError("licensed real WebP not deployed")
                photo.scroll_into_view_if_needed(timeout=10000)
                photo.evaluate("(i)=>i.complete?true:new Promise((r)=>{i.addEventListener('load',()=>r(true),{once:true});i.addEventListener('error',()=>r(false),{once:true})})",timeout=20000)
                size=photo.evaluate("(i)=>({ok:i.complete,w:i.naturalWidth,h:i.naturalHeight})")
                image=meta[slug]
                if not size["ok"] or (size["w"],size["h"])!=(image["pixel_width"],image["pixel_height"]):
                    raise ValueError("wrong or undecoded photograph")
                credits=page.locator(".v114-photo-credit")
                if credits.count()!=1:raise ValueError("visible photo caption not present")
                text=credits.inner_text()
                if entry["author"] not in text or entry["license"] not in text or entry["taken"] not in text:
                    raise ValueError("author or date/license absent")
                if page.locator('meta[property="og:image"]').get_attribute("content")!="https://www.nipponferry.com"+entry["output"]:
                    raise ValueError("OpenGraph still points at staged image")
                if page.locator('link[rel="canonical"]').get_attribute("href")!=url:
                    raise ValueError("canonical changed")
                if page.evaluate("document.documentElement.scrollWidth")>width+12:
                    raise ValueError("horizontal overflow detected")
                if width==390 or slug in ("wakkanai","motobu","ibaraki-hitachinaka"):
                    page.screenshot(path=str(out/f"{slug}-{width}.png"),full_page=False)
                done.append({"slug":slug,"viewport":width,"decoded":True,"source":entry["source"],"og":True,"canonical":True})
            except Exception as e:errors.append(label+": "+str(e)[:200])
        page.close()
        ctx.close()
    browser.close()
result={"passed":len(done)==20 and not errors,"checked":len(done),"expected":20,"errors":errors,"pages":done}
(out/"report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps({k:result[k] for k in ("passed","checked","expected","errors")},ensure_ascii=False))
raise SystemExit(0 if result["passed"] else 1)
