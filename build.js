const fs = require('fs');
const path = require('path');
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
const pages=walk(out);
for(const file of pages) {
  let h=fs.readFileSync(file,'utf8');
  h=h.split('href="/#ferry"').join('href="/ferry/"');
  // Main search journey: Japan cruise pillar; ferry routes remain linked in content.
  h=h.replace(/(<nav class="desktop-nav">)([\s\S]*?)(<\/nav>)/g,(_,start,menu,end)=>start+menu.replace(/<a[^>]*href="\/(?:#ferry|ferry\/|japan-cruise\/)"[^>]*>[^<]*<\/a>/,'<a class="nav-book" href="/japan-cruise/">⛴ 일본크루즈</a>')+end);
  h=h.replace(/(<div class="mobile-menu">)([\s\S]*?)(<\/div>)/g,(_,start,menu,end)=>start+menu.replace(/<a[^>]*href="\/(?:#ferry|ferry\/|japan-cruise\/)"[^>]*>[^<]*<\/a>/,'<a href="/japan-cruise/">일본크루즈</a>')+end);

  h=h.split('<a href="/contents/">📚 콘텐츠</a>').join('');
  h=h.split('<a href="/contents/">여행 콘텐츠</a>').join('');
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
  // Public-facing pages must never display internal release numbers.
  // Keep V## only in GitHub commit history, README and developer CSS class names.
  // Match version prefixes at the beginning of visible text nodes, not V-branded products.
  h=h.replace(/(>\s*)V\d{1,3}\s*[·:—–-]\s*/g,'$1');
  h=h.replace(/(>\s*)V\d{1,3}\b(?=\s*<)/g,'$1');
  fs.writeFileSync(file,h);
}
console.log('Built',pages.length,'HTML pages; merged content navigation');
