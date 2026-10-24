#!/usr/bin/env python3
"""V152 release readiness: inspect published three pilots and track setup, not private GA4 data.
A missing public GA4 script is a measured configuration blocker, not a fabricated zero.
"""
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime,timezone
import re,json,time
ORIGIN="https://www.nipponferry.com"
PILOTS={"naoshima-art-ferry-return":("naoshima",9),
        "teshima-art-ferry-return":("teshima",12),
        "takamatsu-cruise-udon-market-return":("shikoku_food",6)}
class Tags(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.canonicals=[];self.body_ids=[];self.actions=[];self.js=[];self.images=0;self.gtag_scripts=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="h1":self.h1+=1
  if tag=="body":self.body_ids.append(a.get("data-nf-pilot"))
  if tag=="link" and a.get("rel")=="canonical":self.canonicals.append(a.get("href"))
  if tag=="img":self.images+=1
  if tag=="a" and a.get("data-nf-pilot-action"):self.actions.append(a["data-nf-pilot-action"])
  if tag=="script" and a.get("src"):
   self.js.append(a["src"])
   if a.get("data-nf-ga4"):self.gtag_scripts.append(a["data-nf-ga4"])
def fetch(path):
 err=None
 for i in range(4):
  try:
   with urlopen(Request(ORIGIN+path,headers={"User-Agent":"Mozilla/5.0 (compatible; NIPPONFERRY-V152-Readiness/1.0)","Cache-Control":"no-cache"}),timeout=22) as resp:
    return resp.status,resp.headers.get("content-type",""),resp.read(3_000_000).decode("utf-8","replace")
  except (URLError,HTTPError,TimeoutError) as e:err=str(e);time.sleep(2+i)
 raise RuntimeError(err)
rows=[]
for slug,(pilot,minimum) in PILOTS.items():
 path="/things-to-do/"+slug+"/";record={"page":path,"pilot":pilot}
 try:
  status,ctype,html=fetch(path);parser=Tags();parser.feed(html)
  readiness="configured" if parser.gtag_scripts else "needs_GA4_MEASUREMENT_ID"
  checks={"http200":status==200,"html":"html" in ctype.lower(),
   "canonical":parser.canonicals==[ORIGIN+path],
   "single_h1":parser.h1==1,"unchanged_real_image":parser.images>=1,
   "pilot_marker":parser.body_ids==[pilot],
   "cta_instrumentation":len(parser.actions)>=minimum,
   "correct_script_when_configured":not parser.gtag_scripts or (
      len(parser.gtag_scripts)==1 and re.fullmatch(r"G-[A-Z0-9]{7,15}",parser.gtag_scripts[0]) is not None and
      any("nf-v93-booking-clicks.js?v=20261024-v152" in js for js in parser.js)),
   "no_GA4_network_before_consent":not any("googletagmanager.com/gtag/js" in js for js in parser.js),
   "photo_source_retained":'id="nf-v148-photo-credits"' in html}
  record.update({"checks":checks,"pass":all(checks.values()),"readiness":readiness,
                 "actions_count":len(parser.actions),"GA4_configured":bool(parser.gtag_scripts)})
 except Exception as ex:record.update({"pass":False,"error":str(ex)})
 print("PASS" if record["pass"] else "FAIL",path,
    "GA4",record.get("readiness","unavailable"),"click_targets",record.get("actions_count"),
    "failed",[k for k,v in record.get("checks",{}).items() if not v],flush=True)
 rows.append(record)
try:
 status,ctype,script=fetch("/nf-v93-booking-clicks.js?v=20261024-v152")
 asset={"pass":status==200 and "nf_pilot_guide_view" in script and "nf_pilot_action_click" in script,
       "status":status,"consent_only":"consentKey" in script and "if (!event.isTrusted || !enabled)" in script}
 asset["pass"]=asset["pass"] and asset["consent_only"]
except Exception as e:asset={"pass":False,"error":str(e)}
print("PASS" if asset["pass"] else "FAIL","/nf-v93-booking-clicks.js",asset)
configured=[x.get("GA4_configured") for x in rows if x.get("pass")]
same_config=len(set(configured))<=1 and len(configured)==3
report={"date":datetime.now(timezone.utc).isoformat(),"sample":3,"GA4_script_configured_for_all":bool(configured and all(configured)),
 "requires_user_GA4_property_permissions":True,"real_GA4_hits_or_search_clicks_read":False,
 "all_same_measurement_connection_state":same_config,
 "pages":rows,"tracking_asset":asset}
out=Path("audit-output/v152-public");out.mkdir(parents=True,exist_ok=True)
(out/"pilot-ga4-readiness.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",sum(x["pass"] for x in rows),"/",len(rows),
      "tracking_asset",asset["pass"],"connected",report["GA4_script_configured_for_all"],flush=True)
if not all(x["pass"] for x in rows) or not asset["pass"] or not same_config:raise SystemExit(1)
