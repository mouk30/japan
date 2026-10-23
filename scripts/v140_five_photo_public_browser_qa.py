#!/usr/bin/env python3
"""V140 PUBLIC production homepage: five regional cards, actual browser image decode,
hash, responsive crop geometry, credits, SEO, and screenshot evidence."""
from pathlib import Path
import hashlib,json,math
from PIL import Image,ImageStat
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"audit-output/v140-public-five"
OUT.mkdir(parents=True,exist_ok=True)
SOURCE=json.loads((ROOT/"audit-reports/v140/import-report.json").read_text("utf8"))
PREV=json.loads((ROOT/"audit-reports/v124/import-result.json").read_text("utf8"))
by_key={x["key"]:x for x in SOURCE["source_photos"]}
prev={x["slug"]:x for x in PREV["images"]}
CASES=[
  {"key":"okinawa","href":"/okinawa/","path":by_key["okinawa"]["dest"],"sha":by_key["okinawa"]["sha256"],"dim":by_key["okinawa"]["size"],"author":by_key["okinawa"]["author"],"date":by_key["okinawa"]["date"],"lic":by_key["okinawa"]["license"],"src_url":by_key["okinawa"]["source"],"license_url":by_key["okinawa"]["licurl"]},
  {"key":"fukuoka","href":"/japan/fukuoka/","path":by_key["fukuoka"]["dest"],"sha":by_key["fukuoka"]["sha256"],"dim":by_key["fukuoka"]["size"],"author":by_key["fukuoka"]["author"],"date":by_key["fukuoka"]["date"],"lic":by_key["fukuoka"]["license"],"src_url":by_key["fukuoka"]["source"],"license_url":by_key["fukuoka"]["licurl"]},
  {"key":"shimonoseki","href":"/japan/shimonoseki/","path":prev["shimonoseki"]["output"],"sha":prev["shimonoseki"]["sha256"],"dim":[prev["shimonoseki"]["width"],prev["shimonoseki"]["height"]],"author":prev["shimonoseki"]["author"],"date":prev["shimonoseki"]["date"],"lic":prev["shimonoseki"]["license"],"src_url":prev["shimonoseki"]["source"],"license_url":"https://creativecommons.org/licenses/by-sa/4.0/"},
  {"key":"tsushima","href":"/japan/tsushima/","path":prev["tsushima"]["output"],"sha":prev["tsushima"]["sha256"],"dim":[prev["tsushima"]["width"],prev["tsushima"]["height"]],"author":prev["tsushima"]["author"],"date":prev["tsushima"]["date"],"lic":prev["tsushima"]["license"],"src_url":prev["tsushima"]["source"],"license_url":"https://creativecommons.org/publicdomain/zero/1.0/"},
  {"key":"kobe","href":"/japan/kobe/","path":by_key["kobe"]["dest"],"sha":by_key["kobe"]["sha256"],"dim":by_key["kobe"]["size"],"author":by_key["kobe"]["author"],"date":by_key["kobe"]["date"],"lic":by_key["kobe"]["license"],"src_url":by_key["kobe"]["source"],"license_url":by_key["kobe"]["licurl"]},
]
widths=(320,390,768,1440)
report={"version":"V140-public-final","target":"https://www.nipponferry.com/","viewports":list(widths),"cards":len(CASES),"expected":len(CASES)*len(widths),"checks":[],"images":[],"errors":[],"screenshots":[],"limitations":["Automated geometry and captured screenshots cannot conclusively judge human-centered composition; consult evidence screenshots for subjective crop quality."]}
with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
  for width in widths:
    ctx=browser.new_context(viewport={"width":width,"height":900},device_scale_factor=1)
    page=ctx.new_page()
    try:
      res=page.goto(report["target"],wait_until="domcontentloaded",timeout=60000)
      if not res or res.status!=200: raise RuntimeError("homepage status "+str(res.status if res else "no-response"))
      heading=page.title()
      if heading!="일본크루즈 여행 | 가격·일정·기항지 | 일본페리":raise RuntimeError("title SEO changed")
      if page.locator('link[rel="canonical"]').get_attribute("href")!=report["target"]:raise RuntimeError("canonical changed")
      if page.locator('meta[name="description"]').count()!=1:raise RuntimeError("meta description missing")
      if page.locator('.v65-grid .v65-card').count()!=8:raise RuntimeError("popular card count changed")
      if page.evaluate("document.documentElement.scrollWidth")>width+2:raise RuntimeError(f"horizontal overflow at {width}")
      credit=page.locator("p.v140-credit")
      if credit.count()!=1 or not credit.is_visible():raise RuntimeError("V140 credit missing or hidden")
      if credit.evaluate("(e)=>e.getBoundingClientRect().right")>width+3:raise RuntimeError("credit overflows viewport")
      if page.locator('link[href*="nf-v137-mobile-readability.css"]').count()!=1 or page.locator('link[href*="nf-v138-mobile-polish.css"]').count()!=1:raise RuntimeError("mobile styles missing")
      for x in CASES:
        card=page.locator(f'.v65-grid .v65-card:has(a.v65-photo[href="{x["href"]}"])')
        if card.count()!=1:raise RuntimeError(x["key"]+": missing unique card")
        im=card.locator("a.v65-photo img")
        if im.count()!=1:raise RuntimeError(x["key"]+": missing image")
        src=im.get_attribute("src")
        if src!=x["path"]:raise RuntimeError(x["key"]+": wrong deployed image "+str(src))
        if not im.get_attribute("alt"):raise RuntimeError(x["key"]+": no alt")
        if card.locator(".v104-photo-origin").count():raise RuntimeError(x["key"]+": old 'staged' image marker remains")
        im.scroll_into_view_if_needed(timeout=18000)
        ok=im.evaluate("""(e)=>new Promise(done=>{if(e.complete)return done(e.naturalWidth>0);e.addEventListener('load',()=>done(e.naturalWidth>0),{once:true});e.addEventListener('error',()=>done(false),{once:true});setTimeout(()=>done(false),19000)})""",timeout=25000)
        if not ok:raise RuntimeError(x["key"]+": public image failed decode")
        metrics=im.evaluate("""e=>{const r=e.getBoundingClientRect(),p=e.parentElement.getBoundingClientRect(),s=getComputedStyle(e);return {natural:[e.naturalWidth,e.naturalHeight],display:[r.width,r.height],parent:[p.width,p.height],fit:s.objectFit,position:s.objectPosition,opacity:s.opacity}}""")
        if metrics["natural"]!=x["dim"]:raise RuntimeError(x["key"]+": wrong image resolution "+str(metrics["natural"]))
        if metrics["display"][0]<130 or metrics["display"][1]<85:raise RuntimeError(x["key"]+": tiny/hidden display dimensions")
        if abs(metrics["display"][0]-metrics["parent"][0])>4:raise RuntimeError(x["key"]+": photo width not filling card")
        if metrics["fit"]!="cover":raise RuntimeError(x["key"]+": unexpected image fit "+metrics["fit"])
        displayratio=metrics["parent"][0]/metrics["parent"][1]
        naturalratio=metrics["natural"][0]/metrics["natural"][1]
        crop=1-min(displayratio/naturalratio,naturalratio/displayratio)
        if crop>0.31:raise RuntimeError(x["key"]+f": excessive crop {crop:.2%}")
        if credit.locator("a").filter(has_text=x["author"]).count()!=1:raise RuntimeError(x["key"]+": missing author attribution")
        if credit.locator('a[href="'+x["src_url"]+'"]').count()!=1:raise RuntimeError(x["key"]+": wrong/missing original source")
        if credit.locator('a[href="'+x["license_url"]+'"]').count()==0:raise RuntimeError(x["key"]+": no license link")
        full_photo=OUT/f'{x["key"]}-{width}.png'
        im.screenshot(path=str(full_photo),animations="disabled",timeout=30000)
        img=Image.open(full_photo).convert('RGB')
        stdev=sum(ImageStat.Stat(img.resize((96,96))).stddev)/3
        if stdev<6:raise RuntimeError(x["key"]+": image snapshot appears nearly blank")
        report["screenshots"].append(str(full_photo.relative_to(OUT)))
        record={"key":x["key"],"width":width,"decoded":True,"resolution":metrics["natural"],"photo_display":[round(v,1) for v in metrics["display"]],"focal_crop_fraction":round(crop,3),"object_position":metrics["position"],"image_screenshot_stddev":round(stdev,1),"source_verified_on_page":True,"license_verified_on_page":True,"passed":True}
        report["checks"].append(record)
        if width==1440:
          response=page.request.get(report["target"].rstrip('/')+src,timeout=30000)
          if response.status!=200:raise RuntimeError(x["key"]+": photo HTTP "+str(response.status))
          data=response.body();digest=hashlib.sha256(data).hexdigest()
          if digest!=x["sha"]:raise RuntimeError(x["key"]+": deployed image SHA mismatch "+digest)
          report["images"].append({"key":x["key"],"sha256_verified":True,"size_bytes":len(data),"path":src})
      if width in (390,1440):
        credit.scroll_into_view_if_needed(timeout=15000)
        credit.screenshot(path=str(OUT/f"v140-credits-{width}.png"),animations="disabled",timeout=30000)
        report["screenshots"].append(f"v140-credits-{width}.png")
        page.screenshot(path=str(OUT/f"v140-home-{width}.png"),full_page=True,animations="disabled",timeout=60000)
        report["screenshots"].append(f"v140-home-{width}.png")
    except Exception as e:
      report["errors"].append({"width":width,"message":str(e)[:400]})
    finally:
      ctx.close()
  browser.close()
report["passed"]=not report["errors"] and len(report["checks"])==report["expected"] and len(report["images"])==5
(OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"passed":report["passed"],"checked":len(report["checks"]),"expected":report["expected"],"sha_verified":len(report["images"]),"screenshots":len(report["screenshots"]),"errors":report["errors"]},ensure_ascii=False))
raise SystemExit(0 if report["passed"] else 1)
