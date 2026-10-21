#!/usr/bin/env python3
"""V86 live trust-and-conversion QA for six existing NIPPONFERRY pages."""
from pathlib import Path
import json, time
from playwright.sync_api import sync_playwright
BASE="https://www.nipponferry.com"
OUT=Path("audit-output/v86-booking-journey");OUT.mkdir(parents=True,exist_ok=True)
ROUTES={name:(row["primary"],row["secondary"]) for name,row in json.loads((Path(__file__).resolve().parent/"v90_booking_link_targets.json").read_text("utf8"))["routes"].items()}
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
     expected_primary=1 if root!=".nf86-side" else 0
     expected_secondary=1 if root==".nf86-intro" else 0
     expect(main.count()==expected_primary and other.count()==expected_secondary, f"{root} deduplicated official CTA count incorrect",item)
     if main.count()==expected_primary and expected_primary:
      expect(main.get_attribute("href")==primary,f"{root} primary URL mismatched",item)
     if other.count()==expected_secondary and expected_secondary:
      expect(other.get_attribute("href")==secondary,f"{root} secondary URL mismatched",item)
     for a in [*main.all(),*other.all()]:
      expect(a.get_attribute("target")=="_blank",f"{root} target missing",item)
      rel=a.get_attribute("rel") or ""
      expect("noopener" in rel and "noreferrer" in rel,f"{root} rel missing",item)
      a.scroll_into_view_if_needed();box=a.bounding_box()
      if box:
       expect(box["width"]>=110 and box["height"]>=43,f"{root} CTA too small",item)
       expect(box["x"]>=-2 and box["x"]+box["width"]<=w+3,f"{root} CTA off viewport",item)
     if root==".nf86-side":
      jump=node.locator('a.nf92-side-link[href="#nf86-official-entry"]')
      expect(jump.count()==1,f"{root} return-to-reservation jump missing",item)
     if root==".nf86-booking":
      expect(node.locator('a.nf92-facts-link[href="#nf87-verified-operations"]').count()==1,"mid facts return link missing",item)
     if root in [".nf86-intro",".nf86-booking"]:
      try:node.screenshot(path=str(OUT/f"{route}-{name}-{root.replace('.','')}.png"),animations="disabled")
      except Exception as e:item["issues"].append(f"screenshot: {e}")
    expect(page.locator('a.nf86-action').count()==3,"three official booking CTAs expected across each guide",item)
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
     root=page.locator(".nf86-hub-steps")
     expect(page.locator(".nf84-route").count()==4,"V84 banners count changed",item)
    else:
     root=page.locator("#official-ferry-routes")
    expect(root.count()==1,"route booking hub missing",item)
    if root.count()==1:
     cards=root.locator("#nf91-direct-operators .nf91-direct-item")
     expect(cards.count()==4,f"expected four distinct route cards got {cards.count()}",item)
     expect(root.locator(".nf86-hub-grid").count()==0,"duplicate legacy booking grid returned",item)
     for slug,(main_url,_) in ROUTES.items():
      card=cards.locator('[data-route="'+slug+'"]') if False else root.locator('#nf91-direct-operators .nf91-direct-item[data-route="'+slug+'"]')
      expect(card.count()==1,f"missing {slug} card",item)
      if card.count()==1:
       expect(card.locator("a.nf91-direct-primary").get_attribute("href")==main_url,f"incorrect {slug} operator destination",item)
       expect(card.locator("a.nf91-direct-secondary").get_attribute("href")==f"/guide/busan-{slug}-ferry/#nf87-verified-operations",f"missing {slug} facts deep link",item)
     root.scroll_into_view_if_needed()
     try:root.screenshot(path=str(OUT/f"{identifier}-{name}.png"),animations="disabled")
     except Exception as e:item["issues"].append(f"screenshot: {e}")
     if identifier=="booking" and w<=390:
      bubble=page.locator(".kakao-float")
      if bubble.count()==1 and bubble.is_visible():
       for a in root.locator("#nf91-direct-operators .nf91-direct-primary").all():
        a.scroll_into_view_if_needed()
        b=bubble.bounding_box();v=a.bounding_box()
        if b and v:
         intersects=max(b["x"],v["x"]) < min(b["x"]+b["width"],v["x"]+v["width"]) and max(b["y"],v["y"]) < min(b["y"]+b["height"],v["y"]+v["height"])
         expect(not intersects,"Kakao float overlaps direct booking choice",item)
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
