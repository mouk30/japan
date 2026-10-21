#!/usr/bin/env python3
"""V95 NIPPONFERRY: compare REAL consented GA4 ferry handoff events by route and entry page.

This is an offline PRIVATE analytics output, not a website page. Without an
actual GA4 CSV, render unconnected status and UNKNOWN counts, not fabricated 0.
One outbound click is not a reservation, conversion or distinct visitor.
"""
import argparse
import collections
import datetime as dt
import html
import json
import math
from pathlib import Path

from v94_booking_click_report import parse_rows

ROUTES = ("osaka", "fukuoka", "shimonoseki", "tsushima")
NAMES = {
    "osaka": "오사카", "fukuoka": "후쿠오카", "shimonoseki": "시모노세키",
    "tsushima": "대마도", "ferry_hub": "페리 항로 허브", "booking_hub": "예약 안내 허브",
}
BOOKING_STEPS = {"operator_search", "booking_search", "booking_instructions"}
INFORMATION_STEPS = {"route_info", "operator_home"}

PAGES = [
    {"key": "ferry_hub", "label": "페리 항로 허브", "path": "/ferry/", "page_area": "ferry_hub", "route": None},
    {"key": "booking_hub", "label": "예약 안내 허브", "path": "/booking/japan-cruise/", "page_area": "booking_hub", "route": None},
] + [
    {"key": "route_" + r, "label": NAMES[r] + " 가이드", "path": "/guide/busan-" + r + "-ferry/",
     "page_area": "route_guide", "route": r} for r in ROUTES
]

def page_for(row):
    area = row["page_area"]
    route = row["route"]
    if area in ("ferry_hub", "booking_hub"):
        return area
    if area == "route_guide" and route in ROUTES:
        return "route_" + route
    return None

def is_page_view(row):
    return (row["event"] == "ferry_hub_view" and row["page_area"] in ("ferry_hub", "booking_hub")
            or row["event"] == "ferry_route_view" and row["page_area"] == "route_guide")

def is_external_click(row):
    return row["event"] == "ferry_operator_click"

def priority_status(clicks, views, ratio, benchmark, minimum_views=100):
    if views is None or views <= 0:
        return "no_pageview_denominator"
    if views < minimum_views:
        return "low_sample"
    if benchmark is None or benchmark <= 0:
        return "no_comparable_benchmark"
    if ratio is not None and ratio <= benchmark * 0.5:
        return "review_candidate"
    return "monitor"

def summarize(rows, period_label="GA4 실제 CSV 집계 기간", threshold=100):
    pages = {page["key"]: {**page, "pageviews": 0, "has_view_record": False,
                              "outbound_clicks": 0, "booking_entry_clicks": 0,
                              "official_info_clicks": 0} for page in PAGES}
    route_counts = {route: {"booking_entry_clicks": 0, "outbound_clicks": 0,
                             "official_info_clicks": 0, "source_breakdown": {}} for route in ROUTES}
    unknown_route = 0
    ignored_unmapped_sources = 0
    placements = collections.Counter()
    total_external = 0
    booking_total = 0
    view_totals = 0

    for row in rows:
        n = row["count"]
        kind = row["event"]
        key = page_for(row)
        r = row["route"]
        if is_page_view(row) and key:
            pages[key]["pageviews"] += n
            pages[key]["has_view_record"] = True
            view_totals += n
        if not is_external_click(row):
            continue
        total_external += n
        is_booking = row["destination_step"] in BOOKING_STEPS
        if is_booking:
            booking_total += n
        if key:
            pages[key]["outbound_clicks"] += n
            if is_booking: pages[key]["booking_entry_clicks"] += n
            else: pages[key]["official_info_clicks"] += n
        else:
            ignored_unmapped_sources += n
        if r in ROUTES:
            route_counts[r]["outbound_clicks"] += n
            if is_booking: route_counts[r]["booking_entry_clicks"] += n
            else: route_counts[r]["official_info_clicks"] += n
            pair = row["page_area"] + " · " + row["placement"]
            route_counts[r]["source_breakdown"][pair] = route_counts[r]["source_breakdown"].get(pair, 0) + n
        else:
            unknown_route += n
        placements[(row["page_area"], row["placement"],row["destination_step"])] += n

    comparable = []
    for p in pages.values():
        count = p["pageviews"] if p["has_view_record"] and p["pageviews"] > 0 else None
        p["measured_pageviews"] = count
        p["booking_clicks_per_100_views"] = round(100*p["booking_entry_clicks"]/count, 2) if count else None
        p["outbound_clicks_per_100_views"] = round(100*p["outbound_clicks"]/count, 2) if count else None
        if count is not None and count >= threshold:
            comparable.append(p)
    # Aggregate benchmark on pages with adequate, observed denominators ONLY.
    benchmark = (100*sum(p["booking_entry_clicks"] for p in comparable) /
                 sum(p["measured_pageviews"] for p in comparable)) if comparable else None
    for p in pages.values():
        p["data_quality"] = priority_status(p["booking_entry_clicks"],p["measured_pageviews"],
                                            p["booking_clicks_per_100_views"],benchmark,threshold)
        p["review_reasons"] = []
        if p["data_quality"] == "review_candidate":
            p["review_reasons"].append(
                "동의 기반 예약 진입 클릭/조회 비율이 충분한 표본의 사이트 기준치보다 낮음. "
                "버튼 가시성·문구·도착 안내와 해당 기간의 항로 운항 상태부터 점검")
        if p["data_quality"] == "low_sample":
            p["review_reasons"].append("조회 표본 미달 — 저성과 결론을 내리지 말고 측정 기간 확대")
        if p["data_quality"] == "no_pageview_denominator":
            p["review_reasons"].append("GA4 조회 이벤트 분모 미확인 — 0%로 표현하거나 순위 매기지 않음")

    observed = [p for p in pages.values() if p["data_quality"] in ("monitor","review_candidate")]
    rank_pages = sorted(observed, key=lambda p: (-p["booking_clicks_per_100_views"],-p["booking_entry_clicks"],p["key"]))
    for index,p in enumerate(rank_pages,1): p["qualified_activity_rank"] = index
    for p in pages.values():
        if "qualified_activity_rank" not in p: p["qualified_activity_rank"] = None

    route_ranking = sorted(ROUTES, key=lambda r: (-route_counts[r]["booking_entry_clicks"],r))
    # If rows exist but no booking-entry events at all, intent-level metrics may not have been exported.
    has_any_booking = any(row["event"]=="ferry_operator_click" and row["destination_step"] in BOOKING_STEPS for row in rows)
    report = {
        "version":"V95", "status":"real_ga4_export_compared",
        "generated_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "period_label":period_label,"source":"actual GA4 Exploration CSV",
        "unique_reservations":None,
        "pageviews_observed_total":view_totals if view_totals else None,
        "all_official_link_clicks":total_external,
        "booking_entry_clicks_total":booking_total,
        "booking_intent_definition":"operator_search / booking_search / booking_instructions; NOT bookings",
        "measured_booking_entry_category":has_any_booking,
        "unattributed_route_clicks":unknown_route,
        "unmapped_source_clicks":ignored_unmapped_sources,
        "minimum_views_to_rank":threshold,
        "benchmark_per_100_views":round(benchmark,2) if benchmark is not None else None,
        "routes":route_counts,"routes_by_booking_entry_clicks":route_ranking,
        "pages":[pages[p["key"]] for p in PAGES],
        "qualified_page_order":[p["key"] for p in rank_pages],
        "placements":[{"page_area":k[0],"placement":k[1],"destination_step":k[2],"clicks":v}
                      for k,v in sorted(placements.items(),key=lambda kv:(-kv[1],kv[0]))],
        "cautions":[
            "Only visitor-consented recorded GA4 events; visitors who refuse or block analytics are excluded.",
            "Operator information and booking-entry buttons have different intentions; do not equate them.",
            "Booking instructions and operator homepage are not checkout, purchase or reservation completion.",
            "Pageview-based rate is clicks / counted pageviews, not unique visitor conversion and can exceed 100%.",
            "GA4 Explore event aggregates and consent may differ across events or date ranges.",
            "Do not rank pages with absent denominators or fewer than the minimum measured pageviews.",
            "No pre-tag historical comparison, no fabricated traffic and no claim of completed bookings."
        ]
    }
    if not has_any_booking:
        report["status"]="insufficient_booking_step_data"
        # The export can be filtered or the GA4 custom dimension might not be present.
        # Lack of visible booking events is NOT proof that visitors clicked zero times.
        report["booking_entry_clicks_total"]=None
        report["qualified_page_order"]=[]
        for p in report["pages"]:
            p["booking_clicks_per_100_views"]=None
            p["qualified_activity_rank"]=None
            p["data_quality"]="insufficient_booking_event_data"
    return report

def markup(report):
    esc=lambda s: html.escape(str(s),quote=True)
    initial=report["status"]!="real_ga4_export_compared"
    if initial:
        not_connected=report["status"]=="awaiting_real_ga4_export"
        status_title="미연결" if not_connected else "이벤트 자료 부족"
        status_note="GA4 실제 데이터 미제공" if not_connected else "예약 진입 유형 데이터가 없음 · 0건으로 단정 불가"
        cards='<article class="metric"><span>예약·날짜검색 진입 클릭</span><strong>'+status_title+'</strong><small>'+status_note+'</small></article><article class="metric"><span>항로별 클릭 순위</span><strong>미확인</strong><small>가상 숫자를 표시하지 않음</small></article><article class="metric"><span>조회 대비 클릭 활동량</span><strong>미확인</strong><small>페이지 조회 분모 필요</small></article>'
        rows="".join('<tr><th>'+esc(n)+'</th><td>미확인</td><td>미확인</td><td>미확인</td><td>—</td></tr>' for n in ["페리 항로 허브","예약 안내 허브","오사카 가이드","후쿠오카 가이드","시모노세키 가이드","대마도 가이드"])
        message=("실제 GA4 측정 ID가 연결되지 않았거나 GA4 탐색 CSV가 제공되지 않았습니다. 클릭 순위·클릭률은 아직 알 수 없습니다."
                 if not_connected else "CSV는 있지만 예약 진입 유형 이벤트가 없습니다. GA4 이벤트 범위와 맞춤 측정기준을 확인할 때까지 수치를 미확인으로 표시합니다.")
        maxbar=1
        bars=""
    else:
        total=report["booking_entry_clicks_total"]
        ratio=report["benchmark_per_100_views"]
        cards=''.join([
            '<article class="metric"><span>예약·날짜 검색/예약방법 진입 클릭</span><strong>'+f'{total:,}'+'</strong><small>실제 GA4 집계 이벤트 (구매 아님)</small></article>',
            '<article class="metric"><span>공식 선사 모든 외부 링크 클릭</span><strong>'+f'{report["all_official_link_clicks"]:,}'+'</strong><small>운항정보 열람 포함</small></article>',
            '<article class="metric"><span>충분한 표본의 조회 100회당 진입 클릭</span><strong>'+(f'{ratio:g}' if ratio is not None else '계산 불가')+'</strong><small>방문자 전환율이 아닌 페이지 조회당 활동량</small></article>'])
        rows=""
        status_k={"monitor":"측정됨","review_candidate":"검토 후보","low_sample":"표본 부족","no_pageview_denominator":"분모 미확인","no_comparable_benchmark":"비교 기준 부족"}
        for page in report["pages"]:
            v=page["measured_pageviews"]
            rate=page["booking_clicks_per_100_views"]
            rows+='<tr><th><a href="'+esc("https://www.nipponferry.com"+page["path"])+'">'+esc(page["label"])+'</a></th><td>'+ (f"{v:,}" if v is not None else "미확인") +'</td><td>'+f'{page["booking_entry_clicks"]:,}'+'</td><td>'+(f'{rate:g}' if rate is not None else '계산 불가')+'</td><td>'+esc(status_k.get(page["data_quality"],page["data_quality"]))+'</td></tr>'
        maxbar=max([report["routes"][r]["booking_entry_clicks"] for r in ROUTES]+[1])
        bars="".join('<div class="barline"><span>'+esc(NAMES[r])+'</span><div class="bartrack"><div class="barfill" style="width:'+str(round(report["routes"][r]["booking_entry_clicks"]/maxbar*100,2))+'%"></div></div><strong>'+str(report["routes"][r]["booking_entry_clicks"])+'</strong></div>' for r in ROUTES)
        message="실제 GA4 이벤트를 기준으로 항로 및 페이지를 비교했습니다. 기준표본 이상인 경우에만 조회당 활동량 순위를 산출합니다."
    content=f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>NIPPONFERRY · 예약 버튼 클릭 분석</title><style>
:root{{font-family:system-ui,-apple-system,"Malgun Gothic",sans-serif;background:#f2f6f9;color:#133447}}*{{box-sizing:border-box}}body{{margin:0}}main{{max-width:1100px;margin:auto;padding:30px 23px 65px}}header{{background:linear-gradient(110deg,#092d46,#166182);color:#fff;padding:30px;border-radius:18px;margin:0 0 20px}}h1{{font-size:clamp(23px,3vw,36px);margin:4px 0 15px}}header p{{line-height:1.6;color:#d9eef9}}.eyebrow{{font-size:13px;font-weight:800;letter-spacing:.11em}}.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}}.metric,.panel{{background:#fff;border:1px solid #d8e4eb;border-radius:14px;padding:20px;box-shadow:0 5px 18px #11395508}}.metric{{display:flex;flex-direction:column;gap:10px}}.metric span{{font-size:14px;color:#4e6a7c}}.metric strong{{font-size:clamp(22px,3vw,33px);color:#0e4d72}}.metric small{{font-size:12px;color:#6a8291;line-height:1.5}}.panel{{margin-top:17px}}h2{{margin:3px 0 14px;font-size:21px}}.notice{{color:#526c7b;font-size:14px;line-height:1.8}}table{{width:100%;border-collapse:collapse;font-size:14px}}th,td{{border-bottom:1px solid #dce7ed;padding:13px 8px;text-align:left}}th{{font-weight:750}}td{{font-variant-numeric:tabular-nums}}a{{color:#146389}}.barline{{display:grid;grid-template-columns:100px 1fr 42px;gap:11px;align-items:center;margin:15px 0;font-size:14px}}.bartrack{{height:13px;background:#e8eff3;border-radius:10px;overflow:hidden}}.barfill{{height:100%;border-radius:10px;background:linear-gradient(90deg,#2678a2,#1cb6c1)}}.foot{{font-size:13px;color:#536d7c;line-height:1.85;padding-top:12px}}@media(max-width:680px){{main{{padding:13px 10px}}header{{padding:22px 18px}}.grid{{grid-template-columns:1fr}}.panel{{padding:12px}}.scroll{{overflow-x:auto}}table{{min-width:610px}}}}
</style></head><body><main><header><div class="eyebrow">NIPPONFERRY / PRIVATE ANALYTICS</div><h1>예약 버튼 클릭 현황</h1><p>기준: {esc(report.get("period_label","연결 대기"))} · 예약 버튼 클릭 ≠ 예약 완료<br>이 HTML은 사이트에 공개하지 않는 내부 검토용 보고서입니다.</p></header><div class="grid">{cards}</div><section class="panel"><h2>항로별 예약·날짜 검색 진입 클릭</h2><p class="notice">{esc(message)}</p>{bars}</section><section class="panel"><h2>어느 페이지에서 선사로 이동했나?</h2><div class="scroll"><table><thead><tr><th>유입 페이지</th><th>동의 기반 조회</th><th>예약 진입 클릭</th><th>조회 100회당 클릭</th><th>해석</th></tr></thead><tbody>{rows}</tbody></table></div><p class="notice">조회가 적거나 분모가 없는 페이지는 순위를 매기지 않습니다. 관부훼리는 예약 방법 안내 클릭이며 구매가 아닙니다.</p></section><p class="foot">동의하지 않은 방문자와 차단된 GA4 이벤트는 포함되지 않습니다. 같은 사람이 여러 번 클릭할 수 있으므로 고유 이용자 전환율로 읽지 마세요. GA4 가입·설정 이전의 클릭 수는 소급할 수 없습니다.</p></main></body></html>"""
    return content

def write(report,output):
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    (output/"status.json" if report["status"]=="awaiting_real_ga4_export" else output/"report.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    (output/"dashboard.html").write_text(markup(report),encoding="utf8")
    if report["status"]=="real_ga4_export_compared":
        lines=["# 실제 GA4 항로별 예약 클릭 비교", "",
               f"집계기간: {report['period_label']}",
               f"예약·날짜검색 진입 클릭: **{report['booking_entry_clicks_total']}회** (발권 아님)", "",
               "| 페이지 | 측정 조회 | 예약 진입 클릭 | 조회 100회당 클릭 | 상태 |",
               "|---|---:|---:|---:|---|"]
        for p in report["pages"]:
            v = p["measured_pageviews"]
            rate = p["booking_clicks_per_100_views"]
            lines.append(f"| {p['label']} | {v if v is not None else '미확인'} | "
                         f"{p['booking_entry_clicks']} | {rate if rate is not None else '계산 불가'} | {p['data_quality']} |")
        lines.extend(["","※ 외부 선사 이동은 결제·발권 완료가 아닙니다. GA4 동의 기반 집계이며 관부훼리는 예약 방법 안내를 포함합니다."])
        (output/"report.md").write_text("\n".join(lines)+"\n",encoding="utf8")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",help="Actual GA4 Exploration event export CSV")
    parser.add_argument("--output",default="audit-output/v95-private-comparison")
    parser.add_argument("--period",default="실제 GA4 탐색 CSV의 기간")
    parser.add_argument("--min-views",type=int,default=100)
    a=parser.parse_args()
    if a.min_views<20 or a.min_views>100000:parser.error("--min-views must be between 20 and 100000")
    if not a.input:
        report={"version":"V95","status":"awaiting_real_ga4_export",
                "period_label":"실제 데이터 미연결","booking_entry_clicks_total":None,
                "all_official_link_clicks":None,"routes":None,"pages":None,
                "reason":"Public GA4 data not provided; measurement cannot be compared. Do not invent traffic or rankings."}
    else:
        rows=parse_rows(a.input)
        report=summarize(rows,a.period,a.min_views)
    write(report,a.output)
    print(json.dumps({"status":report["status"],
                      "booking_entry_clicks_total":report["booking_entry_clicks_total"],
                      "page_analytics":len(report["pages"]) if report["pages"] else None,
                      "output":a.output},ensure_ascii=False))
if __name__=="__main__":
    main()
