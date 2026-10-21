#!/usr/bin/env python3
"""V87 read-only production QA: 12 established Japan ferry route guide pages."""
import json,time
from pathlib import Path
from playwright.sync_api import sync_playwright
OUT=Path("audit-output/v87-ferry-ops")
OUT.mkdir(parents=True,exist_ok=True)
BASE="https://www.nipponferry.com"
CASES={
"osaka":{"fuel":"25,000원","source":"https://www.panstarcruise.com/support/notice/294","old":"유류할증료는 29,000원"},
"fukuoka":{"fuel":"14,000원","source":"https://koreaferry.kr/eng/bbs/board.php?bo_table=ferry_notice&wr_id=39","old":""},
"shimonoseki":{"fuel":"19,000원","source":"https://www.kampuferry.co.jp/lang_kor/fare/basic/","old":""},
"tsushima":{"fuel":"15,000원","source":"https://www.panstarcruise.com/support/notice/292","old":"유류할증료는 16,000원"}
}
report={"version":"V87","checked_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"results":[],"issues":[]}
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
 for tag,w,h in [("desktop",1440,900),("mobile",360,780)]:
  context=browser.new_context(viewport={"width":w,"height":h},device_scale_factor=1)
  for route,details in CASES.items():
   for suffix in ["ferry","ferry-price","timetable"]:
    slug=f"/guide/busan-{route}-{suffix}/";page=context.new_page()
    r={"path":slug,"viewport":tag,"width":w,"errors":[]}
    def require(ok,msg):
     if not ok:r["errors"].append(msg)
    try:
     resp=page.goto(BASE+slug,wait_until="domcontentloaded",timeout=60000)
     page.wait_for_timeout(1100)
     require(resp is not None and resp.status<400,"page HTTP error")
     panel=page.locator("#nf87-verified-operations")
     require(panel.count()==1,"source-verification panel missing or duplicated")
     if panel.count()==1:
      panel.scroll_into_view_if_needed(timeout=12000)
      page.wait_for_timeout(250)
      require(panel.is_visible(),"audit panel hidden")
      require(panel.locator(".nf87-audit__fact").count()==4,"not exactly four practical audited facts")
      require(panel.locator(".nf87-audit__alert").count()==1,"booking-risk notice missing")
      links=panel.locator(".nf87-audit__sources a")
      require(links.count()>=3,"insufficient official citations")
      urls=[x.get_attribute("href") for x in links.all()]
      require(details["source"] in urls,"missing direct primary evidence URL")
      for link in links.all():
       require((link.get_attribute("href") or "").startswith("https://"),"non-HTTPS evidence link")
       rel=link.get_attribute("rel") or ""
       require("noopener" in rel and "noreferrer" in rel,"external link missing noreferrer or noopener")
      require(details["fuel"] in panel.inner_text(),"current official surcharge missing")
      if route=="tsushima":
       require("10월 20" in panel.inner_text() and "전편 결항" in panel.inner_text(),"Oct 20–21 cancellation information missing")
      if route=="fukuoka":
       require("10월 1일 예약분" in panel.inner_text(),"new fares effective booking date missing")
      pbox=panel.bounding_box()
      require(bool(pbox) and pbox["width"]>280 and pbox["width"]<=w+2,"panel horizontal size incorrect")
      panel.screenshot(path=str(OUT/f"{route}-{suffix}-{tag}.png"),animations="disabled",timeout=30000)
     require(page.locator('link[rel="canonical"]').count()==1,"canonical missing")
     expected=BASE+slug
     if page.locator('link[rel="canonical"]').count()==1:
      require(page.locator('link[rel="canonical"]').get_attribute("href")==expected,"canonical changed")
     require(page.locator('link[href^="/nf-v87-verified-operations.css"]').count()==1,"audit stylesheet missing")
     html=page.content()
     if details["old"]:require(details["old"] not in html,"stale surcharge remains")
     scroll_w=page.evaluate("document.documentElement.scrollWidth")
     require(scroll_w<=w+9,f"horizontal overflow: {scroll_w} > {w}")
     r["scrollWidth"]=scroll_w
    except Exception as e:
     r["errors"].append(f"{type(e).__name__}: {str(e)[:190]}")
    finally:
     r["passed"]=not r["errors"]
     if r["errors"]:report["issues"].extend([slug+" "+tag+": "+x for x in r["errors"]])
     report["results"].append(r);page.close()
  context.close()
 browser.close()
report["passed"]=not report["issues"]
(OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
print(json.dumps({"passed":report["passed"],"tested":len(report["results"]),"issues":report["issues"]},ensure_ascii=False,indent=2))
raise SystemExit(0 if report["passed"] else 1)
