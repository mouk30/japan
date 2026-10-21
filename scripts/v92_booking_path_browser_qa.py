#!/usr/bin/env python3
"""V92: test an actual reader's route->provider journey and absent duplicate CTAs.

Desktop 1440px, phones 390px & 360px. No booking form submission or claims of availability.
"""
import datetime as dt
import json
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

BASE="https://www.nipponferry.com"
ROUTES=json.loads(Path("scripts/v90_booking_link_targets.json").read_text("utf8"))
OUT=Path("audit-output/v92-final-booking-ux")
OUT.mkdir(parents=True,exist_ok=True)
CASES=[("desktop",1440,900),("mobile",390,844),("small-mobile",360,780)]
record={"version":"V92","checked_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"pages":[],"outbound_clicks":[],"internal_journeys":[],"errors":[]}
def fail(item,message):
    item["errors"].append(message)
    record["errors"].append(f"{item['viewport']} {item['path']}: {message}")
def open_page(page,path):
    r=page.goto(BASE+path,wait_until="domcontentloaded",timeout=60000)
    page.wait_for_timeout(900)
    return bool(r and r.status<400)
def rect_overlap(a,b):
    x=a.bounding_box();y=b.bounding_box()
    return bool(x and y and max(x["x"],y["x"])<min(x["x"]+x["width"],y["x"]+y["width"]) and max(x["y"],y["y"])<min(x["y"]+x["height"],y["y"]+y["height"]))
def validate_link(el,url,width,item,external):
    if el.count()!=1:
        fail(item,"missing or repeated action "+url);return
    if el.get_attribute("href")!=url:fail(item,"wrong action href "+str(el.get_attribute("href")))
    if external and (el.get_attribute("target")!="_blank" or not {"noopener","noreferrer"}.issubset(set((el.get_attribute("rel") or "").split()))):
        fail(item,"unsafe official external link")
    el.scroll_into_view_if_needed()
    r=el.bounding_box()
    if not r or r["height"]<44 or r["x"]< -2 or r["x"]+r["width"]>width+3:
        fail(item,"small or horizontally clipped action")
def popup_check(page,el,expected_provider,item,context):
    evt={"viewport":item["viewport"],"source":item["path"],"context":context,"provider":expected_provider}
    try:
        with page.expect_popup(timeout=12000) as info:
            el.click(timeout=13000)
        pop=info.value
        try:pop.wait_for_load_state("domcontentloaded",timeout=14000)
        except Exception:pass
        evt["landing"]=pop.url
        evt["official_host"]=(urlsplit(pop.url).hostname or "").lower() in ROUTES["allowed_hosts"][expected_provider]
        if not evt["official_host"]:fail(item,"clicked action opened unexpected operator domain")
        pop.close()
    except Exception as ex:
        evt["error"]=str(ex)[:170]
        fail(item,"actual external click did not open official browser tab")
    record["outbound_clicks"].append(evt)
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
    for variant,width,height in CASES:
        context=browser.new_context(viewport={"width":width,"height":height},device_scale_factor=1,has_touch=variant!="desktop")
        for route,cfg in ROUTES["routes"].items():
            path=f"/guide/busan-{route}-ferry/"
            page=context.new_page()
            item={"path":path,"viewport":variant,"type":"article","errors":[]}
            try:
                if not open_page(page,path):fail(item,"page HTTP failure")
                hero=page.locator(".nf86-intro")
                middle=page.locator("#ferry.nf86-booking")
                side=page.locator(".nf86-side")
                if hero.count()!=1 or middle.count()!=1 or side.count()!=1:fail(item,"required article decision sections missing")
                for panel in (hero,middle):
                    if panel.count()==1:
                        panel.scroll_into_view_if_needed()
                        panel.screenshot(path=str(OUT/f"{route}-{variant}-{'hero' if panel==hero else 'end'}.png"),animations="disabled",timeout=20000)
                validate_link(hero.locator("a.nf86-action-primary"),cfg["primary"],width,item,True)
                validate_link(hero.locator("a.nf86-action-secondary"),cfg["secondary"],width,item,True)
                validate_link(middle.locator("a.nf86-action-primary"),cfg["primary"],width,item,True)
                if middle.locator("a.nf86-action-secondary").count() or side.locator("a.nf86-action").count():
                    fail(item,"duplicate external booking buttons still present in article end or sidebar")
                if page.locator("a.nf86-action").count()!=3:
                    fail(item,"not exactly three rather than previous six article CTAs")
                validate_link(middle.locator("a.nf92-facts-link"),"#nf87-verified-operations",width,item,False)
                validate_link(side.locator("a.nf92-side-link"),"#nf86-official-entry",width,item,False)
                if hero.locator(".nf92-route-note a").count()!=0:
                    fail(item,"redundant operator link remained in landing explanation")
                preflight=hero.locator(".nf91-preflight li")
                if preflight.count()!=3:fail(item,"essential route preflight checklist has changed")
                if page.locator('link[rel="canonical"]').get_attribute("href")!=BASE+path:
                    fail(item,"canonical URL modified")
                if page.locator('link[href^="/nf-v92-booking-ux.css"]').count()!=1:
                    fail(item,"V92 scoped styles missing")
                if variant!="desktop":
                    chat=page.locator(".kakao-float")
                    if chat.count()==1 and chat.is_visible():
                        for a in (hero.locator("a.nf86-action-primary"),middle.locator("a.nf86-action-primary")):
                            a.scroll_into_view_if_needed()
                            page.wait_for_timeout(70)
                            if rect_overlap(a,chat):fail(item,"Kakao chat covers external booking button")
                if page.evaluate("document.documentElement.scrollWidth")>width+8:
                    fail(item,"horizontal page overflow")
            except Exception as ex:
                fail(item,type(ex).__name__+": "+str(ex)[:185])
            item["passed"]=not item["errors"];record["pages"].append(item);page.close()
        for loc,path in [("ferry","/ferry/"),("booking","/booking/japan-cruise/")]:
            page=context.new_page()
            item={"path":path,"viewport":variant,"type":"route_selector","errors":[]}
            try:
                if not open_page(page,path):fail(item,"booking/ferry hub HTTP error")
                wrapper=page.locator("#nf91-direct-operators")
                if wrapper.count()!=1:fail(item,"single route selector absent")
                if page.locator(".nf86-hub-grid").count()!=0:
                    fail(item,"duplicate four-choice guide grid remains")
                if wrapper.locator(".nf91-direct-item").count()!=4:
                    fail(item,"incorrect route selector card count")
                for route,cfg in ROUTES["routes"].items():
                    card=wrapper.locator(f'.nf91-direct-item[data-route="{route}"]')
                    if card.count()!=1:fail(item,"missing route card "+route);continue
                    primary=card.locator("a.nf91-direct-primary")
                    validate_link(primary,cfg["primary"],width,item,True)
                    details=card.locator("a.nf91-direct-secondary")
                    validate_link(details,f"/guide/busan-{route}-ferry/#nf87-verified-operations",width,item,False)
                    if card.locator("a").count()!=2:fail(item,"more than one external CTA and one guide info link: "+route)
                    if variant!="desktop":
                        chat=page.locator(".kakao-float")
                        if chat.count()==1 and chat.is_visible():
                            primary.scroll_into_view_if_needed()
                            page.wait_for_timeout(100)
                            if rect_overlap(primary,chat):fail(item,"Kakao covers direct operator button "+route)
                    if variant in ("desktop","mobile"):
                        popup_check(page,primary,cfg["provider"],item,"hub_"+loc+"_"+route)
                    if variant=="desktop":
                        # One click from each hub card must land at the existing V87 dated fare/operations facts.
                        details.click(timeout=15000)
                        page.wait_for_load_state("domcontentloaded",timeout=20000)
                        page.wait_for_timeout(450)
                        jump={"from":path,"route":route,"destination":page.url,
                              "facts_present":page.locator("#nf87-verified-operations").count()==1}
                        record["internal_journeys"].append(jump)
                        if urlsplit(page.url).fragment!="nf87-verified-operations" or not jump["facts_present"]:
                            fail(item,"factual guide deep-link failed "+route)
                        page.goto(BASE+path,wait_until="domcontentloaded",timeout=60000)
                        page.wait_for_timeout(600)
                        wrapper=page.locator("#nf91-direct-operators")
                wrapper.scroll_into_view_if_needed()
                wrapper.screenshot(path=str(OUT/f"hub-{loc}-{variant}.png"),animations="disabled",timeout=22000)
                if page.evaluate("document.documentElement.scrollWidth")>width+8:
                    fail(item,"hub horizontal overflow")
                if page.locator('link[rel="canonical"]').get_attribute("href")!=BASE+path:
                    fail(item,"hub canonical changed")
            except Exception as ex:
                fail(item,type(ex).__name__+": "+str(ex)[:185])
            item["passed"]=not item["errors"];record["pages"].append(item);page.close()
        context.close()
    browser.close()
record["passed"]=not record["errors"]
(OUT/"report.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps({"passed":record["passed"],"screens":len(record["pages"]),"outbound_clicks":len(record["outbound_clicks"]),"deep_links":len(record["internal_journeys"]),"errors":record["errors"]},ensure_ascii=False,indent=2))
raise SystemExit(0 if record["passed"] else 1)
