const fs = require('fs');
const path = require('path');
const {enhanceDocument}=require('./scripts/v301-v305-nav.cjs');
const {compactPhotoAttribution}=require('./scripts/v139_photo_credits.cjs');
const {transformJourney}=require('./scripts/v143_contextual_related.cjs');
const src = path.join(__dirname, 'site');
const out = path.join(__dirname, 'dist');
fs.rmSync(out, {recursive:true, force:true});
fs.mkdirSync(out, {recursive:true});
fs.cpSync(src, out, {recursive:true});
// The former content page is now permanently redirected to /things-to-do/.
fs.rmSync(path.join(out,'contents'), {recursive:true,force:true});
function walk(d, a=[]) {
  for(const n of fs.readdirSync(d)) {
    const p=path.join(d,n), s=fs.statSync(p);
    if(s.isDirectory()) walk(p,a);
    else if(n.endsWith('.html')) a.push(p);
  }
  return a;
}
// V93: GA4 measurement IDs are public tags, but must come from Vercel build env.
const ga4Id = (process.env.GA4_MEASUREMENT_ID || '').trim();
if (ga4Id && !/^G-[A-Z0-9]{7,15}$/.test(ga4Id)) {
  throw new Error('Invalid GA4_MEASUREMENT_ID format. Expected a GA4 web stream G- ID.');
}
const pages=walk(out);
let unifiedHeaders=0, legacyWithoutHeader=0, compactedPhotoCaptions=0, photoPages=0, contextualJourneys=0;
for(const file of pages) {
  let h=fs.readFileSync(file,'utf8');
  h=h.split('href="/#ferry"').join('href="/ferry/"');
  // Main search journey: Japan cruise pillar; ferry routes remain linked in content.
  h=h.replace(/(<nav class="desktop-nav">)([\s\S]*?)(<\/nav>)/g,(_,start,menu,end)=>start+menu.replace(/<a[^>]*href="\/(?:#ferry|ferry\/|japan-cruise\/)"[^>]*>[^<]*<\/a>/,'<a class="nav-book" href="/japan-cruise/">⛴ 일본크루즈</a>')+end);
  h=h.replace(/(<div class="mobile-menu">)([\s\S]*?)(<\/div>)/g,(_,start,menu,end)=>start+menu.replace(/<a[^>]*href="\/(?:#ferry|ferry\/|japan-cruise\/)"[^>]*>[^<]*<\/a>/,'<a href="/japan-cruise/">일본크루즈</a>')+end);

  // Remove retired content links as literal strings: no fragile slash escaping in regex literals.
  for (const retired of ['<a href="/contents/">📚 콘텐츠</a>', '<a href="/contents/">여행 콘텐츠</a>']) {
    h = h.replaceAll(retired, '');
  }
  // Show food, shopping and seasons as categories inside the things-to-do hub.
  const categoryNavLink=/<a\b[^>]*href="\/(?:food|shopping|seasons)\/"[^>]*>[\s\S]*?<\/a>/g;
  h=h.replace(/(<nav class="desktop-nav">)([\s\S]*?)(<\/nav>)/g,(_,a,menu,z)=>a+menu.replace(categoryNavLink,'')+z);
  h=h.replace(/(<div class="mobile-menu">)([\s\S]*?)(<\/div>)/g,(_,a,menu,z)=>a+menu.replace(categoryNavLink,'')+z);
  const desktop=h.match(/<nav class="desktop-nav">([\s\S]*?)<\/nav>/);
  if(desktop && !desktop[1].includes('href="/things-to-do/"')) {
    h=h.replace('<nav class="desktop-nav">','<nav class="desktop-nav"><a href="/things-to-do/">🎡 즐길거리</a>');
  }
  const mobile=h.match(/<div class="mobile-menu">([\s\S]*?)<\/div>/);
  if(mobile && !mobile[1].includes('href="/things-to-do/"')) {
    h=h.replace('<div class="mobile-menu">','<div class="mobile-menu"><a href="/things-to-do/">즐길거리</a>');
  }
  // V25: constrain the shared brand image at markup level for legacy cruise templates.
  // Prevent intrinsic 1254px mascot artwork from expanding narrow screens before CSS settles.
  if (file.includes(path.join('things-to-do', ''))) {
    h=h.replace(/(<a class="brand"[^>]*>\s*<img)([^>]*src="\/images\/mascot\.png"[^>]*)(>)/g,
      (_,start,attrs,end)=>start+attrs.replace(/\s+style="[^"]*"/g,'')+' style="width:38px;height:38px;max-width:38px;max-height:38px;object-fit:contain;flex-shrink:0"'+end);
  }
  // Public-facing pages must never display internal release numbers.
  // Keep V## only in GitHub commit history, README and developer CSS class names.
  // Match version prefixes at the beginning of visible text nodes, not V-branded products.
  h=h.replace(/(>\s*)V\d{1,3}\s*[·:—–-]\s*/g,'$1');
  h=h.replace(/(>\s*)V\d{1,3}\b(?=\s*<)/g,'$1');
  // V68: the source-audit release number belongs in Git history, not visitor-facing badges.
  h=h.replaceAll('NIPPONFERRY · V68 SOURCED GUIDE ·', 'NIPPONFERRY · 공식 자료 점검 ·');
  const nav=enhanceDocument(h,file,out);
  h=nav.html;
  // V249: shared mobile navigation + reading controls on V301 pages.
  // The homepage links this stylesheet in its source, so avoid duplicates.
  if (/<header\\b[^>]*class=["'][^"']*\\b(?:nf301-header|nf246-header)\\b/.test(h) &&
      !h.includes('/nf-v249-mobile-consistency.css')) {
    h=h.replace(/<\\/head>/i,'<link rel="stylesheet" href="/nf-v249-mobile-consistency.css?v=20261027"></head>');
  }
  // Track outbound ferry CTAs only when the owner has configured a real GA4 ID.
  // No GA4 library, cookies, requests or consent banner start before visitor opt-in.
  // Analytics is optional: production without an ID is visibly 'not connected' in QA.
  if (ga4Id) {
    const css = '<link rel="stylesheet" href="/nf-v93-booking-clicks.css?v=20261021">';
    const src = '<script defer src="/nf-v93-booking-clicks.js?v=20261024-v153" data-nf-ga4="' + ga4Id + '"><\/script>';
    if (!/<\/head>/i.test(h) || !/<\/body>/i.test(h)) {
      throw new Error('V93 cannot install GA4 consent safely: malformed HTML ' + file);
    }
    h=h.replace(/<\/head>/i,css+'</head>');
    h=h.replace(/<\/body>/i,src+'</body>');
  }
  if(nav.modified)unifiedHeaders++;else legacyWithoutHeader++;
  // Topic continuity: reuse each article's own related article links, not
  // generic English NEXT QUESTION/CITY MAP links unrelated to the article.
  const fileRoute='/'+path.relative(out,file).replaceAll('\\','/').replace(/index\.html$/,'');
  const journey=transformJourney(h,fileRoute);
  h=journey.html;
  if(journey.changed)contextualJourneys++;
  const creditPanel=compactPhotoAttribution(h);
  h=creditPanel.html;
  compactedPhotoCaptions+=creditPanel.credits;
  if(creditPanel.credits)photoPages++;
  fs.writeFileSync(file,h);
}
console.log('Built',pages.length,'HTML pages; V301–V305 unified headers:',unifiedHeaders,'pages; others:',legacyWithoutHeader);
console.log('V139 compact photo attributions:',compactedPhotoCaptions,'across',photoPages,'pages; original rights metadata retained in details panels.');
console.log('V143 contextual next-step sections:',contextualJourneys,'pages; existing topic-specific link destinations preserved.');
