#!/usr/bin/env node
// V362: read-only inventory. A domain/label match is NOT proof of official booking.
import fs from 'node:fs';
import path from 'node:path';
const files=[];
function walk(dir){if(!fs.existsSync(dir))return;for(const e of fs.readdirSync(dir,{withFileTypes:true})){const p=path.join(dir,e.name);if(e.isDirectory())walk(p);else if(e.isFile()&&p.endsWith('.html'))files.push(p)}}
walk('site');
const rows=[];
const intent=/(예약|발권|승선|수속|체크인|운항|요금|유류할증료|boarding|booking|ticket)/i;
for(const file of files){
 const html=fs.readFileSync(file,'utf8').replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,' ');
 for(const match of html.matchAll(/<a\b([^>]*)>([\s\S]*?)<\/a>/gi)){
  const href=match[1].match(/\bhref\s*=\s*["']([^"']+)["']/i)?.[1];
  if(!href)continue;
  const label=match[2].replace(/<[^>]+>/g,' ').replace(/&(?:nbsp|rarr|amp);/g,' ').replace(/\s+/g,' ').trim();
  if(!intent.test(label))continue;
  let host=null,scheme='relative';
  try{const url=new URL(href,'https://www.nipponferry.com/');host=url.hostname;scheme=url.protocol;}catch{scheme='invalid'}
  rows.push({file,label:label.slice(0,140),href,host,scheme,external:!!host&&!/(^|\.)nipponferry\.com$/i.test(host),reviewOnly:true});
 }
}
rows.sort((a,b)=>a.file.localeCompare(b.file)||a.label.localeCompare(b.label));
const summary={pagesScanned:files.length,ctaLinks:rows.length,externalLinks:rows.filter(r=>r.external).length,invalidUrls:rows.filter(r=>r.scheme==='invalid').length,disclaimer:'Read-only candidates. Verify operator ownership, exact booking/check-in destination and current official notice manually before editing.',rows};
fs.mkdirSync('audit-reports/v362',{recursive:true});
fs.writeFileSync('audit-reports/v362/cta-destinations.json',JSON.stringify(summary,null,2)+'\n');
console.log(JSON.stringify({pagesScanned:summary.pagesScanned,ctaLinks:summary.ctaLinks,externalLinks:summary.externalLinks,invalidUrls:summary.invalidUrls}));
