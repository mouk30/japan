/* V301–V305 unified header accessibility + progressive enhancement */
(()=>{'use strict';
const header=document.querySelector('.nf301-header');
if(!header)return;
const mobile=header.querySelector('#nf301-mobile-panel');
const mobileToggle=header.querySelector('.nf301-toggle');
const flyouts=[...header.querySelectorAll('.nf301-item[data-dropdown]')];
function setFly(item,on,reason=''){
 item.dataset.openSource=on?reason:'';
 const btn=item.querySelector('.nf301-disclose');
 item.dataset.open=on?'true':'false';
 btn?.setAttribute('aria-expanded',String(on));
 if(btn)btn.setAttribute('aria-label',btn.getAttribute('aria-label').replace(/펼치기|접기/g,on?'접기':'펼치기'));
}
function closeFly(){flyouts.forEach(i=>setFly(i,false))}
flyouts.forEach(item=>{
 const btn=item.querySelector('.nf301-disclose');
 btn?.addEventListener('click',e=>{
  e.preventDefault();e.stopPropagation();
  const explicit=item.dataset.open==='true'&&item.dataset.openSource==='click';
  closeFly();
  if(!explicit)setFly(item,true,'click');
 });
 item.addEventListener('mouseenter',()=>{if(matchMedia('(min-width: 1200px)').matches){closeFly();setFly(item,true,'hover')}});
 item.addEventListener('mouseleave',()=>{if(matchMedia('(min-width: 1200px)').matches)setFly(item,false)});
 item.addEventListener('focusin',()=>{if(matchMedia('(min-width: 1200px)').matches&&item.dataset.open!=='true'){closeFly();setFly(item,true,'focus')}});
 item.addEventListener('focusout',e=>{
  if(!item.contains(e.relatedTarget))setFly(item,false);
 });
});
// Restore dropdown on actual mouse motion when a page-specific style or browser
// pointer capability causes an intermittent missed mouseenter on desktop.
header.querySelector('.nf301-primary')?.addEventListener('pointermove',e=>{
 if(e.pointerType!=='mouse'||!matchMedia('(min-width:1200px)').matches)return;
 const item=e.target?.closest?.('.nf301-item[data-dropdown]');
 if(item&&item.dataset.open!=='true'){closeFly();setFly(item,true,'hover')}
});
function mobileOpen(next,restoreFocus=false){
 if(!mobile||!mobileToggle)return;
 mobile.dataset.open=next?'true':'false';
 mobileToggle.setAttribute('aria-expanded',String(next));
 mobileToggle.setAttribute('aria-label',next?'전체 메뉴 닫기':'전체 메뉴 열기');
 mobile.inert=!next;
 document.documentElement.classList.toggle('nf301-menu-open',next&&matchMedia('(max-width:1199px)').matches);
 if(next){
  const first=mobile.querySelector('a');
  first?.focus({preventScroll:true});
 }else if(restoreFocus)mobileToggle.focus({preventScroll:true});
}
mobileToggle?.addEventListener('click',()=>mobileOpen(mobile.dataset.open!=='true',false));
for(const btn of header.querySelectorAll('.nf301-mob-expand')){
 btn.addEventListener('click',()=>{
  const panel=document.getElementById(btn.getAttribute('aria-controls'));
  if(!panel)return;
  const next=panel.dataset.open!=='true';
  header.querySelectorAll('.nf301-mob-expand').forEach(other=>{
   if(other!==btn){other.setAttribute('aria-expanded','false');document.getElementById(other.getAttribute('aria-controls'))?.setAttribute('data-open','false')}
  });
  panel.dataset.open=next?'true':'false';
  btn.setAttribute('aria-expanded',String(next));
  btn.setAttribute('aria-label',btn.getAttribute('aria-label').replace(/펼치기|접기/g,next?'접기':'펼치기'));
 });
}
document.addEventListener('click',e=>{
 if(!header.contains(e.target)){closeFly();if(mobile.dataset.open==='true')mobileOpen(false,false)}
});
document.addEventListener('keydown',e=>{
 if(e.key==='Escape'){
  const wasOpen=mobile?.dataset.open==='true';
  closeFly();
  if(wasOpen){mobileOpen(false,true);e.preventDefault()}
 }
});
window.addEventListener('resize',()=>{
 if(matchMedia('(min-width:1200px)').matches&&mobile.dataset.open==='true')mobileOpen(false,false);
});
mobile?.addEventListener('click',e=>{
 const anchor=e.target.closest('a');
 if(anchor&&anchor.hash&&anchor.pathname===location.pathname){
  mobileOpen(false,false);
 }
});
if(location.hash&&['#family','#couple','#parents'].includes(location.hash)){
 const btn=header.querySelector('.nf301-mob-group[data-mob-group="people"] .nf301-mob-expand');
 if(btn){
  const panel=document.getElementById(btn.getAttribute('aria-controls'));
  panel.dataset.open='true';btn.setAttribute('aria-expanded','true');
 }
}
})();