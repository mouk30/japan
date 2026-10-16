# Tokyo V121-V300: 9 batches of 20 distinct specialist guides, no overwrites.
import pathlib,subprocess,json,html,re
from urllib.parse import urlparse
ROOT=pathlib.Path('site')
AUD=pathlib.Path('audit-reports/v121-v300')
AUD.mkdir(parents=True,exist_ok=True)
BASE='https://www.nipponferry.com'
E=lambda s: html.escape(str(s),quote=True)
def load_topics():
    names=['scripts/tokyo_v'+str(x)+'_v'+str(x+19)+'.mjs' for x in range(121,301,20)]
    code="import {batch as a} from './"+names[0]+"';"+ "".join("import {batch as b"+str(i)+"} from './"+f+"';" for i,f in enumerate(names[1:],1))+"console.log(JSON.stringify([...a,"+",".join("...b"+str(i) for i in range(1,9))+"]));"
    return json.loads(subprocess.check_output(['node','--input-type=module','-e',code],text=True))
topics=load_topics()
assert len(topics)==180,len(topics)
assert [t['version'] for t in topics]==list(range(121,301))
assert len(set(t['slug'] for t in topics))==180
for t in topics:
 assert len(set([t['insight'],t['action'],t['warning']]))==3
 assert t['official'].startswith('https://')
def url(t):return '/japan/tokyo/'+t['slug']+'/'
html_head=lambda title,desc,canonical,cat:'<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+E(title)+' | NIPPONFERRY</title><meta name="description" content="'+E(desc[:165])+'"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="'+canonical+'"><meta property="og:type" content="article"><meta property="og:title" content="'+E(title)+'"><meta property="og:description" content="'+E(desc[:165])+'"><meta property="og:url" content="'+canonical+'"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/tokyo-guide.css"><meta name="topic" content="'+E(cat)+'">'
header='''<header class="site-header"><div class="wrap header-in"><a class="brand" href="/"><img src="/images/mascot.png" alt="NIPPONFERRY" width="38" height="38" style="width:38px;height:38px;max-width:38px;max-height:38px;object-fit:contain;flex-shrink:0"><span><strong>NIPPONFERRY</strong><small>크루즈로 만나는 일본 여행</small></span></a><nav class="desktop-nav"><a href="/japan-cruise/">⛴ 일본크루즈</a><a href="/japan/tokyo/">도쿄 220편</a><a href="/things-to-do/cruise-ports/">크루즈 기항지</a><a href="/booking/japan-cruise/">항로·예약</a></nav><button class="menu-toggle" aria-label="메뉴 열기" aria-expanded="false">☰</button><div class="mobile-menu"><a href="/japan/tokyo/">도쿄 전체 220편</a><a href="/japan/">일본 여행지</a><a href="/things-to-do/cruise-ports/">크루즈 기항지</a><a href="/booking/japan-cruise/">항로·예약</a></div></div></header>'''
footer='''<footer class="site-footer"><div class="wrap"><strong>NIPPONFERRY 도쿄 전문 여행 정보</strong><p>방문일 운영·가격·좌석·교통·환불 규정은 이용기관 공식 안내에서 반드시 재확인하세요. 상품 구매·예약은 각 운영기관에서 진행하며 NIPPONFERRY가 발권을 보장하지 않습니다.</p></div></footer><script>document.querySelector(".menu-toggle")?.addEventListener("click",()=>{const b=document.querySelector(".menu-toggle"),m=document.querySelector(".mobile-menu");m?.classList.toggle("open");b?.setAttribute("aria-expanded",m?.classList.contains("open")?"true":"false")});</script>'''
helpful={
 '교통·역별':('/japan/tokyo/tokyo-subway-route-map-korean/','도쿄 공식 지하철 노선도'),
 '교통·노선패스':('/japan/tokyo/tokyo-subway-ticket-24-48-72/','서브웨이 티켓 24·48·72시간 비교'),
 '디즈니·입장권':('/japan/tokyo/tokyo-disneyland-ticket-guide/','디즈니 입장권 직접 확인'),
 '디즈니·놀이기구·호텔':('/japan/tokyo/tokyo-disneysea-ticket-guide/','디즈니씨 입장권·이용조건'),
 '백화점·층별 안내':('/japan/tokyo/tokyo-ginza-department-store-route/','긴자 백화점 쇼핑 코스'),
 '쇼핑·돈키·드러그스토어':('/japan/tokyo/tokyo-mega-donki-shibuya/','시부야 메가돈키 실전 가이드'),
 '도쿄 동네·관광':('/japan/tokyo/tokyo-one-day-best-route/','도쿄 하루 여행 추천 코스'),
 '도쿄 식도락·문화체험':('/japan/tokyo/tokyo-tsukiji-market-street-food/','쓰키지 시장 식도락'),
 '일정·동행·크루즈':('/things-to-do/tokyo-cruise-port-day-trip/','도쿄항 승객 게이트·안전 귀선')
}
def source_label(t):
 h=urlparse(t['official']).netloc.lower()
 if 'tokyodisneyresort' in h:return '도쿄 디즈니리조트 공식 이용·구매 규정'
 if 'tokyometro' in h:return '도쿄메트로 공식 노선도·운임 안내'
 if 'kotsu.metro' in h:return '도에이 지하철·버스 공식 안내'
 if 'mistore' in h:return '미쓰코시·이세탄 공식 건물·층별 지도'
 if 'tobu-dept' in h:return '도부 백화점 공식 플로어 가이드'
 if 'daimaru' in h:return '다이마루 도쿄 공식 층별 지도'
 if 'takashimaya' in h:return '다카시마야 공식 매장·층별 가이드'
 if 'ginza6' in h:return 'GINZA SIX 공식 매장·층별 가이드'
 if 'donki' in h:return '돈키호테 공식 매장·지점 정보'
 if 'loft' in h:return '로프트 도쿄 공식 점포 검색'
 if 'muji' in h:return '무인양품 공식 지점·층별 안내'
 if 'jreast' in h:return 'JR 동일본 공식 역·열차 정보'
 if 'gotokyo' in h:return '도쿄도 공식 관광정보 포털에서 장소명 재확인'
 if 'gourmet' in h:return '도쿄 공식 음식·레스토랑 안내 포털'
 return '운영기관·지역 공식 방문 정보 확인'
def breadcrumb(t):
 return '<script type="application/ld+json">'+json.dumps([{'@context':'https://schema.org','@type':'Article','headline':t['title'],'description':t['insight'],'mainEntityOfPage':BASE+url(t),'datePublished':'2026-10-17','dateModified':'2026-10-17','inLanguage':'ko','publisher':{'@type':'Organization','name':'NIPPONFERRY','url':BASE}}, {'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'일본 여행지','item':BASE+'/japan/'},{'@type':'ListItem','position':2,'name':'도쿄 여행','item':BASE+'/japan/tokyo/'},{'@type':'ListItem','position':3,'name':t['title'],'item':BASE+url(t)}]}],ensure_ascii=False)+'</script>'
def unique_related(t):
 same=[x for x in topics if x['category']==t['category'] and x['slug']!=t['slug']]
 candidates=sorted(same,key=lambda x:abs(x['version']-t['version']))
 return candidates[:5]
for t in topics:
 target=ROOT/'japan'/'tokyo'/t['slug']/'index.html'
 if target.exists():raise RuntimeError('Refusing overwrite existing guide '+str(target))
 canonical=BASE+url(t)
 desc=t['insight']+' '+t['warning']
 deep_url,deep_title=helpful[t['category']]
 related=''.join('<a href="'+url(v)+'">'+E(v['title'])+' →</a>' for v in unique_related(t))
 official=E(t['official'])
 benefit='''<section class="tky-block tky-deep-lead"><h2>이번 주제에서 먼저 알아야 할 사실</h2><p>'''+E(t['insight'])+'''</p><div class="tky-info-list"><div class="tky-info"><b>방문·출발 지역</b><p>'''+E(t['zone'])+'''</p></div><div class="tky-info"><b>소비자에게 가장 중요한 선택</b><p>'''+E(t['action'])+'''</p></div><div class="tky-info"><b>반드시 구분할 제한 사항</b><p>'''+E(t['warning'])+'''</p></div></div></section>'''
 trip='''<section class="tky-block" id="route"><h2>역·출입구·매장부터 실제 이동 순서까지</h2><p>'''+E(t['action'])+'''</p><ol><li><b>실제 출발점:</b> '''+E(t['zone'])+'''의 해당 시설·정류장·쇼핑 건물부터 확인합니다.</li><li><b>목적지 먼저 확정:</b> '''+E(t['insight'])+'''</li><li><b>동행자·짐·대기 고려:</b> '''+E(t['warning'])+'''</li></ol><p>여행 지역의 실제 지도와 영업상태는 공식 홈페이지에서 확인하고, 관광시설 입장권과 철도권·승선권은 별도 상품으로 봐야 합니다.</p></section>'''
 if t['category'].startswith('디즈니'):
  condition='파크 입장권·유료 프리미어 액세스·식당 예약·호텔 특전은 각각 독립된 서비스입니다. 상품 이름이 비슷해도 포함 인원, 적용 파크, 사용 시간, 취소·환불 가능 여부가 달라집니다. 방문일 공식 앱의 현재 상품 상태를 최종 기준으로 합니다.'
 elif t['category']=='백화점·층별 안내':
  condition='층별 브랜드와 면세 안내는 백화점의 공식 층별 지도를 최종 기준으로 합니다. 본관·신관·다른 점포의 동일한 브랜드도 층수가 다릅니다. 매장 영업시간과 면세 카운터 접수 마감도 같다고 가정하지 마세요.'
 elif t['category'].startswith('교통'):
  condition='도쿄메트로·도에이·JR·공항철도·유리카모메는 서로 다른 철도회사입니다. 무료 환승·패스 적용구간·엘리베이터 출입구는 공식 노선도와 역별 안내에서 확인하세요. 열차 소요시간은 현장 대기와 환승 도보를 포함하지 않을 수 있습니다.'
 elif t['category'].startswith('쇼핑'):
  condition='정확한 지점 주소·영업시간·면세 창구·입점 브랜드와 재고는 매장 공식 검색에서 재확인하세요. 일본 면세와 한국 입국 세관·검역은 서로 다른 규정입니다.'
 elif t['category'].startswith('일정'):
  condition='시간대별 관광 가능 여부는 실제 도착·하선·수하물 수취·입장대기와 마지막 공항/크루즈 수속 마감을 고려해야 합니다. 셔틀 무료 여부나 귀선 시각이 확인되지 않으면 장거리 관광을 줄이세요.'
 else:
  condition='관광포털은 목적지·지역 설명을 확인하는 출처입니다. 개별 점포의 실제 좌석·예약 가능시간·입장권 가격·휴관은 각 운영업체에서 따로 확인해야 합니다. 사진이나 지도에 등장하는 모든 시설이 같은 건물·영업상태인 것은 아닙니다.'
 official_section='''<section class="tky-block" id="official"><h2>공식 출처 바로 열기 · 무엇을 확인할까?</h2><p>'''+E(source_label(t))+'''</p><div class="tky-official"><a href="'''+official+'''" rel="noopener noreferrer" target="_blank">공식 기관·운영처에서 원문 확인 ↗<br><small>'''+E(urlparse(t['official']).netloc)+'''</small></a><a href="'''+deep_url+'''">관련 심층 가이드 확인 →<br><small>'''+E(deep_title)+'''</small></a></div><p><strong>원문 확인 순서:</strong> ① 실제 방문 날짜 ② 해당 지점·층별 지도 또는 운영 대상 ③ 현재 입장·발권 또는 매장 운영 ④ 취소·변경·이동 수단입니다.</p></section>'''
 caveat='''<section class="tky-block" id="terms"><h2>예약·가격·운영 조건을 잘못 이해하기 쉬운 부분</h2><div class="tky-alert"><b>날짜별 현장 운영 우선</b><p>'''+E(t['warning'])+'''</p></div><p>'''+E(condition)+'''</p><p>2026년 10월 기준 여행 준비정보이며, 실시간 예약 재고·장소별 층수·당일 운행 확정 자료가 아닙니다. 상업 관광 사이트 링크 자체를 예약 확정으로 오인하지 마세요.</p></section>'''
 faq='''<section class="tky-block"><h2>방문자가 가장 많이 혼동하는 세 가지</h2><h3>이 여행은 어디에서 시작해야 하나요?</h3><p>'''+E(t['zone'])+'''에서 출발점과 해당 철도·매장·시설 운영사를 확인하세요. '''+E(t['action'])+'''</p><h3>가기 전에 돈을 써야 하나요?</h3><p>'''+E(condition)+''' 결제 직전 위 공식 출처에서 날짜와 적용 범위를 확인하세요.</p><h3>이동·예약에서 주의할 점은?</h3><p>'''+E(t['warning'])+'''</p></section>'''
 rel='''<section class="tky-block"><h2>다음에 이어 볼 도쿄 현지정보</h2><div class="tky-official">'''+related+'''</div><p><a href="/japan/tokyo/">도쿄 220편 여행 백과·분야별 주제 찾기 →</a></p></section>'''
 content='''<!doctype html><html lang="ko"><head>'''+html_head(t['title']+' | 도쿄 실전 상세 안내',desc,canonical,t['category'])+breadcrumb(t)+'''</head><body>'''+header+'''<div class="tky-page"><section class="tky-hero"><div class="tky-shell"><nav class="tky-bread" aria-label="페이지 위치"><a href="/">홈</a> › <a href="/japan/">일본 여행지</a> › <a href="/japan/tokyo/">도쿄 여행 220편</a> › '''+E(t['category'])+'''</nav><small class="tky-kicker">TOKYO EXPERT GUIDE · '''+E(t['category'])+'''</small><h1>'''+E(t['title'])+'''</h1><p>'''+E(t['insight'])+'''</p><div class="tky-quick"><a href="#official">공식 이용처 확인 →</a><a href="#route">실제 동선 보기 →</a><a href="/japan/tokyo/">도쿄 220편 전체 보기</a></div></div></section><div class="tky-shell tky-layout"><main class="tky-body"><article><p class="tky-dated">자료 기준: 2026년 10월 17일 · '''+E(t['zone'])+'''</p>'''+benefit+trip+caveat+official_section+faq+rel+'''</article></main><aside class="tky-side"><section class="tky-block"><h2>관련 분야 가이드</h2>'''+''.join('<a class="tky-sidelink" href="'+url(q)+'">'+E(q['title'])+' →</a>' for q in unique_related(t))+'''<a class="tky-sidelink" href="/japan/tokyo/">도쿄 전체 220편 →</a></section></aside></div></div>'''+footer+'''</body></html>'''
 target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text(content,encoding='utf8')
# Extend, do not replace, existing forty-topic Tokyo hub.
hub=ROOT/'japan'/'tokyo'/'index.html'
s=hub.read_text(encoding='utf8')
if 'id="tokyo-v121-v300"' in s:raise RuntimeError('Already published expanded Tokyo hub')
newCategories=[(n,topics[i:i+20]) for n,i in [('역별 출입구·환승',0),('노선·교통권·공항',20),('디즈니 티켓·예약',40),('디즈니 놀이기구·호텔',60),('백화점 층별 공식 지도',80),('돈키호테·쇼핑·드러그스토어',100),('도쿄 20개 동네',120),('먹거리·전시·문화',140),('가족·동행·크루즈 일정',160)]]
hubBlocks=[]
for i,(label,items) in enumerate(newCategories):
 cards=''.join('<a class="tky-card" href="'+url(q)+'"><small>'+E(q['zone'])+'</small><h3>'+E(q['title'])+'</h3><p>'+E(q['insight'])+'</p><strong>공식 안내·예약조건·동선 확인 →</strong></a>' for q in items)
 hubBlocks.append('<details class="tky-exp-group" id="tokyo-extra-'+str(i+1)+'"'+(' open' if i==0 else '')+'><summary><strong>'+E(label)+'</strong><span>20편 · 펼쳐서 보기 <span aria-hidden="true">⌄</span></span></summary><div class="tky-cards">'+cards+'</div></details>')
expansion='<section id="tokyo-v121-v300" class="tky-expanded" aria-label="도쿄 심층 180편"><div class="tky-cat-head"><h2>도쿄 심층 여행 180편</h2><p>공식 안내·층별지도·상품별 예약조건으로 구분</p></div><p class="tky-hub-summary">기존 필수 40편 아래로 분야별 20편씩 확장했습니다. 모든 주제를 한 화면에 펼치지 않고 관심 분야만 선택할 수 있습니다.</p><nav class="tky-extension-nav" aria-label="심층 주제 바로가기">'+''.join('<a href="#tokyo-extra-'+str(i+1)+'">'+E(name)+'</a>' for i,(name,_) in enumerate(newCategories))+'</nav>'+''.join(hubBlocks)+'</section>'
needle='<div class="tky-footnotes">'
if needle not in s:raise RuntimeError('Cannot locate existing 40-category hub footnotes')
s=s.replace(needle,expansion+needle,1)
s=s.replace('도쿄 여행 40개 전문 가이드','도쿄 여행 220개 전문 가이드')
s=s.replace('40개 전문 주제','220개 전문 주제')
s=s.replace('40개 전문 가이드','220개 전문 가이드')
s=s.replace('40개 전문 주제를 확인하세요','220개 전문 주제를 확인하세요')
s=s.replace('8개 분야, 40개 전문 가이드','8개 핵심 분야 40편과 9개 심층 분야 180편')
# Replace JSON-LD CollectionPage hasPart with all unique URLs, preserving other schema.
def change_schema(m):
 value=json.loads(m.group(2))
 if isinstance(value,dict) and value.get('@type')=='CollectionPage':
  seen={x['url'] for x in value.get('hasPart',[])}
  for t in topics:
   u=BASE+url(t)
   if u not in seen:value.setdefault('hasPart',[]).append({'@type':'Article','url':u,'name':t['title']})
  return m.group(1)+json.dumps(value,ensure_ascii=False,separators=(',',':'))+m.group(3)
 return m.group(0)
s=re.sub(r'(<script type="application/ld\+json">)(.*?)(</script>)',change_schema,s,flags=re.S)
hub.write_text(s,encoding='utf8')
# Update homepage popularity info but do not disturb the authenticated Tokyo photograph or other regions.
for filename in [ROOT/'index.html',ROOT/'japan'/'index.html']:
 s=filename.read_text(encoding='utf8')
 if '/japan/tokyo/' not in s:raise RuntimeError('Tokyo destination link missing from '+str(filename))
 s=s.replace('도쿄 여행 40편 전체 보기','도쿄 여행 220편 전체 보기').replace('40개 전문 가이드','220개 전문 가이드').replace('40개 전문 주제','220개 전문 주제').replace('40편의 실전 여행 백과','220편의 실전 여행 백과').replace('40편의 전문 가이드','220편의 전문 가이드')
 filename.write_text(s,encoding='utf8')
sitemap=ROOT/'sitemap.xml'
xml=sitemap.read_text(encoding='utf8')
for t in topics:
 u=BASE+url(t)
 if '<loc>'+u+'</loc>' in xml:raise RuntimeError('Article already in sitemap '+u)
 xml=xml.replace('</urlset>','<url><loc>'+u+'</loc><lastmod>2026-10-17</lastmod></url></urlset>')
sitemap.write_text(xml,encoding='utf8')
report={'completedAt':'2026-10-17','versions':'V121-V300','count':len(topics),'previousTokyoArticles':40,'newTokyoArticles':180,'totalTokyoArticles':220,'newHubPages':0,'groups':[],'topics':[],'photoPolicy':'No location-mismatched hero artwork; existing real Tokyo city photo only on city hub.'}
for a in range(121,301,20):
 group=[t for t in topics if a<=t['version']<a+20]
 groupReport={'versionStart':a,'versionEnd':a+19,'category':group[0]['category'],'count':len(group),'slugs':[t['slug'] for t in group]}
 report['groups'].append(groupReport)
 (AUD/('batch-v'+str(a)+'-v'+str(a+19)+'.json')).write_text(json.dumps(groupReport,ensure_ascii=False,indent=2),encoding='utf8')
for t in topics:
 report['topics'].append({'version':t['version'],'slug':t['slug'],'title':t['title'],'category':t['category'],'path':url(t),'source':t['official']})
(AUD/'editorial-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'pagesCreated':len(topics),'batchCount':len(report['groups']),'TokyoExisting':40,'TokyoTotal':220,'newSitemapEntries':len(topics)},ensure_ascii=False))
