#!/usr/bin/env python3
"""V89 real-site trust/freshness UI QA, and synthetic aging regression.

Reads 12 already published ferry pages, 2 viewport sizes; makes no bookings,
doesn't imply provider live availability, and does not mutate site files.
"""
import json, datetime as dt, time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE="https://www.nipponferry.com"
OUT=Path("audit-output/v89-review-age");OUT.mkdir(parents=True,exist_ok=True)
EXPECTED={
"osaka": ("https://www.panstarcruise.com/support/notice","25,000원"),
"fukuoka":("https://koreaferry.kr/eng/bbs/board.php?bo_table=ferry_notice","14,000원"),
"shimonoseki":("https://www.kampuferry.co.jp/lang_kor/fare/basic/","19,000원"),
"tsushima":("https://www.panstarcruise.com/support/notice","15,000원")
}
SIZES=[("desktop",1440,900),("small-mobile",360,780)]
report={"version":"V89","checked_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"checked":[],"errors":[],"simulation":{}}
def fail(item,msg):
 item.setdefault("errors",[]).append(msg)
 report["errors"].append(item["page"]+" "+item["viewport"]+": "+msg)
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
 for vp,w,h in SIZES:
  ctx=browser.new_context(viewport={"width":w,"height":h},device_scale_factor=1)
  for route,(official,fare) in EXPECTED.items():
   for suffix in ["ferry","ferry-price","timetable"]:
    path=f"/guide/busan-{route}-{suffix}/";page=ctx.new_page()
    item={"page":path,"viewport":vp,"width":w,"errors":[]}
    try:
     resp=page.goto(BASE+path,wait_until="domcontentloaded",timeout=60000)
     page.wait_for_timeout(1200)
     if not resp or resp.status>=400: fail(item,"page HTTP error")
     panel=page.locator("#nf87-verified-operations")
     strip=page.locator("#nf87-verified-operations .nf89-review")
     if panel.count()!=1 or strip.count()!=1: fail(item,"verification header/ribbon not unique")
     else:
      strip.scroll_into_view_if_needed(timeout=12000)
      page.wait_for_timeout(150)
      if strip.get_attribute("data-verified-on")!="2026-10-21":fail(item,"verified date was changed without confirmation")
      if strip.get_attribute("data-age") not in ("checked","review","overdue"):fail(item,"aging script missing")
      if strip.locator(".nf89-review__status").count()!=1:fail(item,"warning/status missing")
      else:
       status=strip.locator(".nf89-review__status").inner_text()
       if not status: fail(item,"empty status")
       if "예약 가능" not in status and "요금" not in status:fail(item,"not clear this is not live availability")
      a=strip.locator(".nf89-review__link")
      if a.count()!=1:fail(item,"official direct link missing")
      else:
       if a.get_attribute("href")!=official:fail(item,"wrong official domain")
       if a.get_attribute("target")!="_blank" or "noopener" not in (a.get_attribute("rel") or ""):fail(item,"insecure external link")
       a.scroll_into_view_if_needed()
       b=a.bounding_box()
       if not b or b["height"]<42 or b["x"]<-1 or b["x"]+b["width"]>w+2:fail(item,"official CTA off-screen or undersized")
      if fare not in panel.inner_text():fail(item,"V87 reviewed fare missing")
      if panel.locator(".nf87-audit__fact").count()!=4:fail(item,"original V87 guide info modified")
      strip.screenshot(path=str(OUT/f"{route}-{suffix}-{vp}.png"),timeout=20000,animations="disabled")
     links=page.locator('link[rel="canonical"]')
     if links.count()!=1 or links.first.get_attribute("href")!=BASE+path:fail(item,"canonical changed")
     if page.locator('script[src^="/nf-v89-verified-date.js"]').count()!=1:fail(item,"date javascript absent")
     if page.locator('link[href^="/nf-v89-verified-date.css"]').count()!=1:fail(item,"date CSS absent")
     scroll=page.evaluate("document.documentElement.scrollWidth")
     if scroll>w+8:fail(item,f"horizontal overflow {scroll}px")
     item["scrollWidth"]=scroll
    except Exception as exc:
     fail(item,f"{type(exc).__name__}: {str(exc)[:210]}")
    finally:
     item["pass"]=not item["errors"];report["checked"].append(item);page.close()
  ctx.close()
 # Synthetic time travel on isolated DOM uses the exact published JS resource.
 page=browser.new_page()
 try:
  page.goto(BASE+"/guide/busan-osaka-ferry/",wait_until="domcontentloaded",timeout=60000)
  raw=page.evaluate("""async() => (await (await fetch('/nf-v89-verified-date.js', {cache:'no-store'})).text())""")
  for stamp,expected in [("2026-10-22","checked"),("2026-11-12","review"),("2026-12-10","overdue")]:
   val=page.evaluate("""({raw,stamp}) => {
     const holder=document.createElement('div');
     holder.innerHTML='<div class="nf89-review" data-verified-on="2026-10-21"><span class="nf89-review__status">unchanged</span></div>';
     const orig=document.querySelectorAll.bind(document);
     const DateOrig=Date;
     const nativeDate=Date;
     class MockDate extends nativeDate { constructor(...args){ if(args.length) super(...args); else super(stamp+'T12:00:00Z');} }
     MockDate.UTC=nativeDate.UTC; MockDate.parse=nativeDate.parse; MockDate.now=()=>new nativeDate(stamp+'T12:00:00Z').getTime();
     const section=holder.firstElementChild;
     try{
       Object.defineProperty(document,'querySelectorAll',{configurable:true,value:(selector)=>selector.includes('.nf89-review')?[section]:orig(selector)});
       window.Date=MockDate;
       (0,eval)(raw);
       return {age:section.getAttribute('data-age'),notice:section.querySelector('.nf89-review__status').textContent};
     } finally{
       window.Date=DateOrig;
       delete document.querySelectorAll;
     }
   }""",{"raw":raw,"stamp":stamp})
   report["simulation"][stamp]=val
   if val["age"]!=expected:report["errors"].append(f"synthetic date {stamp}: expected {expected} got {val['age']}")
 except Exception as e:report["errors"].append("synthetic-date failure: "+str(e)[:200])
 finally: page.close()
 browser.close()
report["passed"]=len(report["errors"])==0
(OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps({"passed":report["passed"],"screens":len(report["checked"]),"simulated":report["simulation"],"failures":report["errors"]},ensure_ascii=False,indent=2))
raise SystemExit(0 if report["passed"] else 1)
