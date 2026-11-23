#!/usr/bin/env node
// V364 read-only review of date-sensitive ferry price claims.
// A match is a review candidate, never proof that a fare is wrong.
import fs from 'node:fs';
import path from 'node:path';
const files=[];
function walk(dir){if(!fs.existsSync(dir))return;for(const item of fs.readdirSync(dir,{withFileTypes:true})){const p=path.join(dir,item.name);if(item.isDirectory())walk(p);else if(item.isFile()&&p.endsWith('.html'))files.push(p)}}
walk('site');
const fare=/(운임|요금|유류\s*할증료|연료\s*할증료|fuel\s*surcharge|fare)/i;
const amount=/(?:[₩¥￥]\s*[\d,]+|[\d,]+\s*(?:원|엔|JPY|KRW))/i;
const date=/(?:20\d{2}\s*[년./-]\s*\d{1,2}|20\d{2}년|\d{1,2}월\s*\d{1,2}일)/;
const rows=[];
for(const file of files){
 const html=fs.readFileSync(file,'utf8').replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,' ').replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi,' ');
 for(const m of html.matchAll(/<(p|li|td|h[1-6])\b[^>]*>([\s\S]*?)<\/\1>/gi)){
  const plain=m[2].replace(/<[^>]*>/g,' ').replace(/&(?:nbsp|amp|yen);/gi,' ').replace(/\s+/g,' ').trim();
  if(plain.length<12||plain.length>800||!fare.test(plain)||!(amount.test(plain)||date.test(plain)))continue;
  rows.push({file,claim:plain.slice(0,350),hasExplicitDate:date.test(plain),hasAmount:amount.test(plain),reviewOnly:true});
 }
}
rows.sort((a,b)=>a.file.localeCompare(b.file)||a.claim.localeCompare(b.claim));
const output='audit-reports/v364/dated-fare-review.json';
fs.mkdirSync(path.dirname(output),{recursive:true});
fs.writeFileSync(output,JSON.stringify({pagesScanned:files.length,reviewCandidates:rows.length,disclaimer:'Do not change a fare or fuel surcharge without a current official operator source for the exact route, date, and passenger category. A date or amount match is not an error.',rows},null,2)+'\n');
console.log(JSON.stringify({pagesScanned:files.length,reviewCandidates:rows.length}));
