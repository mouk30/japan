const fs=require('fs'),path=require('path');
const src=path.join(__dirname,'site'),out=path.join(__dirname,'dist');
fs.rmSync(out,{recursive:true,force:true});fs.mkdirSync(out,{recursive:true});fs.cpSync(src,out,{recursive:true});
function walk(d,a=[]){for(const n of fs.readdirSync(d)){const p=path.join(d,n),s=fs.statSync(p);s.isDirectory()?walk(p,a):n.endsWith('.html')&&a.push(p)}return a}
// The content hub is merged into things-to-do; legacy URL redirects at Vercel.
fs.rmSync(path.join(out,'contents'),{recursive:true,force:true});
const pages=walk(out);
for(const f of pages){
 let h=fs.readFileSync(f,'utf8');
 h=h.replaceAll('href="/#ferry"','href="/ferry/');
 h=h.replace(/<a href="\\/contents\\/">(?:📚 콘텐츠|여행 콘텐츠)<\\/a>/g,'');
 if(h.includes('<nav class="desktop-nav">')&&!/<nav class="desktop-nav">[\\s\\S]*?href="\\/things-to-do\\/"/.test(h.split('</nav>')[0])){
   h=h.replace('<nav class="desktop-nav">','<nav class="desktop-nav"><a href="/things-to-do/">🎡 즐길거리</a>');
 }
 if(h.includes('<div class="mobile-menu">')&&!/<div class="mobile-menu">[\\s\\S]*?href="\\/things-to-do\\/"/.test(h.split('</div>')[0])){
   h=h.replace('<div class="mobile-menu">','<div class="mobile-menu"><a href="/things-to-do/">즐길거리</a>');
 }
 fs.writeFileSync(f,h);
}
console.log('V12 route fix:',pages.length,'html pages');
