/* V301–V305: one canonical, accessible site header at production build.
   Replaces only <header class="site-header"> while preserving article body and SEO.
   Existing source documents are untouched; build.js applies this to every HTML output. */
const path=require('path');
const ROOT='/';
const region=[
['도쿄','220편 실전 백과','/japan/tokyo/'],
['오사카','맛집·도심 관광','/japan/osaka/'],
['후쿠오카','규슈 핵심 여행','/japan/fukuoka/'],
['오키나와','해변·섬 관광','/okinawa/'],
['홋카이도','자연·계절 여행','/japan/hokkaido/'],
['고베','항구·야경','/japan/kobe/'],
['대마도','부산 출발','/japan/tsushima/'],
['시모노세키','항구·시장','/japan/shimonoseki/']];
const topical=[
['식도락','/food/'],['쇼핑','/shopping/'],['4계절·축제','/seasons/'],
['포토스팟','/photo-spots/']];
const people=[
['가족 여행','/things-to-do/travel-companions/#family'],
['커플 여행','/things-to-do/travel-companions/#couple'],
['부모님 여행','/things-to-do/travel-companions/#parents'],
['일본 연애문화','/couple/']];
const practical=[
['교통·승차권','/practical/'],['여행 준비물·eSIM','/practical/esim/'],
['일본 현지생활','/life/'],['쿠폰·바우처','/voucher/']];
const extras=[
['식도락','/food/'],['쇼핑','/shopping/'],['4계절·축제','/seasons/'],
['커플 여행','/things-to-do/travel-companions/#couple'],
['가족 여행','/things-to-do/travel-companions/#family'],
['부모님 여행','/things-to-do/travel-companions/#parents'],
['쿠폰·바우처','/voucher/'],['포토스팟','/photo-spots/']];
const main=[
['cruise','일본크루즈','/japan-cruise/'],
['ports','크루즈 기항지','/things-to-do/cruise-ports/'],
['japan','일본 여행지','/japan/',region],
['things','즐길거리','/things-to-do/',topical],
['people','동행 가이드','/things-to-do/travel-companions/',people],
['practical','여행 정보','/practical/',practical]];
function clean(href){return href.split(/[?#]/)[0].replace(/\/+$/,'')+'/';}
function getGroup(page){
 if(/^\/booking\//.test(page))return 'booking';
 if(/^(\/japan-cruise\/|\/busan-|\/ferry\/|\/routes\/|\/route\/)/.test(page))return 'cruise';
 if(/\/cruise-ports\/|\/(?:[^/]*cruise[^/]*-port-|[^/]*-port-day-trip)/.test(page))return 'ports';
 if(page.startsWith('/things-to-do/travel-companions/')||page.startsWith('/couple/'))return 'people';
 if(['/food/','/shopping/','/seasons/','/season/','/photo-spots/'].some(x=>page.startsWith(x)))return 'things';
 if(page.startsWith('/things-to-do/'))return 'things';
 if(['/practical/','/life/','/tips/','/guide/','/voucher/'].some(x=>page.startsWith(x)))return 'practical';
 if(['/japan/','/explore/','/okinawa/','/osaka/','/fukuoka/'].some(x=>page.startsWith(x)))return 'japan';
 return '';
}
function escape(s){return String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function activeClass(isActive){return isActive?' nf301-active':'';}
function current(isActive){return isActive?' aria-current="page"':'';}
function flyItems(items){return items.map(([title,desc,link])=>'<a href="'+escape(link)+'"><span>'+escape(title)+'</span>'+(desc?'<small>'+escape(desc)+'</small>':'')+'</a>').join('');}
function getHref(href){return clean(href);}
function renderHeader(page){
 const active=getGroup(page), booking=active==='booking';
 const renderItem=([id,label,href,children])=>{
  const isActive=active===id;
  const a='<a class="nf301-mainlink'+activeClass(isActive)+'" href="'+href+'"'+current(isActive&&!children)+'>'+label+'</a>';
  if(!children)return '<div class="nf301-item">'+a+'</div>';
  const items=children.map(([x,y,z])=>z?[x,y,z]:[x,'',y]);
  return '<div class="nf301-item" data-dropdown="'+id+'" data-open="false">'+a+
   '<button type="button" class="nf301-disclose" aria-label="'+label+' 하위 메뉴 펼치기" aria-expanded="false" aria-controls="nf301-fly-'+id+'"><span aria-hidden="true">⌄</span></button>'+
   '<div class="nf301-flyout" id="nf301-fly-'+id+'"><h2>'+label+'</h2><p>원하는 항목을 선택하면 기존 전문 안내 페이지로 이동합니다.</p><div class="nf301-flygrid">'+flyItems(items)+'</div></div></div>';
 };
 const secondary=extras.map(([title,href])=>{
  const isActive=(!href.includes('#')&&page===getHref(href)) || (title==='커플 여행'&&page==='/couple/');
  return '<a href="'+href+'" class="'+(isActive?'nf301-active':'')+'"'+current(isActive)+'>'+title+'</a>';
 }).join('');
 const mobile=main.map(([id,label,href,children])=>{
  const isActive=active===id;
  if(!children)return '<a class="nf301-mob-direct'+activeClass(isActive)+'" href="'+href+'"'+current(isActive)+'>'+label+'</a>';
  const items=children.map(([x,y,z])=>z?[x,z]:[x,y]);
  return '<section class="nf301-mob-group" data-mob-group="'+id+'"><div class="nf301-mob-heading">'+
   '<a href="'+href+'"'+(isActive?' class="nf301-active"':'')+'>'+label+'</a>'+
   '<button class="nf301-mob-expand" type="button" aria-label="'+label+' 하위 항목 펼치기" aria-expanded="false" aria-controls="nf301-mob-'+id+'">⌄</button></div>'+
   '<div class="nf301-mob-options" id="nf301-mob-'+id+'" data-open="false">'+
   '<a href="'+href+'">'+label+' 전체 보기</a>'+
   items.map(([title,link])=>'<a href="'+link+'"'+(!link.includes('#')&&page===getHref(link)?' class="nf301-active"':'')+'>'+title+'</a>').join('')+'</div></section>';
 }).join('');
 const expanded=main.map(renderItem).join('');
 return '<header class="site-header nf301-header" data-nf301="v305">'+
  '<div class="nf301-top"><div class="nf301-width nf301-bar">'+
  '<a class="brand nf301-brand" href="/" aria-label="NIPPONFERRY 홈"><img class="nf301-logo" src="/images/mascot.png" width="39" height="39" alt=""><span class="nf301-brandcopy"><strong>NIPPONFERRY</strong><small>크루즈로 만나는 일본 여행</small></span></a>'+
  '<nav class="desktop-nav nf301-primary" aria-label="주요 여행 카테고리">'+expanded+
  '<a class="nf301-cta'+activeClass(booking)+'" href="/booking/japan-cruise/"'+current(booking)+'>예약 안내 <span aria-hidden="true">→</span></a></nav>'+
  '<div class="nf301-mobile-controls"><a class="nf301-mobile-cta'+activeClass(booking)+'" href="/booking/japan-cruise/">예약 안내</a>'+
  '<button class="nf301-toggle" aria-label="전체 메뉴 열기" aria-expanded="false" aria-controls="nf301-mobile-panel" type="button"><span class="nf301-line"></span><span class="nf301-line"></span><span class="nf301-line"></span></button></div>'+
  '</div></div>'+
  '<div class="nf301-secondary"><nav class="nf301-width nf301-subrow" aria-label="세부 여행 카테고리">'+secondary+'</nav></div>'+
  '<nav id="nf301-mobile-panel" class="nf301-mobile-panel" aria-label="모바일 여행 카테고리" data-open="false" inert>'+
  mobile+'<div class="nf301-mobile-foot"><a href="/voucher/">쿠폰·바우처</a><a href="/photo-spots/">포토스팟</a></div></nav>'+
  '</header>';
}
function enhanceDocument(html,file,out){
 if(html.includes('data-nf301="v305"'))return {html,modified:false};
 const rel=path.relative(out,file).replace(/\\/g,'/');
 const pathname=rel==='index.html'?'/':'/'+rel.replace(/index\.html$/,'');
 // V246: the homepage has its own accessible maritime navigation.
 // Keep V301–V305 unified headers on every other page; never overwrite the
 // home-only hero/header refresh during the Vercel build.
 if(pathname==='/' && /<header\b[^>]*class=["'][^"']*\bnf246-header\b/.test(html)){
  return {html,modified:false,pathname};
 }
 const hasSiteHeader=/<header\b[^>]*class=["'][^"']*\bsite-header\b/.test(html);
 const legacyArticle=pathname.startsWith('/things-to-do/');
 if(!hasSiteHeader&&!legacyArticle)return {html,modified:false};
 let applied=false;
 if(hasSiteHeader){
  html=html.replace(/<header\b[^>]*class=["'][^"']*\bsite-header\b[^"']*["'][^>]*>[\s\S]*?<\/header>/i,()=>{applied=true;return renderHeader(pathname)});
 }else{
  // Replace a standalone old <header class="top|sitebar|sitehead"> only when it precedes main.
  // Some editorial articles have no site header at all: add one just after the body tag,
  // never delete an article's internal heading, figure or breadcrumb.
  const oldHeader=/<header\b[^>]*>[\s\S]*?<\/header>/i.exec(html);
  const mainIndex=html.search(/<main\b/i);
  // Only replace a real legacy SITE header. An article's semantic <header>
  // may contain its only <h1>, location and lead; deleting it breaks SEO.
  const replaceableLegacySiteHeader=oldHeader &&
    /<header\b[^>]*class=["'][^"']*\b(?:top|sitebar|sitehead)\b/i.test(oldHeader[0]) &&
    !/<h1\b/i.test(oldHeader[0]);
  if(replaceableLegacySiteHeader && (mainIndex<0 || oldHeader.index<mainIndex)){
   html=html.slice(0,oldHeader.index)+renderHeader(pathname)+html.slice(oldHeader.index+oldHeader[0].length);
   applied=true;
  }else{
   html=html.replace(/<body\b[^>]*>/i,m=>{applied=true;return m+renderHeader(pathname)});
  }
 }
 if(!applied)return {html,modified:false};
 if(!html.includes('/v301-nav.css'))html=html.replace('</head>','<link rel="stylesheet" href="/v301-nav.css"><script src="/v301-nav.js" defer></script></head>');
 return {html,modified:true,pathname};
}
module.exports={enhanceDocument,renderHeader,getGroup,main,extras,region};
