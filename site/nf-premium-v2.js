/* NIPPONFERRY Premium V2: accessible, consistent responsive navigation.
   Capture-phase click handler works on both old and new templates, avoiding
   duplicate legacy toggles while retaining the existing markup contract. */
(()=>{"use strict";const btn=document.querySelector(".site-header .menu-toggle");
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
