#!/usr/bin/env python3
"""V90 real production booking link tap-target, official redirects and mobile QA.

No form submission, checkout or login; opens only the public provider link.
Screenshots and metadata saved as artifacts of read-only QA.
"""
import json,datetime as dt,time
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
BASE="https://www.nipponferry.com"
OUT=Path("audit-output/v90-booking-mobile");OUT.mkdir(parents=True,exist_ok=True)
CONFIG=json.loads(Path("scripts/v90_booking_link_targets.json").read_text("utf8"))
SIZES=[("desktop",1440,900),("mobile",390,844),("small-mobile",360,780)]
report={"version":"V90","checked_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"pages":[],"clicks":[],"errors":[]}
def issue(data,s):data.setdefault("errors",[]).append(s);report["errors"].append(data["page"]+" "+data.get("viewport","")+": "+s)
def visit(page,rel):
 resp=page.goto(BASE+rel,wait_until="domcontentloaded",timeout=60000)
 page.wait_for_timeout(1000)
 return resp
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
 for vp,w,h in SIZES:
  ctx=browser.new_context(viewport={"width":w,"height":h},device_scale_factor=1,is_mobile=False,has_touch=w<=390)
  for route,entry in CONFIG["routes"].items():
   path=f"/guide/busan-{route}-ferry/"
   page=ctx.new_page();data={"page":path,"viewport":vp,"errors":[]}
   try:
    resp=visit(page,path)
    if not resp or resp.status>=400:issue(data,"HTTP failure")
    for section in (".nf86-intro",".nf86-booking",".nf86-side"):
     root=page.locator(section)
     if root.count()!=1:
      issue(data,section+" unavailable");continue
     one=root.locator("a.nf86-action-primary");two=root.locator("a.nf86-action-secondary")
     if one.count()!=1 or two.count()!=1:
      issue(data,section+" two actions missing");continue
     if one.get_attribute("href")!=entry["primary"] or two.get_attribute("href")!=entry["secondary"]:
      issue(data,section+" target not matching verified provider")
     for link in (one,two):
      link.scroll_into_view_if_needed()
      bounds=link.bounding_box()
      if not bounds or bounds["height"]<44 or bounds["x"] < -2 or bounds["x"]+bounds["width"] > w+3:
       issue(data,section+" too small/offscreen tap target")
      if link.get_attribute("target")!="_blank" or "noopener" not in (link.get_attribute("rel") or ""):
       issue(data,section+" insecure tab target")
     if section in (".nf86-intro",".nf86-booking"):
      root.screenshot(path=str(OUT/f"{route}-{vp}-{section[1:]}.png"),animations="disabled",timeout=20000)
    note=page.locator(".nf86-intro .nf90-arrival-note")
    if note.count()!=1 or not note.is_visible():
     issue(data,"route-specific landing-page notice missing")
    else:
     if note.locator('a[href="'+entry["secondary"]+'"]').count()!=1:
      issue(data,"fallback to operator route/instructions missing")
    if vp!="desktop":
     bubble=page.locator(".kakao-float")
     if bubble.count()==1 and bubble.is_visible():
      b=bubble.bounding_box()
      # Geometry measured after scrolling to each action; floating bubble must not
      # physically obscure the primary or backup booking button.
      for selector in [".nf86-intro a.nf86-action-primary",".nf86-intro a.nf86-action-secondary",".nf86-booking a.nf86-action-primary"]:
       a=page.locator(selector)
       a.scroll_into_view_if_needed()
       page.wait_for_timeout(100)
       bb=bubble.bounding_box();ab=a.bounding_box()
       if bb and ab and max(bb["x"],ab["x"])<min(bb["x"]+bb["width"],ab["x"]+ab["width"]) and max(bb["y"],ab["y"])<min(bb["y"]+bb["height"],ab["y"]+ab["height"]):
        issue(data,"Kakao floating bubble obstructs booking CTA: "+selector)
    sw=page.evaluate("document.documentElement.scrollWidth")
    if sw>w+9:issue(data,f"page horizontal overflow {sw}px")
    canonical=page.locator('link[rel="canonical"]')
    if canonical.count()!=1 or canonical.get_attribute("href")!=BASE+path:issue(data,"SEO canonical changed")
    # Native user click opens a new browser tab, not a fake/test-only navigation.
    if vp in ("mobile","desktop"):
     btn=page.locator(".nf86-intro a.nf86-action-primary")
     btn.scroll_into_view_if_needed()
     click={"page":path,"viewport":vp,"expected":entry["primary"],"outcome":"unverified"}
     try:
      with page.expect_popup(timeout=9000) as popupinfo:
       btn.click(timeout=12000)
      pop=popupinfo.value
      try:pop.wait_for_load_state("domcontentloaded",timeout=12000)
      except Exception:pass # External operators can deliberately block browsers.
      target=pop.url
      click["opened_url"]=target
      provider_host=(urlsplit(target).hostname or "").lower()
      if provider_host not in CONFIG["allowed_hosts"][entry["provider"]]:
       issue(data,"clicked tab landed on unexpected domain "+provider_host)
       click["outcome"]="wrong_domain"
      else:
       click["outcome"]="official_domain_opened"
      pop.close()
     except Exception as e:
      click["error"]=str(e)[:160]
      issue(data,"primary booking CTA did not open a new official tab")
     report["clicks"].append(click)
   except Exception as e:issue(data,type(e).__name__+": "+str(e)[:190])
   finally:
    data["passed"]=not data["errors"];report["pages"].append(data);page.close()
  for section,path in [("ferry","/ferry/"),("booking","/booking/japan-cruise/")]:
   page=ctx.new_page();data={"page":path,"viewport":vp,"errors":[]}
   try:
    resp=visit(page,path)
    if not resp or resp.status>=400:issue(data,"hub HTTP error")
    root=page.locator(".nf86-hub-steps" if section=="ferry" else "#official-ferry-routes")
    if root.count()!=1:issue(data,"booking route-selector hub missing")
    else:
     buttons=root.locator(".nf86-hub-grid a")
     if buttons.count()!=4:issue(data,"not four named routes")
     for route in CONFIG["routes"]:
      href=f"/guide/busan-{route}-ferry/#nf86-official-entry"
      if buttons.locator('xpath=..').count() < 0:pass
      if root.locator('a[href="'+href+'"]').count()!=1:issue(data,"route choice not linked to "+route)
     root.scroll_into_view_if_needed()
     root.screenshot(path=str(OUT/f"hub-{section}-{vp}.png"),animations="disabled",timeout=25000)
    sw=page.evaluate("document.documentElement.scrollWidth")
    if sw>w+9:issue(data,f"hub horizontal overflow {sw}px")
   except Exception as e:issue(data,type(e).__name__+": "+str(e)[:190])
   finally:
    data["passed"]=not data["errors"];report["pages"].append(data);page.close()
  ctx.close()
 browser.close()
report["passed"]=not report["errors"]
(OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps({"pass":report["passed"],"pages":len(report["pages"]),"popup_clicks":len(report["clicks"]),"issues":report["errors"],"outcomes":report["clicks"]},ensure_ascii=False,indent=2))
raise SystemExit(0 if report["passed"] else 1)
