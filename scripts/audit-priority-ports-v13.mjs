import { chromium } from 'playwright';
import { readFile,mkdir,writeFile } from 'node:fs/promises';
import path from 'node:path';
const catalog=JSON.parse(await readFile('scripts/priority-ports-v13.json','utf8'));
const portKeys=Object.keys(catalog.ports);
const output='audit-reports/v13-priority-port-visual';
await mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
const cases=[];
const environments=[['local',process.env.LOCAL_BASE_URL||'http://127.0.0.1:8765'],['production',process.env.LIVE_BASE_URL||'https://www.nipponferry.com']];
const screens=[['mobile',390,844],['desktop',1365,900]];
for(const [environment,base] of environments)for(const [screen,width,height] of screens)for(const [port,info] of Object.entries(catalog.ports))for(const guide of ['family','couple','parents']){
 const slug=port+'-cruise-'+guide+'-guide';
 const uri=base.replace(/\/$/,'')+'/things-to-do/'+slug+'/';
 const page=await browser.newPage({viewport:{width,height},locale:'ko-KR'});
 const problems=[];let actual=null,http=null;
 try{
   const response=await page.goto(uri,{waitUntil:'domcontentloaded',timeout:28000});
   http=response?.status();if(!response?.ok())throw Error('HTTP '+http);
   await page.locator('#nf-precision-v13').waitFor({timeout:11000});
   await page.waitForFunction(()=>[...document.styleSheets].some(sheet=>sheet.href?.includes('companion-precision-v13.css')),{timeout:11000});
   actual=await page.evaluate(()=>{
      const root=document.querySelector('#nf-precision-v13');
      const decks=[...root.querySelectorAll('details.nf-precision-berth')];
      const oldPhotos=[...document.querySelectorAll('#ct-topic-dashboard .ct-card .ct-photo img')];
      const figLinks=[...document.querySelectorAll('#ct-topic-dashboard .ct-card figcaption a')];
      return {
        cssLinked:!!document.querySelector('link[href*="companion-precision-v13.css"]'),
        layoutOverflow:document.documentElement.scrollWidth>window.innerWidth+3,
        cards:decks.map(d=>({
           title:d.querySelector('summary')?.firstChild?.textContent?.trim(),
           header:d.querySelector('summary')?.textContent?.trim(),
           amount:d.querySelector('.nf-precision-leg b')?.textContent?.trim(),
           source:d.querySelector('.nf-precision-body>a')?.href,
           hasTransfer:!!d.querySelector('.nf-precision-body p:nth-of-type(4)'),
           hasReturn:d.querySelector('.nf-precision-body')?.textContent?.includes('귀선 경로'),
           hasPreciseLeg:!!d.querySelector('.nf-precision-leg>span'),
           height:Math.round(d.getBoundingClientRect().height),
           open:d.open,
        })),
        warnings:root.querySelector('.nf-precision-return')?.textContent.trim(),
        hasAttribution:figLinks.length>0,
        photoCount:oldPhotos.length,
        photos:oldPhotos.map(img=>{let r=img.getBoundingClientRect();return {src:img.getAttribute('src'),ratio:r.width?+(r.height/r.width).toFixed(3):0}}),
        linkDisplay:[...root.querySelectorAll('details .nf-precision-body>a')].map(x=>getComputedStyle(x).display)
      };
   });
   if(!actual.cssLinked||!actual.warnings)problems.push('STYLE_OR_FINAL_RETURN_MISSING');
   if(actual.cards.length!==info.berths.length)problems.push('BERTH_CARD_COUNT');
   if(actual.layoutOverflow)problems.push('PAGE_HORIZONTAL_OVERFLOW');
   for(let i=0;i<Math.min(actual.cards.length,info.berths.length);i++){
      const a=actual.cards[i],b=info.berths[i];
      if(!a.header.includes(b.name)||a.amount!==b.amount)problems.push('WRONG_BERTH_OR_QUANTITY_'+(i+1));
      if(a.source!==b.source)problems.push('OFFICIAL_SOURCE_MISMATCH_'+(i+1));
      if(!a.hasReturn||!a.hasPreciseLeg)problems.push('MISSING_RETURN_OR_ORIGIN_'+(i+1));
   }
   if(actual.photoCount!==3)problems.push('VENUE_THUMBNAIL_COUNT');
   if(actual.photos.some(x=>x.ratio&&Math.abs(x.ratio-.75)>.04))problems.push('PHOTO_RATIO_REGRESSION');
   if(actual.linkDisplay.some(x=>x==='flex'||x==='grid'))problems.push('OFFICIAL_LINK_RENDERED_AS_BUTTON');
   // Verify all accordion sections are keyboard operable and expansions reveal critical information.
   if(actual.cards.length>1){
     const selector='#nf-precision-v13 details.nf-precision-berth:nth-child(2) summary';
     await page.locator(selector).focus();
     await page.keyboard.press('Enter');
     if(!(await page.locator('#nf-precision-v13 details.nf-precision-berth:nth-child(2)').evaluate(el=>el.open)))problems.push('ACCORDION_KEYBOARD_NOT_WORKING');
   }
   if(screen==='mobile'&&['ishigaki','naha','yokohama','hakata','nagasaki'].includes(port)&&environment==='production'){
     await page.locator('#nf-precision-v13').screenshot({path:path.join(output,'live-'+slug+'.png'),animations:'disabled',timeout:15000});
   }
 }catch(e){problems.push('AUDIT_EXCEPTION');actual={error:String(e.message).slice(0,250)}}
 cases.push({environment,screen,port,guide,url:uri,http,problems,actual});
 console.log(environment,screen,slug,problems.length?'FAIL '+problems.join(';'):'PASS');
 await page.close();
}
await browser.close();
const summary={guides:15,berthVariants:portKeys.reduce((acc,k)=>acc+catalog.ports[k].berths.length,0),
 caseCount:cases.length,passed:cases.filter(x=>x.problems.length===0).length,failed:cases.filter(x=>x.problems.length>0).length,
 errors:cases.filter(x=>x.problems.length>0).map(x=>({environment:x.environment,screen:x.screen,port:x.port,guide:x.guide,problems:x.problems,details:x.actual?.error}))};
await writeFile(path.join(output,'summary.json'),JSON.stringify(summary,null,2));
await writeFile(path.join(output,'report.json'),JSON.stringify(cases,null,2));
await writeFile(path.join(output,'report.csv'),['environment,screen,port,guide,status,errors',...cases.map(x=>[x.environment,x.screen,x.port,x.guide,x.problems.length?'FAIL':'PASS',x.problems.join(';')].map(v=>'"'+String(v).replaceAll('"','""')+'"').join(','))].join('\n')+'\n');
console.log('SUMMARY',JSON.stringify(summary));
if(summary.failed)process.exitCode=1;
