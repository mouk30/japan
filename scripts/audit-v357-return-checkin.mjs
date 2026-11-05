#!/usr/bin/env node
// V357: identify return/check-in guides missing clearly labeled operator evidence.
import fs from 'node:fs';
import path from 'node:path';
const root='site', pages=[], all=[];
function walk(d){for(const e of fs.readdirSync(d,{withFileTypes:true})){const p=path.join(d,e.name);if(e.isDirectory())walk(p);else if(e.isFile()&&e.name==='index.html')all.push(p)}}
walk(root);
const strip=s=>s.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,' ').replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi,' ').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ');
for(const f of all){
 if(!/guide|booking|ferry|cruise/.test(f))continue;
 const html=fs.readFileSync(f,'utf8'),text=strip(html);
 if(!/귀국|귀선|승선\s*수속|체크인|출항|터미널/.test(text))continue;
 const official=[...html.matchAll(/href=["'](https?:\/\/[^"']+)["']/gi)].map(m=>m[1]).filter(u=>!u.includes('nipponferry.com'));
 const evidence={checkin:/수속\s*(?:마감|시간)|체크인\s*(?:마감|시간)/.test(text),departurePort:/출항\s*(?:항|터미널)|출발\s*(?:항|터미널)/.test(text),lastTransport:/막차|마지막\s*(?:버스|열차|차량)|최종\s*(?:버스|열차)/.test(text),officialLinks:official.length};
 pages.push({page:'/'+path.relative(root,f).replaceAll('\\','/').replace(/index\.html$/,''),...evidence,review:'Absence of these terms is a review hint only; confirm route, timetable and check-in deadlines against operator originals.'});
}
fs.mkdirSync('audit-reports/v357',{recursive:true});
fs.writeFileSync('audit-reports/v357/return-checkin-queue.json',JSON.stringify({pagesScanned:all.length,candidates:pages.length,rows:pages},null,2)+'\n');
console.log(JSON.stringify({pagesScanned:all.length,candidates:pages.length,missingLastTransportMentions:pages.filter(x=>!x.lastTransport).length}));
