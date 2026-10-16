import fs from 'node:fs';
const dir='audit-reports/v71-v80',manifest=JSON.parse(fs.readFileSync(dir+'/manifest.json','utf8'));
const paths=manifest.pages.map(x=>({version:'V'+x.version,slug:x.slug,href:'https://www.nipponferry.com'+x.relativePath}));
const batches=Object.fromEntries(Object.keys(manifest.cohorts).map(x=>[x,{pass:0,fail:0}]));
const history=[],rounds=7;
function chunks(arr,n){return Array.from({length:Math.ceil(arr.length/n)},(_,i)=>arr.slice(i*n,(i+1)*n))}
async function inspect(x){
 const url=x.href+'?quality-release-check='+Date.now();
 let status=0,bytes=0,issues=[],finalURL='';
 try{
  const res=await fetch(url,{headers:{'Cache-Control':'no-cache','User-Agent':'NIPPONFERRY-V71-V80-Release-QA/1.0'},signal:AbortSignal.timeout(17000)});
  status=res.status;finalURL=res.url;
  const html=await res.text();bytes=html.length;
  for(const text of ['id="v'+x.version.slice(1)+'-verification"','class="nf-q80-grid"','class="nf-q80-check"','/v71-v80-quality.css',x.href])
   if(!html.includes(text))issues.push('Missing '+text);
  const cards=(html.match(/class="nf-q80-card"/g)||[]).length;
  if(cards!==3)issues.push('Source cards count '+cards);
  if(!/rel=["']canonical["']/.test(html))issues.push('No canonical');
  if((html.match(/<h1\b/g)||[]).length!==1)issues.push('Invalid H1');
  if(['okinawa-shuri-castle','okinawa-shuri-castle-heritage','okinawa-churaumi-aquarium','okinawa-whale-shark-aquarium'].includes(x.slug)){
    if(!html.includes('class="nf-q80-dated"'))issues.push('Missing dated facility operating notice');
    if(x.slug.includes('shuri')&&(!html.includes('2026년')||!html.includes('11월 23일')))issues.push('Missing Shuri year or opening date');
    if(x.slug.includes('aquarium')&&!html.includes('17:30'))issues.push('Missing aquarium last admission');
  }
  if(x.slug==='aomori-port-nebuta-day-trip'&&html.includes('0420_01_kuruzu.pdf'))issues.push('Stale broken official PDF reference');
 }catch(e){issues.push(String(e).slice(0,160))}
 return {...x,status,bytes,issues,finalURL};
}
for(let i=0;i<rounds;i++){
 const results=[];
 for(const c of chunks(paths,15)){
  const block=await Promise.all(c.map(inspect));
  results.push(...block);
 }
 const failures=results.filter(x=>x.status!==200||x.issues.length);
 history.push({round:i+1,at:new Date().toISOString(),failures:failures.length,results});
 console.log('V71-V80 live attempt '+(i+1)+': '+(200-failures.length)+'/200');
 if(!failures.length)break;
 if(i<rounds-1)await new Promise(done=>setTimeout(done,17000));
}
const result=history.at(-1);
for(const x of result.results){
 const s=batches[x.version];
 if(x.status===200&&!x.issues.length)s.pass++;else s.fail++;
}
let css={status:0,type:'',bytes:0,error:''};
try{
 const r=await fetch('https://www.nipponferry.com/v71-v80-quality.css?audit='+Date.now(),{signal:AbortSignal.timeout(16000)});
 css.status=r.status;css.type=r.headers.get('content-type')||'';
 css.bytes=(await r.text()).length;
}catch(e){css.error=String(e)}
const report={checkedAt:new Date().toISOString(),total:paths.length,attempts:history.length,cohorts:batches,css,passed:result.failures===0&&css.status===200&&css.bytes>1000,checks:result.results,history};
fs.writeFileSync(dir+'/live-production.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({passed:report.passed,attempts:report.attempts,perVersion:batches,css,failed:report.checks.filter(x=>x.status!==200||x.issues.length).slice(0,25)},null,2));
if(!report.passed)process.exitCode=1;
