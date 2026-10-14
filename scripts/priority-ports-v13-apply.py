#!/usr/bin/env python3
"""V13: Compact berth-by-berth access verification inside existing 15 companion guides.
Keeps established 4:3 photograph, attribution and booking sections unchanged.
Routes identify their true starting point; unknown gate-to-entrance minutes stay unknown.
"""
from pathlib import Path
from html import escape
import json,re
manifest=json.loads(Path('scripts/priority-ports-v13.json').read_text(encoding='utf8'))
root=Path('site/things-to-do')
report=[]
def esc(v):return escape(str(v),quote=True)
for port,city in manifest['ports'].items():
 for mode in ('family','couple','parents'):
  fn=root/(port+'-cruise-'+mode+'-guide')/'index.html'
  html=fn.read_text(encoding='utf8')
  if 'id="nf-precision-v13"' in html:
   report.append({'page':str(fn),'state':'already_exists','cards':len(city['berths'])})
   continue
  audiences={
   'family':'가족은 유모차 이동·그늘·화장실·아이 입장 회차까지 확인하세요.',
   'couple':'연인은 관광·식사·체험 예약 시간과 실제 항만 왕복을 구분하세요.',
   'parents':'부모님은 차량 승하차 높이·경사·휴식 장소·귀선 대기 공간을 먼저 확보하세요.'
  }
  blocks=[]
  for idx,x in enumerate(city['berths']):
   if not x['source'].startswith('https://'):raise ValueError('Non-https official source: '+port)
   blocks.append(
    '<details class="nf-precision-berth" '+('open' if idx==0 else '')+'>'
    '<summary>'+esc(x['name'])+' <span>'+esc(x['amount'])+'</span></summary>'
    '<div class="nf-precision-body">'
      '<p class="nf-precision-id"><strong>실제 항만 구분:</strong> '+esc(x['identifier'])+'</p>'
      '<div class="nf-precision-leg"><strong>검증 구간</strong><span>'+esc(x['leg'])+'</span><b>'+esc(x['amount'])+'</b></div>'
      '<p class="nf-precision-origin">'+esc(x['precision'])+'</p>'
      '<p><strong>시설 출입구:</strong> '+esc(x['facility'])+'</p>'
      '<p><strong>교통·셔틀:</strong> '+esc(x['transfer'])+'</p>'
      '<p><strong>귀선 경로:</strong> '+esc(x['return'])+'</p>'
      '<a href="'+esc(x['source'])+'" target="_blank" rel="nofollow noopener noreferrer">공식 항만·시청 자료 확인 ↗</a>'
    '</div></details>'
   )
  part=(
   '<div class="nf-precision-v13" id="nf-precision-v13">'
     '<p class="nf-precision-kicker">V13 · 하선부터 귀선까지 실제 부두별 확인</p>'
     '<h3>'+esc(city['city'])+' — 접안 부두를 선택해 이동 확인</h3>'
     '<p class="nf-precision-intro">'+esc(city['decision'])+'</p>'
     '<p class="nf-precision-mode">'+esc(audiences[mode])+'</p>'
     '<div class="nf-precision-berths">'+''.join(blocks)+'</div>'
     '<p class="nf-precision-facility">'+esc(city['facilityFocus'])+'</p>'
     '<p class="nf-precision-return"><strong>중요:</strong> 이 페이지는 항차별 실제 접안 선석·하선 게이트·셔틀의 당일 운행을 실시간 확인하는 서비스가 아닙니다. <strong>선사 최종 귀선시간</strong>, 선사 지정 승객 출입구와 셔틀 마지막 회차를 별도 확인하세요.</p>'
     '<p class="nf-precision-date">공식 항만·시청·관광청 안내 기준 확인: 2026-10-14 · 이동시간은 정확히 표시된 출발지와 목적지 구간에만 적용됩니다.</p>'
    '</div>'
  )
  if mode in ('family','couple'):
   pattern=r'(<p class="nf-share-berth">[\s\S]*?</p>)'
  else:
   pattern=r'(<div class="nf-port-warning">[\s\S]*?</div>)'
  if len(re.findall(pattern,html))!=1:raise RuntimeError('Source berth section mismatch in '+str(fn))
  html=re.sub(pattern,lambda m:m.group(1)+part,html,count=1)
  if '/companion-precision-v13.css' not in html:
   html=html.replace('</head>','<link rel="stylesheet" href="/companion-precision-v13.css?v=20261014"></head>',1)
  fn.write_text(html,encoding='utf8')
  report.append({'page':str(fn),'port':port,'audience':mode,'state':'published','cards':len(city['berths']),'source_count':len({x['source'] for x in city['berths']})})
summary={'guides':len(report),'published':sum(x['state']=='published' for x in report),'cities':len(manifest['ports']),'distinct_berths':sum(len(x['berths']) for x in manifest['ports'].values()),'rendered_berth_panels':sum(x['cards'] for x in report)}
out=Path('audit-reports/priority-ports-v13.json');out.parent.mkdir(exist_ok=True,parents=True)
out.write_text(json.dumps({'summary':summary,'pages':report},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(summary,ensure_ascii=False))
