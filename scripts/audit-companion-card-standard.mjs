import { chromium } from 'playwright';
import { readdir,mkdir,writeFile } from 'node:fs/promises';
import path from 'node:path';
const baseLocal=(process.env.LOCAL_BASE_URL||'http://127.0.0.1:8765').replace(/\/$/,'');
const baseLive=(process.env.LIVE_BASE_URL||'https://www.nipponferry.com').replace(/\/$/,'');
const slugs=(await readdir('site/things-to-do',{withFileTypes:true})).filter(x=>x.isDirectory()&&/-cruise-(family|couple)-guide$/.test(x.name)).map(x=>x.name).sort();
const dir='audit-reports/card-standard-v10';await mkdir(dir,{recursive:true});
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
const results=[];
for(const env of [{name:'local-build',base:baseLocal},{name:'production',base:baseLive}]){
 for(const size of [{label:'mobile',width:390,height:844},{label:'tablet',width:844,height:1120},{label:'desktop',width:1365,height:900}]){
  for(const slug of slugs){
   const page=await browser.newPage({viewport:{width:size.width,height:size.height},locale:'ko-KR',deviceScaleFactor:1});
   const uri=env.base+'/things-to-do/'+slug+'/';
   const issues=[];let metrics=null;let http=null;
   try{
    const response=await page.goto(uri,{waitUntil:'domcontentloaded',timeout:22000});http=response?.status();
    if(!response?.ok())throw Error('HTTP '+http);
    for(const img of await page.locator('#ct-topic-dashboard .ct-photo img, #ct-experience-booking .act-option figure img').all()){
      await img.scrollIntoViewIfNeeded({timeout:6000});
      await img.evaluate(async el=>{try{await el.decode()}catch{}});
    }
    metrics=await page.evaluate(()=>{
     const select=s=>[...document.querySelectorAll(s)];
     const imgs=select('#ct-topic-dashboard .ct-card .ct-photo img, #ct-experience-booking .act-option figure img');
     const credits=select('#ct-topic-dashboard .ct-card figcaption a, #ct-experience-booking .act-option figcaption a');
     const act=select('#ct-experience-booking .act-options > .act-option');
     const top=select('#ct-topic-dashboard .ct-grid > .ct-card');
     const ratio=el=>{const b=el.getBoundingClientRect();return b.width>0?+(b.height/b.width).toFixed(3):null};
     return {
       standardCssLoaded:select('link[href*="companion-card-standard.css"]').length===1,
       cssFetchReadable:!![...document.styleSheets].find(sheet=>sheet.href?.includes('companion-card-standard.css')&&!sheet.disabled),
       cardCount:top.length,
       images:imgs.map(x=>({src:x.getAttribute('src'),loaded:x.complete&&x.naturalWidth>0,ratio:ratio(x),naturalWidth:x.naturalWidth})),
       credits:credits.map(a=>{const s=getComputedStyle(a);return {text:a.textContent.trim().slice(0,45),display:s.display,background:s.backgroundColor,marginTop:s.marginTop,paddingTop:s.paddingTop}}),
       experience:act.map(x=>({height:Math.round(x.getBoundingClientRect().height),minHeight:getComputedStyle(x).minHeight})),
       experienceGridAlign:document.querySelector('#ct-experience-booking .act-options') ? getComputedStyle(document.querySelector('#ct-experience-booking .act-options')).alignItems : null,
       topicGridAlign:getComputedStyle(document.querySelector('#ct-topic-dashboard .ct-grid')).alignItems,
       overflow:document.documentElement.scrollWidth>innerWidth+3,
     }
    });
    if(!metrics.standardCssLoaded||!metrics.cssFetchReadable)issues.push('MISSING_STANDARD_CSS');
    if(metrics.cardCount!==3)issues.push('TOP3_COUNT');
    if(metrics.images.length<3)issues.push('MISSING_TOP3_PHOTO');
    for(const [i,img] of metrics.images.entries()){
      if(!img.loaded)issues.push('BROKEN_IMAGE_'+(i+1));
      if(img.ratio===null||Math.abs(img.ratio-.75)>.04)issues.push('BAD_THUMBNAIL_RATIO_'+(i+1)+'_'+img.ratio);
    }
    for(const [i,a] of metrics.credits.entries()){
      if(a.display!=='inline'||a.background!=='rgba(0, 0, 0, 0)'||a.marginTop!=='0px'||a.paddingTop!=='0px')issues.push('CREDIT_AS_BUTTON_'+(i+1));
    }
    if((metrics.experienceGridAlign!==null&&metrics.experienceGridAlign!=='start')||metrics.topicGridAlign!=='start')issues.push('GRID_STRETCH');
    if(metrics.experience.some(a=>a.minHeight!=='0px'))issues.push('FORCED_CARD_MINHEIGHT');
    if(metrics.overflow)issues.push('HORIZONTAL_OVERFLOW');
    if(slug.startsWith('hakodate-')){
       await page.locator('#ct-experience-booking .act-options').screenshot({path:path.join(dir,env.name+'-'+size.label+'-'+slug+'-booking.png'),animations:'disabled',timeout:16000});
       await page.locator('#ct-topic-dashboard .ct-grid').screenshot({path:path.join(dir,env.name+'-'+size.label+'-'+slug+'-top3.png'),animations:'disabled',timeout:16000});
    }
   }catch(e){issues.push('PAGE_OR_AUDIT_ERROR');metrics={error:String(e.message).slice(0,240)}}
   results.push({environment:env.name,viewport:size.label,slug,url:uri,http,issues,metrics});
   console.log(env.name,size.label,slug,issues.length?'FAIL '+issues.join(','):'PASS');
   await page.close();
  }
 }
}
await browser.close();
const summary={runAt:new Date().toISOString(),pages:slugs.length,cases:results.length,pass:results.filter(x=>!x.issues.length).length,failed:results.filter(x=>x.issues.length).length,failures:results.filter(x=>x.issues.length).map(x=>({environment:x.environment,viewport:x.viewport,slug:x.slug,issues:x.issues,details:x.metrics?.error}))};
await writeFile(path.join(dir,'results.json'),JSON.stringify({summary,results},null,2));
await writeFile(path.join(dir,'summary.json'),JSON.stringify(summary,null,2));
console.log('FINAL',JSON.stringify(summary));
if(summary.failed)process.exitCode=1;
