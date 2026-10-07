const fs=require('fs'),path=require('path');
const src=path.join(__dirname,'site'),out=path.join(__dirname,'dist');
fs.rmSync(out,{recursive:true,force:true});fs.mkdirSync(out,{recursive:true});fs.cpSync(src,out,{recursive:true});
function walk(d,a=[]){for(const n of fs.readdirSync(d)){const p=path.join(d,n),s=fs.statSync(p);s.isDirectory()?walk(p,a):n.endsWith('.html')&&a.push(p)}return a}
const pages=walk(out);
for(const f of pages){
 let h=fs.readFileSync(f,'utf8');
 h=h.replaceAll('href="/#ferry"','href="/ferry/"');
 fs.writeFileSync(f,h);
}
console.log('V12 route fix:',pages.length,'html pages');
