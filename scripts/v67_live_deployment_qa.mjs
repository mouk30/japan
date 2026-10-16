import fs from 'node:fs';
const base='https://www.nipponferry.com';
const slugs=[
'/japan/fukuoka-food/','/things-to-do/fukuoka-one-day/',
'/japan/shimonoseki-market/','/things-to-do/shimonoseki-one-day/',
'/things-to-do/tsushima-one-day/','/things-to-do/osaka-one-day/',
'/practical/fujiq-highland-guide/','/shopping/japan-tax-free-2026/',
'/life/japan-tax-free-2026/','/life/don-quijote-first-guide/',
'/life/don-quijote-tax-free/','/things-to-do/activity/',
'/things-to-do/food-experience/','/japan/tsushima-food/'
];
const output='audit-reports/v67/live-deploy.json';fs.mkdirSync('audit-reports/v67',{recursive:true});
const history=[];let passed=false;
for(let attempt=0;attempt<7&&!passed;attempt++){
 let good=true;const checks=[];
 for(const slug of slugs){
  let status=0,missing=[],error='',finalUrl='';
  try{
   const response=await fetch(base+slug+'?v67-source-audit='+Date.now(),{headers:{'cache-control':'no-cache','user-agent':'NIPPONFERRY-V67-Live-Quality-Audit/1.0'},signal:AbortSignal.timeout(17000)});
   status=response.status;finalUrl=response.url;
   const html=await response.text();
   missing=['id="v67-official-info"','v67-stamp','2026-10-16','canonical'].filter(x=>!html.includes(x));
   const official=(html.match(/class="v67-block"/g)||[]).length;
   if(official!==3)missing.push('3 approved information cards');
  }catch(ex){error=String(ex)}
  if(status!==200||missing.length||error)good=false;
  checks.push({slug,status,missing,error,finalUrl});
 }
 history.push({attempt:attempt+1,checkedAt:new Date().toISOString(),passed:good,checks});
 passed=good;
 if(!good&&attempt<6)await new Promise(r=>setTimeout(r,12000));
}
const report={checkedAt:new Date().toISOString(),passed,pages:slugs.length,attempts:history.length,finalChecks:history.at(-1).checks,history};
fs.writeFileSync(output,JSON.stringify(report,null,2));
console.log(JSON.stringify({passed,attempts:history.length,failed:report.finalChecks.filter(c=>c.status!==200||c.error||c.missing.length)},null,2));
if(!passed)process.exitCode=1;
