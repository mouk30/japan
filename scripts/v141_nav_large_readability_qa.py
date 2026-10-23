#!/usr/bin/env python3
"""V141 shared premium navigation: live CSS contrast, typography and responsive behavior.
Checks the BUILT site, not raw source headers, across representative content categories.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,os
root=Path(__file__).resolve().parents[1]
out=root/"audit-output/v141";out.mkdir(parents=True,exist_ok=True)
BASE=os.environ.get("NF_NAV_QA_BASE","http://127.0.0.1:8771").rstrip("/")
urls=["/","/japan/tokyo/","/things-to-do/cruise-ports/","/food/"]
widths=[320,390,768,1200,1440]
report={"version":"V141","date":"2026-10-23","base":BASE,"sites":urls,"widths":widths,"results":[],"errors":[],"screenshots":[]}
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
 for url in urls:
  for width in widths:
   page=browser.new_page(viewport={"width":width,"height":900},device_scale_factor=1)
   issues=[]
   try:
    response=page.goto(BASE+url,wait_until="domcontentloaded",timeout=45000)
    if response.status!=200:issues.append("HTTP "+str(response.status))
    header=page.locator(".nf301-header")
    if header.count()!=1:raise RuntimeError("no unified header")
    data=page.evaluate("""()=>{
      let h=document.querySelector('.nf301-header');
      let nav=h.querySelector('.nf301-primary'),sec=h.querySelector('.nf301-subrow');
      let r=e=>{const b=e.getBoundingClientRect();return{x:b.x,w:b.width,right:b.right,y:b.y,h:b.height}};
      let style=e=>({font:parseFloat(getComputedStyle(e).fontSize),color:getComputedStyle(e).color,display:getComputedStyle(e).display,opacity:getComputedStyle(e).opacity});
      return {scrollWidth:document.documentElement.scrollWidth,
        navItems:h.querySelectorAll('.nf301-primary>.nf301-item').length,
        subItems:sec.querySelectorAll('a').length,
        main:style(h.querySelector('.nf301-mainlink')),
        sub:style(sec.querySelector('a')),
        mobile:h.querySelector('.nf301-mobile-panel').dataset.open,
        menu:style(h.querySelector('.nf301-toggle')),
        header:r(h),control:r(h.querySelector('.nf301-mobile-controls'))};
    }""")
    if data["navItems"]!=6 or data["subItems"]!=8:issues.append("changed navigation structure")
    if data["scrollWidth"]>width+2:issues.append("page horizontal overflow "+str(data["scrollWidth"]))
    if width>=1200:
      if data["main"]["font"]<14.4:issues.append("top menu too small "+str(data["main"]["font"]))
      if data["sub"]["font"]<13.9:issues.append("subrow too small "+str(data["sub"]["font"]))
      if data["sub"]["display"]=="none":issues.append("subrow hidden")
      for group in ["japan","things","people","practical"]:
        item=page.locator(f'.nf301-item[data-dropdown="{group}"]')
        item.locator(".nf301-mainlink").hover()
        fly=item.locator(".nf301-flyout")
        # Hover remains a convenience. The disclosure button is the explicit
        # accessible toggle: test it too and measure only while visibly open.
        disclosure=item.locator(".nf301-disclose")
        disclosure.click()
        try:fly.wait_for(state="visible",timeout=2500)
        except:issues.append(group+" menu didn't open via disclosure");continue
        if disclosure.get_attribute("aria-expanded")!="true":
          issues.append(group+" aria-expanded did not sync")
        disclosure.focus()
        colors=fly.locator(".nf301-flygrid>a").first.evaluate("""(e)=>{
          let title=e.querySelector('span'),small=e.querySelector('small'),rect=e.getBoundingClientRect(),fly=e.closest('.nf301-flyout').getBoundingClientRect();
          return{title:parseFloat(getComputedStyle(title).fontSize),
          color:getComputedStyle(title).color,opacity:getComputedStyle(title).opacity,
          desc:small?parseFloat(getComputedStyle(small).fontSize):null,
          bg:getComputedStyle(e).backgroundColor,
          height:rect.height,flyLeft:fly.left,flyRight:fly.right,flyWidth:fly.width}
        }""")
        if colors["title"]<19.5:issues.append(group+" text small "+str(colors["title"]))
        if colors["desc"] and colors["desc"]<13.8:issues.append(group+" description small")
        if colors["height"]<90:issues.append(group+" card height small")
        if colors["opacity"]!="1":issues.append(group+" faded title opacity")
        if colors["flyLeft"]<-1 or colors["flyRight"]>width+1:issues.append(group+" dropdown beyond viewport")
        if group=="japan" and url=="/" and width==1440:
          fly.screenshot(path=str(out/"home-mega-desktop-1440.png"),animations="disabled")
          report["screenshots"].append("home-mega-desktop-1440.png")
        page.keyboard.press("Escape")
    else:
      toggle=header.locator(".nf301-toggle")
      if not toggle.is_visible():issues.append("mobile hamburger not visible")
      toggle.click()
      panel=page.locator("#nf301-mobile-panel")
      if panel.get_attribute("data-open")!="true":issues.append("mobile menu failed to open")
      if page.locator(".kakao-float").count()>0:
        hidden=page.locator(".kakao-float").evaluate("(e)=>getComputedStyle(e).visibility==='hidden'")
        if not hidden:issues.append("floating Kakao button still covers open mobile menu")
      group=panel.locator('.nf301-mob-group[data-mob-group="japan"]')
      btn=group.locator(".nf301-mob-expand")
      btn.click()
      opts=group.locator(".nf301-mob-options")
      if opts.get_attribute("data-open")!="true":issues.append("mobile submenu did not expand")
      font=opts.locator("a").first.evaluate("(e)=>parseFloat(getComputedStyle(e).fontSize)")
      top_font=group.locator(".nf301-mob-heading>a").evaluate("(e)=>parseFloat(getComputedStyle(e).fontSize)")
      if font<16.5:issues.append("mobile submenu too small: "+str(font))
      if top_font<18:issues.append("mobile top category too small: "+str(top_font))
      if url=="/" and width in (320,390):
        panel.screenshot(path=str(out/f"home-mobile-menu-{width}.png"),animations="disabled",timeout=30000)
        report["screenshots"].append(f"home-mobile-menu-{width}.png")
      page.keyboard.press("Escape")
      if panel.get_attribute("data-open")!="false":issues.append("mobile Escape not closing")
    report["results"].append({"path":url,"width":width,"issues":issues})
   except Exception as e:
    issues.append("browser: "+str(e)[:260])
    report["results"].append({"path":url,"width":width,"issues":issues})
   report["errors"].extend(f"{url} {width}px: {i}" for i in issues)
   page.close()
 browser.close()
report["passed"]=not report["errors"] and len(report["results"])==len(urls)*len(widths)
(out/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps({"passed":report["passed"],"screens":len(report["results"]),"screenshots":len(report["screenshots"]),"errors":report["errors"]},ensure_ascii=False))
raise SystemExit(0 if report["passed"] else 1)
