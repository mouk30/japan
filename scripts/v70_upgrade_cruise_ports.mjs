// V70: upgrade 20 EXISTING cruise-port articles; no new editorial URLs.
import fs from 'node:fs';
import path from 'node:path';
const ports=[
['hiroshima','히로시마','https://www.mlit.go.jp/kankocho/cruise/detail/039/index.html','우지나 외무역부두와 이쓰카이치 부두는 별개입니다. 실제 기항 부두가 우지나인지 이쓰카이치인지 먼저 확인하세요.','https://hiroshima-minato.jp/enaccessitsukaichi/','이쓰카이치 대형 크루즈 선박은 부두 내 일반 차량 진입 제한이 있습니다. 우지나 시내교통 동선을 이쓰카이치에 그대로 적용하지 마세요.','https://hiroshima-minato.jp/accessujina/','히로시마항 크루즈터미널(우지나) 교통과 실제 우지나 여객터미널은 구분하세요. 원폭돔·평화공원은 차량·철도 이동을 포함한 귀선 시간을 계산해야 합니다.','우지나 하선이라면 항만 주변 또는 시내 한 권역','이쓰카이치 도착이라면 선사 지정 차량으로 시내 한 권역'],
['takamatsu','다카마쓰','https://www.mlit.go.jp/kankocho/cruise/detail/049/index.html','국토교통성 자료에는 다마모치쿠(선포트 인근)와 아사히신마치 컨테이너터미널 두 접안 구역이 기재되어 있습니다.','https://www.kotoden.co.jp/','JR 다카마쓰역 인근 부두와 아사히신마치의 도심 접근이 다릅니다. 고토덴·시내버스는 정류장·운행시간을 따로 확인하세요.','https://www.my-kagawa.jp/','리쓰린공원은 유료 관람시설이며 시내에서 추가 교통이 필요합니다. 섬행 페리는 크루즈 하선과 별도 발권·별도 귀항 일정입니다.','선포트 접안 시 수변·다마모공원 권역','교통 확보 시 리쓰린공원 한 곳 추가'],
['kumamoto','구마모토항','https://www.mlit.go.jp/kankocho/cruise/detail/089/index.html','구마모토항은 야쓰시로항·미스미항과 다른 항만입니다. 국토교통성은 유메사키지마 -7.5m 선석을 소개합니다.','https://www.mlit.go.jp/kankocho/cruise/detail/065/index.html','야쓰시로항에 입항한 크루즈를 구마모토항으로 오인하지 마세요. 구마모토 시내까지는 차량 이동이 필요하며 현지 셔틀은 선사 확인 사항입니다.','https://kumamoto.guide/en/','구마모토성 관람구역·입장료·운영시간은 시설 안내를 확인하세요. 아소 관광은 기항지 가까운 도보 관광이 아닙니다.','구마모토항 실제 부두에서 출발·복귀 가능한 근거리 코스','차량 예약 시 구마모토성 시내 한 권역'],
['maizuru','마이즈루','https://www.mlit.go.jp/kankocho/cruise/detail/028/index.html','일본 국토교통성의 Kyoto Port(마이즈루) 안내에는 제2부두와 국제부두가 함께 나옵니다. 부두를 확인하지 않고 서마이즈루역 도보 동선을 적용하면 안 됩니다.','https://www.japan.travel/en/destinations/kansai/kyoto/','마이즈루항은 교토시 중심지가 아닙니다. 아마노하시다테와 교토 도심은 각각 장거리 교통을 확인해야 합니다.','https://www.mlit.go.jp/kankocho/cruise/detail/028/index.html','아마노하시다테 관광선·전망 시설은 별도 상품입니다. 영업시간·발권·교통편을 기항일 기준으로 확인하세요.','실제 마이즈루 부두 주변 가까운 코스','선사 차량이 확보되면 아마노하시다테 선택'],
['kure','구레','https://www.city.kure.lg.jp/','구레항 크루즈 부두와 일반 연락선 여객터미널이 같다고 단정하지 마세요. 해당 선박의 하선 장소를 확인합니다.','https://www.city.kure.lg.jp/','야마토뮤지엄·철의 고래관 등은 시내 시설이지만 접안 부두 위치에 따라 도보 가능 여부가 달라집니다.','https://yamato-museum.com/','야마토뮤지엄은 리뉴얼·휴관·운영 변경 가능성이 있으므로 실제 방문일의 공식 개관·입장권 공지를 반드시 확인하세요.','부두 확인 → 항구 수변과 가까운 박물관 한 곳','교통 확보 시 구레 시내 역사·박물관 코스'],
['fushiki-toyama','후시키·도야마','https://www.mlit.go.jp/kankocho/cruise/detail/021/index.html','후시키만요, 가이오, 도야마 등 복수 선석이 공식 항만 자료에 나옵니다. 같은 도야마현이어도 접안 위치가 다릅니다.','https://www.mlit.go.jp/kankocho/cruise/detail/021/index.html','가이오마루역·다카오카역·이와세역 접근 조건은 부두마다 다릅니다. 도야마시내 직행 셔틀이 매 항차 제공된다고 가정하지 마세요.','https://www.info-toyama.com/','가이오마루 공원과 다테야마 구로베 알펜루트는 소요시간이 크게 다릅니다. 산악 관광은 계절·교통·예약을 따로 확인하세요.','실제 부두 주변 수변·공원 한 권역','차량·체류 여유가 있으면 다카오카 관광 선택'],
['tottori','돗토리','https://www.mlit.go.jp/kankocho/cruise/list/index.html','돗토리항과 사카이미나토항은 다른 항만입니다. 선사 예약증의 공식 부두명으로 입항지를 재확인해야 합니다.','https://www.tottori-guide.jp/','돗토리 사구 방문은 접안 장소에서의 왕복 차량·버스 이용을 검토해야 하며 도보 거리에 있다고 안내하지 않습니다.','https://www.tottori-guide.jp/','돗토리 사구와 모래미술관은 서로 다른 시설이며, 유료 전시·휴관 및 이용시간을 별도로 확인해야 합니다.','부두에서 가까운 관광 한 곳','교통이 확보되면 돗토리 사구 한 권역'],
['karatsu','가라쓰','https://www.mlit.go.jp/kankocho/cruise/detail/056/index.html','국토교통성 항만 자료에는 묘켄 부두와 동부두가 나옵니다. 이키 정기페리 승강장을 크루즈 하선 게이트와 혼동하지 마세요.','https://www.city.karatsu.lg.jp/','니시가라쓰역·가라쓰성·니지노마쓰바라는 서로 다른 관광권입니다. 실제 부두에서의 대중교통·차량 경로를 확인하세요.','https://www.mlit.go.jp/kankocho/cruise/detail/056/index.html','가라쓰성 관람 시설과 가라쓰 군치 축제는 운영·개최일이 별도입니다. 사전 예약 가능한 체험인지 공식 안내에서 확인하세요.','하선 부두 인근 해안·시내 한 권역','차량 확보 시 가라쓰성 또는 소나무숲 추가'],
['miyazaki','미야자키','https://www.mlit.go.jp/kankocho/cruise/detail/067/index.html','미야자키항 크루즈 시설은 아부라쓰항(니치난)과 다릅니다. 예약증의 입항 이름을 가장 먼저 확인하세요.','https://www.mlit.go.jp/kankocho/cruise/detail/067/index.html','공식 자료는 미야자키역으로 차량·버스 이동을 안내합니다. 아오시마는 별도 이동지가 필요하므로 짧은 기항의 도보 명소로 안내하지 마세요.','https://www.kanko-miyazaki.jp/','아오시마 신사·해안 관광은 일반 야외 접근과 유료 시설·체험 예약 조건을 구분하세요. 비·태풍 시 현장 변경 가능성이 있습니다.','미야자키항 하선 위치 확인 → 시내 근거리 코스','차량 확보 시 아오시마 주변 관광'],
['atami','아타미','https://www.mlit.go.jp/kankocho/cruise/list/index.html','아타미는 기항 방식과 접안·텐더 가능성이 선박별로 다를 수 있습니다. 해안 유람선·일반 여객 승강장을 크루즈 게이트로 단정하지 마세요.','https://www.city.atami.lg.jp/','해변·온천가의 교통과 언덕 관광지는 별도 이동이 필요합니다. 선사 제공 상륙방식과 복귀 수단부터 확인하세요.','https://www.city.atami.lg.jp/','당일 온천은 목욕만 가능한지, 대절탕 예약이 필요한지, 숙박시설 당일입욕을 허용하는지 업소별로 확인하세요.','상륙 위치에서 가까운 아타미 해안 산책','이동·영업이 확인되면 당일 온천 한 곳'],
['nagoya','나고야','https://www.port-of-nagoya.jp/kanko/senpaku/cruiseguide/1004445.html','나고야항 관리조합은 가든 부두 2·3호와 긴조 부두 80·81호의 크루즈 접안 위치를 구분합니다.','https://www.port-of-nagoya.jp/kanko/senpaku/cruiseguide/1004445.html','가든 부두는 나고야코역 도보 접근, 긴조 부두는 긴조후토역 접근입니다. 도심 철도역까지 이동 방법이 동일하지 않습니다.','https://www.port-of-nagoya.jp/english/aboutport/1001854/1001521.html','가든 부두에 수족관·해양박물관이 있지만 각각 입장권과 휴관 조건이 다릅니다. 긴조 부두는 관광시설 구성이 다릅니다.','가든 부두라면 수족관·수변 중 하나','긴조 부두라면 철도 연결 확인 후 한 권역 관광'],
['wakayama-shimotsu','와카야마·시모쓰','https://www.mlit.go.jp/kankocho/cruise/list/index.html','와카야마 시모쓰항은 여러 항만 구역을 포함하므로 실제 크루즈 선석 확인 전까지 와카야마성·항만 이동시간을 확정하면 안 됩니다.','https://www.wakayama-kanko.or.jp/','와카야마성·기미이데라·마리나시티는 별도 지역입니다. 하선 후 왕복 교통과 시내 대기시간을 구분하세요.','https://www.wakayama-kanko.or.jp/','와카야마성 천수각과 시내 무료 산책은 입장 기준이 다릅니다. 매표시간·휴관·당일 행사 여부를 공식 안내로 확인하세요.','지정 부두의 근거리 산책 또는 차량 관광 하나','왕복 차량 확보 시 와카야마성 관광'],
['yakushima-miyanoura','야쿠시마 미야노우라','https://www.mlit.go.jp/kankocho/cruise/detail/072/index.html','국토교통성은 야쿠시마 미야노우라항의 히노카미야마 선석을 소개합니다. 안보항과는 다른 지역입니다.','https://www.town.yakushima.kagoshima.jp/soshiki/kanko_machizukuri/kankosushin/kankosite_English/2/756.html','야쿠시마 숲길은 차량 이동과 등산 시간이 필요합니다. 미야노우라항에서 조몬스기 코스를 당일 짧은 관광으로 권하지 않습니다.','https://www.mlit.go.jp/kankocho/cruise/detail/072/index.html','야쿠스기 박물관·숲 체험은 개방·안전 통제·가이드 및 입장 조건을 별도 확인해야 합니다. 악천후 때는 탐방을 줄이세요.','미야노우라항 근처 마을·짧은 산책','전용 차량 확보 후 박물관·근거리 자연관광'],
['akita','아키타','https://www.mlit.go.jp/kankocho/cruise/detail/012/index.html','공식 항만 자료는 나카지마 제2·3안벽과 크루즈터미널을 소개합니다. 여객열차 이용 가능 여부는 해당 기항일에 확인해야 합니다.','https://www.mlit.go.jp/kankocho/cruise/detail/012/index.html','국토교통성에 크루즈열차 15분 안내가 있지만 실제 2026년 기항일 운행 보장은 아닙니다. 셀리온 타워 주변과 아키타역 이동을 분리하세요.','https://www.akita-tourism.com/','셀리온 전망대·시내 관광시설의 운영·입장조건과 8월 간토축제 개최일은 별도 확인해야 합니다.','항구 셀리온·터미널 인근 관광','실제 크루즈열차/셔틀 운행 확인 시 아키타 시내'],
['iwakuni','이와쿠니','https://www.pref.yamaguchi.lg.jp/soshiki/91/21621.html','이와쿠니항의 항만 구역과 긴타이쿄 다리 주변은 서로 다른 위치입니다. 선사 공지의 선석·하선 게이트를 확인하세요.','https://www.pref.yamaguchi.lg.jp/soshiki/91/21621.html','긴타이쿄·이와쿠니성은 시내에서 추가 이동이 필요합니다. 입항지에서 바로 도보로 갈 수 있다고 안내하지 않습니다.','https://www.city.iwakuni.lg.jp/','긴타이쿄·로프웨이·성 입장권은 각각 이용요금과 운행조건이 다릅니다. 운영기관 공식 공지에서 방문일을 확인하세요.','항만 출입구 확인 → 차량이 확보된 관광 한 곳','귀선 여유와 시설 운행 확인 시 긴타이쿄·성'],
['amami-naze','아마미 나제','https://www.mlit.go.jp/kankocho/cruise/detail/071/index.html','나제항 크루즈 선석과 아마미공항·섬 북부 해변은 다른 장소입니다. 미나토마치·나가하마 등 실제 하선 지점을 선사에서 확인하세요.','https://www.mlit.go.jp/kankocho/cruise/detail/071/index.html','나제 시가지 관광과 아마미파크·망그로브 탐방은 차량 소요시간이 다릅니다. 대중교통 연결·귀선편을 사전에 확인하세요.','https://www.mlit.go.jp/kankocho/cruise/detail/071/index.html','섬 생태 관광은 가이드·입장 예약과 날씨·보호구역 규제가 별도일 수 있습니다. 해양 체험은 취소조건을 확인하세요.','나제항 주변 상점가·시내 한 권역','차량·가이드 확보 시 자연관광 한 곳'],
['goto-fukue','고토 후쿠에','https://www.mlit.go.jp/kankocho/cruise/detail/060/index.html','고토 후쿠에항 크루즈 승객이 사용하는 오하토 부두를 공식 항만자료에서 확인할 수 있습니다. 다른 섬의 항구와 혼동하지 마세요.','https://www.mlit.go.jp/kankocho/cruise/detail/060/index.html','후쿠에 시내 상점가와 오세자키 등 섬 서쪽 명소는 이동거리가 다릅니다. 외곽 전망대는 차·도로시간을 따로 고려하세요.','https://www.city.goto.nagasaki.jp/','교회·해변·박물관은 운영과 촬영·방문 예절이 각각 다릅니다. 보호 시설은 사전 관람 가능 여부를 확인하세요.','후쿠에항 주변 시내 한 권역','차량·귀선 여유 확보 시 섬 자연명소 한 곳'],
['tomakomai','도마코마이','https://www.mlit.go.jp/kankocho/cruise/detail/002/index.html','도마코마이항은 기타 부두·이리후네 부두 등 시설을 구분합니다. 정기 페리터미널을 크루즈 접안 위치로 단정하지 마세요.','https://www.jptmk.com/','도마코마이역·항구 시장·우토나이호수는 거리와 교통이 다릅니다. 각 관광지 이동·택시 복귀 시간을 별도로 계산하세요.','https://www.city.tomakomai.hokkaido.jp/','우토나이호수 야생조류 관람은 보호수칙이 적용되며, 우포포이 등 유료 문화시설은 예약·운영과 멀리 떨어진 이동시간이 필요합니다.','항구 시장 또는 가까운 수변 관광','차량 확보 시 우토나이호수 한 곳 추가'],
['tokushima-komatsushima','도쿠시마·고마쓰시마','https://www.mlit.go.jp/kankocho/cruise/detail/048/index.html','도쿠시마고마쓰시마항은 아카이시·가나이소·혼코·오키노스 등 복수 선석을 갖습니다. 실제 항차 부두를 확인하세요.','https://www.mlit.go.jp/kankocho/cruise/detail/048/index.html','도쿠시마시 아와오도리 회관과 고마쓰시마항 사이에는 차량 이동이 필요합니다. 축제 기간 교통규제도 고려하세요.','https://www.awanavi.jp/','아와오도리 실제 축제는 날짜별로 진행하고, 공연장 관람은 다른 티켓입니다. 유료 관람석·우천·취소조건을 확인하세요.','실제 부두 근거리 식사·산책','차량·축제일 확정 시 도쿠시마 시내 관광'],
['kumamoto-misumi','구마모토 미스미','https://www.mlit.go.jp/kankocho/cruise/detail/090/index.html','미스미항은 구마모토항·야쓰시로항과 다르며, 국토교통성은 기와사키 -7.5m 부두를 안내합니다.','https://www.mlit.go.jp/kankocho/cruise/detail/090/index.html','미스미역의 도보 접근은 특정 부두 기준입니다. 크루즈 실제 게이트에서 역까지의 도보 허용 여부와 시간은 따로 확인하세요.','https://www.mlit.go.jp/kankocho/cruise/detail/090/index.html','미스미서항 유산 관광과 아마쿠사 유람선은 별도 상품·교통입니다. 배편을 다른 크루즈 승선권으로 오인하지 마세요.','미스미항 주변 문화유산 한 권역','교통·예약 여유 시 미스미서항을 짧게 추가']
];
const css=`<style id="v70-official-port-style">
.v70-verified{color:#173c58;max-width:100%;min-width:0;box-sizing:border-box;background:linear-gradient(135deg,#f0f8fd,#fff);border:1px solid #cfdee8;border-radius:18px;padding:clamp(15px,3vw,27px);margin:20px 0 23px;box-shadow:0 12px 28px rgba(5,55,96,.065)}
.v70-verified *{box-sizing:border-box}.v70-verified .v70-eyebrow{display:block;font-size:11px;font-weight:900;letter-spacing:.11em;color:#0b7c98;margin-bottom:7px}
.v70-verified h2{font-size:clamp(21px,2.65vw,28px);color:#0b446b;line-height:1.36;margin:0 0 10px}
.v70-verified .v70-intro{font-size:14px;color:#587388;line-height:1.75;margin:0 0 15px}
.v70-columns{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.v70-panel{background:#fff;border:1px solid #d8e6ef;border-radius:13px;padding:16px;display:flex;flex-direction:column;gap:8px;min-width:0}
.v70-panel small{font-size:11px;color:#0b7e9d;font-weight:900}.v70-panel h3{font-size:16px;line-height:1.42;margin:0;color:#0a4066}
.v70-panel p{font-size:13px;line-height:1.75;color:#4f6e82;margin:0;flex:1;overflow-wrap:anywhere}.v70-panel a{font-size:12px;color:#065f89;text-decoration:underline;text-underline-offset:3px;font-weight:900;line-height:1.5;overflow-wrap:anywhere}
.v70-safe{margin-top:15px;background:#e8f4fb;border-left:4px solid #0e7eb4;border-radius:9px;padding:14px}
.v70-safe strong{font-size:14px;color:#124766}.v70-safe p{font-size:13px;line-height:1.75;margin:6px 0;color:#45697e}
.v70-safe ol{margin:6px 0;padding-left:22px;line-height:1.8;font-size:13px;color:#46677b}
.v70-next{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0 0}.v70-next a{padding:10px 13px;border-radius:9px;background:#0b6ca4;color:white!important;text-decoration:none;font-size:12px;font-weight:900}
.v70-next a:last-child{background:#fff;border:1px solid #99c2d9;color:#076691!important}.v70-disclosure{margin:13px 0 0;font-size:11px;line-height:1.75;color:#657c8d}
.v70-verified a:focus-visible{outline:3px solid #2eabd2;outline-offset:2px}
@media(max-width:800px){.v70-columns{grid-template-columns:1fr}.v70-panel{padding:13px}.v70-verified{padding:15px}}
@media(max-width:350px){.v70-verified{padding:11px}.v70-next a{font-size:11px}}
</style>`;
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}
function main(){
 const results=[];
 for(const [slug,title,official,berth,transUrl,trans,venueUrl,venue,short,long] of ports){
  const file=path.join('site','things-to-do',slug+'-cruise-port-day-trip','index.html');
  if(!fs.existsSync(file))throw Error('Missing existing page: '+file+'; refusing to create new page');
  let s=fs.readFileSync(file,'utf8');
  if(s.includes('id="v70-port-official"')){results.push({slug,status:'already upgraded'});continue}
  const art=s.indexOf('<article',s.indexOf('<main'));
  const heroClose=s.indexOf('</header>',art);
  if(art<0||heroClose<0)throw Error('Cannot safely identify article header: '+slug);
  if(!s.includes('</head>'))throw Error('Missing head on '+slug);
  const facts=[
   ['접안 시설 · 항차 확인','어느 부두에 내리나요?',berth,official,'공식 항만 자료 · 접안지 확인'],
   ['하선 교통 · 셔틀','시내까지 어떻게 이동하나요?',trans,transUrl,'공식 교통·접근 정보 보기'],
   ['관광 시설 · 발권','입장·취소조건은 어디서 확인하나요?',venue,venueUrl,'공식 시설·관광 안내 확인'],
  ].map(([cat,heading,desc,url,link])=>`<div class="v70-panel"><small>${esc(cat)}</small><h3>${esc(heading)}</h3><p>${esc(desc)}</p><a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(link)} ↗</a></div>`).join('');
  const block=`<section class="v70-verified" id="v70-port-official" aria-label="${esc(title)} 공식 기항지 정보"><span class="v70-eyebrow">OFFICIAL PORT GUIDE · 확인일 2026-10-16</span><h2>${esc(title)} · 실제 하선부터 귀선까지</h2><p class="v70-intro">공식 부두, 시내 이동, 관광·입장권 조건을 따로 구분했습니다. 항만의 일반 정보와 실제 기항일의 최종 선석·셔틀은 다를 수 있습니다.</p><div class="v70-columns">${facts}</div><div class="v70-safe"><strong>안전한 당일 관광 · 최종 귀선 원칙</strong><ol><li>선사 예약증·앱에 표시된 부두·하선 출입구와 승객 최종 귀선 마감을 확인합니다.</li><li>셔틀 유무·무료/유료·탑승장·마지막 복귀편은 항차별 안내로 확인합니다. 미확인 시 차량을 직접 마련한 경우만 장거리 관광을 계획합니다.</li><li>관광 시설 발권과 크루즈 승선권은 다른 상품이며, 취소·환불·실제 입장 가능 여부는 판매처 규정을 적용합니다.</li></ol><p><b>짧은 기항:</b> ${esc(short)}</p><p><b>충분한 기항:</b> ${esc(long)}</p></div><nav class="v70-next" aria-label="관련 여행계획"><a href="/things-to-do/cruise-ports/">기항지 전체·관련 가이드 →</a><a href="/booking/japan-cruise/">항로·승선 준비 확인 →</a></nav><p class="v70-disclosure">출처 검토일 2026-10-16. 위 링크는 공식 설명 또는 운영기관 안내이며 예약·입장 가능 여부의 실시간 확정이 아닙니다. 정확한 선석·차량·귀선 시간은 실제 항차의 선사 공지를 따릅니다.</p></section>`;
  s=s.slice(0,heroClose+'</header>'.length)+block+s.slice(heroClose+'</header>'.length);
  s=s.replace('</head>',css+'</head>');
  fs.writeFileSync(file,s,'utf8');
  results.push({slug,file,official,transUrl,venueUrl});
 }
 const out='audit-reports/v70';
 fs.mkdirSync(out,{recursive:true});
 fs.writeFileSync(path.join(out,'upgraded-ports.json'),JSON.stringify({version:70,updatedAt:'2026-10-16',noNewPages:true,count:results.length,results},null,2));
 console.log(JSON.stringify({upgraded:results.length,slugs:results.map(x=>x.slug)},null,2));
}
main();
