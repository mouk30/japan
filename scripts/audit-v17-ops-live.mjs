import { chromium } from 'playwright';
import { readFile,mkdir,writeFile } from 'node:fs/promises';
import path from 'node:path';

const src=JSON.parse(await readFile('scripts/v17-official-sailings.json','utf8'));
const ports=Object.entries(src.ports);
const output='audit-reports/v17/visual';await mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
const cases=[];
for(const [env,base] of [['build',process.env.LOCAL_BASE_URL||'http://127.0.0.1:8765'],['production',process.env.LIVE_BASE_URL||'https://www.nipponferry.com']])
for(const [viewport,width,height] of [['mobile',390,844],['desktop',1365,900]])
for(const [port,ref] of ports)for(const audience of ['family','couple','parents']){
 const slug=port+'-cruise-'+audience+'-guide';
 const url=base.replace(/\/$/,'')+'/things-to-do/'+slug+'/';
 const page=await browser.newPage({viewport:{width,height},locale:'ko-KR'});
 const errors=[];let result=null;let status=null;
 try{
   const response=await page.goto(url,{waitUntil:'domcontentloaded',timeout:26000});
   status=response?.status();if(!response?.ok())throw Error('HTTP '+status);
   const wrapper=page.locator('#nf-v17-ops');await wrapper.waitFor({timeout:9000});
   await page.waitForFunction(()=>{
     const sources=[...document.styleSheets].map(x=>x.href||'');
     return sources.some(x=>x.includes('companion-ops-v17.css')) &&
            sources.some(x=>x.includes('companion-card-standard.css'));
   },null,{timeout:12000});
   result=await page.evaluate(()=>{
     const panel=document.querySelector('#nf-v17-ops');
     const urls=[...panel.querySelectorAll('a')];
     const rows=[...panel.querySelectorAll('.nf-v17-calls >li')];
     const photos=[...document.querySelectorAll('#ct-topic-dashboard .ct-grid>.ct-card .ct-photo img')];
     return {
       source:urls[0]?.getAttribute('href'),
       notice:panel.querySelector('.nf-v17-safety')?.textContent.trim(),
       status:panel.querySelector('.nf-v17-status')?.textContent.trim(),
       checkDate:panel.querySelector('.nf-v17-label')?.textContent.trim(),
       rows:rows.map(r=>({date:r.dataset.sailingDay,text:r.textContent.trim()})),
       missingNotice:!!panel.querySelector('.nf-v17-unverified'),
       linkDisplay:urls.map(a=>getComputedStyle(a).display),
       cards:document.querySelectorAll('#ct-topic-dashboard .ct-grid>.ct-card').length,
       v16Routes:document.querySelectorAll('#ct-topic-dashboard .ct-grid>.ct-card .nf-v16-route').length,
       photoRatios:photos.map(img=>{const r=img.getBoundingClientRect();return r.width?+(r.height/r.width).toFixed(3):null;}),
       overflow:document.documentElement.scrollWidth>innerWidth+3
     }
   });
   if(result.source!==ref.scheduleSource)errors.push('OFFICIAL_URL_MISMATCH');
   if(!result.notice||!result.notice.includes('최종 승객 귀선'))errors.push('PASSENGER_TIME_WARNING_MISSING');
   if(!result.checkDate?.includes(src.as_of))errors.push('CHECK_DATE_MISSING');
   if(result.rows.length!==ref.calls.length)errors.push('CALL_ROW_COUNT');
   if(!ref.calls.length&&!result.missingNotice)errors.push('UNVERIFIED_STATUS_MISSING');
   if(ref.calls.length&&result.missingNotice)errors.push('VERIFIED_MISLABELED');
   for(let i=0;i<Math.min(ref.calls.length,result.rows.length);i++){
     const a=ref.calls[i],b=result.rows[i];
     if(a.date!==b.date||!b.text.includes(a.ship)||!b.text.includes(a.berth)||
       !b.text.includes(a.arrival)||!b.text.includes(a.departure))errors.push('OFFICIAL_SAILING_ROW_'+i);
   }
   if(result.linkDisplay.some(x=>x==='flex'||x==='grid'))errors.push('OFFICIAL_SOURCE_LINK_BUTTON');
   if(result.cards!==3||result.v16Routes!==3)errors.push('EXISTING_V16_CARD_REGRESSION');
   if(result.photoRatios.some(x=>x!==null&&Math.abs(x-.75)>.045))errors.push('PHOTO_RATIO_REGRESSION');
   if(result.overflow)errors.push('HORIZONTAL_OVERFLOW');
   if(env==='production'&&viewport==='mobile'&&['yokohama','hakata','nagasaki','hakodate','ishigaki'].includes(port)){
     await wrapper.screenshot({path:path.join(output,'production-mobile-'+slug+'.png'),animations:'disabled',timeout:12000});
   }
 }catch(e){errors.push('LOAD_OR_AUDIT_ERROR');result={error:String(e.message).slice(0,180)}}
 cases.push({env,viewport,port,audience,url,status,errors,result});
 console.log(env,viewport,slug,errors.length?'FAIL '+errors.join(','):'PASS');
 await page.close();
}
await browser.close();
const summary={ports:ports.length,guides:45,cases:cases.length,passed:cases.filter(x=>!x.errors.length).length,failed:cases.filter(x=>x.errors.length).length,
 failures:cases.filter(x=>x.errors.length).map(x=>({env:x.env,viewport:x.viewport,port:x.port,audience:x.audience,errors:x.errors,message:x.result?.error}))};
await writeFile(path.join(output,'summary.json'),JSON.stringify(summary,null,2));
await writeFile(path.join(output,'results.json'),JSON.stringify(cases,null,2));
await writeFile(path.join(output,'report.csv'),['environment,viewport,port,audience,status,issues',...cases.map(x=>[x.env,x.viewport,x.port,x.audience,x.errors.length?'FAIL':'PASS',x.errors.join(';')].map(t=>'"'+String(t).replaceAll('"','""')+'"').join(','))].join('\n')+'\n');
console.log('V17_AUDIT',JSON.stringify(summary));
if(summary.failed)process.exitCode=1;
