#!/usr/bin/env python3
"""V94: Aggregate a REAL GA4 Exploration event export. Never create fabricated metrics.

The report measures consented outbound booking-intent clicks, NOT ticket purchases.
CSV headers: Event name, Event count, route, page_area, placement, operator,
destination_step. Both Title Case and snake_case aliases accepted.
"""
import argparse,csv,datetime as dt,json,collections,re
from pathlib import Path
EVENTS={"ferry_operator_click","ferry_info_open","ferry_route_select","ferry_hub_open","ferry_hub_view","ferry_route_view"}
ROUTES={"osaka","fukuoka","shimonoseki","tsushima"}
SOURCES={"ferry_hub","booking_hub","route_guide","editorial","home"}
def canonical(s):
    return re.sub(r"[^a-z0-9가-힣]","",str(s or "").lower())
def parse_rows(path):
    with open(path,encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames:raise ValueError("Empty GA4 event export; no measurements")
        cols={canonical(n):n for n in reader.fieldnames}
        def find(*labels):
            for label in labels:
                if canonical(label) in cols:return cols[canonical(label)]
            return None
        event=find("event_name","event name","이벤트 이름")
        count=find("event_count","event count","이벤트 수")
        route=find("route","항로")
        area=find("page_area","page area","페이지 영역")
        placement=find("placement","버튼 위치")
        operator=find("operator","선사")
        step=find("destination_step","destination step","도착 단계")
        if not event or not count:
            raise ValueError("GA4 export must contain Event name and Event count columns")
        if not route or not area:
            raise ValueError("GA4 Exploration must include custom dimensions route and page_area")
        rows=[]
        for index,item in enumerate(reader,2):
            name=(item.get(event) or "").strip()
            if not name or name not in EVENTS:continue
            raw=(item.get(count) or "").replace(",","").strip()
            if not re.fullmatch(r"\d+",raw):raise ValueError(f"Line {index}: invalid event_count {raw!r}")
            x={
                "event":name,"count":int(raw),
                "route":(item.get(route) or "unknown").strip().lower(),
                "page_area":(item.get(area) or "unknown").strip().lower(),
                "placement":(item.get(placement) or "unknown").strip().lower() if placement else "unknown",
                "operator":(item.get(operator) or "unknown").strip().lower() if operator else "unknown",
                "destination_step":(item.get(step) or "unknown").strip().lower() if step else "unknown"
            }
            if x["count"] > 100_000_000:raise ValueError(f"Line {index}: unexpectedly large count; check export")
            rows.append(x)
    if not rows:raise ValueError("No tracked ferry events in the supplied GA4 export; don't display a zero performance claim")
    return rows

def build_report(rows,file_description=""):
    operator=collections.Counter()
    placement=collections.Counter()
    hubs=collections.Counter()
    guide_views=collections.Counter()
    guide_clicks=collections.Counter()
    info=collections.Counter()
    destinations=collections.Counter()
    total=0
    for row in rows:
        count=row["count"]
        route=row["route"]
        area=row["page_area"]
        kind=row["event"]
        if kind=="ferry_operator_click":
            total+=count
            if route in ROUTES:operator[route]+=count
            placement[(area,row["placement"])]+=count
            destinations[(route,row["destination_step"])]+=count
            if area=="route_guide" and route in ROUTES:guide_clicks[route]+=count
        elif kind=="ferry_hub_view" and area in ("ferry_hub","booking_hub"):
            hubs[area]+=count
        elif kind=="ferry_route_view" and route in ROUTES:
            guide_views[route]+=count
        elif kind=="ferry_info_open":
            info[route]+=count
    source_clicks=collections.Counter()
    for (area,_placement),v in placement.items():source_clicks[area]+=v
    # A single visitor may click several times. This is an activity ratio and can exceed 100.
    hub_ratios={source:{
        "observed_clicks":source_clicks[source],
        "observed_page_views":hubs[source] if hubs[source] else None,
        "clicks_per_100_pageviews":round(100*source_clicks[source]/hubs[source],2) if hubs[source] else None
    } for source in ("ferry_hub","booking_hub")}
    guide_ratios={route:{
        "observed_clicks":guide_clicks[route],
        "observed_page_views":guide_views[route] if guide_views[route] else None,
        "clicks_per_100_pageviews":round(100*guide_clicks[route]/guide_views[route],2) if guide_views[route] else None
    } for route in sorted(ROUTES)}
    return {
       "generated_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
       "status":"real_ga4_export_aggregated",
       "data_source":file_description,
       "metric":"consented operator-site click events, NOT bookings",
       "operator_clicks_total":total,
       "operator_clicks_by_route":{k:operator[k] for k in sorted(ROUTES)},
       "operator_clicks_by_source":dict(sorted(source_clicks.items())),
       "operator_clicks_by_button": [{"page_area":k[0],"placement":k[1],"clicks":v} for k,v in sorted(placement.items())],
       "official_landing_types":[{"route":k[0],"step":k[1],"clicks":v} for k,v in sorted(destinations.items())],
       "factual_info_clicks_by_route":dict(sorted(info.items())),
       "hub_activity":hub_ratios,
       "guide_activity":guide_ratios,
       "limitations":[
          "Numbers are only from the attached GA4 event export and explicit consented tracking.",
          "Consent refusals/ad blockers cause undercount; they are not zero-intent users.",
          "A click is NOT a ticket sale; the report cannot verify actual reservations.",
          "Clicks per 100 pageviews are not unique visitor conversion rates and may exceed 100.",
          "No historical baseline can be recreated before instrumentation was enabled."
       ]
    }
def markdown(data):
    lines=["# NIPPONFERRY — GA4 공식 선사 클릭 분석","",
       f"상태: **{data['status']}** · 소스: {data['data_source']}","",
       "이 보고서는 **공식 선사 이동 클릭 수**만 측정합니다. 실제 결제·발권 수가 아닙니다.","",
       f"측정된 공식 선사 이동 클릭 합계: **{data['operator_clicks_total']:,}회**","",
       "| 항로 | 공식 선사 이동 클릭 |","|---|---:|"]
    lines += [f"| {r} | {v:,} |" for r,v in data["operator_clicks_by_route"].items()]
    lines += ["","| 허브 위치 | 공식 사이트 클릭 | 해당 허브 페이지 조회 | 조회 100회당 클릭 |","|---|---:|---:|---:|"]
    for area,v in data["hub_activity"].items():
        views=v["observed_page_views"]
        ratio=v["clicks_per_100_pageviews"]
        lines.append(f"| {area} | {v['observed_clicks']:,} | {views if views is not None else '미제공'} | {ratio if ratio is not None else '계산 불가'} |")
    lines+=["","**주의:** 클릭이 구매 또는 예약 확정은 아닙니다. 수집 동의한 방문자의 행동만 포함합니다."]
    return "\n".join(lines)+"\n"
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",help="GA4 Exploration CSV exported from your actual account; no synthetic data")
    parser.add_argument("--output",default="audit-output/v94-real-click-report",help="Local report output folder")
    args=parser.parse_args()
    folder=Path(args.output)
    folder.mkdir(parents=True,exist_ok=True)
    if not args.input:
        notice={"status":"awaiting_ga4_account_connection_and_real_csv","operator_clicks_total":None,
                "message":"No analytics export supplied; counts are unknown, NOT zero."}
        (folder/"status.json").write_text(json.dumps(notice,ensure_ascii=False,indent=2)+"\n","utf8")
        print(json.dumps(notice,ensure_ascii=False))
        return
    rows=parse_rows(args.input)
    report=build_report(rows,Path(args.input).name)
    (folder/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
    (folder/"report.md").write_text(markdown(report),"utf8")
    print(json.dumps({"status":report["status"],"operator_clicks_total":report["operator_clicks_total"],
      "routes":report["operator_clicks_by_route"]},ensure_ascii=False))
if __name__=="__main__":
    main()
