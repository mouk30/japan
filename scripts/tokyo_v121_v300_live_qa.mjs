import fs from 'node:fs';
const current=JSON.parse(fs.readFileSync('audit-reports/v121-v300/editorial-manifest.json','utf8'));
const prior=JSON.parse(fs.readFileSync('audit-reports/v81-v120/manifest.json','utf8'));
const root='https://www.nipponferry.com';
const pages=[{slug:'home',url:'/',type:'home'}, {slug:'japan',url:'/japan/',type:'japan'}, {slug:'tokyo-hub',url:'/japan/tokyo/',type:'hub'},
...prior.articlesMeta.map(x=>({slug:x.path.split('/').filter(Boolean).at(-1),url:x.path,type:'existing'})),
...current.topics.map(t=>({slug:t.slug,url:t.path,type:'new',source:t.source}))];
if(pages.length!==223)throw Error('Expected hub, home, region, 40 existing and 180 new: '+pages.length);
const out='audit-reports/v121-v300/live-production.json',log=[];
const sleep=ms=>new Promise(res=>setTimeout(res,ms));
async function check(t){
 let status=0,size=0,issues=[];
 try{
  const r=await fetch(root+t.url+'?tokyoV300live='+Date.now(),{headers:{'Cache-Control':'no-cache','User-Agent':'NIPPONFERRY-v300-Public-Page-QA/1.0'},signal:AbortSignal.timeout(17000)});
  status=r.status;
  const h=await r.text();size=Buffer.byteLength(h,'utf8');
  if(status!==200)issues.push('HTTP '+status);
  if(!h.includes('https://www.nipponferry.com'+t.url))issues.push('canonical');
  if((h.match(/<h1\b/g)||[]).length!==1)issues.push('H1');
  if(t.type==='hub'){
   if((h.match(/class="tky-card"/g)||[]).length!==220)issues.push('220 cards missing');
   if((h.match(/class="tky-exp-group"/g)||[]).length!==9)issues.push('nine cohorts missing');
  }
  if(t.type==='new'){
   if(!h.includes(t.source))issues.push('official link');
   if(!h.includes('id="official"')||!h.includes('id="route"')||!h.includes('id="terms"'))issues.push('missing content sections');
  }
  if(t.type==='home'&&(!h.includes('class="v65-card v81-tokyo"')||!h.includes('220')))issues.push('updated Tokyo popular city missing');
  if(t.type==='japan'&&!h.includes('/japan/tokyo/'))issues.push('Tokyo region missing');
 }catch(e){issues.push(String(e).slice(0,170))}
 return {slug:t.slug,type:t.type,url:t.url,status,size,issues};
}
for(let round=1;round<=8;round++){
 const results=[];
 for(let i=0;i<pages.length;i+=14)results.push(...await Promise.all(pages.slice(i,i+14).map(check)));
 const bad=results.filter(x=>x.issues.length);
 log.push({round,at:new Date().toISOString(),failures:bad.length,results});
 console.log('Tokyo 223 published-page audit round '+round+': '+(pages.length-bad.length)+'/'+pages.length);
 if(!bad.length)break;
 if(round<8)await sleep(13000);
}
const checks=log.at(-1).results,assets=[];
for(const url of ['/tokyo-guide.css','/images/venues/tokyo-city-night-real.webp','/sitemap.xml']){
 let status=0,bytes=0,issue='';
 try{const r=await fetch(root+url+'?tokyoAsset='+Date.now(),{signal:AbortSignal.timeout(15000)});status=r.status;bytes=(await r.arrayBuffer()).byteLength;if(status!==200||bytes<3000)issue='invalid public asset'}catch(e){issue=String(e)}
 assets.push({url,status,bytes,issue});
}
const perBatch={};
for(let a=121;a<=300;a+=20){
 const subset=checks.filter(x=>x.type==='new'&&current.topics.some(t=>t.slug===x.slug&&t.version>=a&&t.version<a+20));
 perBatch['V'+a+'-V'+(a+19)]={pages:subset.length,ok:subset.filter(x=>!x.issues.length).length};
}
const report={time:new Date().toISOString(),pages:pages.length,rounds:log.length,perBatch,checks,assets,passed:checks.every(x=>!x.issues.length)&&assets.every(x=>!x.issue),history:log};
fs.writeFileSync(out,JSON.stringify(report,null,2));
console.log(JSON.stringify({passed:report.passed,rounds:report.rounds,pages:report.pages,perBatch,assets,failures:checks.filter(x=>x.issues.length).slice(0,25)},null,2));
if(!report.passed)process.exitCode=1;
