#!/usr/bin/env python3
"""V111 20 live visits (ten Japan port articles, PC+mobile) with photo evidence."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
items = json.loads((ROOT/"audit-reports/v111/ten-ports-photo-provenance.json").read_text("utf8"))["items"]
out = Path("audit-output/v111")
out.mkdir(parents=True, exist_ok=True)
errors = []
checks = []
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
    for width, height in ((1440, 900), (390, 844)):
        context = browser.new_context(viewport={"width": width, "height": height})
        page = context.new_page()
        for info in items:
            label = f'{info["slug"]}@{width}'
            try:
                url = "https://www.nipponferry.com" + info["page"]
                response = page.goto(url, wait_until="domcontentloaded", timeout=60000)
                if not response or response.status >= 400:
                    raise ValueError("public article returned error")
                cover = page.locator("img.cover")
                if cover.count() != 1:
                    raise ValueError("hero image missing")
                cover.scroll_into_view_if_needed(timeout=10000)
                cover.evaluate("(i)=>i.complete?true:new Promise((res)=>{i.addEventListener('load',()=>res(true),{once:true});i.addEventListener('error',()=>res(false),{once:true})})",timeout=18000)
                if cover.get_attribute("src") != info["asset"]:
                    raise ValueError("old/incorrect hero photo served")
                photo = cover.evaluate("(i)=>({ready:i.complete,nw:i.naturalWidth,nh:i.naturalHeight})")
                if not photo["ready"] or photo["nw"] != info["width"] or photo["nh"] != info["height"]:
                    raise ValueError("expected WebP not completely decoded")
                if page.locator('meta[property="og:image"]').get_attribute("content") != "https://www.nipponferry.com" + info["asset"]:
                    raise ValueError("OG image not the real photographed place")
                if page.locator('link[rel="canonical"]').get_attribute("href") != url:
                    raise ValueError("canonical mismatch")
                if page.locator(".v111-photo-credit").count() != 1:
                    raise ValueError("visible photographer and license missing")
                if info["photographer"] not in page.locator(".v111-photo-credit").inner_text():
                    raise ValueError("incorrect attribution")
                if page.evaluate("document.documentElement.scrollWidth") > width + 12:
                    raise ValueError("horizontal overflow on real page")
                if info["stale_caption_removed"] and page.locator("body").get_by_text("현재는 공통 크루즈 참고 이미지입니다.").count():
                    raise ValueError("obsolete graphic disclaimer remains")
                if info["changed_cover"]:
                    page.screenshot(path=str(out/f'{info["slug"]}-{width}.png'),full_page=False)
                checks.append({"page":label,"photo":info["asset"],"decoded":True,"og":True,"rights":True,"canonical":True})
            except Exception as exc:
                errors.append(label + ": " + str(exc)[:240])
        page.close()
        context.close()
    browser.close()
result = {"passed":not errors and len(checks)==20,"checked":len(checks),"expected":20,"errors":errors,"pages":checks}
(out/"report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps({key:result[key] for key in ("passed","checked","expected","errors")},ensure_ascii=False))
raise SystemExit(0 if result["passed"] else 1)
