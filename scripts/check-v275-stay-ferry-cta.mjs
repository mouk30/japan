/**
 * V275: Only ferry booking CTA wording may change on 28 EXISTING /stay/ pages.
 * Baseline Git byte comparison prevents accidental image, SEO, URL or booking edits.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
const BASE='c17fec39626600b9b83c7890d8a0857ea19d661e';
const dir='site/stay';
const files=['site/stay/index.html',...fs.readdirSync(dir,{withFileTypes:true})
 .filter(d=>d.isDirectory()&&fs.existsSync(path.join(dir,d.name,'index.html')))
 .map(d=>'site/stay/'+d.name+'/index.html')].sort();
assert.equal(files.length,28,'V275 must touch only 28 existing stay guides');
const newText='크루즈·페리 예약 준비 가이드 →',oldText='예약 준비 가이드 →';
const pages=[];
for(const file of files){
 const html=fs.readFileSync(file,'utf8');
 const before=execFileSync('git',['show',BASE+':'+file],{encoding:'utf8'});
 const red=/<a class='red' href='(\/booking\/[^']*)'>크루즈·페리 예약 준비 가이드 →<\/a>/g;
 const matches=[...html.matchAll(red)];
 assert.equal(matches.length,1,'Exactly one V275 CTA per page: '+file);
 const restored=html.replace(red,(_,href)=>"<a class='red' href='"+href+"'>"+oldText+"</a>");
 assert.equal(restored,before,'Only CTA wording is permitted: '+file);
 const href=matches[0][1];
 assert.ok(fs.existsSync(path.posix.join('site',href,'index.html')),'Missing booking guide '+href);
 assert.ok(html.includes("숙소·객실 예약이 아닌 일본 국내 페리 항로 조회"),'Ferry/lodging disclosure missing');
 assert.ok(html.includes("href='https://willer-travel.com/ko/ferry/'"),'Ferry lookup link altered');
 assert.ok(html.includes("aria-label='WILLER TRAVEL에서 일본 국내 페리 항로와 요금 조회 (새 창)'"),'Ferry lookup accessible label missing');
 assert.doesNotMatch(html,/kids-stay\.com|kidsstay-v5\.vercel\.app/i,'KidsStay boundary');
 assert.ok(!html.includes('>예약 준비 가이드 →</a>'),'Old ambiguous label remains');
 const canonical='https://www.nipponferry.com/'+file.replace(/^site\//,'').replace(/index\.html$/,'');
 assert.ok(html.includes(canonical),'Canonical missing '+file);
 pages.push({file,href,changedCTA:1,baselineByteEquivalentAfterReversal:true});
}
const sitemap=fs.readFileSync('site/sitemap.xml','utf8');
assert.equal([...sitemap.matchAll(/<loc>https:\/\/www\.nipponferry\.com\/stay\/[^<]*<\/loc>/g)].length,28);
const result={stage:'V275',generatedAt:new Date().toISOString(),baselineMain:BASE,
 summary:{existingPages:28,clarifiedFerryGuideCTAs:28,bookingHrefChanges:0,otherHTMLChanges:0,newArticles:0},
 pages,limitations:['Local repository check only, not live booking or current ferry availability.',
 'This change does not validate lodging or photo permissions.',
 'Authenticated Vercel Preview remains a separate required merge gate.']};
fs.writeFileSync('audit-reports/v275-stay-cta-generated.json',JSON.stringify(result,null,2)+'\n');
console.log('V275 STATIC PASS '+JSON.stringify(result.summary));