import fs from 'node:fs';
const slugs=['hiroshima','takamatsu','kumamoto','maizuru','kure','fushiki-toyama','tottori','karatsu','miyazaki','atami','nagoya','wakayama-shimotsu','yakushima-miyanoura','akita','iwakuni','amami-naze','goto-fukue','tomakomai','tokushima-komatsushima','kumamoto-misumi'];
const root='https://www.nipponferry.com/things-to-do/';
const save='audit-reports/v70/live-production.json';
fs.mkdirSync('audit-reports/v70',{recursive:true});
const rounds=[];
let complete=false;
for(let round=0;round<12&&!complete;round++){
 const results=await Promise.all(slugs.map(async slug=>{
  let status=0,errors=[],size=0,url='';
  try{
   url=root+slug+'-cruise-port-day-trip/?v70-live='+Date.now();
   const response=await fetch(url,{headers:{'Cache-Control':'no-cache','User-Agent':'NIPPONFERRY-V70-Live-Public-QA'},signal:AbortSignal.timeout(16000)});
   status=response.status;
   const html=await response.text();size=html.length;
   for(const marker of ['id="v70-port-official"','class="v70-columns"','class="v70-safe"','v70-disclosure','canonical',root+slug+'-cruise-port-day-trip/'])
    if(!html.includes(marker))errors.push('Missing '+marker);
   const cards=(html.match(/class="v70-panel"/g)||[]).length;
   if(cards!==3)errors.push('Expected 3 official detail cards, got '+cards);
   if(!html.includes('style="width:38px;height:38px;'))errors.push('Missing production mascot width guard');
   if(slug==='akita'&&!html.includes('www.selion-akita.com'))errors.push('Stale Akita official visitor link');
   if(slug==='kure'&&!html.includes('2026년 4월 23일'))errors.push('Stale Kure museum opening notice');
  }catch(e){errors.push(String(e).slice(0,220))}
  return {slug,status,errors,size};
 }));
 complete=results.every(x=>x.status===200&&x.errors.length===0);
 rounds.push({round:round+1,checkedAt:new Date().toISOString(),passed:complete,results});
 if(!complete&&round<11)await new Promise(resolve=>setTimeout(resolve,12000));
}
const report={checkedAt:new Date().toISOString(),passed:complete,articles:slugs.length,rounds:rounds.length,checks:rounds.at(-1).results,history:rounds};
fs.writeFileSync(save,JSON.stringify(report,null,2));
console.log(JSON.stringify({passed:complete,articles:slugs.length,attempts:rounds.length,failures:report.checks.filter(x=>x.status!==200||x.errors.length)},null,2));
if(!complete)process.exitCode=1;
