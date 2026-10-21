#!/usr/bin/env python3
"""V93 production GA4 readiness check (never prints measurement IDs).

A successful synthetic event test proves instrumentation code works; it does NOT
prove the deployed site has a GA4 property or that reports contain real visitors.
"""
import json,re,urllib.request,urllib.error,datetime as dt
from pathlib import Path
URLS=["https://www.nipponferry.com/","https://www.nipponferry.com/ferry/","https://www.nipponferry.com/booking/japan-cruise/"]
OUT=Path("audit-output/v93-click-analytics");OUT.mkdir(parents=True,exist_ok=True)
report={"checked_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"pages":[]}
for url in URLS:
    page={"url":url,"http_status":None,"ga4_stream_configured":None,"consent_script":None}
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (NIPPONFERRY-editorial-GA4-readiness/1.0)","Cache-Control":"no-cache"})
        with urllib.request.urlopen(req,timeout=16) as res:
            html=res.read(150000).decode("utf8",errors="replace")
            page["http_status"]=res.status
            page["ga4_stream_configured"]=bool(re.search(r'data-nf-ga4=["\x27]G-[A-Z0-9]{7,15}["\x27]',html))
            page["consent_script"]="nf-v93-booking-clicks.js" in html
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,OSError) as exc:
        page["error"]=type(exc).__name__
    report["pages"].append(page)
statuses=[p["ga4_stream_configured"] for p in report["pages"]]
if all(s is True for s in statuses):
    report["status"]="configured_on_public_pages_collection_depends_on_consent"
elif all(s is False for s in statuses):
    report["status"]="public_pages_have_no_ga4_measurement_id"
else:
    report["status"]="inconsistent_or_unverifiable"
report["actual_click_counts"]=None
report["note"]="Tag installed != clicks collected; never infer a number or booking conversion from markup."
(OUT/"public-readiness.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps({"status":report["status"],"pages":report["pages"],"actual_click_counts":None},ensure_ascii=False))
