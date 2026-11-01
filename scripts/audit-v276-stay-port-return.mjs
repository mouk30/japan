/**
 * V276: evidence-only audit of port, terminal, last transit and return-trip
 * statements on the 28 EXISTING /stay/ guides. No schedule is asserted.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
const BASE='c17fec39626600b9b83c7890d8a0857ea19d661e';
const root='site/stay';
const files=['site/stay/index.html',...fs.readdirSync(root,{withFileTypes:true})
 .filter(d=>d.isDirectory()&&fs.existsSync(path.join(root,d.name,'index.html')))
 .map(d=>'site/stay/'+d.name+'/index.html')].sort();
assert.equal(files.length,28,'V276 scope locked to 28 existing /stay/ pages');
const results=[];
const externalExclude=/^(?:willer-travel\.com|open\.kakao\.com|commons\.wikimedia\.org|creativecommons\.org)$/i;
for(const file of files){
 const html=fs.readFileSync(file,'utf8');
 assert.equal(html,execFileSync('git',['show',BASE+':'+file],{encoding:'utf8'}),
  'Audit-only V276 must not modify original stay HTML '+file);
 const main=html.match(/<main\b[^>]*>([\s\S]*?)<\/main>/i)?.[1]??'';
 assert.ok(main,'Missing main content '+file);
 const visible=main.replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi,' ')
  .replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,' ')
  .replace(/<[^>]*>/g,' ').replace(/&nbsp;/g,' ').replace(/\s+/g,' ').trim();
 const terms={
  portOrTerminal:/항구|항만|부두|터미널|접안|입항|출항/.test(visible),
  returnDay:/귀선|귀국일|마지막날|복귀/.test(visible),
  shuttle:/셔틀/.test(visible),
  lastTransit:/막차|막버스|마지막\s*(?:버스|열차|기차|차량|셔틀)|최종\s*(?:귀선|탑승|승선)/.test(visible)
 };
 const timeCandidates=[...visible.matchAll(/.{0,65}\b(?:[01]?\d|2[0-3]):[0-5]\d\b.{0,65}/g)].map(x=>x[0]);
 const distanceCandidates=[...visible.matchAll(/.{0,45}(?:도보|차량|택시|버스|열차)\s*(?:약\s*)?\d+\s*(?:분|시간).{0,45}/g)].map(x=>x[0]);
 const urls=[...main.matchAll(/\bhref=['"](https?:\/\/[^'"]+)['"]/gi)].map(x=>x[1]);
 const candidateSources=[...new Set(urls)].filter(url=>{
  try{return !externalExclude.test(new URL(url).hostname)}catch{return false}
 });
 const route='/' + file.replace(/^site\//,'').replace(/index\.html$/,'');
 assert.ok(html.includes('https://www.nipponferry.com'+route),'Canonical missing '+file);
 assert.doesNotMatch(html,/kids-stay\.com|kidsstay-v5\.vercel\.app/i,'KidsStay boundary '+file);
 const category=terms.lastTransit||timeCandidates.length||distanceCandidates.length?
  'MANUAL_OFFICIAL_SOURCE_VALIDATION_REQUIRED':
  'NO_SPECIFIC_LAST_TRANSIT_FACT_PUBLISHED';
 results.push({route,file,terms,timeCandidates,distanceCandidates,candidateSources,
  category,sourceVerified:false,portTerminalVerified:false,lastServiceVerified:false});
}
const summary={existingPages:28,withPortOrTerminalMention:results.filter(x=>x.terms.portOrTerminal).length,
 withReturnDayMention:results.filter(x=>x.terms.returnDay).length,
 withShuttleMention:results.filter(x=>x.terms.shuttle).length,
 withLastTransitMention:results.filter(x=>x.terms.lastTransit).length,
 withClockTimeCandidates:results.filter(x=>x.timeCandidates.length).length,
 withDistanceCandidates:results.filter(x=>x.distanceCandidates.length).length,
 independentlyVerifiedOfficialSchedules:0,htmlEdits:0,newArticles:0};
const report={stage:'V276',generatedAt:new Date().toISOString(),baselineMain:BASE,summary,pages:results,
 limitations:['Textual keyword and time patterns identify review candidates, not confirmed errors.',
 'No official carrier/port/transit operator timetable was independently fetched or verified.',
 'No exact last bus, return cutoff, dock or shuttle guarantee is inferred from generic guidance.',
 'Earlier V260–V275 Draft PRs remain unmerged; this audit reads unchanged main.',
 'Authenticated Vercel Preview is blocked by team/project 403; do not merge or deploy.']};
fs.writeFileSync('audit-reports/v276-stay-port-return-generated.json',JSON.stringify(report,null,2)+'\n');
console.log('V276 EVIDENCE AUDIT PASS '+JSON.stringify(summary));