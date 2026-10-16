import fs from 'node:fs';
const m=JSON.parse(fs.readFileSync('audit-reports/v81-v120/manifest.json','utf8'));
const root='https://www.nipponferry.com';
const pages=[{path:'/',type:'home'},{path:'/japan/',type:'directory'},{path:'/japan/tokyo/',type:'hub'},...m.articlesMeta.map(x=>({path:x.path,type:'detail',version:x.version}))];
const report={checkedAt:new Date().toISOString(),retries:0,articles:m.articles,publicPages:pages.length,checks:[],errors:[],assets:[],passed:false};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function inspect(p){
 const result={...p,status:0,issues:[],bytes:0};
 try{
  const response=await fetch(root+p.path+'?v120audit='+Date.now(),{headers:{'cache-control':'no-cache','user-agent':'NIPPONFERRY-v120-live-audit/1.0'},signal:AbortSignal.timeout(14000)});
  result.status=response.status;
  const html=await response.text();result.bytes=html.length;
  if(result.status!==200)result.issues.push('HTTP '+result.status);
  if(!html.includes('https://www.nipponferry.com'+p.path))result.issues.push('Canonical route missing');
  if((html.match(/<h1\b/g)||[]).length!==1)result.issues.push('H1 not unique');
  if(p.type==='hub'&&(html.match(/class="tky-card"/g)||[]).length!==40)result.issues.push('Tokyo specialist cards not 40');
  if(p.type==='home'&&!html.includes('class="v65-card v81-tokyo"'))result.issues.push('Tokyo not in popular city carousel');
  if(p.type==='directory'&&!html.includes('href="/japan/tokyo/"'))result.issues.push('Tokyo absent from Japan city hub');
  if(p.type==='detail'&&(!html.includes('id="official"')||!html.includes('id="plan"')||!html.includes('application/ld+json')))result.issues.push('Official links, route or schema missing');
  if(p.type==='detail'&&(html.includes('https://www.gotokyo.org/en/see-and-do/food-and-drink/index.html')||html.includes('https://www.shijou.metro.tokyo.lg.jp/english/')))result.issues.push('Historic 404 official link not repaired');
  if(p.path.includes('tokyo-toyosu-market-auction-guide')&&!html.includes('2026년 10월 24일'))result.issues.push('Toyosu official special-date notice missing');
 }catch(e){result.issues.push(String(e).slice(0,180))}
 return result;
}
for(let attempt=1;attempt<=7;attempt++){
 const all=[];
 for(let i=0;i<pages.length;i+=12)all.push(...await Promise.all(pages.slice(i,i+12).map(inspect)));
 report.retries=attempt;report.checks=all;
 const failures=all.filter(x=>x.issues.length);
 console.log('Tokyo V81–V120 public HTML check '+attempt+': '+(pages.length-failures.length)+'/'+pages.length);
 if(!failures.length)break;
 if(attempt<7)await sleep(13000);
}
for(const dest of ['/tokyo-guide.css','/images/venues/tokyo-city-night-real.webp','/sitemap.xml']){
 const row={path:dest,status:0,bytes:0,issues:[]};
 try{
  const response=await fetch(root+dest+'?audit='+Date.now(),{headers:{'cache-control':'no-cache'},signal:AbortSignal.timeout(16000)});
  row.status=response.status;row.bytes=(await response.arrayBuffer()).byteLength;
  if(row.status!==200||row.bytes<3000)row.issues.push('HTTP or asset bytes');
 }catch(e){row.issues.push(String(e))}
 report.assets.push(row);
}
report.errors=[...report.checks.flatMap(x=>x.issues.map(y=>x.path+': '+y)),...report.assets.flatMap(x=>x.issues.map(y=>x.path+': '+y))];
report.passed=report.errors.length===0;
fs.writeFileSync('audit-reports/v81-v120/live-production.json',JSON.stringify(report,null,2));
console.log(JSON.stringify({passed:report.passed,retries:report.retries,publicPages:report.publicPages,assets:report.assets,errors:report.errors.slice(0,16)},null,2));
if(!report.passed)process.exitCode=1;
