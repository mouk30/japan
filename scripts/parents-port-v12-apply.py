#!/usr/bin/env python3
"""V12 parent-guides: verified berth / station route evidence, exact origin labels and cruise return safeguards.
Never infer unverified port-to-attraction travel minutes or walking distances.
"""
from pathlib import Path
from html import escape
import json, re, urllib.parse
site=Path('site')
data=json.loads(Path('scripts/parents-port-v12-data.json').read_text(encoding='utf-8'))
report=[]
def clean(s):return escape(str(s),quote=True)
for slug,c in data['cities'].items():
    file=site/'things-to-do'/(slug+'-cruise-parents-guide')/'index.html'
    raw=file.read_text(encoding='utf-8')
    if 'id="nf-port-v12"' in raw:
        report.append({'slug':slug,'status':'already_added','sources':len(c['routes'])})
        continue
    official=[]
    cards=[]
    for origin,mode,duration,label,source,note in c['routes']:
        if not source.startswith('https://'):raise ValueError('Not approved URL '+slug)
        official.append(source)
        uncertain=('미확인' in duration or '아님' in duration)
        cards.append('<article class="nf-port-route">'
          '<div class="nf-port-route-category">'+clean(label)+' · '+clean(mode)+'</div>'
          '<h3>'+clean(origin)+'</h3>'
          '<p class="nf-port-route-value'+(' is-unknown' if uncertain else '')+'">'+clean(duration)+'</p>'
          '<p class="nf-port-route-note">'+clean(note)+'</p>'
          '<a href="'+clean(source)+'" target="_blank" rel="noopener noreferrer nofollow">공식 근거·접근 안내 ↗</a>'
          '</article>')
    html=('<section class="nf-port-v12" id="nf-port-v12" aria-labelledby="nf-port-title">'
      '<p class="nf-port-eyebrow">V12 · 출발지 검증된 실전 교통정보</p>'
      '<h2 id="nf-port-title">'+clean(c['city'])+' — 실제 접안 부두별 교통·도보 기준</h2>'
      '<div class="nf-port-warning"><strong>① 먼저 접안 부두 확인</strong><p>'+clean(c['berths'])+'</p></div>'
      '<p class="nf-port-intro">아래 수치는 <strong>각 카드에 표시한 출발지 → 도착지 구간</strong>에만 해당합니다. 역에서 관광지까지의 도보시간을 크루즈선 하선 게이트 출발시간으로 바꾸어 표시하지 않았습니다.</p>'
      '<div class="nf-port-route-grid">'+''.join(cards)+'</div>'
      '<div class="nf-port-return"><strong>🚢 귀선 안전·승하차</strong><p>'+clean(c['caution'])+'</p>'
      '<p>선사에서 공지한 <strong>최종 승객 귀선 마감</strong>을 기준으로 (1) 관광지 출발 (2) 차량 호출·대기 (3) 실주행 (4) 부두 보안게이트·터미널 내부 이동 (5) 승선 대기를 각각 합산하세요. 아래 수치에는 이 모든 과정이 포함된 것이 아닙니다.</p></div>'
      '<p class="nf-port-meta">자료 확인 기준: 2026-10-14 · 항만/관광 공공기관 및 공식 운영처 접근 정보. 교통 체증·계절·항차·셔틀 운휴에 따라 실제 소요시간은 달라집니다.</p>'
      '</section>')
    point=raw.find('<section id="ct-topic-dashboard"')
    if point<0:raise ValueError('Missing TOP3: '+str(file))
    raw=raw[:point]+html+raw[point:]
    if 'companion-port-v12.css' not in raw:
        raw=raw.replace('</head>','<link rel="stylesheet" href="/companion-port-v12.css?v=20261014"></head>',1)
    file.write_text(raw,encoding='utf8')
    report.append({'slug':slug,'status':'added','route_segments':len(c['routes']),'precise_segments':sum(('미확인' not in t[2] and '아님' not in t[2]) for t in c['routes']),'source_urls':list(dict.fromkeys(official))})
summary={'pages':len(report),'added':sum(x['status']=='added' for x in report),'route_segments':sum(x.get('route_segments',0) for x in report),'precise_segments':sum(x.get('precise_segments',0) for x in report),'date':'2026-10-14'}
out=Path('audit-reports/parents-port-v12.json');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps({'summary':summary,'pages':report},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(summary,ensure_ascii=False))
