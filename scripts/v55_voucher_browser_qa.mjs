import { chromium } from 'playwright';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const base = process.env.V55_BASE_URL || 'http://127.0.0.1:8755';
const dir='audit-reports/v55';
await mkdir(dir,{recursive:true});
const browser=await chromium.launch({headless:true});
const errors=[], snapshots=[];
const expectedModes={ticket:8,activity:3,coupon:1,info:1};
try{
 for(const width of [320,390,768,1440]){
  const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
  try{
   await page.goto(base+'/voucher/cruise-ports/',{waitUntil:'domcontentloaded',timeout:20000});
   await page.waitForSelector('.v52-port-card[data-v55-mode]',{timeout:8000});
   const total=await page.locator('.v52-port-card[data-v55-mode]').count();
   if(total!==13)errors.push(width+': expected 13 cards, got '+total);
   const meta=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,inner:innerWidth,filters:[...document.querySelectorAll('[data-v55-filter]')].length}));
   if(meta.scroll>meta.inner+2)errors.push(width+': horizontal overflow '+meta.scroll+' > '+meta.inner);
   if(meta.filters!==5)errors.push(width+': wrong filter count');
   if(width===320||width===1440)await page.screenshot({path:path.join(dir,'viewport-'+width+'.png')});
   for(const [mode,count] of Object.entries(expectedModes)){
    await page.locator('[data-v55-filter="'+mode+'"]').click();
    const visible=await page.locator('.v52-port-card[data-v55-mode]:visible').count();
    const display=await page.locator('#v55-result').innerText();
    if(visible!==count||display!==count+'개 기항지 정보')errors.push(width+': filter '+mode+' shown='+visible+' result='+display);
   }
   await page.locator('[data-v55-filter="all"]').click();
   for(const id of ['naha','ishigaki','hakata','nagasaki','yokohama','aomori','hakodate','kagoshima','beppu','miyakojima','osaka','kobe','sasebo']){
    const card=page.locator('#'+id);
    if(await card.count()!==1)errors.push(width+': missing '+id);
    else{
     if(await card.locator('.v55-quick li').count()!==3)errors.push(width+': steps '+id);
     const cta=card.locator('.v52-primary');
     const href=await cta.getAttribute('href');
     if(!/^https:\/\//.test(href||''))errors.push(width+': non-HTTPS CTA '+id);
     if(await card.locator('details.v54-verified').count()!==1)errors.push(width+': missing conditions '+id);
    }
   }
   const a=page.locator('#beppu details.v54-verified');
   await a.locator('summary').click();
   if(!await a.evaluate(el=>el.open))errors.push(width+': Beppu conditions cannot expand');
   snapshots.push({width,initialCards:total,filterChecks:Object.keys(expectedModes).length,scrollWidth:meta.scroll,viewportWidth:meta.inner});
  }catch(e){errors.push(width+': '+String(e).slice(0,500))}
  finally{await page.close();}
 }
 const page=await browser.newPage({viewport:{width:390,height:844}});
 try{
  await page.goto(base+'/voucher/',{waitUntil:'domcontentloaded',timeout:20000});
  const link=page.locator('a[href="/voucher/cruise-ports/"]').first();
  if(!await link.count())errors.push('voucher hub missing guide CTA');
  else{
   await link.click();
   await page.waitForURL('**/voucher/cruise-ports/');
   if(await page.locator('.v52-port-card').count()!==13)errors.push('voucher hub journey not 13 cards');
  }
 }catch(e){errors.push('voucher hub navigation: '+String(e).slice(0,400))}
 finally{await page.close()}
 const report={runAt:new Date().toISOString(),base,widths:snapshots,expectedModes,errors,passed:errors.length===0};
 await writeFile(path.join(dir,'browser-qa.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report,null,2));
 if(errors.length)process.exitCode=1;
}finally{await browser.close()}
