#!/usr/bin/env python3
"""V130 verify 36 already-sourced real WebP hub cards and 5 priority cruise port pages.
HTML/source and browser rendering only; does NOT certify that a 3rd party
booking accepts reservations, or live berth/shuttle/ticket/return schedules.
"""
import argparse,json,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"
HUB="/things-to-do/cruise-ports/"
BATCHES=("126","127","128","129")
PORTS={
 "naha-cruise-terminal-kokusai-dori":"nahaport.jp",
 "ishigaki-cruise-kabira-bay-bus-taxi":"city.ishigaki.okinawa.jp",
 "hakata-port-hakata-station-access":"hakataport.com",
 "nagasaki-matsugae-glover-garden-cruise-access":"discover-nagasaki.com",
 "yokohama-red-brick-warehouse":"city.yokohama.lg.jp",
}
OUT=ROOT/"audit-output/v130"
def load_plan():
 arr=[]
 for batch in BATCHES:
  arr.extend(json.loads((ROOT/f"audit-reports/v{batch}/photo-plan.json").read_text("utf8"))["selected"])
 assert len(arr)==36 and len(set(x["slug"] for x in arr))==36
 return arr
def run_source():
 html=(SITE/HUB.lstrip("/")/"index.html").read_text("utf8")
 issues=[];success=[]
 for p in load_plan():
  slug=p["slug"];anchor='href="/things-to-do/'+slug+'/"'
  start=html.find(anchor);end=html.find("</a>",start)
  if start<0 or end<0 or html.count(anchor)!=1:issues.append(slug+": missing/duplicate hub link");continue
  card=html[start:end+4]
  imgs=re.findall(r"<img\b[^>]*>",card)
  expected=p["output"]
  if len(imgs)!=1 or 'src="'+expected+'"' not in imgs[0]:issues.append(slug+": incorrect hub image")
  if 'AI 생성' in (imgs[0] if imgs else ""):issues.append(slug+": stale AI image alt")
  if 'nf-v130-photo-credit' not in card or p["author"] not in card or p["license"] not in card:
   issues.append(slug+": photo credit absent")
  webp=SITE/expected.lstrip("/")
  try:
   b=webp.read_bytes()
   if b[:4]!=b"RIFF" or b[8:12]!=b"WEBP":issues.append(slug+": invalid WebP")
  except OSError:issues.append(slug+": missing file")
  path=SITE/"things-to-do"/slug/"index.html"
  if not path.exists():issues.append(slug+": missing article")
  else:
   page=path.read_text("utf8")
   if 'class="cover" src="'+expected+'"' not in page:issues.append(slug+": detail cover mismatch")
   if 'property="og:image" content="https://www.nipponferry.com'+expected+'"' not in page:
    issues.append(slug+": detail OG mismatch")
  success.append(slug)
 for slug,host in PORTS.items():
  page=(SITE/"things-to-do"/slug/"index.html").read_text("utf8")
  if 'rel="canonical"' not in page:issues.append(slug+": no canonical")
  if host not in page:issues.append(slug+": missing priority official-source domain")
  if not any(x in page for x in ("항차별","선사 공지","귀선 마감","귀선 시간")):
   issues.append(slug+": no return-to-ship condition text")
  m=re.search(r'<meta property="og:image" content="([^"]+)"',page)
  ld=re.search(r'<script type="application/ld\\+json">([\\s\\S]*?)</script>',page)
  if not m or not ld:issues.append(slug+": missing image metadata")
  else:
   data=json.loads(ld.group(1))
   article=next((x for x in (data if isinstance(data,list) else [data]) if x.get("@type")=="Article"),None)
   if article and article.get("image") not in ([m.group(1)],m.group(1)):
    issues.append(slug+": Article image does not match OG")
   cover=re.search(r'<img class="cover" src="([^"]+)"',page)
   if cover and m.group(1)!="https://www.nipponferry.com"+cover.group(1):
    issues.append(slug+": real photo cover not synced to OG")
  if slug=="ishigaki-cruise-kabira-bay-bus-taxi" and "nf-v130-access-control" not in page:
   issues.append(slug+": official vehicle restriction notice missing")
 if html.count("nf-v130-photo-credit")!=36:issues.append("hub credit count != 36")
 return {"status":"pass" if not issues else "fail","checked_hub_cards":len(success),"checked_priority_pages":len(PORTS),"issue_count":len(issues),"issues":issues}
def run_live():
 from playwright.sync_api import sync_playwright
 plan=load_plan()
 report={"tested_images":0,"tested_port_pages":0,"views":[],"issues":[]}
 OUT.mkdir(parents=True,exist_ok=True)
 with sync_playwright() as w:
  browser=w.chromium.launch(headless=True,args=["--no-sandbox"])
  for width,height in ((1440,900),(390,844)):
   ctx=browser.new_context(viewport={"width":width,"height":height})
   page=ctx.new_page()
   try:
    resp=page.goto("https://www.nipponferry.com"+HUB,wait_until="domcontentloaded",timeout=60000)
    if resp is None or resp.status!=200:raise ValueError("hub HTTP not 200")
    if page.title().strip()=="":raise ValueError("hub title empty")
    for spec in plan:
     slug=spec["slug"]
     link=page.locator('a[href="/things-to-do/'+slug+'/"]')
     if link.count()!=1:raise ValueError("missing hub card "+slug)
     img=link.locator('img[src="'+spec["output"]+'"]')
     if img.count()!=1:raise ValueError("stale image card "+slug)
     img.scroll_into_view_if_needed(timeout=10000)
     result=img.evaluate("(e)=>new Promise(done=>{if(e.complete)return done(e.naturalWidth>0);e.addEventListener('load',()=>done(true),{once:true});e.addEventListener('error',()=>done(false),{once:true});})",timeout=22000)
     if not result:raise ValueError("image failed to decode "+slug)
     credit=link.locator("span.nf-v130-photo-credit")
     if credit.count()!=1 or spec["author"] not in credit.inner_text():raise ValueError("photo credit not visible "+slug)
     report["tested_images"]+=1
    if page.evaluate("document.documentElement.scrollWidth")>width+12:
     raise ValueError("hub horizontal overflow "+str(width))
    page.screenshot(path=str(OUT/f"hub-{width}.png"),full_page=False)
   except Exception as ex:report["issues"].append("hub-"+str(width)+": "+str(ex)[:180])
   for slug in PORTS:
    try:
     url="https://www.nipponferry.com/things-to-do/"+slug+"/"
     r=page.goto(url,wait_until="domcontentloaded",timeout=60000)
     if not r or r.status!=200:raise ValueError("page HTTP error")
     if page.locator('link[rel="canonical"]').get_attribute("href")!=url:raise ValueError("wrong canonical")
     og=page.locator('meta[property="og:image"]').get_attribute("content")
     schemas=json.loads(page.locator('script[type="application/ld+json"]').first.text_content())
     art=next((o for o in (schemas if isinstance(schemas,list) else [schemas]) if o.get("@type")=="Article"),None)
     if art and art.get("image") not in ([og],og):raise ValueError("Article image versus OG mismatch")
     cover=page.locator("img.cover")
     if cover.count()==1 and og!="https://www.nipponferry.com"+cover.get_attribute("src"):
      raise ValueError("cover/OG mismatch")
     if slug=="ishigaki-cruise-kabira-bay-bus-taxi" and page.locator("#nf-v130-access-control").count()!=1:
      raise ValueError("Ishigaki official vehicle restriction warning missing")
     if page.evaluate("document.documentElement.scrollWidth")>width+12:raise ValueError("horizontal overflow")
     report["tested_port_pages"]+=1
    except Exception as ex:report["issues"].append(slug+"@"+str(width)+": "+str(ex)[:180])
   report["views"].append({"width":width,"images_passed":report["tested_images"],"port_pages_passed":report["tested_port_pages"]})
   page.close();ctx.close()
  browser.close()
 report["passed"]=not report["issues"] and report["tested_images"]==72 and report["tested_port_pages"]==10
 (OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
 return report
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--live",action="store_true");args=p.parse_args()
 result=run_live() if args.live else run_source()
 print(json.dumps(result,ensure_ascii=False,indent=2))
 raise SystemExit(0 if (result.get("passed",result.get("status")=="pass")) else 1)
