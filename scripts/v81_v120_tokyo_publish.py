# V81–V120: forty authored Tokyo specialist travel pages, destination index and SEO links.
# No thin 800-page permutations: each page answers one distinct, verified visitor question.
import os, json, html, pathlib, subprocess
from urllib.parse import urlparse
from datetime import date
ROOT=pathlib.Path('site')
DOMAIN='https://www.nipponferry.com'
IMAGE='/images/venues/tokyo-city-night-real.webp'
topics=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import {topics} from './scripts/v81_v120_tokyo_topics.mjs';console.log(JSON.stringify(topics))"],text=True))
assert len(topics)==40 and [t['version'] for t in topics]==list(range(81,121))
assert len(set(t['slug'] for t in topics))==40
E=lambda s:html.escape(str(s),quote=True)
URL=lambda t:'/japan/tokyo/'+t['slug']+'/'
categories=list(dict.fromkeys(t['category'] for t in topics))
today='2026-10-17'
DESC={
 '미식':'현지 맛집·먹거리 주문·영업과 동선을 결합한 정보',
 '전망대':'무료·유료 전망대의 실제 높이와 예약·입장권',
 '교통':'공식 노선도·공항 이동·교통권 사용 범위',
 '쇼핑':'백화점·기념품·돈키호테 지점과 실제 면세 조건',
 '디즈니':'도쿄 디즈니랜드·디즈니씨 입장권과 마이하마 동선',
 '관광명소':'아사쿠사·시부야·신주쿠·아키하바라·오다이바',
 '체험':'팀랩·미술관·시장과 전시 예약',
 '여행코스':'방문 기간·가족·크루즈에 맞춘 실전 일정'
}
def head(title,description,canonical,kind='article',image=None):
 s=('<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
 '<title>'+E(title)+' | NIPPONFERRY</title><meta name="description" content="'+E(description[:166])+'">'
 '<meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="'+E(canonical)+'">'
 '<meta property="og:type" content="'+kind+'"><meta property="og:title" content="'+E(title)+'">'
 '<meta property="og:description" content="'+E(description[:166])+'"><meta property="og:url" content="'+E(canonical)+'">'
 '<link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/tokyo-guide.css">')
 if image:
  s+='<meta property="og:image" content="'+DOMAIN+image+'"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="'+DOMAIN+image+'">'
 return s
header='''<header class="site-header"><div class="wrap header-in"><a class="brand" href="/"><img src="/images/mascot.png" alt="NIPPONFERRY" width="38" height="38" style="width:38px;height:38px;max-width:38px;max-height:38px;object-fit:contain;flex-shrink:0"><span><strong>NIPPONFERRY</strong><small>크루즈로 만나는 일본 여행</small></span></a><nav class="desktop-nav"><a href="/japan-cruise/">⛴ 일본크루즈</a><a href="/japan/tokyo/">도쿄 여행</a><a href="/things-to-do/cruise-ports/">🚢 크루즈 기항지</a><a href="/booking/japan-cruise/">항로·예약</a></nav><button class="menu-toggle" aria-label="메뉴 열기" aria-expanded="false">☰</button><div class="mobile-menu"><a href="/japan/tokyo/">도쿄 여행 전체</a><a href="/japan/">일본 여행지</a><a href="/things-to-do/cruise-ports/">🚢 크루즈 기항지</a><a href="/booking/japan-cruise/">항로·예약</a></div></div></header>'''
footer='''<footer class="site-footer"><div class="wrap"><strong>NIPPONFERRY · 일본크루즈·도쿄여행</strong><p>운영시간·입장료·교통·취소 규정은 실제 방문일 공식 정보를 확인하세요. 이 웹사이트에서 시설의 좌석이나 예약 확정을 보장하지 않습니다.</p></div></footer><script>document.querySelector(".menu-toggle")?.addEventListener("click",()=>{const menu=document.querySelector(".mobile-menu"),btn=document.querySelector(".menu-toggle");menu?.classList.toggle("open");btn?.setAttribute("aria-expanded",menu?.classList.contains("open")?"true":"false")});</script>'''
def structured(t):
 can=DOMAIN+URL(t)
 return '<script type="application/ld+json">'+json.dumps([{
 "@context":"https://schema.org","@type":"Article","headline":t["title"],"description":t["access"],
 "mainEntityOfPage":can,"inLanguage":"ko","datePublished":today,"dateModified":today,
 "author":{"@type":"Organization","name":"NIPPONFERRY"},
 "publisher":{"@type":"Organization","name":"NIPPONFERRY","url":DOMAIN}
 },{
 "@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
 {"@type":"ListItem","position":1,"name":"일본 여행지","item":DOMAIN+"/japan/"},
 {"@type":"ListItem","position":2,"name":"도쿄 여행","item":DOMAIN+"/japan/tokyo/"},
 {"@type":"ListItem","position":3,"name":t["title"],"item":can}
 ]}],ensure_ascii=False,separators=(',',':'))+'</script>'
for t in topics:
 target=ROOT/'japan'/'tokyo'/t['slug']/'index.html'
 if target.exists():
  raise RuntimeError('Refusing to overwrite pre-existing article '+str(target))
 same=[x for x in topics if x['category']==t['category'] and x['slug']!=t['slug']]
 others=[x for x in topics if x['category']!=t['category'] and x['version']>=t['version']]
 near=(same[:4]+others[:3])[:6]
 aside=''.join('<a class="tky-sidelink" href="'+URL(x)+'">'+E(x['title'])+' →</a>' for x in near)
 related=''.join('<a href="'+URL(x)+'">'+E(x['title'])+' →</a>' for x in near[:4])
 officialHost=urlparse(t['official']).hostname
 secondaryHost=urlparse(t['secondary']).hostname
 desc=t['access']+' '+t['sourceNote']
 page='''<!doctype html><html lang="ko"><head>'''+head(t['title']+' · 도쿄 여행 가이드',desc,DOMAIN+URL(t))+structured(t)+'''</head><body>'''+header+'''<div class="tky-page"><section class="tky-hero"><div class="tky-shell"><nav class="tky-bread" aria-label="현재 위치"><a href="/">홈</a> › <a href="/japan/">일본 여행지</a> › <a href="/japan/tokyo/">도쿄 여행</a> › '''+E(t['category'])+'''</nav><span class="tky-kicker">TOKYO SPECIALIST GUIDE · '''+E(t['category'])+'''</span><h1>'''+E(t['title'])+'''</h1><p>'''+E(t['access'])+'''</p><div class="tky-quick"><a href="#official">공식 운영·발권 정보 →</a><a href="#plan">추천 동선 →</a><a href="/japan/tokyo/">도쿄 전체 가이드</a></div></div></section><div class="tky-shell tky-layout"><main class="tky-body"><article><section class="tky-block"><div class="tky-dated">공식 정보 확인일 2026년 10월 17일 · '''+E(t['zone'])+'''</div><h2>이 주제를 선택하기 전에</h2><p>'''+E(t['access'])+'''</p><p>'''+E(t['decision'])+'''</p><div class="tky-info-list"><div class="tky-info"><b>관광권역·접근</b><p>'''+E(t['zone'])+'''</p></div><div class="tky-info"><b>선택할 때 핵심</b><p>'''+E(t['decision'])+'''</p></div></div></section><section class="tky-block" id="plan"><h2>시간 낭비를 줄이는 실제 여행 동선</h2><p>'''+E(t['route'])+'''</p><h3>동선을 정하는 세 단계</h3><ol><li><b>출발점 확인:</b> '''+E(t['zone'])+''' 주변의 실제 역 출구·입장 장소·다음 교통편을 먼저 선택합니다.</li><li><b>관광지 한 권역에 집중:</b> '''+E(t['route'])+'''</li><li><b>마지막 복귀편 우선:</b> 귀국 항공·크루즈를 이용한다면 관광시설 대기 시간과 실제 최종 승선 수속 마감을 별도로 계산합니다.</li></ol></section><section class="tky-block" id="tickets"><h2>가격·영업시간·예약에서 놓치기 쉬운 조건</h2><p>'''+E(t['caution'])+'''</p><div class="tky-alert"><b>중요: 정보 링크와 예약 완료는 다릅니다</b><p>'''+E(t['sourceNote'])+''' 실제 날짜·시간·연령별 입장료·교통권 사용 범위·입장 지연·환불 규정을 구매 직전 공식 사이트에서 확인하세요.</p></div></section><section class="tky-block" id="official"><h2>공식 운영정보·직접 확인 링크</h2><p>도쿄도 관광안내와 시설·운송회사 홈페이지를 분리했습니다. 링크 중 관광포털은 정확한 날짜별 예약을 확정하는 결제 페이지가 아닙니다.</p><div class="tky-official"><a href="'''+E(t['official'])+'''" target="_blank" rel="noopener noreferrer">공식 시설·운영기관 안내 ↗<br><small>'''+E(officialHost)+'''</small></a><a href="'''+E(t['secondary'])+'''" target="_blank" rel="noopener noreferrer">운임·예약·여행정보 확인 ↗<br><small>'''+E(secondaryHost)+'''</small></a></div><p class="tky-dated">'''+E(t['sourceNote'])+'''</p></section><section class="tky-block"><h2>자주 묻는 질문</h2><h3>처음 방문한다면 무엇을 먼저 준비하나요?</h3><p>'''+E(t['decision'])+''' 이후 방문일·동행 인원과 실제 운영조건을 확인하세요.</p><h3>가장 현실적인 코스는 무엇인가요?</h3><p>'''+E(t['route'])+''' 이동시간과 대기시간은 당일 변동됩니다.</p><h3>취소·변경이나 교통이 자동 포함되나요?</h3><p>아닙니다. '''+E(t['caution'])+''' 입장권·철도권·크루즈 승선권은 각각 다른 상품이며 구매처가 정한 조건이 우선됩니다.</p></section><section class="tky-block"><h2>관련 도쿄 전문 가이드</h2><div class="tky-official">'''+related+'''</div><p><a href="/things-to-do/tokyo-cruise-port-day-trip/">도쿄 기항지 실제 접안 부두·셔틀·귀선 확인 →</a></p></section></article></main><aside class="tky-side"><section class="tky-block"><h2>함께 읽으면 좋은 글</h2>'''+aside+'''<a class="tky-sidelink" href="/japan/tokyo/">도쿄 전체 40편 →</a></section></aside></div></div>'''+footer+'''</body></html>'''
 target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text(page,encoding='utf8')
catblocks=[]
for cat in categories:
 articles=[t for t in topics if t['category']==cat]
 cards=''.join('<a class="tky-card" href="'+URL(t)+'"><small>'+E(t['zone'])+'</small><h3>'+E(t['title'])+'</h3><p>'+E(t['access'])+'</p><strong>공식 정보·동선·예약조건 →</strong></a>' for t in articles)
 catblocks.append('<section class="tky-cat" id="group-'+str(categories.index(cat)+1)+'"><div class="tky-cat-head"><h2>'+E(cat)+' · 5편</h2><p>'+E(DESC[cat])+'</p></div><div class="tky-cards">'+cards+'</div></section>')
canonical=DOMAIN+'/japan/tokyo/'
hubdesc='도쿄 여행 40개 전문 가이드: 도쿄타워·도쿄도청·지하철노선도·디즈니·백화점·돈키호테·식도락 공식 예약 링크와 동선.'
photoCredit='도쿄타워를 포함한 실제 도쿄 야경 (2025년 촬영). David Kernan · Wikimedia Commons · CC BY 4.0 · WebP 리사이즈'
hub='''<!doctype html><html lang="ko"><head>'''+head('도쿄 여행 완전 가이드｜식도락·관광·지하철·디즈니·쇼핑',hubdesc,canonical,'website',IMAGE)+'''<script type="application/ld+json">'''+json.dumps({'@context':'https://schema.org','@type':'CollectionPage','name':'도쿄 여행 실전 백과','url':canonical,'hasPart':[{'@type':'Article','url':DOMAIN+URL(t),'name':t['title']} for t in topics]},ensure_ascii=False)+'''</script></head><body>'''+header+'''<div class="tky-page"><section class="tky-hub-hero"><div class="tky-shell tky-hub-row"><div class="tky-hub-copy"><small class="tky-kicker">TOKYO / COMPLETE TRAVEL GUIDE</small><h1>도쿄 여행,<br>필요한 정보는 여기서 끝.</h1><p>라멘·쓰키지 미식부터 도쿄타워·무료 도쿄도청 전망대, 지하철 노선도와 백화점 쇼핑, 디즈니랜드·디즈니씨, 돈키호테 지점까지. <b>공식 홈페이지와 실제 여행 동선</b>을 연결한 40개 전문 주제를 확인하세요.</p><div class="tky-quick"><a href="#group-1">먹거리부터 보기 →</a><a href="#group-3">지하철 노선도 →</a><a href="#group-5">디즈니 입장권 →</a></div></div><figure class="tky-hub-photo"><img src="'''+IMAGE+'''" alt="2025년 실제 촬영된 도쿄타워와 미나토구 야경" width="1280" height="720" fetchpriority="high"><figcaption>'''+E(photoCredit)+''' · <a href="https://commons.wikimedia.org/wiki/File:Tokyo_Tower,_Minato_City.jpg" target="_blank" rel="noopener noreferrer">원본 사진</a> · <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener noreferrer">저작권 표시</a></figcaption></figure></div></section><main class="tky-hub-main"><div class="tky-shell"><p class="tky-hub-summary"><strong>소비자 중심 도쿄 여행 백과:</strong> 운영기관의 공식 링크, 교통권 사용 범위, 입장권·환불 조건, 실제 지역별 이동 동선을 함께 안내합니다. 아래 8개 분야, 40개 전문 가이드에서 목적별로 선택하세요.</p>'''+''.join(catblocks)+'''<div class="tky-footnotes"><b>여행 준비 안내:</b> 시설별 영업시간·입장료·교통은 날짜마다 변동됩니다. 도쿄 디즈니리조트는 지바현 우라야스이며, 하네다·나리타 공항과 도쿄항 크루즈 부두는 서로 다른 교통 체계입니다.<p><a href="/things-to-do/tokyo-cruise-port-day-trip/">도쿄 국제크루즈터미널·하루미·오이 부두별 하선·귀선 정보 →</a></p></div></div></main></div>'''+footer+'''</body></html>'''
tokyoHub=ROOT/'japan'/'tokyo'/'index.html'
if tokyoHub.exists():raise RuntimeError('Tokyo hub already exists, refuse overwrite')
tokyoHub.write_text(hub,encoding='utf8')
home=ROOT/'index.html'
s=home.read_text(encoding='utf8')
if 'class="v65-card v81-tokyo"' in s:raise RuntimeError('Tokyo already in popular cards')
grid='<div class="v65-grid">'
i=s.find(grid,s.find('id="v65-title"'))
if i<0:raise RuntimeError('Home destination grid not found')
tokyoCard='''<article class="v65-card v81-tokyo"><a class="v65-photo" href="/japan/tokyo/" aria-label="도쿄 여행 40개 전문 가이드"><img src="'''+IMAGE+'''" alt="실제 촬영된 도쿄타워와 도쿄 야경" loading="lazy" decoding="async" width="1280" height="720"><span class="v65-type">도쿄 필수 관광·교통·쇼핑</span></a><div class="v65-info"><small>TOKYO · SHIBUYA · ASAKUSA</small><h3>도쿄</h3><p>도쿄타워·무료 도쿄도청·디즈니·지하철 공식 노선도·백화점·돈키호테까지. 40개 전문 가이드.</p><div class="v65-actions"><a href="/japan/tokyo/">도쿄 여행 전체 가이드 →</a><a href="/japan/tokyo/tokyo-subway-route-map-korean/">도쿄 지하철 노선도 바로 보기 ↗</a></div></div></article>'''
s=s[:i+len(grid)]+tokyoCard+s[i+len(grid):]
s=s.replace('<article class="v65-card v65-featured"><a class="v65-photo" href="/okinawa/"','<article class="v65-card"><a class="v65-photo" href="/okinawa/"',1)
s=s.replace('<p class="v65-note">사진은 각 지역의 특정 장소를 나타냅니다.','<p class="v65-note">도쿄 이미지는 실제 야경 사진입니다 (David Kernan · CC BY 4.0 · WebP 변환). 사진은 각 지역의 특정 장소를 나타냅니다.',1)
home.write_text(s,encoding='utf8')
japan=ROOT/'japan'/'index.html'
j=japan.read_text(encoding='utf8')
if 'href="/japan/tokyo/"' in j:raise RuntimeError('Tokyo already in Japan region hub')
j=j.replace('content="후쿠오카·오사카·대마도·시모노세키의 먹거리, 쇼핑, 교통, 코스를 한곳에서 찾아보세요."','content="도쿄·오사카·후쿠오카·홋카이도·오키나와·대마도의 먹거리, 관광, 교통과 실전 코스를 한곳에서 찾아보세요."')
d='<div class="dirgrid">'
i=j.find(d)
if i<0:raise RuntimeError('Japan destination grid absent')
newCard='''<a class="dircard" href="/japan/tokyo/"><img alt="실제 촬영한 도쿄타워 야경" loading="lazy" src="'''+IMAGE+'''"/><div class="dirin"><small>도쿄 · 40개 전문 주제</small><h2>도쿄 여행 완전 가이드</h2><p>도쿄타워·지하철노선도·디즈니·돈키호테·백화점·식도락의 공식 안내까지.</p></div></a>'''
j=j[:i+len(d)]+newCard+j[i+len(d):]
japan.write_text(j,encoding='utf8')
tokyoPort=ROOT/'things-to-do'/'tokyo-cruise-port-day-trip'/'index.html'
pt=tokyoPort.read_text(encoding='utf8')
pt=pt.replace('<figcaption>AI 생성 여행 참고 이미지로 실제 항구에서 촬영한 사진이 아니며, 지형·시설 등의 모습이 실제 현지와 다를 수 있습니다.</figcaption>','')
pt=pt.replace('content="도쿄 기항지 여행 AI 생성 이미지"','content="2024년 실제 촬영한 도쿄 국제크루즈터미널역 사진"')
pt=pt.replace('<a class="back" href="/things-to-do/cruise-ports/">','<a class="back" href="/japan/tokyo/">도쿄 관광·교통·쇼핑 40편 →</a><a class="back" href="/things-to-do/cruise-ports/">')
tokyoPort.write_text(pt,encoding='utf8')
sitemap=ROOT/'sitemap.xml'
x=sitemap.read_text(encoding='utf8')
newUrls=['/japan/tokyo/']+[URL(t) for t in topics]
for endpoint in newUrls:
 u=DOMAIN+endpoint
 if '<loc>'+u+'</loc>' in x:raise RuntimeError('Existing sitemap '+u)
 x=x.replace('</urlset>','<url><loc>'+u+'</loc><lastmod>'+today+'</lastmod></url></urlset>')
sitemap.write_text(x,encoding='utf8')
audit=pathlib.Path('audit-reports/v81-v120')
audit.mkdir(parents=True,exist_ok=True)
report={'createdAt':today,'articles':len(topics),'versions':[t['version'] for t in topics],'categoryCounts':{c:sum(t['category']==c for t in topics) for c in categories},'image':IMAGE,'imageLicense':'CC BY 4.0','imageAuthor':'David Kernan','imageSource':'https://commons.wikimedia.org/wiki/File:Tokyo_Tower,_Minato_City.jpg','newSitemapUrls':newUrls,'articlesMeta':[{'version':t['version'],'title':t['title'],'path':URL(t),'category':t['category'],'sources':[t['official'],t['secondary']]} for t in topics]}
(audit/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'createdArticles':len(topics),'tokyoHub':str(tokyoHub),'categories':report['categoryCounts'],'sitemapUrls':len(newUrls),'popularTokyoCard':True},ensure_ascii=False))
