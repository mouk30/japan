import fs from 'node:fs';
const BASE='https://www.nipponferry.com';
const checks=[
 {path:'/',markers:['d61-home-region','/images/venues/v62-karato-market-real.webp','/images/venues/v62-izuhara-port-real.webp']},
 {path:'/things-to-do/shimonoseki-one-day/',markers:['v62-karato-market-real.webp','실제 현장 사진']},
 {path:'/things-to-do/tsushima-one-day/',markers:['v62-izuhara-port-real.webp','실제 현장 사진']}
];
const pics=['/images/venues/v62-karato-market-real.webp','/images/venues/v62-izuhara-port-real.webp'];
const out='audit-reports/v62/live-site-qa.json';
fs.mkdirSync('audit-reports/v62',{recursive:true});
const history=[];
let passed=false;
for(let retry=0;retry<13&&!passed;retry++){
 let pass=true;
 const check=[];
 for(const entry of checks){
  let status=0, missing=[],error='',finalURL='';
  try {
   const dest=BASE+entry.path+(entry.path.includes('?')?'&':'?')+'v62-review='+Date.now();
   const res=await fetch(dest,{headers:{'cache-control':'no-cache','user-agent':'NIPPONFERRY-Site-Release-QA/1.0'},signal:AbortSignal.timeout(19000)});
   status=res.status;finalURL=res.url;
   const body=await res.text();
   missing=entry.markers.filter(m=>!body.includes(m));
  }catch(e){error=String(e)}
  if(status!==200||missing.length||error)pass=false;
  check.push({path:entry.path,status,finalURL,missing,error});
 }
 if(pass)for(const pic of pics){
  let status=0,type='',bytes=0,error='';
  try{
   const res=await fetch(BASE+pic+'?v62-image-check='+Date.now(),{signal:AbortSignal.timeout(19000)});
   status=res.status;type=res.headers.get('content-type')||'';
   const buff=await res.arrayBuffer();bytes=buff.byteLength;
  }catch(e){error=String(e)}
  if(status!==200||!type.includes('image/')||bytes<25000||error)pass=false;
  check.push({path:pic,status,type,bytes,error});
 }
 history.push({attempt:retry+1,time:new Date().toISOString(),pass,checks:check});
 passed=pass;
 if(!pass&&retry<12)await new Promise(r=>setTimeout(r,20000));
}
const report={passed,tests:checks.length+pics.length,checks:history.at(-1)?.checks,attempts:history.length,
 comments:'Site URL checked from GitHub Actions runner (not a search-engine cached result).',
 history};
fs.writeFileSync(out,JSON.stringify(report,null,2));
console.log(JSON.stringify({passed,attempts:history.length,final:report.checks},null,2));
if(!passed)process.exitCode=1;
