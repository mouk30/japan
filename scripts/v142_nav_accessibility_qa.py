#!/usr/bin/env python3
"""V142: built-site and optionally public-site premium navigation accessibility tests.
Tests 6 viewport sizes, 6 route types, current-category auto expansion, focus
containment, Escape, accordion consistency, existing SEO and menu link counts.
"""
from pathlib import Path
import os,json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"audit-output/v142"; OUT.mkdir(parents=True,exist_ok=True)
BASE=os.environ.get("NF_V142_BASE","http://127.0.0.1:8782").rstrip("/")
SAMPLES=[
 ("/",None),
 ("/japan/tokyo/","japan"),
 ("/food/","things"),
 ("/things-to-do/travel-companions/","people"),
 ("/practical/","practical"),
 ("/things-to-do/cruise-ports/",None)
]
WIDTHS=[320,390,768,1199,1200,1440]
report={"version":"V142","target":BASE,"widths":WIDTHS,
        "routes":[x[0] for x in SAMPLES],"results":[],"errors":[],
        "screenshots":[],"new_articles":0,"seo_or_links_changed":False}
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
 for route,active_group in SAMPLES:
  for width in WIDTHS:
   page=browser.new_page(viewport={"width":width,"height":900},device_scale_factor=1)
   errors=[];info={"route":route,"width":width}
   try:
    response=page.goto(BASE+route,wait_until="domcontentloaded",timeout=45000)
    if not response or response.status!=200:raise RuntimeError("HTTP not 200")
    header=page.locator(".nf301-header")
    if header.count()!=1:raise RuntimeError("canonical site header not found")
    if page.locator('link[rel="canonical"]').count()!=1:errors.append("missing canonical")
    if page.locator('title').count()!=1:errors.append("missing title")
    if page.locator('.nf301-primary .nf301-item').count()!=6:errors.append("top links changed")
    if page.locator('.nf301-subrow a').count()!=8:errors.append("secondary links changed")
    if page.locator('.nf301-mob-group').count()!=4:errors.append("accordion groups changed")
    sw=page.evaluate("document.documentElement.scrollWidth")
    if sw>width+2:errors.append(f"horizontal page overflow {sw}>{width}")
    if width<1200:
     toggle=header.locator(".nf301-toggle")
     if not toggle.is_visible():errors.append("hamburger hidden")
     toggle.click()
     panel=header.locator("#nf301-mobile-panel")
     if panel.get_attribute("data-open")!="true":errors.append("mobile overlay didn't open")
     if toggle.get_attribute("aria-expanded")!="true":errors.append("aria-expanded false while menu is open")
     if page.evaluate("document.querySelector('#nf301-mobile-panel').inert"):errors.append("open panel incorrectly inert")
     if not page.evaluate("document.documentElement.classList.contains('nf301-menu-open')"):errors.append("body scroll lock missing")
     if active_group:
      group=header.locator(f'.nf301-mob-group[data-mob-group="{active_group}"]')
      btn=group.locator('.nf301-mob-expand')
      opts=group.locator('.nf301-mob-options')
      if btn.get_attribute('aria-expanded')!='true' or opts.get_attribute('data-open')!='true':
       errors.append("active category did not expand: "+active_group)
      others=header.locator('.nf301-mob-expand[aria-expanded="true"]')
      if others.count()!=1:errors.append("multiple default accordion groups expanded")
     else:
      if header.locator('.nf301-mob-expand[aria-expanded="true"]').count()!=0:
       errors.append("unrelated category autoexpanded")
     first=header.locator(".nf301-brand")
     last=header.locator('.nf301-mobile-foot a').last
     last.focus()
     page.keyboard.press("Tab")
     if not first.evaluate("(e)=>document.activeElement===e"):errors.append("Tab escaped open menu instead of wrapping to brand")
     first.focus()
     page.keyboard.press("Shift+Tab")
     if not last.evaluate("(e)=>document.activeElement===e"):errors.append("reverse Tab escaped instead of wrapping to last menu link")
     if route=="/" and width in (320,390):
      japan=header.locator('.nf301-mob-group[data-mob-group="japan"] .nf301-mob-expand')
      japan.click()
      if japan.get_attribute("aria-expanded")!="true":errors.append("manual Japan disclosure fails")
      pic=f"home-accordion-{width}.png"
      panel.screenshot(path=str(OUT/pic),animations="disabled",timeout=20000)
      report["screenshots"].append(pic)
     if route=="/japan/tokyo/" and width==390:
      pic="tokyo-current-menu-390.png"
      panel.screenshot(path=str(OUT/pic),animations="disabled",timeout=20000)
      report["screenshots"].append(pic)
     page.keyboard.press("Escape")
     if panel.get_attribute('data-open')!='false':errors.append("Escape failed to close overlay")
     if toggle.get_attribute('aria-expanded')!='false':errors.append("aria-expanded true when closed")
     if not page.evaluate("document.querySelector('#nf301-mobile-panel').inert"):errors.append("closed panel remains focusable")
     if page.evaluate("document.documentElement.classList.contains('nf301-menu-open')"):errors.append("scroll lock retained after closing")
     if not toggle.evaluate("(e)=>document.activeElement===e"):errors.append("Escape failed to restore menu button focus")
     info["mobile"]="menu/focus/active category/Escape"
    else:
     item=header.locator('.nf301-item[data-dropdown="japan"]')
     button=item.locator('.nf301-disclose')
     button.click()
     fly=item.locator('.nf301-flyout')
     state=item.evaluate("""(e)=>({open:e.dataset.open,source:e.dataset.openSource,
       aria:e.querySelector('.nf301-disclose').getAttribute('aria-expanded'),
       css:getComputedStyle(e.querySelector('.nf301-flyout')).display,
       hovered:e.matches(':hover'),focused:e.contains(document.activeElement),
       scripts:document.querySelectorAll('script[src*="v301-nav.js"]').length})""")
     try:fly.wait_for(state="visible",timeout=3500)
     except Exception as exc:
      later=item.evaluate("""(e)=>({open:e.dataset.open,source:e.dataset.openSource,
       aria:e.querySelector('.nf301-disclose').getAttribute('aria-expanded'),
       css:getComputedStyle(e.querySelector('.nf301-flyout')).display})""")
      raise RuntimeError("desktop disclosure diagnostic before="+str(state)+" after="+str(later)) from exc
     if button.get_attribute("aria-expanded")!="true":errors.append("desktop aria-expanded didn't sync")
     if fly.locator('.nf301-flygrid a').count()!=8:errors.append("destination links missing in flyout")
     if width==1440 and route=="/":
      pic="home-japan-desktop-1440.png"
      fly.screenshot(path=str(OUT/pic),animations="disabled",timeout=20000)
      report["screenshots"].append(pic)
     page.keyboard.press("Escape")
     if button.get_attribute("aria-expanded")!="false":errors.append("desktop Escape didn't close flyout")
     info["desktop"]="dropdown/aria/Escape"
    info["errors"]=errors
   except Exception as e:
    errors.append("browser error: "+str(e)[:200])
    info["errors"]=errors
   report["results"].append(info)
   report["errors"].extend(f"{route} {width}px: {e}" for e in errors)
   page.close()
 browser.close()
report["passed"]=len(report["results"])==len(SAMPLES)*len(WIDTHS) and not report["errors"]
(OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps({"passed":report["passed"],"checks":len(report["results"]),
                  "screenshots":len(report["screenshots"]),"errors":report["errors"]},ensure_ascii=False))
raise SystemExit(0 if report["passed"] else 1)
