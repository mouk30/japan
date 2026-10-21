#!/usr/bin/env python3
"""V96: editorial review priorities from two REAL, equal-length consented GA4 CSV exports.

No source data -> no click figures. No automatic edits to public HTML.
Heuristics flag review candidates, not statistically significant changes.
"""
import argparse
import datetime as dt
import json
from pathlib import Path

from v94_booking_click_report import parse_rows
from v95_booking_comparison import summarize

def compare(previous, current, previous_days, current_days, threshold=100):
    if previous_days < 1 or current_days < 1:
        raise ValueError("A period needs at least one day")
    if previous_days != current_days:
        raise ValueError("Periods must have equal lengths before comparing click activity")
    earlier = summarize(previous, "이전 기간", threshold)
    latest = summarize(current, "최근 기간", threshold)
    keys = {p["key"]:p for p in earlier["pages"]}
    findings = []
    for page in latest["pages"]:
        old = keys[page["key"]]
        a = old["booking_clicks_per_100_views"]
        b = page["booking_clicks_per_100_views"]
        obs_old = old["measured_pageviews"]
        obs_now = page["measured_pageviews"]
        adequate = bool(obs_old is not None and obs_old >= threshold and obs_now is not None and obs_now >= threshold)
        relative = round((b-a)/a*100,1) if adequate and a is not None and a>0 and b is not None else None
        delta = round(b-a,2) if adequate and a is not None and b is not None else None
        if not adequate:
            decision="hold_insufficient_comparable_views"
            action="동일한 수집 설정과 충분한 조회 표본이 확보될 때까지 판단 보류"
        elif (delta is not None and delta <= -2 and relative is not None and relative <= -25):
            decision="editorial_review_candidate"
            action="버튼 첫 화면 노출·설명문·동선·외부 선사 URL과 해당 기간 결항/예약제한을 확인. 실제 원인 확정 전 변경 금지"
        elif delta is not None and delta > 0:
            decision="improved_activity"
            action="변경 유지하며 공식 링크 품질과 관찰 기간을 계속 점검"
        else:
            decision="monitor"
            action="급한 수정 근거 없음. 주간 추세 재확인"
        findings.append({
            "page":page["key"],"label":page["label"],"path":page["path"],
            "prior_views":obs_old,"recent_views":obs_now,
            "prior_booking_entry_clicks":old["booking_entry_clicks"],
            "recent_booking_entry_clicks":page["booking_entry_clicks"],
            "prior_clicks_per_100_views":a if adequate else None,
            "recent_clicks_per_100_views":b if adequate else None,
            "change_points_per_100_views":delta,
            "relative_change_percent":relative,
            "decision":decision,"review_step":action,
        })
    order={"editorial_review_candidate":0,"monitor":1,"improved_activity":2,"hold_insufficient_comparable_views":3}
    findings.sort(key=lambda x:(order[x["decision"]],x["page"]))
    return {
        "version":"V96","status":"real_ga4_two_period_comparison",
        "generated_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "period_days":current_days,"minimum_pageviews_each_period":threshold,
        "review_candidate_count":sum(x["decision"]=="editorial_review_candidate" for x in findings),
        "pages":findings,
        "limits":[
            "This is a heuristic request for human review, not statistical proof that a design change caused traffic changes.",
            "GA4-consented sessions, operator schedules, seasonality and source mix may vary between the two periods.",
            "Clicks are booking-search/instruction entry, NOT ticket sales.",
            "No automatic edits to published pages, prices, metadata, or booking destinations.",
            "Equal period length and sufficient observations do not imply matched audiences or controlled A/B tests.",
        ]
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--previous",help="Actual GA4 export for prior period")
    p.add_argument("--current",help="Actual GA4 export for recent period")
    p.add_argument("--previous-days",type=int,default=7)
    p.add_argument("--current-days",type=int,default=7)
    p.add_argument("--min-views",type=int,default=100)
    p.add_argument("--output",default="audit-output/v96-editorial-review")
    args=p.parse_args()
    target=Path(args.output)
    target.mkdir(parents=True,exist_ok=True)
    if not args.previous or not args.current:
        status={"status":"awaiting_two_real_ga4_exports","review_candidate_count":None,
                "pages":None,"reason":"No connected real GA4 data. Cannot infer booking clicks, rankings or changes."}
        (target/"status.json").write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n","utf8")
        print(json.dumps(status,ensure_ascii=False))
        return
    if args.min_views<20: p.error("min-views must be 20 or higher")
    result=compare(parse_rows(args.previous),parse_rows(args.current),
                   args.previous_days,args.current_days,args.min_views)
    (target/"review_queue.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n","utf8")
    lines=["# NIPPONFERRY 실제 데이터 기반 편집 검토 대기표","",
           f"이전/최근 각각 {result['period_days']}일, 표본 기준 {result['minimum_pageviews_each_period']}조회","",
           "이 보고서는 실제 예약 매출이 아니라 동의 기반 선사 예약 화면 진입 클릭을 비교합니다.","",
           "| 페이지 | 이전 100조회당 진입 | 최근 100조회당 진입 | 판단 |",
           "|---|---:|---:|---|"]
    for x in result["pages"]:
        a=x["prior_clicks_per_100_views"]
        b=x["recent_clicks_per_100_views"]
        lines.append(f"| {x['label']} | {a if a is not None else '미확인'} | {b if b is not None else '미확인'} | {x['decision']} |")
    lines.extend(["","## 검토 후보만 상세 확인",""])
    candidates=[x for x in result["pages"] if x["decision"]=="editorial_review_candidate"]
    for x in candidates:
        lines.append(f"- {x['label']} ({x['path']}): {x['review_step']}")
    if not candidates: lines.append("검토 후보 없음. 이 결과가 매출이나 UX 개선을 증명하는 것은 아닙니다.")
    lines.extend(["","데이터가 실제로 달라졌더라도 자동으로 홈페이지 코드를 고치지 않습니다."])
    (target/"review_queue.md").write_text("\n".join(lines)+"\n","utf8")
    print(json.dumps({"status":result["status"],"review_candidate_count":result["review_candidate_count"]},ensure_ascii=False))
if __name__=="__main__":
    main()
