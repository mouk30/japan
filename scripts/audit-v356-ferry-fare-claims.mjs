#!/usr/bin/env node
// V356: read-only review queue for time-sensitive ferry fare and surcharge claims.
// This script never decides current prices; compare each match with dated operator sources.
import fs from 'node:fs';
import path from 'node:path';
const root='site', matches=[];
const files=[];
function walk(d){for(const e of fs.readdirSync(d,{withFileTypes:true})){const p=path.join(d,e.name);if(e.isDirectory())walk(p);else if(e.isFile()&&e.name.endsWith('.html'))files.push(p)}}
walk(root);
const fare=/(?:유류할증료|유류\s*할증|운임|요금|편도|왕복|터미널\s*(?:이용료|시설이용료)|국제관광여객세)/;
const amounts=/(?:[\d,]{3,}\s*(?:원|엔|JPY|KRW)|(?:₩|¥)\s*[\d,]{3,})/;
const strip=s=>s.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,' ').replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi,' ').replace(/<[^>]+>/g,' ').replace(/&nbsp;/g,' ').replace(/\s+/g,' ').trim();
for(const f of files){
 if(!/ferry|booking|cruise|guide/.test(f))continue;
 const text=strip(fs.readFileSync(f,'utf8'));
 const sentences=text.split(/(?<=[.!?。])\s+|(?<=다\.)/);
 for(const sentence of sentences){
  if(!fare.test(sentence)||!amounts.test(sentence))continue;
  const snippet=sentence.slice(0,350);
  matches.push({page:'/'+path.relative(root,f).replaceAll('\\','/').replace(/index\.html$/,''),snippet,review:'Verify current fare, date, currency, fuel surcharge and mandatory extras against the operator; do not auto-update.'});
 }
}
fs.mkdirSync('audit-reports/v356',{recursive:true});
fs.writeFileSync('audit-reports/v356/fare-claims.json',JSON.stringify({filesScanned:files.length,candidates:matches.length,rows:matches},null,2)+'\n');
console.log(JSON.stringify({filesScanned:files.length,fareClaimsToReview:matches.length}));
