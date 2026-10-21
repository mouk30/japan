#!/usr/bin/env python3
"""V91 production booking conversion QA: 4 route checklists + 2 direct operator hubs."""
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

BASE="https://www.nipponferry.com"
ROOT=Path(__file__).resolve().parents[1]
CONF=json.loads((ROOT/"scripts/v90_booking_link_targets.json").read_text("utf8"))
OUT=ROOT/"audit-output/v91-direct-booking"
OUT.mkdir(parents=True,exist_ok=True)
SIZES=[("desktop",1440,900),("mobile",390,844),("small-mobile",360,780)]
RESULT={"version":"V91","checked_at_utc":datetime.now(timezone.utc).isoformat(),"checks":[],"actual_clicks":[],"errors":[]}
URLS={key:value["primary"] for key,value in CONF["routes"].items()}
def err(test,s):
    test.setdefault("errors",[]).append(s)
    RESULT["errors"].append(f"{test['page']} @ {test['viewport']}: {s}")
def load(page,path):
    res=page.goto(BASE+path,wait_until="domcontentloaded",timeout=60000)
    page.wait_for_timeout(950)
    return bool(res and res.status<400)
def geometry_ok(a,w):
    a.scroll_into_view_if_needed(timeout=10000)
    b=a.bounding_box()
    return bool(b and b["height"]>=44 and b["width"]>=115 and b["x"]>=-2 and b["x"]+b["width"]<=w+3)
def overlap(a,b):
    x,y=a.bounding_box(),b.bounding_box()
    if not x or not y:return False
    return max(x["x"],y["x"])<min(x["x"]+x["width"],y["x"]+y["width"]) and max(x["y"],y["y"])<min(x["y"]+x["height"],y["y"]+y["height"])
with sync_playwright() as playwright:
    browser=playwright.chromium.launch(headless=True,args=["--no-sandbox"])
    for name,width,height in SIZES:
        ctx=browser.new_context(viewport={"width":width,"height":height},has_touch=(width<=390),device_scale_factor=1)
        for route in URLS:
            path=f"/guide/busan-{route}-ferry/"
            page=ctx.new_page()
            test={"page":path,"viewport":name,"type":"route_checklist","errors":[]}
            try:
                if not load(page,path):err(test,"existing route HTTP error")
                preflight=page.locator(".nf86-intro .nf91-preflight")
                if preflight.count()!=1:err(test,"expected one new concise checklist")
                else:
                    if preflight.locator("li").count()!=3:err(test,"expected precisely 3 route-specific checklist items")
                    if not geometry_ok(preflight,width):err(test,"checklist overflow or too narrow")
                    preflight.screenshot(path=str(OUT/f"{route}-{name}-preflight.png"),animations="disabled",timeout=22000)
                for cls in (".nf86-intro",".nf86-booking",".nf86-side"):
                    primary=page.locator(cls+" a.nf86-action-primary")
                    if primary.count()!=1 or primary.get_attribute("href")!=URLS[route]:
                        err(test,cls+" original operator booking CTA broken")
                if page.locator('link[rel="canonical"]').get_attribute("href")!=BASE+path:
                    err(test,"canonical changed")
                scroll=page.evaluate("document.documentElement.scrollWidth")
                if scroll>width+9:err(test,"horizontal overflow "+str(scroll))
                test["scrollWidth"]=scroll
            except Exception as e:err(test,str(type(e).__name__)+": "+str(e)[:200])
            finally:
                test["passed"]=not test["errors"]
                RESULT["checks"].append(test)
                page.close()
        for group,path in (("ferry","/ferry/"),("booking","/booking/japan-cruise/")):
            page=ctx.new_page()
            test={"page":path,"viewport":name,"type":"direct_operators","errors":[]}
            try:
                if not load(page,path):err(test,"hub HTTP error")
                root=page.locator("#nf91-direct-operators")
                if root.count()!=1:err(test,"new direct operator hub missing")
                else:
                    cards=root.locator(".nf91-direct-item")
                    if cards.count()!=4:err(test,"expected 4 distinct route cards")
                    for route in URLS:
                        card=root.locator('.nf91-direct-item[data-route="'+route+'"]')
                        if card.count()!=1:err(test,"missing card for "+route);continue
                        a=card.locator("a.nf91-direct-primary")
                        b=card.locator("a.nf91-direct-secondary")
                        if a.count()!=1 or a.get_attribute("href")!=URLS[route]:
                            err(test,"incorrect one-click operator target for "+route)
                            continue
                        if b.count()!=1 or b.get_attribute("href")!=f"/guide/busan-{route}-ferry/#nf87-verified-operations":
                            err(test,"existing route detail link missing for "+route)
                        if a.get_attribute("target")!="_blank" or not {"noopener","noreferrer"}.issubset(set((a.get_attribute("rel") or "").split())):
                            err(test,"unsafe external tab for "+route)
                        if not geometry_ok(a,width):err(test,"tap target too small/offscreen for "+route)
                        bubble=page.locator(".kakao-float")
                        if width<=390 and bubble.count()==1 and bubble.is_visible():
                            page.wait_for_timeout(75)
                            if overlap(a,bubble):
                                err(test,"Kakao float overlaps one-click operator button for "+route)
                        if name in ("desktop","mobile") and a.count()==1:
                            event={"hub":group,"route":route,"viewport":name,"expected":URLS[route]}
                            try:
                                with page.expect_popup(timeout=10000) as info:
                                    a.click(timeout=14000)
                                newtab=info.value
                                try:newtab.wait_for_load_state("domcontentloaded",timeout=12000)
                                except Exception:pass
                                event["opened_url"]=newtab.url
                                actual_host=urlsplit(newtab.url).hostname or ""
                                event["correct_operator_domain"]=actual_host in CONF["allowed_hosts"][CONF["routes"][route]["provider"]]
                                if not event["correct_operator_domain"]:
                                    err(test,"one-click popup landed on wrong domain: "+route+" "+actual_host)
                                newtab.close()
                            except Exception as e:
                                event["error"]=str(e)[:160]
                                err(test,"one-click CTA did not open new operator tab: "+route)
                            RESULT["actual_clicks"].append(event)
                    root.scroll_into_view_if_needed()
                    root.screenshot(path=str(OUT/f"hub-{group}-{name}.png"),animations="disabled",timeout=24000)
                oldroot=page.locator(".nf86-hub-grid")
                if oldroot.count()!=1 or oldroot.locator("a").count()!=4:
                    err(test,"original four existing SEO/internal guide links disrupted")
                sw=page.evaluate("document.documentElement.scrollWidth")
                if sw>width+9:err(test,"hub horizontal overflow "+str(sw))
                test["scrollWidth"]=sw
            except Exception as e:err(test,str(type(e).__name__)+": "+str(e)[:200])
            finally:
                test["passed"]=not test["errors"]
                RESULT["checks"].append(test)
                page.close()
        ctx.close()
    browser.close()
RESULT["passed"]=not RESULT["errors"]
(OUT/"report.json").write_text(json.dumps(RESULT,ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps({"pass":RESULT["passed"],"page_viewport_checks":len(RESULT["checks"]),"actual_clicks":len(RESULT["actual_clicks"]),"errors":RESULT["errors"]},ensure_ascii=False,indent=2))
raise SystemExit(0 if RESULT["passed"] else 1)
