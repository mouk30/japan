#!/usr/bin/env node
// V359: review external booking CTAs that may imply completed booking or live inventory.
import fs from 'node:fs';
import path from 'node:path';
const root='site',files=[],rows=[];
function walk(d){for(const e of fs.readdirSync(d,{withFileTypes:true})){const p=path.join(d,e.name);if(e.isDirectory())walk(p);else if(e.isFile()&&p.endsWith('.html'))files.push(p)}}
walk(root);
for(const file of files){
 const html=fs.readFileSync(file,'utf8');
 for(const m of html.matchAll(/<a\b([^>]*)>([\s\S]*?)<\/a>/gi)){
  const href=(m[1].match(/\bhref=["']([^"']+)["']/i)||[])[1]||'';
  const label=m[2].replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim();
  if(!/예약|발권|좌석|운항|수속/.test(label))continue;
  if(!href)continue;
  const external=/^https?:\/\//.test(href)&&!href.includes('nipponferry.com');
  const liveClaim=/실시간\s*(?:예약|좌석|잔여)|예약\s*확정|즉시\s*발권/.test(label);
  const generic=/^예약(?:하기|하기\s*→|\s*→)?$/.test(label);
  if(!external&&!liveClaim&&!generic)continue;
  rows.push({page:'/'+path.relative(root,file).replaceAll('\\','/').replace(/index\.html$/,''),label,href,external,liveClaim,generic,review:'Verify actual destination and distinguish operator information, check-in and real booking; do not infer inventory from CTA text.'});
 }
}
fs.mkdirSync('audit-reports/v359',{recursive:true});
fs.writeFileSync('audit-reports/v359/booking-cta-review.json',JSON.stringify({pagesScanned:files.length,candidates:rows.length,rows},null,2)+'\n');
console.log(JSON.stringify({pagesScanned:files.length,ctaReviewCandidates:rows.length,liveClaims:rows.filter(x=>x.liveClaim).length}));
