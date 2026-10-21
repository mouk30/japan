#!/usr/bin/env python3
"""V85: live production V84 banner responsive/image/link/provenance QA (read-only).
Artifacts: screenshots and machine-readable report; never auto-confirms bookings.
"""
import json, time, traceback
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE="https://www.nipponferry.com"
OUT=Path("audit-output/v85-route-banners")
OUT.mkdir(parents=True,exist_ok=True)
SIZES=[("desktop",1440,900),("laptop",1024,768),("tablet",768,1024),("mobile",390,844),("small-mobile",360,780)]
EXPECTED=[
    ("osaka","/guide/busan-osaka-ferry/"),
    ("fukuoka","/guide/busan-fukuoka-ferry/"),
    ("shimonoseki","/guide/busan-shimonoseki-ferry/"),
    ("tsushima","/guide/busan-tsushima-ferry/"),
]
report={"version":"V85","site":BASE,"viewports":[],"live_targets":{},"errors":[],"warnings":[],"generated_at_utc":time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
def fail(msg):report["errors"].append(msg)
def warn(msg):report["warnings"].append(msg)

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
    for slug in ["","ferry/"]:
        url=BASE+"/"+slug
        page=browser.new_page(viewport={"width":1440,"height":900},device_scale_factor=1)
        try:
            response=page.goto(url,wait_until="domcontentloaded",timeout=60000)
            page.wait_for_timeout(2000)
            report["live_targets"][url]={"status":response.status if response else None,"title":page.title()}
            if not response or response.status>=400: fail(f"HTTP invalid {url}: {response.status if response else 'empty'}")
            if slug:
                banner=page.locator("#recommended-ferry-routes .nf84-route")
                if banner.count()!=4:fail(f"expected 4 live routes, got {banner.count()}")
                for route,expected in EXPECTED:
                    node=page.locator(".nf84-route",has=page.locator(f"#nf84-{route}-title"))
                    if node.count()!=1:
                        fail(f"route missing {route}");continue
                    href=node.locator(".nf84-route__cta").get_attribute("href")
                    if href!=expected:fail(f"{route} CTA wrong: {href} expected {expected}")
                    if node.locator(".nf84-route__source").count()!=1:fail(f"{route} missing operator link")
                    if node.locator(".nf84-route__caption").count()!=1:fail(f"{route} missing provenance")
                    if node.locator("img").evaluate("(e)=>e.complete && e.naturalWidth > 350") is not True:fail(f"{route} failed to load image")
            else:
                home=page.locator("#nf84-home-routes")
                if home.count()!=1:fail("Home V84 route banner absent")
                elif home.locator("a[href='/ferry/#recommended-ferry-routes']").count()!=1:fail("Home V84 CTA absent")
        except Exception as e:fail(f"{url}: {type(e).__name__} {str(e)[:200]}")
        finally: page.close()

    # Follow internal route destinations and CSS/image production resources.
    pages=["/","/ferry/"]+[href for _,href in EXPECTED]
    for target in pages+["/nf-v84-route-banners.css"]:
        try:
            response=browser.new_context().request.get(BASE+target,timeout=45000)
            report["live_targets"][BASE+target]={"status":response.status, "bytes":len(response.body())}
            if response.status>=400:fail(f"Broken internal target {target}: HTTP {response.status}")
        except Exception as e:fail(f"Internal target {target}: {str(e)[:150]}")

    for name,width,height in SIZES:
        context=browser.new_context(viewport={"width":width,"height":height},device_scale_factor=1,is_mobile=False,has_touch=width<=390)
        for route_type,route in [("ferry","/ferry/"),("home","/")]:
            page=context.new_page()
            record={"viewport":name,"width":width,"height":height,"page":route_type,"cards":[],"issues":[]}
            try:
                response=page.goto(BASE+route,wait_until="domcontentloaded",timeout=60000)
                page.wait_for_timeout(1300)
                root=page.locator("#recommended-ferry-routes" if route_type=="ferry" else "#nf84-home-routes")
                if root.count()!=1: raise Exception(f"V84 root missing for {route_type}")
                root.scroll_into_view_if_needed(timeout=10000)
                page.wait_for_timeout(500)
                try:root.screenshot(path=str(OUT/f"{route_type}-{name}.png"),timeout=20000,animations="disabled")
                except Exception as e:warn(f"Screenshot unavailable {route_type}/{name}: {e}")
                metrics=page.evaluate("""() => ({vw: innerWidth, scrollW:document.documentElement.scrollWidth})""")
                record["scrollWidth"]=metrics["scrollW"]
                if metrics["scrollW"]>width+4:
                    record["issues"].append("Horizontal overflow on page")
                targets=page.locator(".nf84-route" if route_type=="ferry" else ".nf84-home__banner")
                for i in range(targets.count()):
                    elem=targets.nth(i)
                    item=elem.evaluate("""el=>{
                        let R=el.getBoundingClientRect(), inner=el.querySelector('.nf84-route__inner, .nf84-home__content'),
                            caption=el.querySelector('.nf84-route__caption'),
                            photo=el.querySelector('img'),
                            links=Array.from(el.querySelectorAll('a:not(.nf84-route__caption a)'));
                        let ir=inner?.getBoundingClientRect(), cr=caption?.getBoundingClientRect();
                        let desc=inner?.querySelector('.nf84-route__desc, .nf84-home__content p');
                        let dr=desc?.getBoundingClientRect();
                        return {
                          x:R.x,y:R.y,w:R.width,h:R.height,
                          contentBottom:ir?.bottom,captionTop:cr?.top,
                          descBottom:dr?.bottom,
                          imageLoaded:photo?.complete && photo?.naturalWidth>350,
                          imageWidth:photo?.naturalWidth,
                          captionOverlap:!!(cr && dr && cr.top < dr.bottom+8),
                          horizontalOverflow:ir && (ir.right>R.right+3 || ir.left<R.left-3),
                          buttons:links.map(a=>{
                            let b=a.getBoundingClientRect();
                            return {text:a.innerText.slice(0,60),href:a.getAttribute('href'),left:b.left,right:b.right,top:b.top,bottom:b.bottom,height:b.height,width:b.width}
                          })
                        }
                    }""")
                    if not item["imageLoaded"]:record["issues"].append(f"banner {i+1} image missing")
                    if item["captionOverlap"]:record["issues"].append(f"banner {i+1} caption overlaps content")
                    if item["horizontalOverflow"]:record["issues"].append(f"banner {i+1} content outside card")
                    for button in item["buttons"]:
                        if button["left"]< -1 or button["right"]>width+1:
                            record["issues"].append(f"banner {i+1} off-viewport CTA {button['text']}")
                        if button["height"]<38:record["issues"].append(f"banner {i+1} small CTA: {button['height']}px")
                    record["cards"].append(item)
                record["pass"]=not record["issues"]
                if record["issues"]: fail(f"{route_type}/{name}: "+ "; ".join(record["issues"]))
            except Exception as e:
                record["pass"]=False;record["issues"].append(f"{type(e).__name__}: {str(e)[:200]}");fail(f"{route_type}/{name}: {record['issues'][-1]}")
            finally:
                report["viewports"].append(record);page.close()
        context.close()
    browser.close()

report["passed"] = len(report["errors"])==0
(OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"passed":report["passed"],"failures":len(report["errors"]),"viewports":len(report["viewports"]),"errors":report["errors"],"warnings":report["warnings"]},ensure_ascii=False,indent=2))
raise SystemExit(0 if report["passed"] else 1)
