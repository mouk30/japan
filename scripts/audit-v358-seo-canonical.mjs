#!/usr/bin/env node
// V358: report canonical/JSON-LD defects in existing pages; no content rewriting.
import fs from 'node:fs';
import path from 'node:path';
const root='site', files=[], rows=[];
function walk(d){for(const e of fs.readdirSync(d,{withFileTypes:true})){const p=path.join(d,e.name);if(e.isDirectory())walk(p);else if(e.isFile()&&p.endsWith('.html'))files.push(p)}}
walk(root);
for(const f of files){
 const html=fs.readFileSync(f,'utf8'),relative=path.relative(root,f).replaceAll('\\','/');
 const expected='https://www.nipponferry.com/'+relative.replace(/index\.html$/,'');
 const canon=[...html.matchAll(/<link\b[^>]*rel=["']canonical["'][^>]*>/gi)].map(m=>(m[0].match(/href=["']([^"']+)/i)||[])[1]);
 const scripts=[...html.matchAll(/<script\b[^>]*type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi)];
 const issues=[];
 if(canon.length!==1)issues.push('canonical count '+canon.length);
 else if(canon[0]!==expected)issues.push('canonical differs from expected path');
 for(const m of scripts){try{JSON.parse(m[1])}catch{issues.push('invalid JSON-LD syntax')}}
 if(!/<meta\s+name=["']description["']/i.test(html))issues.push('meta description missing');
 if(issues.length)rows.push({file:relative,canonical:canon,expected,issues});
}
fs.mkdirSync('audit-reports/v358',{recursive:true});
fs.writeFileSync('audit-reports/v358/seo-review.json',JSON.stringify({pagesScanned:files.length,candidates:rows.length,rows,note:'Canonical path exceptions (redirects, aliases) require manual review before editing.'},null,2)+'\n');
console.log(JSON.stringify({pagesScanned:files.length,seoReviewCandidates:rows.length}));
