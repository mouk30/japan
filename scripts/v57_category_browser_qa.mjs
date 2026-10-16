import {chromium} from 'playwright';
import {readFile, mkdir, writeFile, stat} from 'node:fs/promises';
import {join} from 'node:path';

const base='http://127.0.0.1:8757';
const outDir='audit-reports/v57';
await mkdir(outDir,{recursive:true});
const config={onsen:5,nature:5,activity:5,'food-experience':4,seasonal:4};
const report={time:new Date().toISOString(),pages:[],checks:[],errors:[],warnings:[]};
const browser=await chromium.launch({headless:true});
const imgCheck=new Set();
try{
 for(const [slug,wanted] of Object.entries(config)){
  for(const width of [320,390,768,1440]){
   const page=await browser.newPage({viewport:{width,height:850},deviceScaleFactor:1});
   const name=slug+'-'+width;
   try{
    await page.goto(base+'/things-to-do/'+slug+'/',{waitUntil:'domcontentloaded',timeout:30000});
    const cards=page.locator('.v57card');
    const n=await cards.count();
    if(n!==wanted)report.errors.push(name+' card count expected '+wanted+' got '+n);
    const size=await page.evaluate(()=>({outer:document.documentElement.scrollWidth,width:innerWidth}));
    if(size.outer>size.width+2)report.errors.push(name+' overflow: '+size.outer+'>'+size.width);
    const main=await page.locator('main .v57h1').count();
    if(main!==1)report.errors.push(name+' missing single category H1');
    if(width===390){
     for(let i=0;i<n;i++){
      const card=cards.nth(i);
      const href=await card.locator('.v57button').first().getAttribute('href');
      if(!href?.startsWith('/'))report.errors.push(name+' bad CTA '+i);
      if(href&&href.startsWith('/')){
       const url=href.replace(/[?#].*$/,'');
       try{const sr=await stat(join('site',url,'index.html'));if(!sr.isFile())report.errors.push(name+' CTA not a page '+href)}
       catch{report.errors.push(name+' nonexistent CTA '+href)}
      }
      const src=await card.locator('img').getAttribute('src');
      if(src?.startsWith('/')){
       try{await stat(join('site',src));}catch{report.errors.push(name+' nonexistent image '+src)}
      }
     }
    }
    if(width===1440){
      for(let i=0;i<n;i++){
       const image=cards.nth(i).locator('img');
       await image.scrollIntoViewIfNeeded({timeout:8000});
       try{await image.evaluate(async el=>{if(!el.complete)await new Promise((resolve,reject)=>{el.addEventListener('load',resolve,{once:true});el.addEventListener('error',()=>reject(new Error('failed image')),{once:true});setTimeout(()=>reject(new Error('image timeout')),12000)});if(!el.naturalWidth)throw new Error('zero natural width')},{timeout:16000});}
       catch(e){report.errors.push(name+' image '+i+': '+String(e).slice(0,140));}
      }
      await page.locator('.v57hero').scrollIntoViewIfNeeded();
      await page.screenshot({path:outDir+'/'+slug+'-desktop.png',fullPage:false});
    }
    if(width===390){
      await page.locator('.v57hero').scrollIntoViewIfNeeded();
      await page.screenshot({path:outDir+'/'+slug+'-mobile.png',fullPage:false});
    }
    report.checks.push({name,cardCount:n,scrollWidth:size.outer});
   }catch(e){report.errors.push(name+': '+String(e).slice(0,330))}
   finally{await page.close()}
  }
 }
 const page=await browser.newPage({viewport:{width:390,height:830}});
 try{
  await page.goto(base+'/things-to-do/',{waitUntil:'domcontentloaded'});
  if(await page.locator('.v57-entry a').count()!==5)report.errors.push('hub direct guide links not 5');
  for(const href of ['/things-to-do/onsen/','/things-to-do/nature/','/things-to-do/activity/','/things-to-do/food-experience/','/things-to-do/seasonal/']){
   if(await page.locator('.v28-grid > a.v28-card[href="'+href+'"]').count()!==1)report.errors.push('hub missing category '+href);
  }
  if(await page.locator('a.v28-card[href="/things-to-do/culture/"]').count()!==1)report.errors.push('culture category missing');
  const l=page.locator('.v57-entry a[href="/things-to-do/japan-diving-first-time/"]');
  await l.click();await page.waitForURL('**/things-to-do/japan-diving-first-time/');
  if(!(await page.title()).includes('다이빙'))report.errors.push('hub diving shortcut wrong destination');
 }catch(e){report.errors.push('hub navigation: '+String(e).slice(0,300))}finally{await page.close()}
}finally{await browser.close()}
report.passed=report.errors.length===0;
await writeFile(outDir+'/browser-qa.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({passed:report.passed,pages:Object.keys(config).length,viewports:report.checks.length,errors:report.errors,warnings:report.warnings},null,2));
if(!report.passed)process.exitCode=1;
