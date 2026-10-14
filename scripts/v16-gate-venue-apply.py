#!/usr/bin/env python3
"""V16 targeted visitor route checklist for all 15 ports x 3 companion audiences.

The actual call's berth, passenger security exit, private transfer and last return shuttle
are not inferable from generic public transport information. This intentionally labels
them as day-of verification, while providing explicit official port and venue links.
Uses existing, licensed 4:3 photos; does not change titles, meta or canonicals.
"""
from pathlib import Path
from html import escape
import re, json, urllib.parse

spec=json.loads(Path('scripts/v16-gate-venue-transport.json').read_text(encoding='utf8'))
root=Path('site/things-to-do')
out=Path('audit-reports/v16')
out.mkdir(parents=True,exist_ok=True)
audiences={
 'family':'어린이·유모차 승하차 가능 여부, 화장실, 입장 회차, 왕복 교통을 함께 확인하세요.',
 'couple':'체험·식사 예약시간을 교통 대기와 분리하고 출발 장소·귀선 시간을 역산하세요.',
 'parents':'차량 승하차 높이, 엘리베이터·계단, 짧은 보행과 앉아서 쉴 곳을 우선하세요.'
}
def enc(x):return escape(str(x),quote=True)
def pick_hint(city,title):
  for pattern,hint in city['areas']:
    if re.search(pattern,title,re.I):
      return hint,True
  return '이 관광시설 입구까지의 하선 게이트 출발 실측 이동시간은 아직 확인되지 않았습니다. 시설 운영처와 차량·대중교통 정보를 재확인하세요.',False

audit=[]
for port,city in spec['ports'].items():
  for audience,notice in audiences.items():
    fn=root/(port+'-cruise-'+audience+'-guide')/'index.html'
    if not fn.is_file():raise RuntimeError('Guide does not exist: '+str(fn))
    content=fn.read_text(encoding='utf8')
    if 'id="nf-v16-brief"' in content:
      audit.append(dict(page=str(fn),status='already_exists'))
      continue
    dashboard=content.find('id="ct-topic-dashboard"')
    if dashboard<0:raise RuntimeError('No TOP3 dashboard '+str(fn))
    grid=content.find('<div class="ct-grid">',dashboard)
    if grid<0:raise RuntimeError('TOP3 grid missing '+str(fn))
    # One concise factual gate/shuttle note per page; not 3 near-identical full port descriptions.
    brief=(
      '<div class="nf-v16-brief" id="nf-v16-brief" aria-label="실제 승객 게이트 및 셔틀 운영 확인">'
      '<p class="nf-v16-eyebrow">V16 · 하선 게이트부터 관광시설 입구까지</p>'
      '<p><strong>접안 후보:</strong> '+enc(city['berths'])+'</p>'
      '<p><strong>당일 승객 출입구:</strong> '+enc(city['gate'])+'</p>'
      '<p class="nf-v16-shuttle"><strong>셔틀·픽업 운영:</strong> '+enc(city['shuttle'])+'</p>'
      '<p><strong>동행자별 확인:</strong> '+enc(notice)+'</p>'
      '<a href="'+enc(city['url'])+'" target="_blank" rel="noopener noreferrer nofollow">항만 공식 안내·항차 확인 ↗</a>'
      '<p class="nf-v16-notice">고정된 터미널 정보와 실제 항차의 게이트·차량 운행은 다릅니다. 표시되지 않은 실측 도보거리·교통 소요시간은 미확인으로 유지합니다.</p>'
      '</div>'
    )
    # Must be inserted before first TOP3 card without replacing any photograph or metadata.
    content=content[:grid]+brief+content[grid:]
    grid=content.find('<div class="ct-grid">',grid+len(brief))
    # The article matches the TOP3 card without consuming unrelated booking cards.
    end=content.find('<div class="ct-panel"',grid)
    if end<0:raise RuntimeError('Cannot locate section close for '+str(fn))
    region=content[grid:end]
    matched=[]
    def annotate(m):
      body=m.group(1)
      title_m=re.search(r'<h3>([^<]+)</h3>',body)
      if not title_m:raise RuntimeError('Unnamed venue card in '+str(fn))
      title=title_m.group(1)
      hint,hit=pick_hint(city,title)
      urlmatches=re.findall(r'<a\b[^>]*href="([^"]+)"',body)
      if not urlmatches:raise RuntimeError('No venue information link: '+str(fn)+' '+title)
      venue_link=urlmatches[-1]
      if not venue_link.startswith('https://'):raise RuntimeError('Non-HTTPS facility link '+venue_link)
      # Facility URLs already published are retained without describing them as booking-confirmed.
      journey=(
       '<details class="nf-v16-route">'
       '<summary>하선 게이트 → 시설 입구 · 귀선 확인</summary>'
       '<div class="nf-v16-route-body">'
       '<p><strong>① 실제 출발점</strong> <span class="nf-v16-status">항차별 확인</span><span>'+enc(city['berths'])+'. 선사 공지의 승객 출구·픽업 지점을 확인하세요.</span></p>'
       '<p><strong>② '+enc(title)+' 접근</strong><span>'+enc(hint)+'</span></p>'
       '<p><strong>③ 정확한 시설 현관·도보 거리</strong> <span class="nf-v16-status">실측 미확인</span><span>하선 보안게이트에서 시설 입구까지의 검증된 총 이동시간은 제공되지 않습니다. 시설별 정문·하차 위치를 확인하세요.</span></p>'
       '<p><strong>④ 셔틀·차량</strong><span>'+enc(city['shuttle'])+'</span></p>'
       '<p><strong>⑤ 귀선</strong><span>'+enc(city['return'])+' 선사 <b>최종 승객 귀선 마감</b> 전에 차량 대기·보안 출입·탑승 시간까지 확보하세요.</span></p>'
       '<div class="nf-v16-evidence"><a href="'+enc(city['url'])+'" target="_blank" rel="noopener noreferrer nofollow">항만 공식 자료 ↗</a><a href="'+enc(venue_link)+'" target="_blank" rel="noopener noreferrer nofollow">기존 시설 안내 페이지 ↗</a></div>'
       '</div></details>'
      )
      anchor='<div class="ct-distance">'
      if anchor not in body:raise RuntimeError('Venue location footer missing: '+str(fn)+' '+title)
      body=body.replace(anchor,journey+anchor,1)
      matched.append({'venue':title,'hint_matched':hit,'existing_venue_link':venue_link,'port_source':city['url']})
      return '<article class="ct-card">'+body+'</article>'
    region,count=re.subn(r'<article class="ct-card">([\s\S]*?)</article>',annotate,region)
    if count!=3:raise RuntimeError('Expected 3 cards in '+str(fn)+' got '+str(count))
    content=content[:grid]+region+content[end:]
    if '/companion-gate-v16.css' not in content:
      content=content.replace('</head>','<link rel="stylesheet" href="/companion-gate-v16.css?v=20261014"></head>',1)
    fn.write_text(content,encoding='utf8')
    audit.append({'port':port,'audience':audience,'page':str(fn),'status':'published','cards':count,'venues':matched})
counts={'ports':len(spec['ports']),'pages':len(audit),'published':sum(x['status']=='published' for x in audit),
        'venue_cards':sum(x.get('cards',0) for x in audit),
        'venue_hint_matched':sum(sum(y['hint_matched'] for y in x.get('venues',[])) for x in audit),
        'venue_hint_needs_review':sum(sum(not y['hint_matched'] for y in x.get('venues',[])) for x in audit)}
(out/'coverage.json').write_text(json.dumps({'summary':counts,'pages':audit},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(counts,ensure_ascii=False))
