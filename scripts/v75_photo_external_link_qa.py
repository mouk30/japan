#!/usr/bin/env python3
"""V75: validate seven distinct photo-source/licensing destinations by real Chromium browser.
Destination availability is reported separately from site layout correctness.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright
URLS=[
"https://commons.wikimedia.org/wiki/File:Yokohama_Red_Brick_Warehouse.jpg",
"https://commons.wikimedia.org/wiki/File:Miyajima-Ferry-STA_JR-Gate.jpg",
"https://commons.wikimedia.org/wiki/File:Shodo-shima_ferry_port_in_Tonosho_(6453360287).jpg",
"https://commons.wikimedia.org/wiki/File:Shuri_Castle_Reconstruction.jpg",
"https://creativecommons.org/licenses/by-sa/4.0/",
"https://creativecommons.org/licenses/by/2.0/",
"https://creativecommons.org/publicdomain/zero/1.0/",
]
out=Path("audit-output/v75-link-qa");out.mkdir(parents=True,exist_ok=True)
rows=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
    page=browser.new_page(viewport={"width":1280,"height":800},locale="en-US")
    for url in URLS:
        result={"url":url}
        try:
            response=page.goto(url,wait_until="domcontentloaded",timeout=25000)
            result["http_status"]=response.status if response else None
            result["final_url"]=page.url
            result["title"]=page.title()
            result["ok"]=result["http_status"]==200 and bool(result["title"].strip()) and (("File:" in result["title"]) if "commons.wikimedia.org" in url else True)
        except Exception as e:
            result["ok"]=False;result["error"]=str(e)[:350]
        rows.append(result);print(json.dumps(result,ensure_ascii=False),flush=True)
    page.close();browser.close()
report={"checked_at_utc":datetime.now(timezone.utc).isoformat(),"ok":sum(x["ok"] for x in rows),"total":len(rows),"results":rows,"scope":"Browser navigation to photo source and CC license destination; not full legal interpretation"}
(out/"report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
if not all(x["ok"] for x in rows):raise SystemExit("Some external links unavailable; review report")
