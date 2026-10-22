#!/usr/bin/env python3
"""V131 five priority cruise stops: factual-source, booking caution, return travel and browser QA.
Live availability, last shuttle times and paid tickets require actual vessel/date.
URL HTTP health never means seat/berth/return booking is confirmed.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright
import argparse,json,re,datetime
ROOT=Path(__file__).resolve().parents[1]
BASE="https://www.nipponferry.com"
FIVE=[
 ("naha-cruise-terminal-kokusai-dori",["nahaport.jp/users/kyakusen/","nahaport.jp/sp/faq/"]),
 ("ishigaki-cruise-kabira-bay-bus-taxi",["city.ishigaki.okinawa.jp/soshiki/kowan/kuruzusenn/370.html","www.azumabus.co.jp/localbus/","www.azumabus.co.jp/"]),
 ("hakata-port-hakata-station-access",["hakataport.com/center/","hakataport.com/access/"]),
 ("nagasaki-matsugae-glover-garden-cruise-access",["nagasaki-p.com/access/","nagasaki-p.com/cruise/","www.discover-nagasaki.com/en/transit/100790","www.discover-nagasaki.com/ko/transit/100790","glover-garden.jp/guide/"]),
 ("yokohama-red-brick-warehouse",["city.yokohama.lg.jp/lang/overseas/port/cruise/terminal_info.html","www.yokohama-akarenga.jp/"])
]
PRESERVE=[
 "https://www.azumabus.co.jp/localbus/",
 "https://www.discover-nagasaki.com/en/transit/100790",
]
OUTPUT=ROOT/"audit-output/v131"
def static():
 issues=[];result=[]
 for slug,links in FIVE:
  path=ROOT/"site/things-to-do"/slug/"index.html"
  text=path.read_text("utf8")
  canonical=BASE+"/things-to-do/"+slug+"/"
  section=re.findall(r'<section id="nf-v131-verification"[^>]*>([\s\S]*?)</section>',text)
  if len(section)!=1:issues.append(slug+": V131 review card absent or duplicate")
  if text.count('rel="canonical"')!=1 or f'<link rel="canonical" href="{canonical}"' not in text:
   issues.append(slug+": canonical error")
  if len(re.findall(r'<h1\b',text))!=1:issues.append(slug+": H1 not unique")
  if not re.search(r'<meta name="description" content="[^"]+"',text):issues.append(slug+": description missing")
  if section:
   for term in ("① 접안 위치","② 셔틀","③ 마지막 귀선편","④ 공식 예약","미확인","2026.10.22","선사"):
    if term not in section[0]:issues.append(slug+": missing "+term)
   for url in links:
    if url not in section[0]:issues.append(slug+": missing official reference "+url)
   for url in PRESERVE:
    if url in links and f'href="{url}"' not in text:
     issues.append(slug+": required original link removed "+url)
  if slug=="ishigaki-cruise-kabira-bay-bus-taxi":
   for term in ("9번·11번","NACRU","2~3시간"):
    if term not in section[0]:issues.append(slug+": Ishigaki public information missing "+term)
  if slug=="nagasaki-matsugae-glover-garden-cruise-access":
   for term in ("1,300엔","650엔","19:40"):
    if term not in section[0]:issues.append(slug+": Glover Garden official information missing "+term)
  if slug=="hakata-port-hakata-station-access":
   for term in ("여권·승선권","500m","크루즈선 착안 예정시각"):
    if term not in section[0]:issues.append(slug+": port passenger safety rules missing "+term)
  if slug in ("naha-cruise-terminal-kokusai-dori","hakata-port-hakata-station-access"):
   if "대표 이미지는 AI 생성 참고 장면" in text:issues.append(slug+": stale AI photo disclosure")
  result.append({"slug":slug,"official_references":len(links),"review_card_present":len(section)==1})
 return {"scope":"five_existing_priority_ports","checked":len(result),"issues":issues,"passed":not issues,"pages":result}
def verify_http(url):
 headers={"User-Agent":"Mozilla/5.0 NIPPONFERRY V131 QualityReview","Accept":"text/html,*/*"}
 data={"url":url,"classification":"unverified","status":None,"error":None}
 for method in ("HEAD","GET"):
  try:
   req=Request(url,headers=headers,method=method)
   with urlopen(req,timeout=14) as r:
    if method=="GET":r.read(512)
    code=r.status
  except HTTPError as e:code=e.code
  except Exception as e:
   data["error"]=type(e).__name__;continue
  data["status"]=code
  if 200<=code<400:data["classification"]="reachable";break
  if code in (404,410):
   if method=="GET":
    try:
     with urlopen(Request(url,headers=headers,method="GET"),timeout=12) as q:other=q.status
    except HTTPError as e:other=e.code
    except Exception:other=None
    data["classification"]="confirmed_broken" if other in (404,410) else "unverified"
   continue
 return data
def links():
 with ThreadPoolExecutor(max_workers=2) as p:
  rows=list(p.map(verify_http,PRESERVE))
 return {"checked":len(rows),"rows":rows,"warning":"Unverified due to anti-bot/5xx/network is not proof of broken link"}
def live():
 from playwright.sync_api import sync_playwright
 output={"passed":False,"tested":0,"expected":10,"errors":[],"pages":[]}
 OUTPUT.mkdir(parents=True,exist_ok=True)
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
  for width,height in ((1440,900),(390,844)):
   ctx=browser.new_context(viewport={"width":width,"height":height})
   page=ctx.new_page()
   for slug,urls in FIVE:
    case={"slug":slug,"viewport":width}
    try:
     uri=BASE+"/things-to-do/"+slug+"/"
     resp=page.goto(uri,wait_until="domcontentloaded",timeout=60000)
     if resp is None or resp.status!=200:raise ValueError("article HTTP response not 200")
     sec=page.locator("#nf-v131-verification")
     if sec.count()!=1 or not sec.is_visible():raise ValueError("V131 evidence card unavailable")
     if page.locator('link[rel="canonical"]').get_attribute("href")!=uri:raise ValueError("canonical differs from original URL")
     if page.locator("h1").count()!=1:raise ValueError("missing or duplicate H1")
     cover=page.locator("img.cover")
     if cover.count()==1:
      cover.scroll_into_view_if_needed(timeout=12000)
      loaded=cover.evaluate("(e)=>new Promise(f=>{if(e.complete)return f(e.naturalWidth>0);e.addEventListener('load',()=>f(true),{once:true});e.addEventListener('error',()=>f(false),{once:true})})",timeout=20000)
      if not loaded:raise ValueError("broken existing cover photo")
     for link in urls:
      if sec.locator('a[href*="'+link+'"]').count()<1:raise ValueError("missing expected official source link "+link)
     if page.evaluate("document.documentElement.scrollWidth")>width+12:
      raise ValueError("horizontal overflow")
     sec.screenshot(path=str(OUTPUT/f"{slug}-{width}.png"),timeout=30000,animations="disabled")
     output["tested"]+=1
     case["passed"]=True
    except Exception as e:
     case["passed"]=False;case["error"]=str(e)[:220];output["errors"].append(slug+"@"+str(width)+": "+str(e)[:220])
    output["pages"].append(case)
   page.close();ctx.close()
  browser.close()
 output["passed"]=output["tested"]==output["expected"] and not output["errors"]
 (OUTPUT/"live-report.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n","utf8")
 return output
if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--live",action="store_true");ap.add_argument("--links",action="store_true")
 args=ap.parse_args()
 if args.live:result=live()
 elif args.links:
  result=links();OUTPUT.mkdir(parents=True,exist_ok=True)
  (OUTPUT/"two-preserved-official-links.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n","utf8")
 else:result=static()
 print(json.dumps(result if not args.live else {k:result[k] for k in ("passed","tested","expected","errors")},ensure_ascii=False,indent=2))
 if not args.links:raise SystemExit(0 if result["passed"] else 1)
