#!/usr/bin/env python3
"""V15 berth-first reference guides for five more Japanese cruise ports.
Do not convert station-to-berth or station-to-facility distances into ship-gate to attraction measurements.
Keep any date-specific shuttle or security access conditional.
"""
from pathlib import Path
from html import escape
import json,re
catalog=json.loads(Path("scripts/third-five-ports-v15.json").read_text(encoding="utf-8"))
base=Path("site/things-to-do")
report=[]
def e(x):return escape(str(x),quote=True)
for slug,port in catalog["ports"].items():
  for mode in ["family","couple","parents"]:
    filename=base/(slug+"-cruise-"+mode+"-guide")/"index.html"
    if not filename.is_file():raise RuntimeError(f"Missing guide {filename}")
    html=filename.read_text(encoding="utf-8")
    if 'id="nf-precision-v15"' in html:
      report.append({"port":slug,"mode":mode,"status":"already_exists","berths":len(port["berths"])})
      continue
    cards=[]
    for idx,berth in enumerate(port["berths"]):
      if not berth["source"].startswith("https://") or not berth["extra"].startswith("https://"):raise ValueError("Non-HTTPS official source")
      cards.append('<details class="nf-precision-berth"'+(' open' if idx==0 else '')+'>'
        '<summary>'+e(berth["name"])+' <span>'+e(berth["measure"])+'</span></summary>'
        '<div class="nf-precision-body">'
        '<p class="nf-precision-id"><strong>접안 장소:</strong> '+e(berth["tag"])+'</p>'
        '<div class="nf-precision-leg"><strong>검증 이동구간</strong><span>'+e(berth["leg"])+'</span><b>'+e(berth["measure"])+'</b></div>'
        '<p class="nf-precision-origin">'+e(berth["scope"])+'</p>'
        '<p><strong>관광시설 접근:</strong> '+e(berth["facility"])+'</p>'
        '<p><strong>교통·셔틀:</strong> '+e(berth["transport"])+'</p>'
        '<p><strong>귀선 장소:</strong> '+e(berth["return"])+'</p>'
        '<a href="'+e(berth["source"])+'" target="_blank" rel="noopener noreferrer nofollow">공식 항만 자료 확인 ↗</a>'
        ' · <a href="'+e(berth["extra"])+'" target="_blank" rel="noopener noreferrer nofollow">추가 공식 교통 자료 ↗</a>'
        '</div></details>')
    body=('<div id="nf-precision-v15" class="nf-precision-v13">'
      '<p class="nf-precision-kicker">V15 · 실제 접안부두부터 관광과 귀선까지</p>'
      '<h3>'+e(port["name"])+' — 부두 선택 후 공식 교통 정보 확인</h3>'
      '<p class="nf-precision-intro">'+e(port["decision"])+'</p>'
      '<p class="nf-precision-mode">'+e(port["audience"][mode])+'</p>'
      '<div class="nf-precision-berths">'+''.join(cards)+'</div>'
      '<p class="nf-precision-facility">숫자는 반드시 표시된 <strong>출발지 → 도착지 구간</strong>에만 적용합니다. 관광지 현관까지의 미검증 도보분은 더하지 않았습니다.</p>'
      '<p class="nf-precision-return"><strong>🚢 귀선 안전:</strong> 당일 선박의 실제 접안 선석·여객 게이트·기사 픽업 승인·셔틀 최종편과 선사 최종 승객 귀선 마감을 별도로 확인하세요. 공식 자료는 실시간 셔틀 배차나 예약 가능 여부를 보장하지 않습니다.</p>'
      '<p class="nf-precision-date">자료 확인일: 2026-10-14 · 관공서·항만 공식정보 우선. 실제 항차·기상·운영에 따라 변동됩니다.</p>'
      '</div>')
    if mode in ["family","couple"]:
      key=r'(<p class="nf-share-berth">[\s\S]*?</p>)'
    else:
      key=r'(<div class="nf-port-warning">[\s\S]*?</div>)'
    if len(re.findall(key,html))!=1:raise RuntimeError("Missing anchor or duplicated berth panel: "+str(filename))
    html=re.sub(key,lambda m:m.group(1)+body,html,count=1)
    if '/companion-precision-v13.css' not in html:
      html=html.replace("</head>",'<link rel="stylesheet" href="/companion-precision-v13.css?v=20261014"></head>',1)
    filename.write_text(html,encoding="utf-8")
    report.append({"port":slug,"mode":mode,"status":"published","file":str(filename),"berths":len(port["berths"]),"source_urls":len({x["source"] for x in port["berths"]})})
summary={"ports":len(catalog["ports"]),"guides":len(report),"updated":sum(x["status"]=="published" for x in report),"different_berths":sum(len(x["berths"]) for x in catalog["ports"].values()),"rendered_berth_cards":sum(x["berths"] for x in report)}
out=Path("audit-reports/third-five-v15.json");out.parent.mkdir(exist_ok=True,parents=True)
out.write_text(json.dumps({"summary":summary,"guides":report},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(summary,ensure_ascii=False))
