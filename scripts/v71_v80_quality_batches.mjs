import fs from 'node:fs';
import path from 'node:path';
const root='site/things-to-do';
const existing=fs.readdirSync(root,{withFileTypes:true}).filter(d=>d.isDirectory()&&fs.existsSync(path.join(root,d.name,'index.html'))).map(d=>d.name).sort();
const already=new Set(('yokohama nagasaki hakata naha ishigaki osaka kobe hakodate aomori kagoshima beppu sasebo shimonoseki shimizu kanazawa sendai kochi niigata matsuyama sakaiminato hiroshima takamatsu kumamoto maizuru kure fushiki-toyama tottori karatsu miyazaki atami nagoya wakayama-shimotsu yakushima-miyanoura akita iwakuni amami-naze goto-fukue tomakomai tokushima-komatsushima kumamoto-misumi').split(' ').map(x=>x+'-cruise-port-day-trip'));
const ports=existing.filter(x=>x.endsWith('-cruise-port-day-trip')&&!already.has(x));
const companions=existing.filter(x=>/-cruise-(couple|family|parents)-guide$/.test(x));
const okinawa=existing.filter(x=>x.startsWith('okinawa-'));
const portPractical=existing.filter(x=>/port-(day-trip|.*shore|.*sightseeing)|-shore-excursion|shore-excursion|island-access|cruise-terminal|cruise-area|cruise-day-trip|port-to-experience|port-half-day|experience-booking-checklist|family-with-kids|accessible-slow-travel|rainy-day/.test(x)&&!x.endsWith('-cruise-port-day-trip')&&!companions.includes(x)&&!okinawa.includes(x));
const extra=['aomori-port-nebuta-day-trip','beppu-port-onsen-day-trip','hakata-port-hakata-station-access','hiroshima-miyajima-ferry-crossing','ishigaki-cruise-new-port-shuttle','ishigaki-cruise-kabira-bay-bus-taxi','nagasaki-matsugae-glover-garden-cruise-access','nagasaki-cruise-peace-park-tram'];
const batches={
71:ports.slice(0,20),72:ports.slice(20,40),73:ports.slice(40,60),74:ports.slice(60,80),
75:companions.slice(0,20),76:companions.slice(20,40),
77:okinawa.slice(0,20),78:okinawa.slice(20,40),79:portPractical.slice(0,20),
80:[...companions.slice(40),...okinawa.slice(40),...extra]};
if(ports.length!==80||companions.length!==45||okinawa.length!==47||portPractical.length!==20)throw Error('Unexpected inventory: '+JSON.stringify({ports:ports.length,companions:companions.length,okinawa:okinawa.length,portPractical:portPractical.length}));
const flat=Object.values(batches).flat();
if(Object.keys(batches).length!==10||flat.length!==200||new Set(flat).size!==200||Object.values(batches).some(a=>a.length!==20))throw Error('Invalid exactly 20 unique pages per batch');
if(flat.some(x=>!existing.includes(x)))throw Error('Refusing to create new pages: '+flat.filter(x=>!existing.includes(x)).join(','));
const stats={ports:ports.length,companions:companions.length,okinawa:okinawa.length,portPractical:portPractical.length,extra:extra.length};
fs.mkdirSync('audit-reports/v71-v80',{recursive:true});
const esc=x=>String(x||'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
function plain(s){return String(s||'').replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,'').replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi,'').replace(/<[^>]+>/g,' ').replaceAll('&nbsp;',' ').replaceAll('&amp;','&').replace(/\s+/g,' ').trim()}
function firstHeader(h,tag){
  return plain(h.match(new RegExp('<'+tag+'\\b[^>]*>([\\s\\S]*?)<\\/'+tag+'>','i'))?.[1]||'');
}
function anchors(h){
 const items=[];
 for(const m of h.matchAll(/<a\b[^>]*\bhref=["'](https?:\/\/[^"']+)["']/gi)){
   const url=m[1].replaceAll('&amp;','&');
   try{
    const host=new URL(url).hostname.toLowerCase();
    if(/nipponferry|wikimedia|creativecommons|kakao|facebook|instagram|youtube|viator|klook|getyourguide|kkday|booking\.com|trip\.com/.test(host))continue;
    const official=/(^|\.)(go\.jp|lg\.jp|pref\.[a-z-]+\.jp|city\.[a-z-]+\.jp|town\.[a-z-]+\.jp|mlit\.go\.jp|japan\.travel|visitokinawajapan\.com|okinawastory\.jp|visitokinawa\.jp|www\.visitokinawa\.jp|jnto\.go\.jp)$/i.test(host)||
       /(airport|museum|aquarium|temple|shrine|railway|port|cruise|ferry|tourism)/i.test(host);
    if(!items.some(t=>t.url===url))items.push({url,host,official,anchorContext:plain(h.slice(m.index,Math.min(h.length,m.index+400))).slice(0,100)});
   }catch{}
 }
 return items;
}
function hrefMark(url,label,newtab=true){return '<a href="'+esc(url)+'"'+(newtab?' target="_blank" rel="noopener noreferrer"':'')+'>'+esc(label)+' ↗</a>'}
function choose(rows){
 const priority=x=>x.official?0:1;
 const sorted=[...rows].sort((a,b)=>priority(a)-priority(b));
 return sorted[0]||null;
}
const fallback={port:'https://www.mlit.go.jp/kankocho/cruise/list/index.html',okinawa:'https://visitokinawajapan.com/',travel:'https://www.japan.travel/ko/',family:'https://www.japan.travel/ko/'};
const operators={
 'okinawa-churaumi-aquarium':'https://churaumi.okinawa/',
 'okinawa-whale-shark-aquarium':'https://churaumi.okinawa/',
 'okinawa-gyokusendo-cave':'https://www.gyokusendo.co.jp/okinawaworld/',
 'okinawa-shuri-castle':'https://oki-park.jp/shurijo/',
 'okinawa-shuri-castle-heritage':'https://oki-park.jp/shurijo/',
 'okinawa-nakijin-castle':'https://www.nakijinjoseki-osi.jp/',
 'okinawa-katsuren-castle':'https://www.katsuren-jo.jp/',
 'okinawa-nakagusuku-castle':'https://www.nakagusuku-jo.jp/',
 'okinawa-busena-marine-park':'https://www.busena-marinepark.com/',
 'okinawa-sefa-utaki':'https://www.city.nanjo.okinawa.jp/',
};
function facts(category,title,source,lead,slug,html){
 const official=source?.url|| (category==='port'?fallback.port:category==='okinawa'?(operators[slug]||fallback.okinawa):fallback.travel);
 const officialLabel=source?'원문에 연결된 운영·항만 자료 보기':(category==='port'?'국토교통성 공식 항구 목록 검색':'공식 지역 관광포털에서 시설명 찾기');
 const subheads=[...html.matchAll(/<h[23]\b[^>]*>([\s\S]*?)<\/h[23]>/gi)].map(x=>plain(x[1])).filter(x=>x.length>2&&x.length<120&&!/홈|함께 읽|관련|FAQ|자주 묻/.test(x));
 const candidates=subheads.slice(0,7).map(s=>s.replace(/^\d+\s*[.、)]\s*/,'')).filter(s=>s.length<70);
 const focus=candidates.length?candidates[0]:title;
 if(category==='port'){
  return [
   ['실제 하선 장소','선석·출입구 확인', '이 글은 '+title+'을(를) 소개하지만 실제 선석, 승객 출입구, 텐더 상륙 여부는 항차별로 달라질 수 있습니다. 관광 전에 선사의 하선 공지를 우선 확인하세요.', official, officialLabel],
   ['시내 교통·셔틀','셔틀 운행 여부는 미확인','부두·일반 여객터미널·관광지 승강장을 같은 곳으로 간주하지 마세요. 공식 하선 지점에서 시내까지의 버스·택시 및 왕복 이동 수단을 별도로 확인해야 합니다. 특히 무료 셔틀은 확약 정보가 아닙니다.','/things-to-do/cruise-ports/','다른 기항지의 부두 정보와 비교'],
   ['관광시설 이용조건',focus+' 방문 판단','본문에서 소개한 관광지는 운영시간·입장권·휴관·날씨에 따라 방문 가능 여부가 바뀔 수 있습니다. 유료 관광권의 취소·환불은 구매처 조건을 우선 확인하세요.', official, '입장·예약 운영기관 안내 확인']
  ];
 }
 if(category==='companion'){
  const typ=slug.includes('-parents-')?'parents':slug.includes('-family-')?'family':'couple';
  const tip=typ==='family'?'유모차 이동·어린이 입장 연령·화장실·휴식 지점':typ==='parents'?'계단·경사·화장실·휠체어 접근과 쉴 곳':'야간 운행 여부·식당 및 개인탕 예약·시간 지정 입장권';
  return [
    ['동행자별 실제 이용조건','시설 입장규정 확인','이 글의 '+title+' 추천 명소도 '+tip+'을(를) 방문일에 확인해야 합니다. 무료 입장과 개별 체험·입장권은 구분하세요.', official, officialLabel],
    ['차량·가이드·픽업','선사 게이트에서 픽업 확인', '여행 상품을 예약한다면 상품에 지정 항구 픽업과 지정 게이트로의 복귀가 포함되는지 확인하세요. 예약 안내 링크만으로 픽업·좌석이 확정되지는 않습니다.','/things-to-do/travel-companions/','동행 가이드 비교'],
    ['귀선·취소','돌아올 수 있는 한 권역 선택','동행자 이동속도와 주차·입장 대기 시간을 반영해 실제 귀선 마감에서 역산하세요. 취소 조건은 관광시설·차량·선편에 각각 적용됩니다.', official,'공식 방문 조건·운영 공지 확인']
  ];
 }
 if(category==='okinawa'){
  const water=/beach|sea|coast|cape|bridge|rock|sunset|snorkel|marine|island|palm/.test(slug);
  const heritage=/castle|shuri|sefa|garden|memorial/.test(slug);
  const food=/soba|seafood/.test(slug);
  const extra=water?'수영 가능 구역·파고·조류·안전요원·기상 통제':heritage?'보수공사·입장구역·사진촬영 허용범위·유료 전시':food?'점포 영업일·메뉴 판매량·결제수단·식품 알레르기':'체험별 실제 운영·입장권·대기시간·시설별 정기 휴무';
  return [
    ['정확한 위치·운영','실제 방문 지점 확인','이 글의 '+title+'은(는) 사진에 나온 분위기만으로 시설 출입구를 특정할 수 없습니다. '+extra+'을(를) 실제 운영기관의 최신 안내에서 확인하세요.',official,officialLabel],
    ['항구에서의 이동','나하항 도보 거리로 단정 금지','오키나와 본섬의 지역별 관광지는 나하 크루즈 부두에서 멀리 떨어질 수 있습니다. 도착한 크루즈 게이트와 목적지의 왕복 차량·교통편을 먼저 확보하세요.','/things-to-do/naha-cruise-port-day-trip/','나하항 접안·귀선 실전 정보'],
    ['예약·사진 구분','입장·사진 출처 구분','AI 여행 참고 이미지는 실제 시설 상태와 다를 수 있습니다. 구매·방문 결정을 하기 전 공식 시설 사진과 운영일·가격·환불조건을 확인하세요.',official,'공식 장소·시설 정보 확인']
  ];
 }
 return [
  ['하선·교통','출발점부터 다시 확인',title+' 안내는 기항 항구별로 출발점이 달라질 수 있습니다. 실제 하선 게이트와 출입 수속, 차량 집결지를 확정한 뒤 안내 동선을 적용하세요.',official,officialLabel],
  ['방문·발권','운영정보와 구매조건 구분','관광 내용에 포함된 '+focus+' 등 시설·체험은 방문일 운영·요금·입장조건·취소규정을 각 운영처에서 다시 확인하세요.',official,'공식 지역 방문정보 확인'],
  ['귀선·대체동선','정시 귀선 우선','하선·왕복 교통·현장 대기·관광·선사 승선 마감을 시간표의 별도 항목으로 계산하세요. 장거리 관광은 교통 지연 시 포기할 대안을 준비하세요.','/things-to-do/cruise-ports/','항구별 비교 · 귀선 주의사항']
 ];
}
const manifest={createdAt:'2026-10-17',scope:'V71–V80',total:flat.length,noNewEditorialPages:true,allocation:stats,cohorts:{},pages:[]};
for(const [version,slugs] of Object.entries(batches)){
 manifest.cohorts['V'+version]={count:slugs.length,slugs,category:version<=74?'cruise-port':version<=76?'companion':version<=78?'okinawa':version===79?'shore-and-planning':'mixed'};
 for(const slug of slugs){
  const p=path.join(root,slug,'index.html');
  let html=fs.readFileSync(p,'utf8');
  const marker='id="v'+version+'-verification"';
  if(html.includes(marker)){manifest.pages.push({version:Number(version),slug,status:'already exists'});continue}
  const title=firstHeader(html,'h1')||firstHeader(html,'title')||slug;
  const h1pos=html.search(/<h1\b/i);
  const category=slug.endsWith('-cruise-port-day-trip')?'port':/-cruise-(couple|family|parents)-guide$/.test(slug)?'companion':slug.startsWith('okinawa-')?'okinawa':'other';
  const src=choose(anchors(html));
  const [lead]=[plain(html.match(/<p\b[^>]*>([\s\S]*?)<\/p>/i)?.[1]||'').slice(0,210)];
  const cards=facts(category,title,src,lead,slug,html);
  const cardsHTML=cards.map(([k,t,body,url,l])=>'<div class="nf-q80-card"><small>'+esc(k)+'</small><h3>'+esc(t)+'</h3><p>'+esc(body)+'</p>'+hrefMark(url,l,!url.startsWith('/'))+'</div>').join('');
  const cue=category==='port'?'항차별 접안·셔틀·귀선':category==='companion'?'동행자별 시설·예약':category==='okinawa'?'실제 장소·시설 운영':'실제 접근·예약·귀선';
  const htmlBlock='<section id="v'+version+'-verification" class="nf-q80" aria-label="'+esc(title)+' 실전 확인 가이드"><p class="nf-q80-eyebrow">NIPPONFERRY · '+esc(cue)+' · 확인 자료 기준 2026.10</p><h2>'+esc(title)+' · 여행 전 3가지 확인</h2><p class="nf-q80-intro">실제 입장·예약 가능한 정보와 여행 참고 내용은 다릅니다. 아래에서 공식 출처 확인, 이동, 안전한 복귀를 순서대로 점검하세요.</p><div class="nf-q80-grid">'+cardsHTML+'</div><div class="nf-q80-check"><strong>기항일 최종 판단</strong><p>① 실제 하선 게이트와 선사 최종 귀선시간 ② 왕복 교통·셔틀의 운행 여부와 탑승 장소 ③ 해당 관광시설의 방문일 운영·요금·취소 규정. 세 가지 중 하나라도 확인되지 않았다면 동선을 줄여 계획하세요.</p></div><nav class="nf-q80-nav" aria-label="여행 연관 정보"><a href="/things-to-do/cruise-ports/">크루즈 기항지 찾아보기 →</a><a href="/booking/japan-cruise/">항로·승선 준비 확인 →</a></nav><p class="nf-q80-disclaimer">자료 점검: 2026년 10월 17일 · 출처가 특정 시설이 아니라 지역·국가 공식 포털인 경우 해당 장소 이름을 다시 검색하세요. 개별 항차·셔틀·좌석·현재 입장 가능 여부는 실시간 확인된 정보가 아닙니다. 선사·판매처의 공식 안내를 최종 기준으로 따르세요.</p></section>';
  // Insert after article hero if it exists, otherwise before first section heading of main content.
  const main=html.indexOf('<main');
  const art=html.indexOf('<article',main);
  const heroClose=art>=0&&art<main+2500?html.indexOf('</header>',art):-1;
  let insert=-1;
  if(heroClose>=0&&heroClose<art+4500)insert=heroClose+'</header>'.length;
  else {
   const nextH2=html.indexOf('<h2',Math.max(main,0));
   if(nextH2>=0)insert=nextH2;
   else if(h1pos>=0)insert=html.indexOf('</h1>',h1pos)+'</h1>'.length;
  }
  if(insert<0)throw Error('No safe content insertion point for '+slug);
  html=html.slice(0,insert)+htmlBlock+html.slice(insert);
  if(!html.includes('</head>'))throw Error('Head missing for '+slug);
  html=html.replace('</head>','<link rel="stylesheet" href="/v71-v80-quality.css"></head>');
  fs.writeFileSync(p,html,'utf8');
  manifest.pages.push({version:Number(version),slug,category,title,originalExternalReference:src?.url||null,refClass:src?.official?'candidate official source':'official search portal / linked source',lead:lead.slice(0,100),relativePath:'/things-to-do/'+slug+'/'});
 }
}
fs.writeFileSync('audit-reports/v71-v80/manifest.json',JSON.stringify(manifest,null,2)+'\n');
for(let v=71;v<=80;v++){
 const arr=manifest.pages.filter(x=>x.version===v);
 fs.writeFileSync('audit-reports/v71-v80/v'+v+'.json',JSON.stringify({version:'V'+v,pages:arr,cardCount:arr.length*3,newEditorialPages:0},null,2)+'\n');
}
console.log(JSON.stringify({total:manifest.pages.length,cohorts:Object.entries(manifest.cohorts).map(([k,v])=>({version:k,count:v.count,category:v.category})),originalReferences:manifest.pages.filter(x=>x.originalExternalReference).length},null,2));
