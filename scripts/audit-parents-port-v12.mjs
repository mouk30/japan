import { chromium } from 'playwright';
import { readFile,mkdir,writeFile } from 'node:fs/promises';
import path from 'node:path';
const manifest=JSON.parse(await readFile('scripts/parents-port-v12-data.json','utf8'));
const outDir='audit-reports/parents-port-v12-visual';await mkdir(outDir,{recursive:true});
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
const bases=[['build',process.env.LOCAL_BASE_URL||'http://127.0.0.1:8765'],['live',process.env.LIVE_BASE_URL||'https://www.nipponferry.com']];
const dims=[['mobile',390,844],['desktop',1365,900]];
const cases=[];
for(const [environment,base] of bases)for(const [view,width,height] of dims)for(const [slug,ref] of Object.entries(manifest.cities)){
 const url=base.replace(/\/$/,'')+'/things-to-do/'+slug+'-cruise-parents-guide/';
 const page=await browser.newPage({viewport:{width,height},locale:'ko-KR'});
 const issues=[];let report={};
 try{
   const result=await page.goto(url,{waitUntil:'domcontentloaded',timeout:23000});
   if(!result?.ok())throw Error('HTTP '+result?.status());
   await page.locator('#nf-port-v12').waitFor({timeout:9000});
   report=await page.evaluate(()=>{
      const panel=document.querySelector('#nf-port-v12');
      const links=[...panel.querySelectorAll('.nf-port-route>a')];
      const cards=[...panel.querySelectorAll('.nf-port-route')];
      const sourceLinks=links.map(el=>el.href);
      const metrics=cards.map(el=>({title:el.querySelector('h3')?.textContent.trim(),value:el.querySelector('.nf-port-route-value')?.textContent.trim(),height:Math.round(el.getBoundingClientRect().height),minHeight:getComputedStyle(el).minHeight}));
      return {
        cssPresent:!!document.querySelector('link[href*="companion-port-v12.css"]'),
        title:document.querySelector('#nf-port-title')?.textContent,
        sourceLinks,metrics,
        returnSafety:!!document.querySelector('.nf-port-return'),
        hasOriginNote:!!document.querySelector('.nf-port-intro'),
        hasHorizontalOverflow:document.documentElement.scrollWidth>innerWidth+3,
        bodyWidth:innerWidth
      };
   });
   if(!report.cssPresent)issues.push('MISSING_V12_CSS');
   if(!report.returnSafety||!report.hasOriginNote)issues.push('MISSING_SAFETY_OR_ORIGIN');
   if(report.metrics.length!==ref.routes.length)issues.push('WRONG_ROUTE_CARD_COUNT');
   if(report.hasHorizontalOverflow)issues.push('HORIZONTAL_OVERFLOW');
   for(let i=0;i<Math.min(ref.routes.length,report.metrics.length);i++){
      const [title,mode,time,label,official]=ref.routes[i];
      if(report.metrics[i].title!==title||report.metrics[i].value!==time)issues.push('ROUTE_TEXT_MISMATCH_'+(i+1));
      if(report.sourceLinks[i]!==official)issues.push('SOURCE_LINK_MISMATCH_'+(i+1));
      if(report.metrics[i].minHeight!=='0px')issues.push('FORCED_CARD_HEIGHT_'+(i+1));
   }
   if(['ishigaki','kagoshima','kanazawa','yokohama','naha'].includes(slug)){
      await page.locator('#nf-port-v12').screenshot({path:path.join(outDir,environment+'-'+view+'-'+slug+'.png'),animations:'disabled',timeout:16000});
   }
 }catch(e){issues.push('PAGE_LOAD_OR_AUDIT_FAILED');report={error:String(e.message).slice(0,220)}}
 cases.push({environment,view,slug,url,issues,report});
 console.log(environment,view,slug,issues.length?issues.join(','):'PASS');
 await page.close();
}
await browser.close();
const summary={pages:Object.keys(manifest.cities).length,cases:cases.length,passed:cases.filter(x=>!x.issues.length).length,failed:cases.filter(x=>x.issues.length).length,failures:cases.filter(x=>x.issues.length).map(x=>({environment:x.environment,view:x.view,slug:x.slug,issues:x.issues,error:x.report?.error}))};
await writeFile(path.join(outDir,'summary.json'),JSON.stringify(summary,null,2));
await writeFile(path.join(outDir,'full-results.json'),JSON.stringify(cases,null,2));
await writeFile(path.join(outDir,'report.csv'),['environment,view,slug,status,issues',...cases.map(x=>[x.environment,x.view,x.slug,x.issues.length?'FAIL':'PASS',x.issues.join(';')].map(s=>'"'+String(s).replaceAll('"','""')+'"').join(','))].join('\n')+'\n');
console.log('FINAL',JSON.stringify(summary));
if(summary.failed)process.exitCode=1;
