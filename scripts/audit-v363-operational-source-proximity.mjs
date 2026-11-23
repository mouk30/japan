#!/usr/bin/env node
// V363: read-only source-proximity review; never treat a nearby link as proof.
import fs from 'node:fs';
import path from 'node:path';
const pages=[];
function walk(dir){if(!fs.existsSync(dir))return;for(const e of fs.readdirSync(dir,{withFileTypes:true})){const p=path.join(dir,e.name);if(e.isDirectory())walk(p);else if(e.isFile()&&p.endsWith('.html'))pages.push(p)}}
walk('site');
const claims=/(출항|입항|수속\s*마감|체크인\s*마감|유류\s*할증료|운항\s*(?:일정|시간|요일)|막차|마지막\s*(?:버스|셔틀)|터미널\s*(?:변경|이전))/i;
const rows=[];
for(const file of pages){
 const raw=fs.readFileSync(file,'utf8').replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,' ').replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi,' ');
 for(const m of raw.matchAll(/<(p|li|td|h[2-5])\b[^>]*>([\s\S]*?)<\/\1>/gi)){
  const plain=m[2].replace(/<[^>]*>/g,' ').replace(/&(?:nbsp|amp|rarr);/g,' ').replace(/\s+/g,' ').trim();
  if(plain.length<20||plain.length>700||!claims.test(plain))continue;
  const start=m.index,context=raw.slice(Math.max(0,start-1400),Math.min(raw.length,start+m[0].length+1400));
  const links=[...context.matchAll(/<a\b[^>]*href\s*=\s*["'](https?:\/\/[^"']+)["']/gi)].map(x=>x[1]).filter(x=>!/(?:^|\/)nipponferry\.com\//i.test(x)).slice(0,5);
  rows.push({file,claim:plain.slice(0,300),nearbyExternalLinks:links,needsHumanSourceVerification:true});
 }
}
rows.sort((a,b)=>a.file.localeCompare(b.file)||a.claim.localeCompare(b.claim));
fs.mkdirSync('audit-reports/v363',{recursive:true});
fs.writeFileSync('audit-reports/v363/operational-claim-source-review.json',JSON.stringify({pagesScanned:pages.length,claimsForReview:rows.length,withoutNearbyExternalLink:rows.filter(r=>!r.nearbyExternalLinks.length).length,disclaimer:'Proximity does not prove support, currency, accuracy, rights, or official status. Compare each claim against the actual operator notice before editing.',rows},null,2)+'\n');
console.log(JSON.stringify({pagesScanned:pages.length,claimsForReview:rows.length,withoutNearbyExternalLink:rows.filter(r=>!r.nearbyExternalLinks.length).length}));
