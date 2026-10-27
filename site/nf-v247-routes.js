/* V247 — information-only route selector; no APIs, inventory or prices. */
(()=>{'use strict';
const root=document.querySelector('[data-nf247-finder]');
if(!root)return;
const origins=[...root.querySelectorAll('[data-nf247-origin]')];
const types=[...root.querySelectorAll('[data-nf247-type]')];
const cards=[...root.querySelectorAll('[data-nf247-card]')];
const title=root.querySelector('[data-nf247-title]');
const count=root.querySelector('[data-nf247-count]');
const help=root.querySelector('[data-nf247-help]');
const note=root.querySelector('[data-nf247-note]');
const status=root.querySelector('[data-nf247-status]');
if(!origins.length||!types.length||!cards.length||!title||!count||!help||!note||!status)return;
const labels={
 busan:{
  international:'부산 출발 · 일본 국제여객선',
  cruise:'부산에서 준비하는 일본 크루즈'
 },
 japan:{
  international:'일본 출발 · 부산행 국제여객선',
  coastal:'일본 현지 · 섬을 잇는 연안페리',
  cruise:'일본 크루즈 · 기항지 하선 가이드'
 }
};
let origin='busan';
let type='international';
function update(nextOrigin,nextType,announce){
 origin=nextOrigin==='japan'?'japan':'busan';
 type=['international','coastal','cruise'].includes(nextType)?nextType:'international';
 // There is no Busan-to-Japanese-island domestic ferry in this category.
 if(origin==='busan'&&type==='coastal')type='international';
 for(const btn of origins){
  btn.setAttribute('aria-pressed',String(btn.dataset.nf247Origin===origin));
 }
 for(const btn of types){
  const unavailable=origin==='busan'&&btn.dataset.nf247Type==='coastal';
  btn.disabled=unavailable;
  btn.setAttribute('aria-pressed',String(btn.dataset.nf247Type===type));
  if(unavailable)btn.title='일본 내 연안페리는 일본 현지 출발을 선택하세요';
  else btn.removeAttribute('title');
 }
 let visible=0;
 for(const card of cards){
  const show=card.dataset.nf247From===origin&&card.dataset.nf247Kind===type;
  card.hidden=!show;
  if(show)visible++;
 }
 const name=labels[origin]?.[type]||'바다 여행 가이드';
 title.textContent=name;
 count.textContent=visible+'개 가이드';
 help.textContent=origin==='busan'
  ?'일본 현지 연안페리는 ‘일본 현지 출발’을 선택하면 확인할 수 있습니다.'
  :'일본 현지에서 부산으로 돌아오는 국제여객선과 일본 내 섬 이동은 서로 다른 항로입니다.';
 note.textContent=type==='cruise'
  ?'크루즈 기항지는 개별 크루즈 상품의 항해 일정과 접안 부두에 따라 달라집니다. 여기서는 기항지 관광·하선·귀선 안내만 제공하며 실제 크루즈 운항편을 검색하지 않습니다.'
  :'각 항로의 운항일·요금·잔여 좌석·수속 장소는 변동될 수 있습니다. 이 화면은 예약 조회가 아니라 기존 가이드 탐색이며, 연결된 선사 공식 안내에서 최종 확인해 주세요.';
 if(announce)status.textContent=name+', '+visible+'개 안내가 표시됐습니다.';
}
for(const btn of origins)btn.addEventListener('click',()=>update(btn.dataset.nf247Origin,type,true));
for(const btn of types)btn.addEventListener('click',()=>{if(!btn.disabled)update(origin,btn.dataset.nf247Type,true)});
update('busan','international',false);
})();
