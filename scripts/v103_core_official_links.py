#!/usr/bin/env python3
"""V103 - audit official ferry source anchors across 12 core articles and two booking hubs.

Classify transport failures, server/BOT blocks, and confirmed broken/redirected URLs
separately. This does not verify prices, seat inventory or completed bookings.
V90 continues to verify route-specific official BOOKING landing semantics.
"""
import argparse
import concurrent.futures
import datetime as dt
import json
import re
import sys
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
GUIDES=[
    f"site/guide/busan-{route}-{suffix}/index.html"
    for route in ("osaka","fukuoka","shimonoseki","tsushima")
    for suffix in ("ferry","ferry-price","timetable")
]
PAGES=["site/ferry/index.html","site/booking/japan-cruise/index.html"]+GUIDES
OPERATOR_HOSTS={
    "www.panstarcruise.com","panstarcruise.com",
    "www.koreaferry.co.kr","koreaferry.co.kr","www.koreaferry.kr","koreaferry.kr",
    "www.kampuferry.co.jp","kampuferry.co.jp","yoyaku.kampuferry.co.jp",
    "www.pukwan.co.kr","pukwan.co.kr",
    "www.busanpa.com","busanpa.com",
}
DISALLOWED=[
    "https://www.kampuferry.co.jp/lang_kor/reserve/",
    "https://www.kampuferry.co.jp/yoyaku/en/",
    "https://www.kampuferry.co.jp/lang_kor/fare/basic/",
    "https://www.pukwan.co.kr/",
]
TARGETS=ROOT/"scripts/v90_booking_link_targets.json"

class Anchors(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[]
        self.canonicals=[]
    def handle_starttag(self, tag, attrs):
        data=dict(attrs)
        if tag=="a":
            href=data.get("href","") or ""
            if href.lower().startswith(("https://","http://")):
                self.links.append({"url":href,"target":data.get("target"),
                    "rel":data.get("rel","")})
        elif tag=="link" and data.get("rel")=="canonical":
            self.canonicals.append(data.get("href",""))

def origin_host(url):
    return (urlparse(url).hostname or "").lower()

def inventory(root=ROOT):
    errors=[]
    occurrences=defaultdict(list)
    details={}
    for path in PAGES:
        try:s=(root/path).read_text(encoding="utf-8")
        except OSError:
            errors.append({"page":path,"reason":"missing_site_page"});continue
        tags=Anchors();tags.feed(s)
        matches=[]
        for a in tags.links:
            url=a["url"]
            if origin_host(url) not in OPERATOR_HOSTS:continue
            matches.append(url)
            if urlparse(url).scheme!="https":
                errors.append({"page":path,"url":url,"reason":"official_link_not_https"})
            if url in DISALLOWED:
                errors.append({"page":path,"url":url,"reason":"reintroduced_reported_broken_or_unresponsive_link"})
            # External official source links should always open in a secure new tab.
            if a["target"]!="_blank" or not {"noopener","noreferrer"}.issubset(set(a["rel"].split())):
                errors.append({"page":path,"url":url,"reason":"unsafe_external_link_attributes"})
            occurrences[url].append(path)
        expected="https://www.nipponferry.com/"+path[len("site/"):]
        if path.endswith("index.html"):
            expected=expected[:-len("index.html")]
        if expected not in tags.canonicals:
            errors.append({"page":path,"reason":"canonical_absent_or_modified","expected":expected})
        details[path]={"official_anchor_count":len(matches),"distinct_official_sources":len(set(matches))}
    cfg=json.loads((root/"scripts/v90_booking_link_targets.json").read_text("utf8"))
    for route,record in cfg["routes"].items():
        guide=f"site/guide/busan-{route}-ferry/index.html"
        for key in ("primary","secondary"):
            if guide not in occurrences.get(record[key],[]):
                errors.append({"page":guide,"reason":"registered_booking_target_not_linked","url":record[key]})
        for hub in ("site/ferry/index.html","site/booking/japan-cruise/index.html"):
            if hub not in occurrences.get(record["primary"],[]):
                errors.append({"page":hub,"reason":"missing_one_click_official_booking_url","url":record["primary"]})
    return {"pages":details,"occurrences":{u:sorted(set(paths)) for u,paths in sorted(occurrences.items())},
            "errors":errors}

def evaluate_url(url,status=200,final_url=None,content_type="text/html"):
    final_url=final_url or url
    original=origin_host(url)
    landed=origin_host(final_url)
    if original not in OPERATOR_HOSTS:
        return {"classification":"ignore","reason":"not_one_of_scoped_official_hosts"}
    if landed not in OPERATOR_HOSTS:
        return {"classification":"needs_review","reason":"unexpected_final_domain"}
    if original!=landed:
        # www and non-www aliases within the *same operator family* can be normal.
        def strip_www(s):return s.removeprefix("www.")
        if strip_www(original)!=strip_www(landed):
            return {"classification":"needs_review","reason":"cross_operator_or_port_authority_redirect"}
    if status in (404,410):
        return {"classification":"needs_review","reason":"confirmed_404_or_410"}
    if status in (401,403,429) or status>=500:
        return {"classification":"unverified","reason":"access_control_bot_defense_or_temporary_server_failure"}
    if status>=400 or status<200:
        return {"classification":"unverified","reason":"unexpected_http_status"}
    if status not in (200,203,206):
        return {"classification":"unverified","reason":"redirect_or_nonstandard_final_status"}
    if "html" not in content_type.lower() and "xml" not in content_type.lower():
        return {"classification":"unverified","reason":"unexpected_content_type"}
    if urlparse(url).path not in ("","/") and urlparse(final_url).path in ("","/"):
        return {"classification":"needs_review","reason":"deep_link_became_generic_homepage"}
    return {"classification":"reached_official_html","reason":"http_ok_without_claiming_correct_booking_content"}

def probe(url,timeout=13):
    try:
        import requests
        response=requests.get(url,timeout=timeout,allow_redirects=True,headers={
            "User-Agent":"Mozilla/5.0 (compatible; NIPPONFERRY-official-source-monitor/1.0)",
            "Accept":"text/html,application/xhtml+xml,*/*;q=0.8",
        },stream=True)
        result=evaluate_url(url,response.status_code,response.url,response.headers.get("Content-Type",""))
        result.update({"url":url,"http_status":response.status_code,
                       "redirected":response.url!=url,"final_host":origin_host(response.url)})
        response.close()
        return result
    except Exception as ex:
        return {"url":url,"classification":"unverified","reason":"network_tls_timeout_or_source_access",
                "error_class":type(ex).__name__}

def run(live=False):
    data=inventory()
    live_results=[]
    if live and data["occurrences"]:
        urls=list(data["occurrences"])
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            results=pool.map(probe,urls)
            live_results=list(results)
    return {
        "version":"V103",
        "checked_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "scope_pages":len(PAGES),
        "checked_source_files":len(data["pages"]),
        "official_anchor_occurrences":sum(d["official_anchor_count"] for d in data["pages"].values()),
        "distinct_official_urls":len(data["occurrences"]),
        "source_errors":data["errors"],
        "source_url_occurrences":data["occurrences"],
        "online_probes":live_results,
        "review_items":[r for r in live_results if r["classification"]=="needs_review"],
        "unverified":[r for r in live_results if r["classification"]=="unverified"],
        "readiness":"source_errors" if data["errors"] else "review_links" if any(
            r["classification"]=="needs_review" for r in live_results) else "source_clean",
        "notes":[
            "HTTP 200 and known domain are not proof that the intended reservation UI works.",
            "Bot defense, TLS errors or server 5xx are unverified, never declared valid or permanently broken.",
            "V90 monitors deeper semantic correctness of primary booking URLs.",
            "No automatic price, schedule, SEO or booking link edits.",
        ],
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--live",action="store_true",help="Probe all unique official source URLs once")
    p.add_argument("--output",default="audit-output/v103-official-link-inventory")
    p.add_argument("--strict",action="store_true",help="Fail if sources are invalid or actionable live review exists")
    a=p.parse_args()
    report=run(a.live)
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    (out/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    lines=["# V103 official source links","",
        f"Existing pages: **{report['checked_source_files']} / {report['scope_pages']}**",
        f"Official link occurrences: **{report['official_anchor_occurrences']}**",
        f"Unique official URLs: **{report['distinct_official_urls']}**",
        f"Source errors: **{len(report['source_errors'])}**",
        f"Actionable online review: **{len(report['review_items'])}**",
        f"Unverified due to access/network: **{len(report['unverified'])}**",
        "", "## Review required", ""]
    for row in report["source_errors"]:
        lines.append("- Source: "+row.get("page","")+" / "+row.get("reason",""))
    for row in report["review_items"]:
        lines.append("- "+row["url"]+" / "+row["reason"])
    lines.extend(["","## Not yet verifiable (not proof of failure)",""])
    for row in report["unverified"]:
        lines.append("- "+row["url"]+" / "+row["reason"])
    lines+=["","Every successful HTTP fetch still needs correct page-content verification for booking intent.",
            "This audit does not book tickets, claim actual reservation inventory or write site files."]
    (out/"summary.md").write_text("\n".join(lines)+"\n","utf8")
    print(json.dumps({key:report[key] for key in ("readiness","scope_pages","checked_source_files",
        "official_anchor_occurrences","distinct_official_urls")},ensure_ascii=False))
    print(json.dumps({"source_errors":len(report["source_errors"]),
        "review_items":len(report["review_items"]),
        "unverified":len(report["unverified"])},ensure_ascii=False))
    if a.strict and (report["source_errors"] or report["review_items"]):return 2
    return 1 if report["source_errors"] else 0

if __name__=="__main__":
    sys.exit(main())
