#!/usr/bin/env node
// V370 read-only review of external links opening new tabs.
// No automatic content edits or assertions about booking availability.
import fs from 'node:fs';
import path from 'node:path';
const root = process.cwd();
const skip = new Set(['.git','node_modules','.next','dist','build','coverage','audit-reports']);
const files=[];
function walk(dir){
  for(const ent of fs.readdirSync(dir,{withFileTypes:true})){
    if(skip.has(ent.name))continue;
    const full=path.join(dir,ent.name);
    if(ent.isDirectory())walk(full);
    else if(ent.isFile()&&ent.name.endsWith('.html'))files.push(full);
  }
}
walk(root);
const findings=[];
for(const file of files){
  const html=fs.readFileSync(file,'utf8');
  const anchor=/<a\b([^>]*?)>/gi;
  for(const match of html.matchAll(anchor)){
    const attrs=match[1];
    const get=(key)=>{const re=new RegExp('(?:^|\\s)'+key+'\\s*=\\s*(?:"([^"]*)"|\\'([^\\']*)\\'|([^\\s>]+))','i');const m=attrs.match(re);return m?(m[1]??m[2]??m[3]):'';};
    const href=get('href').trim(),target=get('target').toLowerCase(),rel=get('rel').toLowerCase().split(/\s+/);
    if(target!=='_blank'||!/^https?:\/\//i.test(href))continue;
    if(rel.includes('noopener')||rel.includes('noreferrer'))continue;
    const line=html.slice(0,match.index).split('\n').length;
    findings.push({file:path.relative(root,file).replaceAll(path.sep,'/'),line,href,reason:'external target=_blank without explicit noopener/noreferrer; modern browsers may implicitly protect'});
  }
}
const report={version:'V370',scope:'read-only external new-tab rel review',scannedHtml:files.length,count:findings.length,findings};
fs.mkdirSync(path.join(root,'audit-reports','v370'),{recursive:true});
fs.writeFileSync(path.join(root,'audit-reports','v370','external-new-tab-review.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({scannedHtml:files.length,reviewCandidates:findings.length}));
