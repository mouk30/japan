#!/usr/bin/env python3
"""Production QA for 10 port articles at desktop and mobile widths."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
items=json.loads((ROOT/"audit-reports/v110/ten-port-photo-sources.json").read_text("utf8"))["items"]
errors=[];passed=0
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
    for w,h in [(1440,900),(390,844)]:
        ctx=browser.new_context(viewport={"width":w,"height":h})
        page=ctx.new_page()
        for spec in items:
            label=spec["slug"]+"/"+str(w)
            try:
                url="https://www.nipponferry.com"+spec["url"]
                response=page.goto(url,wait_until="domcontentloaded",timeout=55000)
                if response is None or response.status>=400:raise ValueError("page request failed")
                img=page.locator("img.cover")
                img.scroll_into_view_if_needed(timeout=10000)
                img.evaluate("(i)=>i.complete?true:new Promise(resolve=>{i.addEventListener('load',()=>resolve(true),{once:true});i.addEventListener('error',()=>resolve(false),{once:true})})",timeout=18000)
                if img.get_attribute("src")!=spec["asset"]:raise ValueError("cover not deployed")
                if not img.evaluate("(i)=>i.complete && i.naturalWidth>=600 && i.naturalHeight>=500"):raise ValueError("cover not decoded")
                if page.locator('meta[property="og:image"]').get_attribute("content")!="https://www.nipponferry.com"+spec["asset"]:raise ValueError("OG not deployed")
                if page.locator('link[rel="canonical"]').get_attribute("href")!=url:raise ValueError("canonical URL changed")
                credits=page.locator(".v110-photo-credit")
                if credits.count()!=1 or spec["author"] not in credits.inner_text():raise ValueError("photo credit missing")
                if page.evaluate("document.documentElement.scrollWidth")>w+12:raise ValueError("horizontal page overflow")
                passed+=1
            except Exception as e:errors.append(label+" "+str(e)[:160])
        page.close();ctx.close()
    browser.close()
result={"passed":passed==20 and not errors,"checked":passed,"expected":20,"errors":errors}
Path("audit-output/v110").mkdir(parents=True,exist_ok=True)
Path("audit-output/v110/report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps(result,ensure_ascii=False))
raise SystemExit(0 if result["passed"] else 1)
