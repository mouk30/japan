import fs from 'node:fs';
import path from 'node:path';
const root=process.cwd();
const excluded=new Set(['node_modules','.git','.next','dist','build','audit-reports']);
function walk(dir,out=[]){for(const entry of fs.readdirSync(dir,{withFileTypes:true})){if(excluded.has(entry.name))continue;const p=path.join(dir,entry.name);if(entry.isDirectory())walk(p,out);else if(entry.name.endsWith('.html'))out.push(p)}return out}
const files=walk(root);const findings=[];let checked=0;
for(const file of files){const html=fs.readFileSync(file,'utf8');const ids=new Set([...html.matchAll(/\\bid\\s*=\\s*["']([^"']+)["']/gi)].map(m=>m[1]));const hrefs=[...html.matchAll(/<a\\b[^>]*?\\bhref\\s*=\\s*["']#([^"']+)["'][^>]*>/gi)];for(const m of hrefs){const anchor=m[1];if(!anchor||anchor==='!'||anchor.startsWith('/'))continue;checked++;let decoded=anchor;try{decoded=decodeURIComponent(anchor)}catch{}if(!ids.has(anchor)&&!ids.has(decoded))findings.push({file:path.relative(root,file),anchor,kind:'missing-local-fragment-target'})}}
const report={version:'V367',mode:'read-only',htmlFiles:files.length,localFragmentsChecked:checked,findingsCount:findings.length,findings};fs.mkdirSync('audit-reports/v367',{recursive:true});fs.writeFileSync('audit-reports/v367/local-fragments.json',JSON.stringify(report,null,2)+'\\n');console.log(JSON.stringify({htmlFiles:files.length,localFragmentsChecked:checked,findingsCount:findings.length}));
