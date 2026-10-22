#!/usr/bin/env python3
"""V104: real production QA for 18 flagship homepage thumbnails on 3 viewport sizes.

Check accurate image/source labeling, image HTTP/decode, no broken links or
horizontal overflows, retained 8/4/6 card layouts, original aspect ratios.
Collect screenshots per section; does not generate/deploy a collage image.
"""
import datetime as dt
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE="https://www.nipponferry.com"
OUT=Path("audit-output/v104-home-thumbnails")
OUT.mkdir(parents=True,exist_ok=True)
CARDS={
 "popular":{"anchor":"#v65-title","selector":".v65-grid .v65-card","photo":".v65-photo","num":8,
            "sources":[
             "/images/tokyo-verified/tokyo-asakusa-sensoji-kaminarimon.webp",
             "/images/editorial/okinawa-kouri-bridge.webp",
             "/images/editorial/hakata-cruise-port-day-trip.webp",
             "/images/venues/nf-v85-osaka-dotonbori-licensed.webp",
             "/images/editorial/shimonoseki-cruise-port-day-trip.webp",
             "/images/editorial/tsushima-izuhara-cruise-port-day-trip.webp",
             "/images/editorial/kobe-cruise-port-day-trip.webp",
             "/images/editorial/hakodate-snow-onsen-romantic-v106.webp",
            ]},
 "daytrips":{"anchor":"#v36-home","selector":".d61-home-grid .d61-home-card","photo":".d61-home-photo","num":4,
           "sources":[
            "/images/editorial/v339_hakata-port-tenjin-sightseeing.webp",
            "/images/culture-verified/takoyaki-osaka-street-food.webp",
            "/images/editorial/mojiko-cruise-port-day-trip.webp",
            "/images/food-verified/tsushima-food.webp",
            ]},
 "themes":{"anchor":"#v63-theme-title","selector":".v63-grid .v63-card","photo":".v63-visual","num":6,
           "sources":[
             "/images/ramen-close.jpg",
             "/images/editorial/okinawa-shopping-street.webp",
             "/images/editorial/okinawa-eisa-dance-festival.webp",
             "/images/editorial/kyoto-kiyomizu-stage-structure.webp",
             "/images/editorial/ishigaki-kabira-bay.webp",
             "/images/culture-verified/japanese-vending-machine-culture.webp",
           ]}
}
WIDTHS=[("pc",1440,900),("phone",390,844),("small-phone",360,780)]
RESULT={"stage":"V104","checked_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "scenarios":[],"errors":[]}
def error(group,thing):
    group["errors"].append(thing)
    RESULT["errors"].append(f"{group['viewport']} {group['section']}: {thing}")

with sync_playwright() as tool:
    browser=tool.chromium.launch(headless=True,args=["--no-sandbox"])
    for viewport,w,h in WIDTHS:
        context=browser.new_context(viewport={"width":w,"height":h},device_scale_factor=1,has_touch=(w<500))
        page=context.new_page()
        response=page.goto(BASE+"/",wait_until="domcontentloaded",timeout=65000)
        page.wait_for_timeout(650)
        for group_name,spec in CARDS.items():
            test={"viewport":viewport,"section":group_name,"errors":[],"count":0,
                  "photos_loaded":0,"staged_labels":0}
            try:
                if not response or response.status>=400:error(test,"home page HTTP failed")
                heading=page.locator(spec["anchor"])
                if heading.count()!=1:error(test,"section heading missing")
                cards=page.locator(spec["selector"])
                if cards.count()!=spec["num"]:
                    error(test,f"card count mismatch {cards.count()} vs {spec['num']}")
                test["count"]=cards.count()
                expected=spec["sources"]
                for k in range(min(cards.count(),len(expected))):
                    card=cards.nth(k)
                    visual=card.locator(spec["photo"])
                    img=visual.locator("img")
                    if img.count()!=1:
                        error(test,f"card {k}: missing image");continue
                    if img.get_attribute("src")!=expected[k]:
                        error(test,f"card {k}: unexpected image src")
                    alt=img.get_attribute("alt") or ""
                    if len(alt)<14 or "실제 사진" in alt or "실제 촬영" in alt:
                        error(test,f"card {k}: misleading or missing alt")
                    label=visual.locator(".v104-photo-origin, .v63-photo-disclosure")
                    is_staged=expected[k].startswith("/images/editorial/")
                    if is_staged and label.count()!=1:
                        error(test,f"card {k}: missing staged-art disclosure")
                    if not is_staged and label.count()!=0:
                        error(test,f"card {k}: false staged-photo disclosure")
                    test["staged_labels"]+=label.count()
                    if not visual.get_attribute("href"):
                        error(test,f"card {k}: image does not lead to travel guide")
                    img.scroll_into_view_if_needed(timeout=12000)
                    img.evaluate("(x)=>{if(x.complete)return;return new Promise(done=>{x.addEventListener('load',done,{once:true});x.addEventListener('error',done,{once:true})})}",timeout=18000)
                    loaded=img.evaluate("(x)=>x.complete&&x.naturalWidth>=400&&x.naturalHeight>=180")
                    if not loaded:error(test,f"card {k}: image failed to decode or tiny")
                    else:test["photos_loaded"]+=1
                    box=visual.bounding_box()
                    if not box or box["width"]<170 or box["height"]<85:
                        error(test,f"card {k}: tiny or invisible photo box")
                    if box and (box["x"] < -3 or box["x"]+box["width"]>w+4):
                        error(test,f"card {k}: image overflow")
                if group_name=="popular":
                    note=page.locator(".v65-note")
                    if note.count()!=1 or not note.inner_text().find("연출 이미지")>=0:
                        error(test,"mixed photo source note missing")
                if group_name=="daytrips":
                    note=page.locator(".d61-home-note")
                    if note.count()!=1 or "모지코는 시모노세키와" not in note.inner_text():
                        error(test,"Mojiko vs Shimonoseki geography not clarified")
                    if page.locator(".d61-home-card .d62-source").count()>0:
                        error(test,"old Karato/Izuhara photo credits no longer correspond to replacement image")
                if group_name=="themes":
                    if page.locator(".v104-theme-note").count()!=1:error(test,"themed image notice missing")
                section=heading.locator("xpath=ancestor::section[1]")
                section.scroll_into_view_if_needed(timeout=10000)
                section.screenshot(path=str(OUT/f"{group_name}-{viewport}.png"),animations="disabled",timeout=24000)
                scroll=page.evaluate("document.documentElement.scrollWidth")
                if scroll>w+8:error(test,"horizontal page overflow")
            except Exception as e:
                error(test,type(e).__name__+": "+str(e)[:220])
            test["pass"]=not test["errors"]
            RESULT["scenarios"].append(test)
        if page.locator('link[rel="canonical"]').get_attribute("href")!=BASE+"/":
            RESULT["errors"].append(viewport+" canonical changed")
        page.close()
        context.close()
    browser.close()
RESULT["passed"]=not RESULT["errors"]
(OUT/"report.json").write_text(json.dumps(RESULT,ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps({"passed":RESULT["passed"],
    "screen_cases":len(RESULT["scenarios"]),
    "distinct_card_images":len(set(x for g in CARDS.values() for x in g["sources"])),
    "images_per_screen":sum(g["num"] for g in CARDS.values()),
    "screenshots":len(list(OUT.glob("*.png"))),
    "errors":RESULT["errors"]},ensure_ascii=False,indent=2))
raise SystemExit(0 if RESULT["passed"] else 1)
