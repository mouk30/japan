/* Static companion guide: all inputs are visitor-provided Japan-local clock values. No tracking or booking. */
document.addEventListener('click',function(event){
const button=event.target.closest('[data-nf-return-calc]');
if(!button)return;
const section=button.closest('.nf-return');
if(!section)return;
const deadline=section.querySelector('[data-nf-deadline]').value;
const drive=Number(section.querySelector('[data-nf-drive]').value);
const reserve=Number(section.querySelector('[data-nf-reserve]').value);
const output=section.querySelector('[data-nf-result]');
const re=/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})$/;
const match=deadline.match(re);
if(!match||!Number.isFinite(drive)||!Number.isFinite(reserve)||drive<=0||reserve<0||section.querySelector('[data-nf-drive]').value===''||section.querySelector('[data-nf-reserve]').value===''){
output.textContent='선사의 최종 귀선 마감시각, 관광지→항만 소요분, 추가 여유분을 모두 입력하세요.';
return;
}
if(drive>1440||reserve>1440){output.textContent='이동시간과 여유시간을 확인해 다시 입력하세요.';return;}
const utc=Date.UTC(Number(match[1]),Number(match[2])-1,Number(match[3]),Number(match[4]),Number(match[5]));
if(!Number.isFinite(utc)){output.textContent='귀선 마감시각이 올바르지 않습니다.';return;}
const arrive=utc-reserve*60000;
const depart=arrive-drive*60000;
const asClock=ms=>new Date(ms).toISOString().slice(0,16).replace('T',' ');
output.innerHTML='<strong>관광지 출발 목표: '+asClock(depart)+' (일본 현지시각)</strong> → 항만 도착 목표: '+asClock(arrive)+' → 최종 귀선 마감: '+asClock(utc)+'.<span class="nf-warn">반드시 이보다 더 일찍 출발할 수 있도록 준비하세요. 위 계산에는 출입국 지연·셔틀 승차 대기·터미널 수속·사고·도로 통제가 자동 반영되지 않습니다. 여유시간 '+reserve+'분이 충분한지는 선사와 실제 이동수단을 통해 확인해야 합니다.</span>';
});