#!/usr/bin/env python3
"""V17: add an evidence-dated berth schedule appendix to 45 existing companion guides.
Unverified ports remain visibly unverified; scheduled arrival/departure is NOT passenger final boarding.
"""
from pathlib import Path
from html import escape
import json,re
raw=json.loads(Path('scripts/v17-official-sailings.json').read_text(encoding='utf8'))
root=Path('site/things-to-do')
out=Path('audit-reports/v17');out.mkdir(parents=True,exist_ok=True)
result=[]
def e(s):return escape(str(s),quote=True)
for slug,port in raw['ports'].items():
    for audience in ['family','couple','parents']:
        p=root/(slug+'-cruise-'+audience+'-guide')/'index.html'
        s=p.read_text(encoding='utf8')
        if 'id="nf-v17-ops"' in s:
            result.append({'slug':slug,'audience':audience,'state':'already'})
            continue
        if s.count('id="nf-v16-brief"')!=1:raise ValueError('Cannot find V16 introduction '+str(p))
        status=('공식 예정표 확인 · 항차 당일 변경 가능' if port['calls'] else '항차별 개별 일정 미검증')
        if port['calls']:
            calls=[]
            for x in port['calls']:
                if x['date']<raw['as_of']:raise ValueError('Historical calls not intended '+slug)
                calls.append('<li data-sailing-day="'+e(x['date'])+'">'
                   '<span class="nf-v17-day">'+e(x['date'])+'</span> '
                   '<strong>'+e(x['ship'])+'</strong> · '
                   '<span class="nf-v17-berth">'+e(x['berth'])+'</span>'
                   '<span class="nf-v17-times">입항 예정 '+e(x['arrival'])+
                   ' / 출항 예정 '+(e(x['departure_date'])+' ' if x['departure_date']!=x['date'] else '')+e(x['departure'])+'</span>'
                   '</li>')
            list_html='<ul class="nf-v17-calls">'+''.join(calls)+'</ul>'
        else:
            list_html='<p class="nf-v17-unverified">정확한 선박명·날짜·예정 선석은 이번 검수에서 확인되지 않았습니다. 아래 항만 공식 페이지에서 해당 항차를 조회하세요.</p>'
        card=(
            '<section id="nf-v17-ops" class="nf-v17-ops" aria-label="항차별 공식 예정·미확인 정보">'
              '<p class="nf-v17-label">V17 · 항차별 부두 운영정보 <span>'+e(raw['as_of'])+' 기준</span></p>'
              '<p class="nf-v17-status"><strong>'+e(status)+'</strong></p>'
              +list_html+
              '<p class="nf-v17-note">'+e(port['note'])+'</p>'
              '<a href="'+e(port['scheduleSource'])+'" target="_blank" rel="noopener noreferrer nofollow">공식 운항·항만 공지에서 재확인 ↗</a>'
              '<p class="nf-v17-safety">주의: 표의 입·출항 예정시각은 선사의 <b>최종 승객 귀선 마감</b> 시간이 아닙니다. 실제 승객 출입 게이트, 셔틀 운영·막차, 교통·보안 검색시간은 항차별 추가 확인이 필요합니다.</p>'
              '</section>'
        )
        old='<p class="nf-v16-notice">'
        if s.count(old)!=1:raise ValueError('V16 notice location mismatch '+str(p))
        s=s.replace(old,card+old,1)
        if '/companion-ops-v17.css' not in s:
            s=s.replace('</head>','<link rel="stylesheet" href="/companion-ops-v17.css?v=20261014"></head>',1)
        p.write_text(s,encoding='utf8')
        result.append({'slug':slug,'audience':audience,'state':'published','official_records':len(port['calls']),'source':port['scheduleSource'],'status':port['status']})
summary={'pages':len(result),'updated':sum(x['state']=='published' for x in result),'ports':len(raw['ports']),'ports_with_checked_official_calls':sum(bool(x['calls']) for x in raw['ports'].values()),'ports_not_verified':sum(not x['calls'] for x in raw['ports'].values()),'unique_official_call_rows':sum(len(x['calls']) for x in raw['ports'].values()),'route_gate_to_venue_measurements_verified':0,'shuttle_actual_trip_verified':0,'as_of':raw['as_of']}
(out/'coverage.json').write_text(json.dumps({'summary':summary,'pages':result},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(summary,ensure_ascii=False))
