#!/usr/bin/env node
// V366: read-only JSON-LD URL consistency inventory; complements V358 syntax/canonical audit.
import fs from 'node:fs';
import path from 'node:path';
const root='site', pages=[], rows=[];
function walk(dir){if(!fs.existsSync(dir))return;for(const entry of fs.readdirSync(dir,{withFileTypes:true})){const p=path.join(dir,entry.name);if(entry.isDirectory())walk(p);else if(entry.isFile()&&p.endsWith('.html'))pages.push(p)}}
walk(root);
const base='https://www.nipponferry.com/';
for(const file of pages){
 const html=fs.readFileSync(file,'utf8');
 const relative=path.relative(root,file).replaceAll('\\','/');
 const canonical=(html.match(/<link\b(?=[^>]*\brel\s*=\s*["']canonical["'])[^>]*\bhref\s*=\s*["']([^"']+)/i)||[])[1];
 const scripts=[...html.matchAll(/<script\b[^>]*\btype\s*=\s*["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi)];
 const issues=[];
 for(let i=0;i<scripts.length;i++){
  let data;try{data=JSON.parse(scripts[i][1])}catch{continue} // syntax covered by V358
  function inspect(node,location){
   if(!node||typeof node!=='object')return;
   if(Array.isArray(node)){node.forEach((v,j)=>inspect(v,location+'['+j+']'));return}
   const types=[].concat(node['@type']||[]);
   const pageType=types.some(t=>['WebPage','Article','BlogPosting','NewsArticle','TouristAttraction'].includes(t));
   for(const key of ['url','@id']){
    const value=node[key];
    if(pageType&&typeof value==='string'&&value.startsWith(base)){
     const normalized=value.split('#')[0].split('?')[0].replace(/\/$/,'');
     if(canonical&&normalized!==canonical.split('#')[0].split('?')[0].replace(/\/$/,''))
      issues.push({script:i,location,key,value,canonical,reason:'page-schema-url-differs-from-canonical'});
    }
   }
   for(const [k,v] of Object.entries(node))if(k!=='@context')inspect(v,location+'.'+k);
  }
  inspect(data,'$');
 }
 if(issues.length)rows.push({file:relative,issues,reviewOnly:true});
}
rows.sort((a,b)=>a.file.localeCompare(b.file));
const output='audit-reports/v366/jsonld-url-consistency.json';
fs.mkdirSync(path.dirname(output),{recursive:true});
fs.writeFileSync(output,JSON.stringify({pagesScanned:pages.length,pagesFlagged:rows.length,note:'Candidates only. JSON-LD entity IDs and tourist attraction URLs can intentionally differ from the page canonical. Human verification required before any edits. V358 covers canonical presence and JSON syntax.',rows},null,2)+'\n');
console.log(JSON.stringify({pagesScanned:pages.length,pagesFlagged:rows.length}));
