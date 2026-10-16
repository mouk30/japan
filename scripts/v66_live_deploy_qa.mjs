import fs from 'node:fs';
const base='https://www.nipponferry.com';
const urls=[
 {uri:'/',contains:['id="v63-theme-title"','id="v64-heading"','id="v65-title"','href="/booking/japan-cruise/"','property="og:image"','type="application/ld+json"']},
 {uri:'/japan/fukuoka/',contains:['rel="canonical"']},
 {uri:'/things-to-do/fukuoka-one-day/',contains:['rel="canonical"']},
 {uri:'/life/japan-cash-how-much/',contains:['rel="canonical"']},
 {uri:'/life/don-quijote-first-guide/',contains:['rel="canonical"']},
 {uri:'/season/japan-summer-festival-guide/',contains:['rel="canonical"']},
 {uri:'/things-to-do/naha-cruise-port-day-trip/',contains:['rel="canonical"']},
 {uri:'/booking/japan-cruise/',contains:['rel="canonical"']},
 {uri:'/images/venues/naha-shureimon.webp',image:true},
 {uri:'/images/venues/hakodate-goryokaku-tower.webp',image:true},
 {uri:'/images/culture-verified/yatai-japanese-food-stalls.webp',image:true},
];
const report={createdAt:new Date().toISOString(),base,attempts:[],passed:false};
const out='audit-reports/v66/live-deploy.json';
fs.mkdirSync('audit-reports/v66',{recursive:true});
for(let attempt=0;attempt<13&&!report.passed;attempt++){
 let ok=true;
 const checks=[];
 for(const u of urls){
  let status=0,missing=[],type='',bytes=0,error='',target='';
  try{
   target=base+u.uri+(u.uri.includes('?')?'&':'?')+'v66check='+Date.now();
   const res=await fetch(target,{headers:{'cache-control':'no-cache','user-agent':'NIPPONFERRY-Production-V66-QA/1.0'},signal:AbortSignal.timeout(18000)});
   status=res.status;type=res.headers.get('content-type')||'';
   if(u.image){const buf=await res.arrayBuffer();bytes=buf.byteLength;if(!type.includes('image/')||bytes<20000)ok=false;}
   else {const page=await res.text();missing=(u.contains||[]).filter(m=>!page.includes(m));}
  }catch(e){error=String(e)}
  if(status!==200||missing.length||error)ok=false;
  checks.push({uri:u.uri,status,missing,type:u.image?type:undefined,bytes:u.image?bytes:undefined,error});
 }
 report.attempts.push({time:new Date().toISOString(),checks,passed:ok});
 report.passed=ok;
 if(!ok&&attempt<12)await new Promise(done=>setTimeout(done,20000));
}
report.totalChecks=urls.length;
report.finalChecks=report.attempts.at(-1).checks;
fs.writeFileSync(out,JSON.stringify(report,null,2));
console.log(JSON.stringify({passed:report.passed,attempts:report.attempts.length,checks:report.finalChecks},null,2));
if(!report.passed)process.exitCode=1;
