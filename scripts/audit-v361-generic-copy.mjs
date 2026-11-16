#!/usr/bin/env node
// V361: read-only inventory of repeated generic paragraphs in existing pages.
import fs from 'node:fs';
import path from 'node:path';
const pages=[];
function walk(dir){for(const e of fs.readdirSync(dir,{withFileTypes:true})){const p=path.join(dir,e.name);if(e.isDirectory())walk(p);else if(e.isFile()&&p.endsWith('.html'))pages.push(p)}}
walk('site');
const occurrences=new Map();
for(const page of pages){
 const html=fs.readFileSync(page,'utf8').replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,' ').replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi,' ');
 const unique=new Set();
 for(const m of html.matchAll(/<(?:p|li)\b[^>]*>([\s\S]*?)<\/(?:p|li)>/gi)){
  const s=m[1].replace(/<[^>]*>/g,' ').replace(/&nbsp;/g,' ').replace(/\s+/g,' ').trim();
  if(s.length<45||s.length>400||!/[가-힣]/.test(s))continue;
  unique.add(s);
 }
 for(const s of unique){if(!occurrences.has(s))occurrences.set(s,[]);occurrences.get(s).push(page)}
}
const rows=[...occurrences].filter(([,p])=>p.length>=5).map(([text,pages])=>({text,pagesCount:pages.length,samplePages:pages.slice(0,12),reviewOnly:true})).sort((a,b)=>b.pagesCount-a.pagesCount);
fs.mkdirSync('audit-reports/v361',{recursive:true});
fs.writeFileSync('audit-reports/v361/repeated-copy.json',JSON.stringify({pagesScanned:pages.length,repeatGroups:rows.length,rows},null,2)+'\n');
console.log(JSON.stringify({pagesScanned:pages.length,repeatGroups:rows.length}));
