#!/usr/bin/env python3
"""V99: GA4 attribution and operator-integrity audit over REAL V98 event CSV.

Never publish results automatically. Fail closed on missing consented data.
All checks use aggregate events only, not users or private booking information.
"""
import argparse
import collections
import datetime as dt
import json
from pathlib import Path
from v94_booking_click_report import parse_rows

ROUTE_OPERATOR = {
    "osaka": "panstar",
    "tsushima": "panstar",
    "fukuoka": "koreaferry",
    "shimonoseki": "kampuferry",
}
KNOWN_AREA={"ferry_hub","booking_hub","route_guide","home","editorial"}
KNOWN_PLACE={"hub_card","guide_hero","guide_end","guide_sidebar","route_banner","other"}
KNOWN_STEP={"operator_search","booking_search","booking_instructions","route_info","operator_home"}
UNKNOWN={"","unknown","(not set)","(not provided)","not set","(other)","unset"}

def analyze(rows, min_operator_clicks=20):
    if min_operator_clicks < 1:
        raise ValueError("min_operator_clicks must be positive")
    operator_events = [x for x in rows if x["event"]=="ferry_operator_click"]
    total = sum(r["count"] for r in operator_events)
    if not total:
        return {
            "version":"V99","status":"no_verifiable_outbound_click_data",
            "operator_clicks":None,"missing_metadata_events":None,
            "problem_events":None,"operator_matches":None,
            "actions":["Check Vercel GA4 tag, opt-in, custom dimensions and GA4 export; do not infer 0 user interest."]
        }

    reason_counts=collections.Counter()
    examples=collections.Counter()
    by_route=collections.Counter()
    valid=0
    for row in operator_events:
        count=row["count"]
        route=row["route"].lower()
        provider=row["operator"].lower()
        area=row["page_area"].lower()
        place=row["placement"].lower()
        step=row["destination_step"].lower()
        by_route[route]+=count
        issues=[]
        if route not in ROUTE_OPERATOR:
            issues.append("route_unknown")
        if provider in UNKNOWN:
            issues.append("operator_unset")
        if area not in KNOWN_AREA:
            issues.append("page_area_unknown")
        if place not in KNOWN_PLACE:
            issues.append("placement_unknown")
        if step not in KNOWN_STEP:
            issues.append("destination_step_unknown")
        if route in ROUTE_OPERATOR and provider not in UNKNOWN and provider!=ROUTE_OPERATOR[route]:
            issues.append("route_operator_mismatch")
        if route=="fukuoka" and provider=="koreaferry" and step!="booking_search" and place in ("hub_card","guide_hero","guide_end"):
            issues.append("fukuoka_main_cta_not_booking_calendar")
        if route=="shimonoseki" and provider=="kampuferry" and step=="booking_search":
            issues.append("shimonoseki_instructions_mislabeled_checkout")
        if not issues:
            valid+=count
        else:
            for issue in set(issues):
                reason_counts[issue]+=count
            examples[(route,area,provider)]+=count

    missing = sum(r["count"] for r in operator_events if any(
        r[x].lower() in UNKNOWN for x in ("route","page_area","placement","operator","destination_step")))
    bad = total - valid
    invalid_share = round(100*bad/total,2)
    status = "clean_attribution" if bad==0 else "requires_manual_measurement_review"
    if total<min_operator_clicks:
        status = "small_sample_unreliable" if bad==0 else "small_sample_with_issues"
    report = {
        "version":"V99",
        "generated_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "status":status,
        "operator_clicks":total,
        "valid_attribution_events":valid,
        "problem_events":bad,
        "invalid_share_percent":invalid_share,
        "missing_metadata_events":missing,
        "minimum_clicks_for_interpretation":min_operator_clicks,
        "issues":[{"reason":k,"affected_events":n} for k,n in reason_counts.most_common()],
        "top_affected_combinations":[{"route":k[0],"page_area":k[1],"operator":k[2],"events":v}
                                     for k,v in examples.most_common(10)],
        "clicks_by_route":dict(sorted(by_route.items())),
        "actions":[
            "Fix GA4 custom dimension registration and onsite tracking mappings only after verifying actual data.",
            "Keep independent V90 official link and sailing validity checks; a GA4 click cannot prove booking success.",
            "Do not use missing consented event counts or low sample sizes as evidence of low site demand.",
            "Avoid automatically editing prices, indexed content or booking links based solely on analytics.",
        ],
    }
    return report

def markdown(report):
    header=["# V99 — GA4 예약버튼 항로·출처 정확성 검사","",
            "수집 동의 기반 실제 GA4 외부 예약 링크 클릭만 검사합니다.","",
            "상태: **"+report["status"]+"**",""]
    if report.get("operator_clicks") is None:
        return "\n".join(header+["**실제 클릭 데이터를 확인할 수 없어 오류 비율·클릭 합계 모두 미확인입니다.**",""])
    header+=["| 검사 항목 | 값 |","|---|---:|",
        f"| 측정된 선사 링크 클릭 이벤트 | {report['operator_clicks']:,} |",
        f"| 항로·선사·출처 일치 이벤트 | {report['valid_attribution_events']:,} |",
        f"| 측정 설정 재확인 대상 이벤트 | {report['problem_events']:,} |",
        f"| 미등록/미설정 구분값 포함 | {report['missing_metadata_events']:,} |","",
        "※ 이 값은 실제 발권/구매가 아닌 **선사 사이트 링크 클릭 수**입니다.","",
        "## 데이터 품질 검토",""]
    for item in report["issues"]:
        header.append(f"- {item['reason']}: {item['affected_events']:,} 이벤트")
    if not report["issues"]:header.append("- 구분값 누락 또는 항로-선사 불일치가 집계에서 발견되지 않음")
    return "\n".join(header+["","이 분석으로 검색 노출·수익 증가를 보장하거나 사이트 글을 자동 변경하지 않습니다.",""])

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",help="Actual V98 GA4 Data API CSV or GA4 Explore export")
    p.add_argument("--output",default="private-analytics/v99")
    p.add_argument("--min-clicks",type=int,default=20)
    args=p.parse_args()
    output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
    if not args.input:
        report={"version":"V99","status":"awaiting_real_ga4_data",
            "operator_clicks":None,"problem_events":None,
            "missing_metadata_events":None,
            "message":"Real GA4 consented click exports have not been supplied; not zero."}
    else:
        report=analyze(parse_rows(args.input),args.min_clicks)
    (output/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
    (output/"report.md").write_text(markdown(report),"utf8")
    print(json.dumps({"status":report["status"],
        "operator_clicks":report["operator_clicks"],
        "problem_events":report["problem_events"]},ensure_ascii=False))

if __name__=="__main__":main()
