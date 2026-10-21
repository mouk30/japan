#!/usr/bin/env python3
"""V93: local built-site GA4 hook QA. Uses a fake public G-ID and intercepts outbound GA script.

Tests genuine user clicks, consent denial/revocation, route/source event taxonomy.
NEVER sends events to a real Google Analytics property.
"""
import json
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

BASE="http://127.0.0.1:8765"
CONF=json.loads(Path("scripts/v90_booking_link_targets.json").read_text("utf8"))
OUT=Path("audit-output/v93-click-analytics")
OUT.mkdir(parents=True,exist_ok=True)
RESULT={"suite":"V93","ga4_id":"synthetic G-TEST123456","checks":[],"sample_events":[],"errors":[]}

def check(condition,message):
    RESULT["checks"].append({"name":message,"pass":bool(condition)})
    if not condition:RESULT["errors"].append(message)

def events(page,name="ferry_operator_click"):
    return page.evaluate("""(requested) => (window.dataLayer || []).filter(a => a[0] === 'event' && a[1] === requested).map(a => ({name:a[1],params:a[2]}))""",name)

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
    ctx=browser.new_context(viewport={"width":390,"height":844},has_touch=True)
    ga_requests=[]
    ctx.route("https://www.googletagmanager.com/**",lambda route:(ga_requests.append(route.request.url),route.fulfill(status=200,content_type="application/javascript",body="")))
    page=ctx.new_page()
    page.goto(BASE+"/ferry/",wait_until="domcontentloaded")
    check(page.locator(".nf93-consent").count()==1,"Consent dialog visible with test GA4 stream configured")
    check(page.locator(".nf93-consent").is_visible(),"No pre-opt-in hidden collection")
    check(len(ga_requests)==0,"Zero requests to Google before visitor consent")
    check(page.evaluate("typeof window.gtag")=="undefined","No GA4 API before visitor consent")
    page.locator(".nf93-reject").click()
    check(not page.locator(".nf93-consent").is_visible(),"Reject closes opt-in prompt")
    check(len(ga_requests)==0,"No GA request after explicit refusal")
    # Verify first-party links remain usable after refusal; do not navigate away.
    a=page.locator('.nf91-direct-item[data-route="fukuoka"] a.nf91-direct-primary')
    with page.expect_popup(timeout=9000) as popup:
        a.click()
    popup.value.close()
    check(len(ga_requests)==0,"Ferry booking click remains functional and is NOT collected after refusal")
    check(len(events(page))==0,"No ferry_operator_click event when refused")
    page.locator(".nf93-manage").click()
    check(page.locator(".nf93-consent").is_visible(),"Visitor can reopen consent settings")
    page.locator(".nf93-accept").click()
    check(page.evaluate("typeof window.gtag")=="function","GTAG API initialized after explicit consent")
    check(len(ga_requests)>=1,"GA4 library loads only after consent")
    check(not page.locator(".nf93-consent").is_visible(),"Consent prompt hidden after decision")

    for loc in ("ferry","booking/japan-cruise"):
        page.goto(BASE+"/"+loc+"/",wait_until="domcontentloaded")
        for route,settings in CONF["routes"].items():
            card=page.locator('.nf91-direct-item[data-route="'+route+'"]')
            link=card.locator("a.nf91-direct-primary")
            check(link.get_attribute("href")==settings["primary"],f"{loc} {route} approved operator URL")
            count=len(events(page))
            with page.expect_popup(timeout=11000) as popup:
                link.click()
            target=popup.value.url
            popup.value.close()
            check((urlsplit(target).hostname or "").lower() in CONF["allowed_hosts"][settings["provider"]],
                  f"{loc} {route} valid operator popup")
            current=events(page)
            check(len(current)==count+1,f"{loc} {route} produces one event per real click, no duplicate")
            if current:
                fields=current[-1]["params"]
                check(fields.get("route")==route,f"{loc} {route} canonical route attribution")
                check(fields.get("placement")=="hub_card",f"{loc} {route} hub-card position")
                check(fields.get("operator")==settings["provider"],f"{loc} {route} operator code")
                check(fields.get("page_area")==("ferry_hub" if loc=="ferry" else "booking_hub"),
                      f"{loc} {route} page placement")
                check(set(fields).issubset({"route","placement","operator","destination_step","page_area","transport_type"}),
                      f"{loc} {route} no visitor PII / URLs / prices in event payload")
                RESULT["sample_events"].append({"route":route,"hub":loc,"event":current[-1]})
        page.screenshot(path=str(OUT/f"hub-{loc.replace('/','-')}-mobile-consented.png"),animations="disabled")

    for route,settings in CONF["routes"].items():
        page.goto(BASE+f"/guide/busan-{route}-ferry/",wait_until="domcontentloaded")
        for place,css in (("guide_hero",".nf86-intro"),("guide_end",".nf86-booking")):
            link=page.locator(css+" a.nf86-action-primary")
            prior=len(events(page))
            with page.expect_popup(timeout=11000) as popup:
                link.click()
            popup.value.close()
            now=events(page)
            check(len(now)==prior+1,f"{route} {place} exactly one booking event")
            if now:
                check(now[-1]["params"].get("placement")==place,f"{route} {place} correct CTA location")

    # Revoke permission. Old GTAG may remain loaded but no new user events may be emitted.
    page.locator(".nf93-manage").click()
    page.locator(".nf93-reject").click()
    before=len(events(page))
    with page.expect_popup(timeout=11000) as popup:
        page.locator(".nf86-intro a.nf86-action-primary").click()
    popup.value.close()
    check(len(events(page))==before,"Previously accepted consent can be revoked; subsequent clicks not recorded")
    page.reload(wait_until="domcontentloaded")
    check(len(ga_requests)>=1 and page.evaluate("typeof window.gtag")=="undefined",
          "After revocation and reload GA4 no longer initializes")
    check(not page.locator(".nf93-consent").is_visible(),
          "Stored explicit refusal honored on later page loads")
    browser.close()

RESULT["passed"]=len(RESULT["errors"])==0
(OUT/"report.json").write_text(json.dumps(RESULT,ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps({"passed":RESULT["passed"],"checks":len(RESULT["checks"]),"sample_events":len(RESULT["sample_events"]),"errors":RESULT["errors"]},ensure_ascii=False,indent=2))
raise SystemExit(0 if RESULT["passed"] else 1)
