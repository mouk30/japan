import fs from 'node:fs';
import path from 'node:path';
function walk(d,a=[]){for(const f of fs.readdirSync(d)){const p=path.join(d,f);const s=fs.statSync(p);if(s.isDirectory())walk(p,a);else if(f.endsWith('.html'))a.push(p)}return a}
const result={time:new Date().toISOString(),total:0,upgraded:0,notCovered:[],subgroups:{}};
for(const p of walk('dist')){
 result.total++;
 const c=fs.readFileSync(p,'utf8');
 const rel=path.relative('dist',p).replaceAll('\\','/');
 if(c.includes('data-nf301="v305"')){result.upgraded++;continue}
 const group=rel.includes('/')?rel.split('/')[0]:'(root)';
 const head=(c.match(/<header\b[^>]*>/i)||[])[0]||'';
 const first=c.slice(c.indexOf('<body'),c.indexOf('<body')+900);
 result.notCovered.push({file:rel,group,oldHeader:head,title:(c.match(/<title[^>]*>([^<]*)/i)||[])[1]?.slice(0,80),hasBody:!!c.match(/<body\b/i),bodyStart:first.slice(0,410)});
 result.subgroups[group]=(result.subgroups[group]||0)+1;
}
fs.mkdirSync('audit-reports/v301-v305',{recursive:true});
fs.writeFileSync('audit-reports/v301-v305/coverage.json',JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({total:result.total,upgraded:result.upgraded,notCovered:result.notCovered.length,subgroups:result.subgroups,samples:result.notCovered.slice(0,15)},null,2));
