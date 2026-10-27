#!/usr/bin/env python3
"""V102: reject the previously refused Kampu Ferry reservation URL everywhere users click.

Static source checks always run. Optional live check records whether Vercel has
actually deployed the fix; no claim of success from GitHub commits alone.
Distinguishes unsupported network failures from confirmed old page deployment.
"""
import argparse,datetime as dt,json,re,urllib.error,urllib.request
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]
SITE="https://www.nipponferry.com"
CONFIG=ROOT/"scripts/v90_booking_link_targets.json"
OLD="https://www.kampuferry.co.jp/lang_kor/reserve/"
NEW="https://kampuferry.co.jp/news/20261023systemmaintenance.html"
EN="https://kampuferry.co.jp/news/20261023systemmaintenance.html"
SOURCE_PAGES=[
"site/guide/busan-shimonoseki-ferry/index.html",
"site/guide/busan-shimonoseki-ferry-price/index.html",
"site/guide/busan-shimonoseki-timetable/index.html",
"site/ferry/index.html",
"site/booking/japan-cruise/index.html"
]
SOURCES_TO_AVOID=[
OLD,
"https://www.kampuferry.co.jp/yoyaku/en/",
"https://www.kampuferry.co.jp/lang_kor/fare/basic/",
"https://www.kampuferry.co.jp/lang_kor/passenger_info/schedule/",
"https://www.kampuferry.co.jp/lang_kor/passenger_info/t_access/checkin.html",
]
PRODUCTION={"/ferry/":NEW,
    "/booking/japan-cruise/":NEW,
    "/guide/busan-shimonoseki-ferry/":NEW,
    "/guide/busan-shimonoseki-ferry-price/":NEW,
    "/guide/busan-shimonoseki-timetable/":NEW}
class Links(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.canonical=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="a":
            self.links.append((a.get("href") or "").replace("&amp;","&"))
        if tag=="link" and a.get("rel")=="canonical":
            self.canonical.append(a.get("href"))

def verify_sources(root=ROOT):
    issues=[]
    cfg=json.loads((root/"scripts/v90_booking_link_targets.json").read_text("utf8"))
    ferry=cfg["routes"]["shimonoseki"]
    if ferry["primary"]!=NEW or ferry["secondary"]!=EN or cfg["hub_route_info"]["shimonoseki"]!=NEW:
        issues.append("single-source official suspension notice target registry mismatch")
    for path in SOURCE_PAGES:
        text=(root/path).read_text("utf8")
        for old in SOURCES_TO_AVOID:
            if old in text:issues.append(path+" still contains refused or unverified Kampu URL "+old)
        parsed=Links();parsed.feed(text)
        if NEW not in parsed.links:issues.append(path+" missing current official Kampu reservation suspension notice")
        if path.endswith("shimonoseki-ferry/index.html"):
            if EN not in parsed.links:issues.append(path+" missing current official suspension notice")
            if "051-464-2700" not in text:issues.append(path+" missing official 부산 예약 contact fallback")
        if path=="site/ferry/index.html" and len(parsed.canonical)!=1:
            issues.append("ferry hub lost canonical SEO URL")
    return issues

def inspect_deployed_html(html,expected,source):
    parser=Links();parser.feed(html)
    if OLD in parser.links or OLD in html:
        return {"url":source,"status":"old_link_still_published"}
    if expected not in parser.links:
        return {"url":source,"status":"replacement_not_visible"}
    return {"url":source,"status":"corrected_link_visible"}

def live_check(fetch=None):
    def get(url):
        req=urllib.request.Request(url,headers={
            "User-Agent":"Mozilla/5.0 (compatible; NIPPONFERRY-V102-external-link-verification/1.0)",
            "Cache-Control":"no-cache"})
        with urllib.request.urlopen(req,timeout=18) as r:
            return r.read(800000).decode("utf8","replace")
    fetch=fetch or get
    result=[]
    for path,expected in PRODUCTION.items():
        url=SITE+path
        try:
            html=fetch(url)
            result.append(inspect_deployed_html(html,expected,url))
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,OSError) as e:
            result.append({"url":url,"status":"fetch_unavailable","reason":type(e).__name__})
    status=[i["status"] for i in result]
    if all(x=="corrected_link_visible" for x in status):
        state="production_updated"
    elif any(x=="old_link_still_published" for x in status):
        state="production_old_link_pending_deployment"
    else:state="production_incomplete_or_unverifiable"
    return {"status":state,"pages":result}

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--check-production",action="store_true")
    a.add_argument("--require-live",action="store_true",
                   help="Fail if production still has the old URL; use AFTER Vercel redeploy.")
    a.add_argument("--output",default="audit-output/v102-kampu-link-recovery")
    args=a.parse_args()
    report={"version":"V102",
            "checked_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
            "source_issues":verify_sources(),"production":None}
    if args.check_production or args.require_live:
        report["production"]=live_check()
    p=Path(args.output);p.mkdir(parents=True,exist_ok=True)
    (p/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
    print(json.dumps({"source_issues":report["source_issues"],
                      "production_status":report["production"]["status"] if report["production"] else "not_checked"},
                      ensure_ascii=False))
    if report["source_issues"]:return 1
    if args.require_live and report["production"]["status"]!="production_updated":return 2
    return 0

if __name__=="__main__":raise SystemExit(main())
