import fs from 'node:fs';
const paths=[
'/life/japan-cash-how-much/','/practical/japan-atm-cash-guide/','/life/japan-card-payment-error/',
'/practical/japan-ic-card-guide/','/japan/fukuoka-transport/','/practical/japan-airport-bus-guide/',
'/practical/japan-esim-setup/','/practical/japan-esim-vs-sim-wifi/','/practical/japan-data-usage/',
'/life/japan-convenience-shopping-list/','/life/japan-convenience-atm/','/life/japan-supermarket-discount-time/',
'/shopping/japan-souvenir-buying-guide/','/shopping/japan-food-bring-korea/','/shopping/korea-customs-return/',
'/couple/kyoto-romantic-date/','/couple/japan-onsen-couple-trip/','/japan/fukuoka-photo/',
'/stay/hakone/','/season/japan-summer-festival-guide/'
];
const base='https://www.nipponferry.com';
const output='audit-reports/v68/production.json';
fs.mkdirSync('audit-reports/v68',{recursive:true});
const history=[],limit=7;
let passed=false;
for(let i=0;i<limit&&!passed;i++){
 const batch=await Promise.all(paths.map(async p=>{
   let status=0,error='',missing=[],links=0;
   try{
     const u=base+p+'?v68-check='+Date.now();
     const res=await fetch(u,{headers:{'cache-control':'no-cache','user-agent':'NIPPONFERRY-V68-Production-QA/1.0'},signal:AbortSignal.timeout(18000)});
     status=res.status;
     const html=await res.text();
     const mandatory=['id="v68-precision"','class="v68-facts"','v68-foot','canonical'];
     missing=mandatory.filter(v=>!html.includes(v));
     links=(html.match(/class="v68-fact"/g)||[]).length;
     if(links!==3)missing.push('Expected three cards: '+links);
     if(!html.includes('https://www.nipponferry.com'+p))missing.push('Canonical URL mismatch');
   }catch(ex){error=String(ex)}
   return {page:p,status,error,missing,sourceCards:links};
 }));
 const ok=batch.every(x=>x.status===200&&!x.error&&!x.missing.length);
 history.push({attempt:i+1,checkedAt:new Date().toISOString(),passed:ok,results:batch});
 passed=ok;
 if(!ok&&i<limit-1)await new Promise(resolve=>setTimeout(resolve,12000));
}
const report={checkedAt:new Date().toISOString(),passed,expected:paths.length,attempts:history.length,checks:history.at(-1).results,history};
fs.writeFileSync(output,JSON.stringify(report,null,2));
console.log(JSON.stringify({passed,tries:report.attempts,pages:report.expected,failures:report.checks.filter(x=>x.status!==200||x.error||x.missing.length)},null,2));
if(!passed)process.exitCode=1;
