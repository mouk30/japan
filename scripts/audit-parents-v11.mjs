import { chromium } from 'playwright';
import { readFile, readdir, mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
const specs=JSON.parse(await readFile('scripts/parents-v11-manifest.json','utf8'));
const slugs=Object.keys(specs.data).map(p=>p+'-cruise-parents-guide');
const baseLocal=(process.env.LOCAL_BASE_URL||'http://127.0.0.1:8765').replace(/\/$/,'');
const baseLive=(process.env.LIVE_BASE_URL||'https://www.nipponferry.com').replace(/\/$/,'');
const output='audit-reports/parents-visual-v11';await mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
const rows=[];
for(const env of [{name:'preview',url:baseLocal},{name:'production',url:baseLive}])
for(const vp of [{name:'mobile',w:390,h:844},{name:'desktop',w:1365,h:900}])
for(const slug of slugs){
 const page=await browser.newPage({viewport:{width:vp.w,height:vp.h},locale:'ko-KR',deviceScaleFactor:1});
 const url=env.url+'/things-to-do/'+slug+'/';let result=null;let issues=[];let http=null;
 try {
   const response=await page.goto(url,{waitUntil:'domcontentloaded',timeout:24000});
   http=response?.status();
   if(!response?.ok())throw Error('HTTP '+http);
   const root=page.locator('#ct-topic-dashboard .ct-grid');
   await root.waitFor({timeout:9000});
   for(const x of await root.locator('.ct-card img').all()){
       await x.scrollIntoViewIfNeeded({timeout:8000});
       await x.evaluate(async img=>{try{await img.decode()}catch(e){}});
   }
   result=await page.evaluate(()=>{
      const cards=[...document.querySelectorAll('#ct-topic-dashboard .ct-grid > .ct-card')];
      const ratio=img=>{let r=img.getBoundingClientRect();return r.width?+(r.height/r.width).toFixed(3):0};
      return {title:document.title,
          standardCss:!!document.querySelector('link[href*="companion-card-standard.css"]'),
          parentCss:!!document.querySelector('link[href*="companion-parents-v11.css"]'),
          summaryPresent:!!document.querySelector('#nf-parents-summary'),
          gridAlign: getComputedStyle(document.querySelector('#ct-topic-dashboard .ct-grid')).alignItems,
          hasHorizontalOverflow:document.documentElement.scrollWidth>innerWidth+4,
          cards:cards.map(c=>{
            const img=c.querySelector('.ct-photo img'), fig=c.querySelector('.ct-photo figcaption');
            const credit=fig?[...fig.querySelectorAll('a')].map(a=>({label:a.textContent.trim(),display:getComputedStyle(a).display,background:getComputedStyle(a).backgroundColor,marginTop:getComputedStyle(a).marginTop,padding:getComputedStyle(a).paddingTop,url:a.href})):[];
            const steps=c.querySelectorAll('.nf-parents-facts>div');
            let facts=[...steps].map(x=>x.textContent.trim());
            return {title:c.querySelector('h3')?.textContent.trim(),imageSrc:img?.getAttribute('src')||null,loaded:!!img&&img.complete&&img.naturalWidth>0,ratio:img?ratio(img):null,
             source:credit.some(a=>a.url.includes('commons.wikimedia.org')), license:credit.some(a=>a.url.includes('creativecommons.org')||a.url.includes('commons.wikimedia.org')),
             credits:credit,descriptionPresent:!!c.querySelector('h3 + p')||!!c.querySelector('.ct-photo + p'),
             facts,factsCount:steps.length,cardHeight:Math.round(c.getBoundingClientRect().height),minHeight:getComputedStyle(c).minHeight};
          })};
   });
   if(!result.standardCss||!result.parentCss||!result.summaryPresent)issues.push('MISSING_STANDARD_OR_SUMMARY');
   if(result.cards.length!==3)issues.push('TOP3_COUNT');
   if(result.gridAlign!=='start')issues.push('GRID_STRETCHED');
   if(result.hasHorizontalOverflow)issues.push('HORIZONTAL_OVERFLOW');
   const countNoImage=result.cards.filter(c=>!c.imageSrc).length;
   if(countNoImage>1)issues.push('UNEXPECTED_MISSING_IMAGES');
   result.cards.forEach((c,i)=>{
      if(c.factsCount!==4)issues.push('MOBILITY_INFO_MISSING_'+(i+1));
      if(c.imageSrc){
        if(!c.loaded)issues.push('PHOTO_BROKEN_'+(i+1));
        if(c.ratio===null||Math.abs(c.ratio-.75)>.035)issues.push('BAD_RATIO_'+(i+1)+'_'+c.ratio);
        if(!c.source||!c.license)issues.push('CREDIT_MISSING_'+(i+1));
        if(c.credits.some(a=>a.display!=='inline'||a.background!=='rgba(0, 0, 0, 0)'||a.padding!=='0px'))issues.push('CREDIT_AS_BUTTON_'+(i+1));
      }
      if(c.minHeight!=='0px')issues.push('FORCED_HEIGHT_'+(i+1));
   });
   if(['hakodate','hirara-miyakojima','kanazawa','naha','yokohama'].some(t=>slug.startsWith(t))){
       await root.screenshot({path:path.join(output,env.name+'-'+vp.name+'-'+slug+'.png'),timeout:14000,animations:'disabled'});
   }
 } catch(e) {issues.push('PAGE_CHECK_FAILED');result={error:String(e.message).slice(0,250)};}
 rows.push({environment:env.name,viewport:vp.name,slug,url,http,issues,result});
 console.log(env.name,vp.name,slug,issues.length?issues.join(','):'PASS');
 await page.close();
}
await browser.close();
const summary={pages:15,cases:rows.length,pass:rows.filter(r=>!r.issues.length).length,failed:rows.filter(r=>r.issues.length).length,errors:rows.filter(r=>r.issues.length).map(r=>({environment:r.environment,viewport:r.viewport,slug:r.slug,issues:r.issues,reason:r.result?.error}))};
await writeFile(path.join(output,'report.json'),JSON.stringify({summary,rows},null,2));
await writeFile(path.join(output,'summary.json'),JSON.stringify(summary,null,2));
const csv=[['env','viewport','slug','status','issues'].join(','),...rows.map(r=>[r.environment,r.viewport,r.slug,r.issues.length?'FAIL':'PASS',r.issues.join(';')].map(x=>'"'+x.replaceAll('"','""')+'"').join(','))];await writeFile(path.join(output,'report.csv'),csv.join('\n'));
console.log('FINAL',JSON.stringify(summary));
if(summary.failed)process.exitCode=1;
