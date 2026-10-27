/* V249 — homepage mobile navigation polish. Keep V2 capture-phase
   toggle and all existing route links; decorate its state, do not replace it. */
(()=>{'use strict';
const header=document.querySelector('.nf246-header');
if(!header)return;
const toggle=header.querySelector('.menu-toggle');
const menu=header.querySelector('#nf-mobile-menu');
const glyph=toggle?.querySelector('.nf-toggle-symbol');
const text=toggle?.querySelector('.nf246-toggle-label');
if(!toggle||!menu||!glyph||!text)return;
const mobile=()=>window.matchMedia('(max-width:1150px)').matches;
let lastOpen=false;
function update(){
 const open=mobile()&&menu.classList.contains('open');
 // The V2 handler remains the single source of truth for .open and aria-expanded.
 if(!mobile()&&menu.classList.contains('open'))menu.classList.remove('open');
 toggle.setAttribute('aria-expanded',String(open));
 toggle.setAttribute('aria-label',open?'메뉴 닫기':'메뉴 열기');
 glyph.textContent=open?'×':'☰';
 text.textContent=open?'닫기':'메뉴';
 menu.inert=!open;
 menu.setAttribute('aria-hidden',String(!open));
 document.documentElement.classList.toggle('nf249-menu-open',open);
 document.body.classList.toggle('nf249-menu-open',open);
 if(open&&!lastOpen){
  menu.scrollTop=0;
  // Match the focus behavior of the existing shared V301 mobile menu.
  const first=menu.querySelector('a[href]');
  first?.focus({preventScroll:true});
 }
 lastOpen=open;
}
new MutationObserver(update).observe(menu,{attributes:true,attributeFilter:['class']});
document.addEventListener('keydown',event=>{
 if(event.key!=='Tab'||!mobile()||!menu.classList.contains('open'))return;
 const links=[...menu.querySelectorAll('a[href]')].filter(a=>a.getClientRects().length&&!a.closest('[inert]'));
 const order=[toggle,...links];
 if(order.length<2)return;
 const here=document.activeElement;
 if(event.shiftKey&&(here===order[0]||!order.includes(here))){
  event.preventDefault();order[order.length-1].focus();
 }else if(!event.shiftKey&&(here===order[order.length-1]||!order.includes(here))){
  event.preventDefault();order[0].focus();
 }
},true);
window.addEventListener('resize',update,{passive:true});
update();
})();
