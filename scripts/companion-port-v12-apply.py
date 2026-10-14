#!/usr/bin/env python3
"""V12.1: Reuse 15 official route manifests in 30 family/couple guides.

Shows numbers only for the precise documented origin-to-destination leg.
Never converts station-side guidance into a cruise-terminal claim.
"""
from pathlib import Path
import json,html
from datetime import date

root=Path('site')
routes=json.loads(Path('scripts/parents-port-v12-data.json').read_text(encoding='utf8'))
port_notes={
 'osaka':('덴포잔 가이유칸·레고랜드와 USJ는 서로 다른 일정입니다. 아이의 입장 회차를 먼저 잡고 실제 접안 부두를 확인하세요.','덴포잔 수변 데이트와 시내 이동을 섞기 전에 실제 부두를 확인하고 입장·식사 예약시간을 역산하세요.'),
 'yokohama':('오산바시·신코·다이코쿠는 같은 도보 동선이 아닙니다. 아이와 함께라면 입장시설 한 곳과 실내 휴식부터 선택하세요.','도심 수변 산책·에어캐빈을 선택할 때 다이코쿠 접안이라면 셔틀·차량 왕복 시간을 먼저 빼세요.'),
 'kobe':('하버랜드·호빵맨 박물관을 선택해도 나카토테와 포트터미널 출발 동선은 다릅니다. 유모차 반입·휴식 확인이 먼저입니다.','메리켄파크·하버랜드 산책은 나카토테와 포트터미널의 실제 하선 장소에 따라 시작점이 달라집니다.'),
 'hakata':('호빵맨 박물관·과학관은 시내 서로 다른 권역입니다. 역에서 부두까지 교통시간을 시설로 가는 시간과 혼동하지 마세요.','오호리공원이나 도심 데이트를 고를 때 귀선용 중앙부두·하카타부두 구분과 버스 정류장 위치를 확인하세요.'),
 'nagasaki':('펭귄 수족관은 항만 가까운 글로버정원과 달리 차량 이동이 필요한 코스입니다. 아이와 짧은 일정이라면 한 곳만 선택하세요.','글로버정원 경사와 이나사야마 로프웨이 대기시간을 확인하세요. 노면전차·역 출발 수치는 선박에서 직접 걸리는 시간이 아닙니다.'),
 'shimizu':('드림플라자는 가까운 식사·실내 휴식 후보이고 니혼다이라는 차량 관광입니다. 상점 셔틀과 크루즈 셔틀을 구분하세요.','시미즈 수변 산책과 니혼다이라 전망 중 한 권역만 선택하고, JR역 셔틀을 선박 귀선 교통으로 오인하지 마세요.'),
 'ishigaki':('신항 크루즈 부두와 낙도터미널은 다릅니다. 시내까지 긴 도보를 피하고 글라스보트 왕복 차량·파고를 확인하세요.','가비라만 데이트는 신항에서 별도 차량 이동이 필요합니다. 보트 출항 회차·대기·날씨를 확인하고 귀선 시간을 역산하세요.'),
 'sasebo':('우라가시라 하선이면 구주쿠시마 수족관·유람선까지 바로 도보 관광할 수 없습니다. 유모차·선박 승하선 조건을 미리 확인하세요.','우라가시라 조건부 셔틀을 매일 확정 교통으로 간주하지 마세요. 도심·하우스텐보스 데이트는 왕복편 확보 후 선택하세요.'),
 'kanazawa':('항만에서 도심까지 버스 이동 뒤 미술관·체험 한 곳을 선택하세요. 겐로쿠엔 자갈길과 아이 휴식시간을 별도로 잡으세요.','겐로쿠엔·미술관·히가시차야를 모두 급히 돌기보다 근거리 두 곳까지 선택하고 도심↔크루즈항 교통을 먼저 확보하세요.'),
 'kagoshima':('마린포트 안쪽 터미널까지의 이동 부담을 계산하세요. 이오월드·센간엔은 서로 다른 권역이고 아이와는 한 곳 중심이 좋습니다.','사쿠라지마 페리를 추가하면 크루즈 외 별도 승선과 대기가 생깁니다. 마린포트 접안이면 우선 차량 교통을 확보하세요.'),
 'aomori':('네부타 와랏세·ASPAM은 역 주변 기준 안내가 많습니다. 실제 부두에서 이동하는 길과 아이의 실내 휴식시간은 따로 확인하세요.','베이에어리어 산책은 역 출발 도보 구간과 선박 하선 출입구를 구분하고 핫코다 외곽 일정은 차량·날씨에 따라 선택하세요.'),
 'hakodate':('가네모리·고료카쿠·로프웨이는 동일 권역이 아닙니다. 유모차와 겨울 보행을 고려해 관람 한 곳을 우선하세요.','하코다테 항구 데이트는 실제 와카마쓰·니시·미나토초 접안 여부와 로프웨이 운휴·대기를 먼저 확인하세요.'),
 'beppu':('우미타마고·지옥순례·기지마 고원은 서로 다른 권역입니다. 지옥은 목욕시설이 아니므로 가족 체험과 혼동하지 마세요.','벳푸 온천 데이트는 당일 입욕 가능한 개별 시설부터 선택하고 로프웨이·지옥을 무리하게 연속 방문하지 마세요.'),
 'naha':('나하항 접안 위치에 따라 슈리성·DMM 수족관까지 이동이 달라집니다. 아이와는 차량 왕복과 실내 휴식 먼저 확인하세요.','국제거리·슈리성·DMM은 다른 권역이므로 한두 곳만 선택하고 접안 게이트 및 티켓 예약시간을 먼저 확인하세요.'),
 'hirara-miyakojima':('시기라 남부와 해중공원 북부를 한 코스로 묶지 마세요. 아이 동반은 차량 왕복과 더위·휴식 장소부터 확인하세요.','시기라 온천·마에하마 해변을 선택할 때 히라라항 픽업과 날씨·개별 이용권·귀선 시간을 분리해 확인하세요.')
}
assert set(port_notes)==set(routes['cities'])
report=[]
def e(v):return html.escape(str(v),quote=True)
for port,record in routes['cities'].items():
 for mode in ('family','couple'):
  path=root/'things-to-do'/f'{port}-cruise-{mode}-guide'/'index.html'
  if not path.is_file():raise RuntimeError('Guide file missing '+str(path))
  source=path.read_text(encoding='utf8')
  if 'id="nf-shared-port-v12"' in source:
   report.append({'page':str(path),'status':'already_exists','cards':len(record['routes'])})
   continue
  if '<section id="ct-topic-dashboard"' not in source:raise RuntimeError('Cannot find venue dashboard '+str(path))
  specific=port_notes[port][0 if mode=='family' else 1]
  focus=('👨‍👩‍👧 가족·아이와 이동' if mode=='family' else '💕 연인·예약 시간 관리')
  if mode=='family':
   focus_text='유모차·어린이와 함께라면 보안 게이트에서 차량 또는 대중교통까지의 이동, 엘리베이터·계단, 식사·화장실·대기 시간을 별도로 더하세요. 공식 입장 안내와 날짜 지정 티켓을 구분해 주세요.'
  else:
   focus_text='체험 예약·식사 예약 시간에 늦지 않도록 실제 부두와 각 예약 장소의 이동을 분리해 계산하세요. 시간표와 마지막 입장·취소 조건은 시설 공식 페이지에서 확인하세요.'
  cards=[]
  for origin,transport,value,type_,official,explain in record['routes']:
   if not official.startswith('https://'):raise RuntimeError('Invalid source URL: '+official)
   uncertain=any(token in value for token in ('미확인','아님'))
   cards.append('<article class="nf-share-route">'
    '<p class="nf-share-type">'+e(type_)+' · '+e(transport)+'</p>'
    '<h3>'+e(origin)+'</h3>'
    '<p class="nf-share-value'+(' nf-share-unverified' if uncertain else '')+'">'+e(value)+'</p>'
    '<p class="nf-share-explain">'+e(explain)+'</p>'
    '<a href="'+e(official)+'" target="_blank" rel="noopener noreferrer nofollow">공식 자료·구간 확인 ↗</a>'
    '</article>')
  panel=('<section id="nf-shared-port-v12" class="nf-share-port '+mode+'" aria-labelledby="nf-share-port-title">'
   '<p class="nf-share-kicker">V12 · 출발지 명시된 공식 교통자료</p>'
   '<h2 id="nf-share-port-title">'+e(record['city'])+' 크루즈 기항, 실제 어디에서 출발하나요?</h2>'
   '<p class="nf-share-berth"><strong>먼저 확인할 접안 부두</strong> · '+e(record['berths'])+'</p>'
   '<p class="nf-share-focus"><strong>'+e(focus)+'</strong> · '+e(specific)+'</p>'
   '<p class="nf-share-concept">아래 시간·거리는 표시된 <strong>출발지 → 목적지 구간</strong>에만 적용합니다. 역·도선장·버스정류장 출발 시간은 크루즈 하선 게이트 출발 시간이 아닙니다.</p>'
   '<div class="nf-share-grid">'+''.join(cards)+'</div>'
   '<div class="nf-share-tips"><strong>'+e(focus)+'</strong><p>'+e(focus_text)+'</p></div>'
   '<div class="nf-share-return"><strong>🚢 귀선 안전</strong><p>'+e(record['caution'])+'</p>'
   '<p>선사 공지 <strong>최종 승객 귀선 마감</strong>에서 부두 복귀시간·차량 대기·보안 출입·탑승 대기를 거꾸로 계산하세요. 위 수치는 전체 관광 동선 시간이나 예약 확정이 아닙니다.</p></div>'
   '<p class="nf-share-source-note">자료 기준 2026-10-14 · 공식 항만/관광 안내. 실제 항차·교통편·계절·시설 운영에 따라 변동될 수 있습니다.</p>'
   '</section>')
  source=source.replace('<section id="ct-topic-dashboard"',panel+'<section id="ct-topic-dashboard"',1)
  if '/companion-shared-port-v12.css' not in source:
   if '</head>' not in source:raise RuntimeError('Head missing '+str(path))
   source=source.replace('</head>','<link rel="stylesheet" href="/companion-shared-port-v12.css?v=20261014"></head>',1)
  path.write_text(source,encoding='utf8')
  report.append({'page':str(path),'mode':mode,'port':port,'status':'added','cards':len(cards),'numeric':sum(not any(x in q[2] for x in ('미확인','아님')) for q in record['routes']),'official_sources':len(set(q[4] for q in record['routes']))})
summary={'guides':len(report),'added':sum(r['status']=='added' for r in report),'route_cards':sum(r['cards'] for r in report),'numeric_source_segments':sum(r.get('numeric',0) for r in report),'all_ports':len(routes['cities'])}
output=Path('audit-reports/companion-port-v12.json')
output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(json.dumps({'summary':summary,'guides':report},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(summary,ensure_ascii=False))
