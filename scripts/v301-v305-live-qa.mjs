import fs from 'node:fs';
const root='https://www.nipponferry.com';
const pages=['/','/japan/','/japan/tokyo/','/japan/tokyo/disney-dpa-app-purchase/','/japan-cruise/','/booking/japan-cruise/',
'/things-to-do/','/things-to-do/cruise-ports/','/things-to-do/travel-companions/','/things-to-do/naha-cruise-port-day-trip/',
'/things-to-do/aomori-cruise-family-guide/','/things-to-do/aizu-wakamatsu-tsurugajo/',
'/food/','/shopping/','/seasons/','/photo-spots/','/voucher/','/practical/','/couple/','/life/don-quijote-first-guide/','/okinawa/'];
const report={time:new Date().toISOString(),versions:'V301-V305',pages:pages.length,attempts:[],assets:[],passed:false};
async function inspect(p){
 let status=0,bytes=0,errors=[];
 try{
  const r=await fetch(root+p+'?headerQa='+Date.now(),{headers:{'Cache-Control':'no-cache','User-Agent':'NIPPONFERRY-V305-Header-Deployment-QA/1.0'},signal:AbortSignal.timeout(17500)});
  status=r.status;
  const h=await r.text();bytes=Buffer.byteLength(h,'utf8');
  if(status!==200)errors.push('HTTP '+status);
  if(!h.includes('data-nf301="v305"'))errors.push('unified header absent');
  if((h.match(/data-nf301="v305"/g)||[]).length!==1)errors.push('duplicate or missing unified header');
  if(!h.includes('v301-nav.css')||!h.includes('v301-nav.js'))errors.push('CSS or JS absent');
  if((h.match(/class="nf301-item"/g)||[]).length!==6)errors.push('main menu count incorrect');
  if((h.match(/class="nf301-mob-group"/g)||[]).length!==4)errors.push('mobile accordion count incorrect');
  if(!h.includes('href="/booking/japan-cruise/"'))errors.push('booking preparation CTA missing');
  if(!h.includes('href="/japan/tokyo/"'))errors.push('Tokyo destination missing');
  if(p==='/'&&(h.match(/class="nf305-shortcut(?: nf305-shortcut-first)?"/g)||[]).length!==6)errors.push('premium homepage six shortcuts missing');

  const canonical=h.match(/<link\b[^>]*rel=["']canonical["'][^>]*href=["']([^"']+)/i)?.[1];
  if(canonical!=='https://www.nipponferry.com'+p)errors.push('canonical mismatch '+canonical);
 }catch(e){errors.push(String(e).slice(0,200))}
 return {url:p,status,bytes,errors};
}
const pause=ms=>new Promise(r=>setTimeout(r,ms));
for(let attempt=1;attempt<=7;attempt++){
 const results=[];
 for(let i=0;i<pages.length;i+=8)results.push(...await Promise.all(pages.slice(i,i+8).map(inspect)));
 report.attempts.push({attempt,time:new Date().toISOString(),results});
 console.log('Live V301-V305 header '+attempt+': '+results.filter(x=>!x.errors.length).length+'/'+results.length);
 if(results.every(x=>!x.errors.length))break;
 if(attempt<7)await pause(14500);
}
for(const p of ['/v301-nav.css','/v301-nav.js']){
 let status=0,bytes=0,issue='';
 try{
  const r=await fetch(root+p+'?cache='+Date.now(),{signal:AbortSignal.timeout(15000)});
  status=r.status;const raw=await r.arrayBuffer();bytes=raw.byteLength;
  if(status!==200||bytes<1800)issue='public asset invalid';
  if(p.endsWith('.js')&&!new TextDecoder().decode(raw).includes('scheduleFlyClose'))issue='latest desktop pointer interaction not yet deployed';
 }catch(e){issue=String(e)}
 report.assets.push({url:p,status,bytes,issue});
}
const last=report.attempts.at(-1).results;
report.passed=last.every(x=>!x.errors.length)&&report.assets.every(x=>!x.issue);
report.checks=last;
fs.mkdirSync('audit-reports/v301-v305',{recursive:true});
fs.writeFileSync('audit-reports/v301-v305/live-production.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({passed:report.passed,rounds:report.attempts.length,pages:last.length,assets:report.assets,failures:last.filter(x=>x.errors.length)},null,2));
if(!report.passed)process.exitCode=1;
