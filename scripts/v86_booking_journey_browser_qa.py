#!/usr/bin/env python3
"""V86 live trust-and-conversion QA for six existing NIPPONFERRY pages."""
from pathlib import Path
import json, time
from playwright.sync_api import sync_playwright
BASE="https://www.nipponferry.com"
OUT=Path("audit-output/v86-booking-journey");OUT.mkdir(parents=True,exist_ok=True)
ROUTES={
 "osaka":("https://www.panstarcruise.com/","https://www.panstarcruise.com/product/osaka/info"),
 "fukuoka":("https://www.koreaferry.co.kr/rs/idv/reservation","https://www.koreaferry.kr/"),
 "shimonoseki":("https://www.kampuferry.co.jp/lang_kor/reserve/","https://www.kampuferry.co.jp/yoyaku/en/"),
 "tsushima":("https://www.panstarcruise.com/","https://www.panstarcruise.com/product/daemado/info")
}
SIZES=[("desktop",1440,900),("mobile",390,844),("small-mobile",360,780)]
report={"version":"V86","created_at_utc":time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),"tests":[],"issues":[]}
def expect(cond,msg,detail):
 if not cond:
  detail["issues"].append(msg);report["issues"].append(detail["path"]+" "+detail["viewport"]+": "+msg)
def load(page,path):
 last=None
 for attempt in range(4):
  try:
   resp=page.goto(BASE+path,wait_until="domcontentloaded",timeout=60000)
   page.wait_for_timeout(1400+attempt*600)
   if not resp or resp.status>=400:raise Exception("HTTP "+str(resp.status if resp else "unknown"))
   return
  except Exception as e:
   last=e
   page.wait_for_timeout(1200)
 raise last

with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
 for name,w,h in SIZES:
  ctx=browser.new_context(viewport={"width":w,"height":h},device_scale_factor=1,has_touch=name!="desktop")
  for route,(primary,secondary) in ROUTES.items():
   path=f"/guide/busan-{route}-ferry/"
   page=ctx.new_page();item={"path":path,"viewport":name,"width":w,"issues":[],"anchors":{}}
   try:
    load(page,path)
    for root in [".nf86-intro",".nf86-booking",".nf86-side"]:
     node=page.locator(root)
     expect(node.count()==1,f"{root} missing or duplicated",item)
     if node.count()!=1:continue
     main=node.locator("a.nf86-action-primary");other=node.locator("a.nf86-action-secondary")
     expect(main.count()==1 and other.count()==1, f"{root} official CTA pair missing", item)
     if main.count()!=1 or other.count()!=1:continue
     expect(main.get_attribute("href")==primary,f"{root} primary URL mismatched",item)
     expect(other.get_attribute("href")==secondary,f"{root} secondary URL mismatched",item)
     for a in [main,other]:
      expect(a.get_attribute("target")=="_blank",f"{root} target missing",item)
      rel=a.get_attribute("rel") or ""
      expect("noopener" in rel and "noreferrer" in rel,f"{root} rel missing",item)
      a.scroll_into_view_if_needed();box=a.bounding_box()
      if box:
       expect(box["width"]>=110 and box["height"]>=43, f"{root} CTA too small",item)
       expect(box["x"]>=-2 and box["x"]+box["width"]<=w+3,f"{root} CTA off viewport",item)
     if root in [".nf86-intro",".nf86-booking"]:
      try:node.screenshot(path=str(OUT/f"{route}-{name}-{root.replace('.','')}.png"),animations="disabled")
      except Exception as e:item["issues"].append(f"screenshot: {e}")
    text=page.content()
    expect("willer-travel.com/ko/ferry/" not in text,"unrelated domestic ferry CTA remains",item)
    expect('rel="canonical"' in text,"canonical missing",item)
    expect(page.locator('a[href="/ferry/"]').count()>0,"missing route hub return link",item)
    expect(page.locator('#ferry').count()==1,"legacy mid-article #ferry anchor removed",item)
    extent=page.evaluate('document.documentElement.scrollWidth')
    item["scrollWidth"]=extent
    expect(extent<=w+7,f"horizontal overflow {extent}px vs {w}px",item)
    item["anchors"]={"primary":primary,"secondary":secondary}
   except Exception as e:expect(False,str(e)[:220],item)
   finally:
    item["pass"]=not item["issues"];report["tests"].append(item);page.close()
  for path,identifier in [("/ferry/","ferry"),("/booking/japan-cruise/","booking")]:
   page=ctx.new_page();item={"path":path,"viewport":name,"width":w,"issues":[]}
   try:
    load(page,path)
    if identifier=="ferry":
     root=page.locator(".nf86-hub-steps");selector="div.nf86-hub-grid a"
     expect(page.locator(".nf84-route").count()==4,"V84 banners count changed",item)
    else:
     root=page.locator("#official-ferry-routes");selector=".nf86-hub-grid a"
    expect(root.count()==1,"route booking hub missing",item)
    if root.count()==1:
     links=root.locator(selector)
     expect(links.count()==4,f"expected 4 named route guide links got {links.count()}",item)
     for slug in ROUTES:
      href=f"/guide/busan-{slug}-ferry/#nf86-official-entry"
      expect(root.locator('a[href="'+href+'"]').count()==1,f"missing {slug} internal route entry",item)
     root.scroll_into_view_if_needed()
     try:root.screenshot(path=str(OUT/f"{identifier}-{name}.png"),animations="disabled")
     except Exception as e:item["issues"].append(f"screenshot: {e}")
    expect("willer-travel.com/ko/ferry/" not in page.content(),"unrelated domestic ferry service remains",item)
    extent=page.evaluate('document.documentElement.scrollWidth');item["scrollWidth"]=extent
    expect(extent<=w+7,f"horizontal overflow {extent}px vs {w}px",item)
   except Exception as e:expect(False,str(e)[:220],item)
   finally:
    item["pass"]=not item["issues"];report["tests"].append(item);page.close()
  ctx.close()
 browser.close()
report["passed"]=len(report["issues"])==0
(OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"passed":report["passed"],"tested":len(report["tests"]),"failed":len(report["issues"]),"issues":report["issues"]},ensure_ascii=False,indent=2))
raise SystemExit(0 if report["passed"] else 1)
