#!/usr/bin/env python3
"""NIPPONFERRY V100: end-to-end PRIVATE, read-only GA4 ferry booking-intent pulse.

Fetch two completed nonoverlapping seven-day GA4 Data API periods (Asia/Seoul
calendar), verify V99 route/provider attribution, make V95 private activity
dashboard and V96 editorial review ONLY if both periods are trustworthy.
Never read an invented click count, never upload user analytics to public
GitHub Actions, never alter any public page or booking URL.
"""
import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

from v98_ga4_data_api import AnalyticsDataError, config_status, fetch_paginated, load_service_account
from v99_ga4_attribution_qa import analyze as check_attribution, markdown as quality_markdown
from v95_booking_comparison import summarize as compare_pages, write as write_dashboard
from v96_booking_change_review import compare as compare_periods
from v94_booking_click_report import parse_rows
from v98_ga4_data_api import write_private_csv

SEOUL = ZoneInfo("Asia/Seoul")
ROOT = Path("private-analytics/v100")
MIN_EVENTS = 20
STATUSES = {
    "awaiting_account_connection",
    "source_unavailable",
    "no_current_event_data",
    "current_attribution_review",
    "current_only_no_baseline",
    "prior_attribution_review",
    "qualified_weekly_review_ready",
    "insufficient_current_click_sample",
}

def windows(as_of, days=7):
    """Use completed KST dates. as_of itself is excluded."""
    if days < 1 or days > 31:
        raise ValueError("Comparison days must be between 1 and 31")
    if not isinstance(as_of, dt.date) or isinstance(as_of, dt.datetime):
        raise ValueError("as_of must be a date")
    recent_end = as_of - dt.timedelta(days=1)
    recent_start = recent_end - dt.timedelta(days=days-1)
    prior_end = recent_start - dt.timedelta(days=1)
    prior_start = prior_end - dt.timedelta(days=days-1)
    return {
        "timezone":"Asia/Seoul",
        "as_of":as_of.isoformat(),
        "period_days":days,
        "previous":{"start":prior_start.isoformat(),"end":prior_end.isoformat()},
        "recent":{"start":recent_start.isoformat(),"end":recent_end.isoformat()},
    }

def private_status(out, status, windows_data, blocker=None, diagnostics=None):
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    value={
        "version":"V100","status":status,
        "window":windows_data,
        "actual_click_counts":None,
        "confirmed_bookings":None,
        "source":"Google Analytics Data API — actual user-consented aggregate events only",
        "blocker":blocker,
        "diagnostics":diagnostics or {},
        "note":"Unknown is not zero. No visitor-identifying data and no real report is written to public site or repository."
    }
    (out/"status.json").write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n","utf8")
    return value

def execute(property_id, credentials_path, *, as_of, days=7, output=ROOT,
            fetcher=fetch_paginated, token_loader=load_service_account,
            threshold=100):
    """Credentials are resolved only after checking configuration, never printed."""
    root=Path(output)
    period=windows(as_of,days)
    state=config_status(property_id,credentials_path)
    if state!="ready_to_query":
        return private_status(root,"awaiting_account_connection",period,blocker=state)
    if threshold<20 or threshold>100000:
        raise ValueError("threshold must be between 20 and 100000")

    try:
        token=token_loader(credentials_path)
        # Read-only fetch, never a mutation/booking action.
        recent_raw=fetcher(property_id,token,period["recent"]["start"],period["recent"]["end"])
        if not recent_raw:
            return private_status(root,"no_current_event_data",period,
                                  blocker="No tracked events observed. Cannot infer 0 site interest.")
        recent_quality=check_attribution_from_api(recent_raw)
        if recent_quality["status"] in ("requires_manual_measurement_review","small_sample_with_issues"):
            return private_status(root,"current_attribution_review",period,
                                  blocker="Wrong or unset route/provider/booking-step classification",
                                  diagnostics=quality_summary(recent_quality))
        if recent_quality["status"]=="no_verifiable_outbound_click_data":
            return private_status(root,"no_current_event_data",period,
                                  blocker="Event rows exist but no verified outbound booking-click event.")
        # Read the prior period only after latest data passes the basic integrity gate.
        previous_raw=fetcher(property_id,token,period["previous"]["start"],period["previous"]["end"])
    except AnalyticsDataError as exc:
        return private_status(root,"source_unavailable",period,blocker=str(exc))

    current_path=root/"recent-actual.ga4.actual.csv"
    write_private_csv(recent_raw,current_path)
    current_rows=parse_rows(current_path)
    current=compare_pages(current_rows,period["recent"]["start"]+" ~ "+period["recent"]["end"],threshold)
    write_dashboard(current,root/"recent-dashboard")
    (root/"recent-data-quality.json").write_text(
        json.dumps(recent_quality,ensure_ascii=False,indent=2)+"\n","utf8")
    if not previous_raw:
        return final_report(root,period,"current_only_no_baseline",current,recent_quality,
                            prior=None,trend=None)
    prior_quality=check_attribution_from_api(previous_raw)
    if prior_quality["status"] in ("requires_manual_measurement_review","small_sample_with_issues"):
        # Keep current valid comparison only; no misleading week-over-week result.
        (root/"previous-data-quality.json").write_text(
            json.dumps(prior_quality,ensure_ascii=False,indent=2)+"\n","utf8")
        return final_report(root,period,"prior_attribution_review",current,recent_quality,
                            prior=None,trend=None)
    if prior_quality["status"]=="no_verifiable_outbound_click_data":
        return final_report(root,period,"current_only_no_baseline",current,recent_quality,
                            prior=None,trend=None)

    previous_path=root/"previous-actual.ga4.actual.csv"
    write_private_csv(previous_raw,previous_path)
    previous_rows=parse_rows(previous_path)
    previous=compare_pages(previous_rows,period["previous"]["start"]+" ~ "+period["previous"]["end"],threshold)
    if (current.get("status")!="real_ga4_export_compared"
            or previous.get("status")!="real_ga4_export_compared"):
        return final_report(root,period,"current_only_no_baseline",current,recent_quality,
                            prior=previous,trend=None)
    trend=compare_periods(previous_rows,current_rows,days,days,threshold)
    (root/"trend-review.json").write_text(json.dumps(trend,ensure_ascii=False,indent=2)+"\n","utf8")
    return final_report(root,period,
            "qualified_weekly_review_ready" if recent_quality["operator_clicks"]>=MIN_EVENTS
            else "insufficient_current_click_sample",
            current,recent_quality,prior=previous,trend=trend)

def check_attribution_from_api(raw):
    """Data API rows carry GA4's exact event dimensions, not identity fields."""
    shaped=[]
    for x in raw:
        shaped.append({
            "event":x["Event name"], "count":int(x["Event count"]),
            "route":str(x.get("route","unknown")).lower(),
            "page_area":str(x.get("page_area","unknown")).lower(),
            "placement":str(x.get("placement","unknown")).lower(),
            "operator":str(x.get("operator","unknown")).lower(),
            "destination_step":str(x.get("destination_step","unknown")).lower(),
        })
    return check_attribution(shaped)

def quality_summary(q):
    return {"status":q["status"],"attribution_issue_kinds":[x["reason"] for x in q.get("issues",[])]}

def final_report(root,window,status,current,quality,prior,trend):
    result={
        "version":"V100","status":status,"window":window,
        "confirmed_bookings":None,
        "current_booking_entry_clicks":current.get("booking_entry_clicks_total"),
        "current_operator_clicks":quality.get("operator_clicks"),
        "previous_booking_entry_clicks":prior.get("booking_entry_clicks_total") if prior else None,
        "trend_review_candidates":trend.get("review_candidate_count") if trend else None,
        "current_dashboard":"recent-dashboard/dashboard.html",
        "source":"actual GA4 Data API aggregate records (consented visitors only)",
        "interpretation":"Operator handoff clicks, NOT issued tickets, sales or a statistically proven effect."
    }
    (root/"report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n","utf8")
    (root/"README-PRIVATE.txt").write_text(
        "NIPPONFERRY internal GA4 report. Never upload any of these actual GA4 exports or reports to public GitHub.\n"
        "V100 status: "+status+"\n"
        "Actual events are consented aggregates; an outbound click is not a booked seat.\n","utf8")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--property-id",default=os.environ.get("GA4_PROPERTY_ID",""))
    p.add_argument("--credentials",default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS",""))
    p.add_argument("--as-of",help="End-exclusive YYYY-MM-DD (Asia/Seoul). Default: current local calendar day.")
    p.add_argument("--days",type=int,default=7)
    p.add_argument("--threshold",type=int,default=100)
    p.add_argument("--output",default=str(ROOT))
    p.add_argument("--strict",action="store_true",help="Exit 2 unless two trusted complete periods are compared.")
    a=p.parse_args()
    try:
        as_of=dt.date.fromisoformat(a.as_of) if a.as_of else dt.datetime.now(SEOUL).date()
        result=execute(a.property_id,a.credentials,as_of=as_of,days=a.days,
                       threshold=a.threshold,output=a.output)
    except (ValueError,KeyError,TypeError) as exc:
        print(json.dumps({"status":"invalid_input","error":type(exc).__name__,
              "actual_click_counts":None},ensure_ascii=False))
        return 2
    # Never log access tokens, file paths to private keys or individual GA4 records.
    public={k:v for k,v in result.items() if k in ("status","current_booking_entry_clicks",
         "current_operator_clicks","previous_booking_entry_clicks","trend_review_candidates",
         "actual_click_counts","confirmed_bookings","blocker")}
    print(json.dumps(public,ensure_ascii=False))
    if a.strict and result["status"]!="qualified_weekly_review_ready":
        return 2
    return 0

if __name__=="__main__":sys.exit(main())
