#!/usr/bin/env python3
"""V90: inspect official external booking CTAs, redirect destinations and site markup.

No booking submitted and no fares or article pages automatically altered.
403/429, JS gate or human verification are 'unverified', not 'link broken'.
"""
import datetime as dt
import hashlib
import json
import os
import re
import time
from pathlib import Path
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
CONF=ROOT/"scripts/v90_booking_link_targets.json"
OUT=ROOT/"audit-reports/v90/current"
H={"User-Agent":"Mozilla/5.0 (compatible; NIPPONFERRY-Reservation-Link-QA/1.0)","Accept-Language":"ko-KR,ko;q=0.9,en;q=0.8"}
def host(url):
    return (urlsplit(url).hostname or "").lower()
def marker(text,markers):
    return any(k.lower() in (text or "").lower() for k in markers)
def fingerprint(data):
    return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
def hrefs_for_class(soup,css):
    return [x.get("href") for x in soup.select(css)]
def examine_local(config):
    errors=[]
    routes=config["routes"]
    details={}
    for route,settings in routes.items():
        path=ROOT/"site/guide"/f"busan-{route}-ferry"/"index.html"
        if not path.is_file():
            errors.append({"route":route,"problem":"missing guide","path":str(path)});continue
        soup=BeautifulSoup(path.read_text("utf-8"),"html.parser")
        expected=(settings["primary"],settings["secondary"])
        counts={}
        for section in (".nf86-intro",".nf86-booking",".nf86-side"):
            el=soup.select_one(section)
            if el is None:
                errors.append({"route":route,"problem":"required booking section missing","section":section})
                continue
            primary=hrefs_for_class(el,"a.nf86-action-primary")
            secondary=hrefs_for_class(el,"a.nf86-action-secondary")
            counts[section]=[primary,secondary]
            desired=([expected[0]],[expected[1]]) if section==".nf86-intro" else ([expected[0]],[]) if section==".nf86-booking" else ([],[])
            if primary!=desired[0] or secondary!=desired[1]:
                errors.append({"route":route,"problem":"incorrect V92 section-specific CTA or duplicated outbound link","section":section,"got":counts[section]})
            for a in el.select("a.nf86-action"):
                if a.get("target")!="_blank" or not {"noopener","noreferrer"}.issubset(set(a.get("rel",[]))):
                    errors.append({"route":route,"problem":"unsafe external CTA rel","section":section})
        hero_note=soup.select_one(".nf86-intro .nf92-route-note")
        if hero_note is None or hero_note.select_one("a") is not None:
            errors.append({"route":route,"problem":"route arrival context missing or contains redundant link"})
        if hrefs_for_class(soup,".nf86-side a.nf92-side-link")!=["#nf86-official-entry"]:
            errors.append({"route":route,"problem":"sidebar must return to primary booking hero without duplicate outbound link"})
        if hrefs_for_class(soup,".nf86-booking a.nf92-facts-link")!=["#nf87-verified-operations"]:
            errors.append({"route":route,"problem":"bottom primary CTA missing factual fallback link"})
        if len(soup.select("a.nf86-action"))!=3:
            errors.append({"route":route,"problem":"must have exactly three decisive external operator buttons"})
        if soup.select_one('link[rel="canonical"]') is None:
            errors.append({"route":route,"problem":"canonical missing"})
        details[route]={"html":str(path.relative_to(ROOT)),"primary":expected[0],"secondary":expected[1],"panels":counts}
    for page in ["site/ferry/index.html","site/booking/japan-cruise/index.html"]:
        path=ROOT/page
        if not path.exists():
            errors.append({"problem":"missing hub","path":page});continue
        content=path.read_text("utf8")
        html=BeautifulSoup(content,"html.parser")
        if html.select_one(".nf86-hub-grid") is not None:
            errors.append({"problem":"redundant legacy four-link grid must be removed","path":page})
        if len(html.select("#nf91-direct-operators .nf91-direct-item"))!=4:
            errors.append({"problem":"missing four operator-choice cards","path":page})
        for route in routes:
            card=html.select_one('#nf91-direct-operators .nf91-direct-item[data-route="'+route+'"]')
            if not card or hrefs_for_class(card,"a.nf91-direct-primary")!=[routes[route]["primary"]] or hrefs_for_class(card,"a.nf91-direct-secondary")!=[f"/guide/busan-{route}-ferry/#nf87-verified-operations"]:
                errors.append({"problem":"invalid direct operator or factual guide link","path":page,"route":route})
        if page=="site/ferry/index.html":
            root=BeautifulSoup(content,"html.parser")
            for route in routes:
                card=root.select_one('article[aria-labelledby="nf84-'+route+'-title"]')
                expected=config["hub_route_info"][route]
                if card is None or hrefs_for_class(card,"a.nf84-route__source")!=[expected]:
                    errors.append({"problem":"wide banner official link is not route-specific","path":page,"route":route,"expected":expected})
    return {"pages_checked":6,"routes":details,"errors":errors}

def evaluate_response(url,response,config,provider,kind):
    """Pure classification; never treat a valid HTTP status alone as proof of correct page."""
    result={"source_url":url,"kind":kind,"provider":provider,"status_code":response.status_code,
            "final_url":response.url,"redirects":[{"status":r.status_code,"url":r.url} for r in response.history],
            "classification":"unverified","reason":None}
    if len(response.history)>config["max_redirects"]:
        result.update(classification="needs_review",reason="excess_redirect_hops")
        return result
    if host(response.url) not in config["allowed_hosts"][provider]:
        result.update(classification="needs_review",reason="redirected_to_unexpected_domain")
        return result
    if response.status_code in (404,410):
        result.update(classification="suspected_broken",reason="official_page_not_found")
        return result
    if response.status_code in (401,403,429):
        result.update(classification="unverified",reason="login_or_bot_or_rate_limit")
        return result
    if response.status_code >= 500 or response.status_code in (408,425):
        result.update(classification="unverified",reason="temporary_server_or_timeout")
        return result
    if response.status_code < 200 or response.status_code >= 400:
        result.update(classification="unverified",reason="unexpected_http_status")
        return result
    original_path=urlsplit(url).path.rstrip("/")
    actual_path=urlsplit(response.url).path.rstrip("/")
    if original_path not in ("","/") and actual_path in ("","/"):
        result.update(classification="needs_review",reason="deep_link_redirected_to_operator_home")
        return result
    if kind in ("route_info","booking_entry","booking_calendar_search","reservation_instructions") and original_path and actual_path!=original_path:
        result.update(classification="needs_review",reason="specific_booking_or_route_path_changed")
        return result
    content_type=response.headers.get("content-type","").lower()
    if content_type and not any(x in content_type for x in ("html","xhtml")):
        result.update(classification="needs_review",reason="non_html_destination")
        return result
    soup=BeautifulSoup(response.text[:1600000],"html.parser")
    for n in soup.select("script,style,noscript,nav,footer"):
        n.decompose()
    title=soup.title.get_text(" ",strip=True) if soup.title else ""
    body=soup.get_text(" ",strip=True)
    result["page_title"]=title[:180]
    result["body_length"]=len(body)
    if not marker(title+" "+body,config["minimum_expected_text"][provider]):
        if len(body)>=150:
            result.update(classification="needs_review",reason="substantial_unexpected_operator_content")
        else:
            result.update(classification="unverified",reason="operator_identity_not_visible_or_js_rendered")
        return result
    if kind=="booking_calendar_search" and not marker(title+" "+body,("공실조회","최저가 달력","departure date","vacancy inquiry","step.1")):
        result.update(classification="unverified",reason="actual_booking_calendar_not_visible")
        return result
    if kind=="route_info":
        lowered=(title+" "+body).lower()
        terms=(("osaka","오사카") if "osaka" in original_path else
               ("tsushima","대마도","히타카츠","이즈하라","쓰시마"))
        if not any(word in lowered for word in terms):
            if len(body)>=150:
                result.update(classification="needs_review",reason="wrong_route_or_unrelated_official_content")
            else:
                result.update(classification="unverified",reason="route_specific_content_not_visible")
            return result
    # All identified pages must have honest labels as homepage, instructions or booking entry.
    # A landing confirmation does not imply a date is in inventory.
    result.update(classification="operator_landing_verified",reason="provider_identity_and_path_match")
    return result

def examine_urls(config,session=None):
    own=session or requests.Session()
    urlmap={}
    for route,settings in config["routes"].items():
        for name in ("primary","secondary"):
            url=settings[name]
            if url not in urlmap:
                urlmap[url]={"provider":settings["provider"],"kind":settings[name+"_kind"],"routes":[route]}
            else:
                urlmap[url]["routes"].append(route)
    result=[]
    for url,item in urlmap.items():
        try:
            resp=own.get(url,headers=H,timeout=(12,28),allow_redirects=True)
            value=evaluate_response(url,resp,config,item["provider"],item["kind"])
        except requests.RequestException as e:
            value={"source_url":url,"kind":item["kind"],"provider":item["provider"],
                   "classification":"unverified","reason":"network_error","error":str(e)[:150]}
        value["routes"]=item["routes"]
        result.append(value)
    return result

def main():
    config=json.loads(CONF.read_text("utf8"))
    local=examine_local(config)
    urls=examine_urls(config)
    report={"version":"V90","checked_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
            "source_review_date":config["reviewed_at"],"local":local,"external_destinations":urls,
            "issues":[],"uncertain":[]}
    for issue in local["errors"]:
        report["issues"].append({"kind":"broken_internal_cta_or_markup",**issue})
    for item in urls:
        if item["classification"] in ("suspected_broken","needs_review"):
            report["issues"].append({"kind":"external_destination_requires_manual_review",
                                     "url":item["source_url"],"reason":item["reason"],
                                     "final_url":item.get("final_url"),"routes":item["routes"]})
        elif item["classification"]=="unverified":
            report["uncertain"].append({"url":item["source_url"],"reason":item["reason"],"routes":item["routes"]})
    report["counts"]={k:sum(v["classification"]==k for v in urls) for k in ("operator_landing_verified","unverified","needs_review","suspected_broken")}
    report["status"]="needs_review" if report["issues"] else "unverified_sources" if report["uncertain"] else "verified_landing_only"
    report["fingerprint"]=fingerprint(report["issues"])
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
    lines=["# V90 booking destination health — "+report["status"],"",
           "Checked: "+report["checked_at_utc"],"Target URLs: "+str(len(urls)),
           "Local CTA errors: "+str(len(local["errors"])),"Actionable destination issues: "+str(len(report["issues"])),
           "Unverifiable due to bot/login/JS/temporary errors: "+str(len(report["uncertain"])), "",
           "HTTP 200 confirms only a response, not a purchasable sailing. 403/429 are not proof of a broken reservation page.",""]
    for issue in local["errors"]:
        lines.append("- LOCAL CTA ERROR | "+json.dumps(issue,ensure_ascii=False))
    for v in urls:
        lines.append("- "+v["classification"]+" | "+v["source_url"]+" → "+str(v.get("final_url","unknown"))+" | "+str(v["reason"]))
    (OUT/"summary.md").write_text("\n".join(lines)+"\n","utf8")
    with open(os.environ.get("GITHUB_OUTPUT",os.devnull),"a",encoding="utf8") as fh:
        fh.write("attention="+("true" if report["issues"] else "false")+"\n")
        fh.write("fingerprint="+report["fingerprint"]+"\n")
    print(json.dumps({"status":report["status"],"checked_urls":len(urls),"counts":report["counts"],
                      "issues":report["issues"],"uncertain":report["uncertain"]},ensure_ascii=False))
    return 1 if local["errors"] else 0

if __name__=="__main__":
    raise SystemExit(main())
