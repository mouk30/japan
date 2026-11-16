import fs from 'node:fs';
import path from 'node:path';
const root=process.cwd();
const skip=new Set(['.git','node_modules','.next','dist','build','audit-reports']);
function walk(dir,out=[]){for(const e of fs.readdirSync(dir,{withFileTypes:true})){if(skip.has(e.name))continue;const p=path.join(dir,e.name);if(e.isDirectory())walk(p,out);else if(e.name.endsWith('.html'))out.push(p)}return out}
const files=walk(root),known=new Set(files.map(f=>path.resolve(f))),findings=[];
let checked=0;
for(const file of files){
 const html=fs.readFileSync(file,'utf8');
 for(const m of html.matchAll(/<a\b[^>]*?\bhref\s*=\s*["']([^"']+)["'][^>]*>/gi)){
  const href=m[1].trim();
  if(!href||href.startsWith('#')||href.startsWith('//')||/^[a-z][a-z\d+.-]*:/i.test(href))continue;
  let pathname=href.split(/[?#]/,1)[0];if(!pathname)continue;
  try{pathname=decodeURIComponent(pathname)}catch{findings.push({file:path.relative(root,file),href,reason:'invalid-url-encoding'});continue}
  if(pathname.includes('\\'))continue;
  checked++;
  const base=pathname.startsWith('/')?root:path.dirname(file);
  const target=path.resolve(base,pathname.replace(/^\/+/, ''));
  if(!target.startsWith(root+path.sep))continue;
  const candidates=[target,path.join(target,'index.html'),target+'.html'];
  if(!candidates.some(p=>known.has(p)||fs.existsSync(p)))findings.push({file:path.relative(root,file),href,reason:'unresolved-local-path-review'});
 }
}
const report={version:'V368',mode:'read-only',htmlFiles:files.length,localLinksChecked:checked,findingsCount:findings.length,findings};
fs.mkdirSync('audit-reports/v368',{recursive:true});
fs.writeFileSync('audit-reports/v368/internal-page-links.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({htmlFiles:files.length,localLinksChecked:checked,findingsCount:findings.length}));
