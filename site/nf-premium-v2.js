/* NIPPONFERRY Premium V2: accessible, consistent responsive navigation.
   Capture-phase click handler works on both old and new templates, avoiding
   duplicate legacy toggles while retaining the existing markup contract. */
(()=>{"use strict";
/* The V301 shared header owns its menu and keyboard behavior in v301-nav.js.\n   Do not run the legacy link injector against nested V301 dropdown links: a\n   descendant is not a direct insertBefore reference and raises NotFoundError. */
if(document.querySelector(".site-header.nf301-header"))return;
/* V116 independent kids theme: add to existing shared desktop/mobile menus only if absent.
   Legacy pages keep their existing title, canonical and search-indexed article content. */
for(const nav of document.querySelectorAll(".site-header .desktop-nav, .site-header .mobile-menu")){
 if(!nav.querySelector('a[href="/kids/"]')){
  const kids=document.createElement("a");
  kids.href="/kids/";kids.className="nf-kids-menu";kids.textContent="키즈여행";
  const before=nav.querySelector('a[href="/things-to-do/travel-companions/"]')||nav.querySelector(".nf-nav-reserve");
  if(before&&before.parentNode===nav)nav.insertBefore(kids,before);else nav.appendChild(kids);
 }
}
const btn=document.querySelector(".site-header .menu-toggle");
const menu=document.querySelector(".site-header .mobile-menu");
if(!btn||!menu)return;
const sync=()=>{const open=menu.classList.contains("open");btn.setAttribute("aria-expanded",open?"true":"false");btn.setAttribute("aria-label",open?"메뉴 닫기":"메뉴 열기");};
btn.addEventListener("click",e=>{
  e.preventDefault();e.stopImmediatePropagation();
  menu.classList.toggle("open");sync();
},{capture:true});
new MutationObserver(sync).observe(menu,{attributes:true,attributeFilter:["class"]});
document.addEventListener("keydown",e=>{if(e.key==="Escape"&&menu.classList.contains("open")){menu.classList.remove("open");sync();btn.focus();}});
document.addEventListener("click",e=>{if(!btn.contains(e.target)&&!menu.contains(e.target)&&menu.classList.contains("open")){menu.classList.remove("open");sync();}});
menu.addEventListener("click",e=>{if(e.target.closest("a")){menu.classList.remove("open");sync();}});
sync();})();
