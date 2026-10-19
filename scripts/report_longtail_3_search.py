#!/usr/bin/env python3
"""Import REAL search-page CSV exports for the 3-page NIPPONFERRY long-tail experiment.

No Google/Naver API or traffic backend is assumed. Missing rows are never shown as zero.
This script accepts URL/page-level exports; query-only CSVs are rejected.
"""
import argparse
import csv
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, unquote

ORIGIN="https://www.nipponferry.com"
PAGES={
    "busan_hakata":"busan-hakata-ferry-reservation",
    "bukan_shimonoseki":"bukan-ferry-shimonoseki-price",
    "panstar_cabins":"panstar-miracle-osaka-cabin-types",
}
TARGETS={name:"/japan-cruise/"+slug+"/" for name,slug in PAGES.items()}

FIELDS={
 "url":{"page","pages","top pages","url","landing page","페이지","상위 페이지","방문 페이지"},
 "clicks":{"clicks","click","클릭수","클릭"},
 "impressions":{"impressions","impression","노출수","노출"},
 "ctr":{"ctr","클릭률"},
 "position":{"position","average position","avg position","average ranking","게재순위","평균 게재순위","평균순위"},
}
def normalize_field(value):
    return re.sub(r"\s+"," ",str(value or "").strip().lower().replace("\ufeff",""))
def source_columns(columns):
    normalized={normalize_field(c):c for c in columns if c}
    result={}
    for key,aliases in FIELDS.items():
        found=[normalized[a] for a in aliases if a in normalized]
        if found:
            result[key]=sorted(found)[0]
    required={"url","clicks","impressions"}
    missing=sorted(required-set(result))
    if missing:
        raise ValueError("URL별 페이지 성과 CSV가 아닙니다. 필요한 열 누락: "+", ".join(missing)
                         + " (예: Top pages, Clicks, Impressions). 검색어 전용 CSV는 사용할 수 없습니다.")
    return result

def canonical_path(value):
    value=(value or "").strip()
    if not value: return None
    split=urlsplit(value)
    if split.scheme and split.scheme.lower() not in ("http","https"):return None
    if split.netloc:
        if split.hostname not in ("www.nipponferry.com","nipponferry.com"):return None
        path=split.path
    else:
        path=split.path
    path=unquote(path).rstrip("/")+"/"
    if not path.startswith("/"):path="/"+path
    return path

def number(value,integer=True):
    s=str(value or "").strip().replace("\u00a0","").replace(" ","").replace("%","")
    if not s:return None
    if "," in s and "." not in s:
        s=s.replace(",",".") if re.search(r",\d{1,2}$",s) else s.replace(",","")
    else:s=s.replace(",","")
    try:v=float(s)
    except ValueError:raise ValueError("숫자 형식 오류: "+repr(value))
    if not (v>=0 and v<float("inf")):raise ValueError("음수·무한대 숫자는 허용하지 않습니다: "+repr(value))
    if integer:
        if v!=int(v):raise ValueError("클릭·노출 숫자는 정수여야 합니다: "+repr(value))
        return int(v)
    return v

def load(path):
    content=Path(path).read_text(encoding="utf-8-sig")
    try:dialect=csv.Sniffer().sniff(content[:4096],delimiters=",;\t")
    except csv.Error:dialect=csv.excel
    reader=csv.DictReader(content.splitlines(),dialect=dialect)
    if not reader.fieldnames:raise ValueError("빈 CSV: "+str(path))
    cols=source_columns(reader.fieldnames)
    seen={}
    for line,row in enumerate(reader,start=2):
        parsed=canonical_path(row.get(cols["url"],""))
        if parsed not in TARGETS.values():continue
        if parsed in seen:raise ValueError("같은 URL의 중복 행: "+parsed+
                                            " (날짜별·쿼리별 데이터는 페이지별로 다시 내보내세요)")
        clicks=number(row.get(cols["clicks"]),True)
        impressions=number(row.get(cols["impressions"]),True)
        if clicks is None or impressions is None:raise ValueError("URL 행에 클릭·노출 값 누락: "+parsed)
        if impressions==0 and clicks>0:raise ValueError("노출 0에 클릭 > 0인 행: "+parsed)
        ctr=number(row.get(cols["ctr"]),False) if "ctr" in cols else None
        position=number(row.get(cols["position"]),False) if "position" in cols else None
        seen[parsed]={"status":"observed","impressions":impressions,"clicks":clicks,
                      "ctr_percent":round(clicks*100/impressions,2) if impressions else None,
                      "exported_ctr_percent":ctr,
                      "average_position":position}
    return seen

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gsc-pages",type=Path,help="GSC > Performance > Pages CSV (real export)")
    ap.add_argument("--naver-pages",type=Path,help="Naver URL/page-level CSV if provided; not query-only")
    ap.add_argument("--start",required=True,help="Measurement period start YYYY-MM-DD")
    ap.add_argument("--end",required=True,help="Measurement period end YYYY-MM-DD")
    ap.add_argument("--out",default="audit-output/longtail-3/search-evidence",help="Directory to write JSON and Markdown")
    args=ap.parse_args()
    if not args.gsc_pages and not args.naver_pages:ap.error("GSC 또는 Naver CSV 한 개 이상 필요")
    try:
        start=date.fromisoformat(args.start);end=date.fromisoformat(args.end)
        if end<start:ap.error("기간 종료가 시작보다 빠릅니다")
    except ValueError:ap.error("날짜는 YYYY-MM-DD 형식이어야 합니다")
    inputs={"Google":args.gsc_pages,"Naver":args.naver_pages}
    collected={}
    for source,file in inputs.items():
        collected[source]=load(file) if file else None
    report={"experiment":"longtail_ferry_trial","period":{"start":str(start),"end":str(end)},
            "generated_utc":datetime.now(timezone.utc).isoformat(),
            "evidence":"search console exported URL/page rows; no GA4 or booking claims",
            "sources":{}}
    md=["# NIPPONFERRY 3편 실제 검색 성과",
        f"측정 기간: **{start} ~ {end}**",
        "검색 실측 자료만 반영했습니다. 미연결 및 CSV에 없는 URL은 0이 아니라 **미측정**입니다.",
        "| 검색엔진 | 주제 | 노출 | 클릭 | CTR | 평균 게재순위 | 상태 |",
        "|---|---|---:|---:|---:|---:|---|"]
    for source,items in collected.items():
        report["sources"][source]={"provided":items is not None,"pages":{}}
        for name,path in TARGETS.items():
            x=items.get(path) if items is not None else None
            status=x["status"] if x else ("not_in_export" if items is not None else "not_provided")
            report["sources"][source]["pages"][name]=x or {"status":status}
            if x:
                imp=str(x["impressions"]);click=str(x["clicks"])
                ctr=("%0.2f%%"%x["ctr_percent"]) if x["ctr_percent"] is not None else "-"
                pos=str(x["average_position"]) if x["average_position"] is not None else "-"
            else:imp=click=ctr=pos="미측정"
            md.append(f"| {source} | {name} | {imp} | {click} | {ctr} | {pos} | {status} |")
    md+=["","**측정하지 못한 항목:** GA4 유기적 방문, 공식 예약 링크의 실제 클릭, 예약 확정, 매출.",
          "페이지 수나 체류 시간 추정으로 위 항목을 대신하지 않습니다.",
          "자료가 충분히 쌓이기 전까지 신규 페이지 증산을 보류합니다."]
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    (out/"summary.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    (out/"summary.md").write_text("\n".join(md)+"\n",encoding="utf-8")
    print("\n".join(md))
    print("\nWritten:",out.resolve())

if __name__=="__main__":
    main()
