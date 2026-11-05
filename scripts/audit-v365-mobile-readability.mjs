#!/usr/bin/env node
// V365 read-only mobile readability inventory. Heuristics require manual review.
import fs from 'node:fs';
import path from 'node:path';
const pages=[];
function walk(dir){if(!fs.existsSync(dir))return;for(const ent of fs.readdirSync(dir,{withFileTypes:true})){const p=path.join(dir,ent.name);if(ent.isDirectory())walk(p);else if(ent.isFile()&&p.endsWith('.html'))pages.push(p)}}
walk('site');
const rows=[];
for(const file of pages){
 const html=fs.readFileSync(file,'utf8');
 const issues=[];
 if(!/<meta\s+[^>]*name\s*=\s*["']viewport["']/i.test(html))issues.push('missing-viewport-meta');
 const styleBlocks=[...html.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/gi)].map(m=>m[1]).join('\n');
 const inlineStyles=[...html.matchAll(/\bstyle\s*=\s*["']([^"']+)["']/gi)].map(m=>m[1]).join('\n');
 const css=styleBlocks+'\n'+inlineStyles;
 const tiny=[...css.matchAll(/font-size\s*:\s*(\d+(?:\.\d+)?)px\b/gi)].filter(m=>Number(m[1])<12);
 if(tiny.length)issues.push('font-size-under-12px:'+tiny.length);
 const fixed=[...css.matchAll(/(?:min-)?width\s*:\s*(\d+)px\b/gi)].filter(m=>Number(m[1])>390);
 if(fixed.length)issues.push('fixed-width-over-390px:'+fixed.length);
 const images=[...html.matchAll(/<img\b[^>]*>/gi)];
 const noAlt=images.filter(m=>!(/\balt\s*=/i.test(m[0]))).length;
 if(noAlt)issues.push('img-without-alt:'+noAlt);
 if(issues.length)rows.push({file,issues,reviewOnly:true});
}
rows.sort((a,b)=>a.file.localeCompare(b.file));
const out='audit-reports/v365/mobile-readability.json';
fs.mkdirSync(path.dirname(out),{recursive:true});
fs.writeFileSync(out,JSON.stringify({pagesScanned:pages.length,pagesFlagged:rows.length,disclaimer:'Static heuristic only. Verify actual mobile screenshots at 390px, 768px and 1440px before editing. Fixed widths, small fonts and missing alt can be intentional or covered by external styles.',rows},null,2)+'\n');
console.log(JSON.stringify({pagesScanned:pages.length,pagesFlagged:rows.length}));
