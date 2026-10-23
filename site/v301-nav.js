/* V301–V305 unified header accessibility + progressive enhancement */
(()=>{'use strict';
const header=document.querySelector('.nf301-header');
if(!header)return;
const mobile=header.querySelector('#nf301-mobile-panel');
const mobileToggle=header.querySelector('.nf301-toggle');
const flyouts=[...header.querySelectorAll('.nf301-item[data-dropdown]')];
const leaveTimers=new WeakMap();
/* Keep an explicitly clicked mega-menu open while the pointer crosses
   neighboring navigation tabs. Hover-only menus remain switchable. */
function hasClickLockedFlyout(){
 return flyouts.some(i=>i.dataset.open==='true'&&i.dataset.openSource==='click');
}
function cancelFlyClose(item){const id=leaveTimers.get(item);if(id)clearTimeout(id);leaveTimers.delete(item)}
function scheduleFlyClose(item){
 cancelFlyClose(item);
 // Explicit arrow-button activation must remain open while the user
 // moves from the narrow top navigation to the much larger mega-panel.
 // Only a second button click, Escape or outside click closes it.
 if(item.dataset.openSource==='click')return;
 leaveTimers.set(item,setTimeout(()=>{
  if(!item.matches(':hover')&&!item.contains(document.activeElement))setFly(item,false);
  leaveTimers.delete(item);
 },260));
}
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
 item.addEventListener('mouseenter',()=>{
  cancelFlyClose(item);
  if(matchMedia('(min-width: 1200px)').matches&&!hasClickLockedFlyout()){
   closeFly();setFly(item,true,'hover');
  }
 });
 item.addEventListener('mouseleave',()=>{if(matchMedia('(min-width: 1200px)').matches)scheduleFlyClose(item)});
 item.addEventListener('focusin',()=>{
  if(matchMedia('(min-width: 1200px)').matches&&item.dataset.open!=='true'&&!hasClickLockedFlyout()){
   closeFly();setFly(item,true,'focus');
  }
 });
 item.addEventListener('focusout',e=>{
  /* A pointer-activated flyout must not disappear when focus momentarily
     leaves its narrow trigger. Escape, second click or outside click closes. */
  if(!item.contains(e.relatedTarget)&&item.dataset.openSource!=='click')setFly(item,false);
 });
});
// Restore dropdown on actual mouse motion when a page-specific style or browser
// pointer capability causes an intermittent missed mouseenter on desktop.
header.querySelector('.nf301-primary')?.addEventListener('pointermove',e=>{
 if(e.pointerType!=='mouse'||!matchMedia('(min-width:1200px)').matches)return;
 const item=e.target?.closest?.('.nf301-item[data-dropdown]');
 if(item&&!hasClickLockedFlyout()){
  cancelFlyClose(item);
  if(item.dataset.open!=='true'){closeFly();setFly(item,true,'hover')}
 }
});
/* V142: one accordion state manager for buttons and matching link panels. */
function setMobileGroup(button,open){
 const panel=button&&document.getElementById(button.getAttribute('aria-controls'));
 if(!panel)return;
 header.querySelectorAll('.nf301-mob-expand').forEach(other=>{
  const child=document.getElementById(other.getAttribute('aria-controls'));
  const active=other===button&&open;
  other.setAttribute('aria-expanded',String(active));
  other.setAttribute('aria-label',other.getAttribute('aria-label').replace(/펼치기|접기/g,active?'접기':'펼치기'));
  if(child)child.dataset.open=String(active);
 });
}
function expandCurrentMobileGroup(){
 const active=mobile?.querySelector('.nf301-mob-group .nf301-mob-heading > a.nf301-active');
 const btn=active?.parentElement?.querySelector('.nf301-mob-expand');
 if(btn&&btn.getAttribute('aria-expanded')!=='true')setMobileGroup(btn,true);
}
function mobileOpen(next,restoreFocus=false){
 if(!mobile||!mobileToggle)return;
 mobile.dataset.open=next?'true':'false';
 mobileToggle.setAttribute('aria-expanded',String(next));
 mobileToggle.setAttribute('aria-label',next?'전체 메뉴 닫기':'전체 메뉴 열기');
 mobile.inert=!next;
 document.documentElement.classList.toggle('nf301-menu-open',next&&matchMedia('(max-width:1199px)').matches);
 if(next){
  /* Deep pages show their relevant section without requiring an extra tap. */
  expandCurrentMobileGroup();
  mobile.scrollTop=0;
  const first=mobile.querySelector('a');
  first?.focus({preventScroll:true});
 }else if(restoreFocus)mobileToggle.focus({preventScroll:true});
}
mobileToggle?.addEventListener('click',()=>mobileOpen(mobile.dataset.open!=='true',false));
for(const btn of header.querySelectorAll('.nf301-mob-expand')){
 btn.addEventListener('click',()=>{
  const panel=document.getElementById(btn.getAttribute('aria-controls'));
  if(panel)setMobileGroup(btn,panel.dataset.open!=='true');
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
 /* When the navigation covers the screen, Tab stays inside its visible
    brand, booking action, close button and links — not behind the overlay. */
 if(e.key==='Tab'&&mobile?.dataset.open==='true'&&matchMedia('(max-width:1199px)').matches){
  const visible=[...header.querySelectorAll('a[href],button:not([disabled])')].filter(el=>
   el.getClientRects().length>0&&getComputedStyle(el).visibility!=='hidden'&&!el.closest('[inert]'));
  if(!visible.length)return;
  const first=header.querySelector('.nf301-brand')||visible[0];
  const last=mobile.querySelector('.nf301-mobile-foot a:last-child')||visible[visible.length-1];
  const here=document.activeElement;
  if(e.shiftKey&&(here===first||!visible.includes(here))){e.preventDefault();last.focus()}
  else if(!e.shiftKey&&(here===last||here===visible[visible.length-1]||!visible.includes(here))){
   e.preventDefault();first.focus();
  }
 }
},true); // Capture Tab/Escape before legacy page handlers can intercept them.
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
  setMobileGroup(btn,true);
 }
}
})();