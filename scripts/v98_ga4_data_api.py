#!/usr/bin/env python3
"""V98: Retrieve ACTUAL opt-in ferry events using the GA4 Data API (read-only).

GA4 Data API v1beta, service account with Analytics Viewer permission.
Never send user identifiers or raw booking PII; export only aggregate event counts.
No credentials/property -> status unknown, NOT zero. Never auto-upload real data.
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

EVENTS = (
    "ferry_operator_click", "ferry_hub_view", "ferry_route_view",
    "ferry_info_open", "ferry_route_select", "ferry_hub_open",
)
CUSTOM_FIELDS = ("route", "page_area", "placement", "operator", "destination_step")
DIMENSIONS = ("eventName",) + tuple("customEvent:" + x for x in CUSTOM_FIELDS)
METRIC = "eventCount"
HEADER = ("Event name", "Event count") + CUSTOM_FIELDS
SCOPES = ("https://www.googleapis.com/auth/analytics.readonly",)
OUTPUT = Path("private-analytics/v98")
PROPERTY_PATTERN = re.compile(r"^[0-9]{5,16}$")
MAX_ROWS = 10000
PAGE_SIZE = 1000

class AnalyticsDataError(Exception):
    """Actionable configuration or API problem, not a zero-traffic claim."""

def config_status(property_id, credentials_file):
    if not property_id:
        return "missing_ga4_property_id"
    if not PROPERTY_PATTERN.fullmatch(str(property_id)):
        return "invalid_ga4_property_id"
    if not credentials_file:
        return "missing_service_account_credentials"
    if not Path(credentials_file).is_file():
        return "service_account_file_unavailable"
    return "ready_to_query"

def create_request(start="7daysAgo",end="yesterday",limit=PAGE_SIZE,offset=0):
    if not isinstance(limit,int) or limit<1 or limit>PAGE_SIZE:
        raise ValueError("Invalid paging limit")
    if not isinstance(offset,int) or offset<0:
        raise ValueError("Invalid offset")
    return {
        "dateRanges":[{"startDate":start,"endDate":end}],
        "dimensions":[{"name":x} for x in DIMENSIONS],
        "metrics":[{"name":METRIC}],
        "dimensionFilter":{"filter":{"fieldName":"eventName",
            "inListFilter":{"values":list(EVENTS), "caseSensitive":True}}},
        "limit":str(limit),"offset":str(offset),
        "keepEmptyRows":False,
        "returnPropertyQuota":False,
    }

def api_request(url,payload,access_token,transport=None):
    if not access_token:
        raise AnalyticsDataError("Missing OAuth access token")
    post = json.dumps(payload,separators=(",",":")).encode("utf8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=post,
        method="POST" if post is not None else "GET",
        headers={
            "Authorization":"Bearer "+access_token,
            "Content-Type":"application/json",
            "Accept":"application/json",
            "User-Agent":"NIPPONFERRY-ReadOnlyGA4/1.0",
        },
    )
    fetch = transport or urllib.request.urlopen
    try:
        with fetch(request, timeout=25) as result:
            payload = json.loads(result.read(4000000).decode("utf8"))
            if not isinstance(payload,dict):
                raise AnalyticsDataError("GA4 response was not an object")
            return payload
    except urllib.error.HTTPError as e:
        # Do not echo provider response bodies or access credentials to logs.
        message = {
            400: "GA4 request rejected; verify custom event dimensions and property metadata.",
            401: "Service account authentication was rejected.",
            403: "Service account needs Viewer access to the GA4 property (or Data API must be enabled).",
            404: "GA4 property ID unavailable; GA4 Measurement ID G-... is NOT the numeric Property ID.",
            429: "GA4 Data API quota reached; retry later.",
        }.get(e.code,"Google Analytics API returned an HTTP error")
        raise AnalyticsDataError(message + f" [HTTP {e.code}]") from None
    except (urllib.error.URLError,TimeoutError,OSError) as e:
        raise AnalyticsDataError(f"GA4 network unavailable: {type(e).__name__}") from None
    except (json.JSONDecodeError,UnicodeError) as e:
        raise AnalyticsDataError(f"Malformed GA4 response: {type(e).__name__}") from None

def ensure_metadata(data):
    names = {item.get("apiName") for item in data.get("dimensions",[]) if isinstance(item,dict)}
    missing = sorted(set(DIMENSIONS) - names)
    if missing:
        raise AnalyticsDataError(
            "GA4 registered event custom dimensions missing or unavailable: "+", ".join(missing)+
            ". Register route, page_area, placement, operator, destination_step with Event scope in GA4 Admin > Custom definitions.")
    metrics = {item.get("apiName") for item in data.get("metrics",[]) if isinstance(item,dict)}
    if METRIC not in metrics:
        raise AnalyticsDataError("GA4 eventCount metric unavailable in property metadata")
    return True

def parse_report(response):
    """Return normalized aggregate event rows, FAIL CLOSED on thresholding or ambiguities."""
    meta=response.get("metadata") or {}
    if meta.get("dataLossFromOtherRow"):
        raise AnalyticsDataError("GA4 marked dataLossFromOtherRow; results might omit rare route labels")
    if meta.get("subjectToThresholding"):
        raise AnalyticsDataError("GA4 report is subject to privacy thresholding; cannot compare route performance reliably")
    dim_headers = [x.get("name") for x in response.get("dimensionHeaders",[])]
    metrics = [x.get("name") for x in response.get("metricHeaders",[])]
    if dim_headers != list(DIMENSIONS) or metrics != [METRIC]:
        raise AnalyticsDataError("GA4 returned unexpected dimensions/metric layout")
    result=[]
    for pos,row in enumerate(response.get("rows",[]),1):
        dims = [x.get("value","") for x in row.get("dimensionValues",[])]
        values = [x.get("value","") for x in row.get("metricValues",[])]
        if len(dims)!=len(DIMENSIONS) or len(values)!=1:
            raise AnalyticsDataError(f"GA4 returned malformed aggregate row {pos}")
        if not re.fullmatch(r"[0-9]+",values[0]):
            raise AnalyticsDataError(f"Invalid aggregate event count on row {pos}")
        result.append({
            "Event name":dims[0],
            "Event count":int(values[0]),
            **{name:value for name,value in zip(CUSTOM_FIELDS,dims[1:])},
        })
    if any(x["Event name"] not in EVENTS for x in result):
        raise AnalyticsDataError("GA4 returned events outside the requested ferry event names")
    return result

def fetch_paginated(property_id,access_token,start="7daysAgo",end="yesterday",
                    request_func=api_request,max_rows=MAX_ROWS):
    base=f"https://analyticsdata.googleapis.com/v1beta/properties/{property_id}"
    ensure_metadata(request_func(base+"/metadata",None,access_token))
    offset=0
    rows=[]
    row_count=None
    while row_count is None or offset < row_count:
        response=request_func(base+":runReport",create_request(start,end,limit=PAGE_SIZE,offset=offset),access_token)
        if row_count is None:
            try:row_count=int(response["rowCount"])
            except (KeyError,ValueError,TypeError):
                raise AnalyticsDataError("GA4 rowCount is missing; cannot verify complete report") from None
            if row_count<0 or row_count>max_rows:
                raise AnalyticsDataError("GA4 aggregate rows exceed bounded extraction limit; narrow date range")
        chunk=parse_report(response)
        if not chunk and row_count and offset<row_count:
            raise AnalyticsDataError("GA4 pagination ended early; abort incomplete report")
        rows.extend(chunk)
        offset+=len(chunk)
        if offset>row_count:
            raise AnalyticsDataError("GA4 pagination exceeded declared rowCount")
        if row_count==0:break
    if offset!=row_count:
        raise AnalyticsDataError("GA4 pagination incomplete; never rank from partial data")
    return rows

def load_service_account(path):
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
    except ImportError:
        raise AnalyticsDataError("Install google-auth and requests to read GA4 Data API") from None
    try:
        creds=service_account.Credentials.from_service_account_file(path,scopes=SCOPES)
        creds.refresh(Request())
        if not creds.token:raise AnalyticsDataError("Google service account token missing")
        return creds.token
    except AnalyticsDataError:
        raise
    except Exception:
        # Never put private-key text or endpoint response into any diagnostics.
        raise AnalyticsDataError("Service account OAuth failed. Check key, Data API and GA4 property Viewer access.") from None

def write_private_csv(rows,out):
    out=Path(out)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",encoding="utf-8",newline="") as file:
        writer=csv.DictWriter(file,fieldnames=HEADER,extrasaction="ignore")
        writer.writeheader()
        for row in rows:writer.writerow(row)
    try: os.chmod(out,0o600)
    except OSError:pass
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--property-id",default=os.environ.get("GA4_PROPERTY_ID",""))
    p.add_argument("--credentials",default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS",""))
    p.add_argument("--start",default="7daysAgo")
    p.add_argument("--end",default="yesterday")
    p.add_argument("--output",default=str(OUTPUT/"actual-ferry-events.ga4.actual.csv"))
    p.add_argument("--strict",action="store_true",help="Exit nonzero if property/auth unavailable")
    args=p.parse_args()
    state=config_status(args.property_id,args.credentials)
    if state!="ready_to_query":
        # do not overwrite any existing real report or expose the credentials path
        print(json.dumps({"status":"not_connected","blocker":state,"real_click_data":None},ensure_ascii=False))
        return 2 if args.strict else 0
    try:
        token=load_service_account(args.credentials)
        rows=fetch_paginated(args.property_id,token,args.start,args.end)
        # A zero-row result is not a verified zero click performance trend.
        if not rows:
            print(json.dumps({"status":"no_matching_ga4_events_in_period",
                "real_click_data":None,
                "note":"Confirm actual consented events and registered event custom dimensions; never infer 0 demand."},
                ensure_ascii=False))
            return 2 if args.strict else 0
        path=write_private_csv(rows,args.output)
        # One command produces the Korean private V95 comparison dashboard from
        # exactly the returned GA4 aggregates. Never deploy dashboard to site/.
        try:
            from v95_booking_comparison import summarize, write
            from v94_booking_click_report import parse_rows
            output_dir=path.parent/"v98-real-dashboard"
            report=summarize(parse_rows(path),period_label=args.start+" ~ "+args.end)
            write(report,output_dir)
            report_status=report["status"]
            booking_entry_clicks=report.get("booking_entry_clicks_total")
        except (ImportError,ValueError,KeyError) as e:
            raise AnalyticsDataError("Actual GA4 extraction worked, but comparison report failed: "+type(e).__name__) from None
        print(json.dumps({"status":"actual_ga4_aggregates_and_private_dashboard_ready",
            "aggregate_rows":len(rows),
            "private_report_path":str(path),
            "private_dashboard_path":str(output_dir/"dashboard.html"),
            "analytics_status":report_status,
            "measured_booking_entry_clicks":booking_entry_clicks,
            "date_range":{"start":args.start,"end":args.end},
            "purchase_count":None},ensure_ascii=False))
        return 0
    except AnalyticsDataError as exc:
        print(json.dumps({"status":"ga4_api_verification_failed",
            "reason":str(exc),"real_click_data":None},ensure_ascii=False))
        return 2

if __name__=="__main__":
    sys.exit(main())
