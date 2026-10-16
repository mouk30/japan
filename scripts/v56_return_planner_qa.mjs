import { chromium } from 'playwright';
import { mkdir, writeFile } from 'node:fs/promises';

const base=process.env.V56_BASE_URL || 'http://127.0.0.1:8756';
const dir='audit-reports/v56';
await mkdir(dir,{recursive:true});
const browser=await chromium.launch({headless:true});
const errors=[], checks=[];
try {
 for (const width of [320,390,768,1440]) {
  const page=await browser.newPage({viewport:{width,height:940},deviceScaleFactor:1});
  try {
   await page.goto(base+'/voucher/cruise-ports/',{waitUntil:'domcontentloaded',timeout:20000});
   const count=await page.locator('.v52-port-card').count();
   if(count!==13)errors.push(width+'px: expected 13 cards, got '+count);
   const overflow=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,width:innerWidth}));
   if(overflow.scroll>overflow.width+2)errors.push(width+'px: horizontal overflow '+overflow.scroll);
   const form=page.locator('#v56-return-form');
   if(!await form.count())throw new Error('missing return form');
   const noDeadline=await page.locator('#v56-deadline').inputValue();
   if(noDeadline)errors.push(width+'px: should not set a fictional boarding deadline');
   await page.locator('#v56-port').selectOption('hakodate');
   await page.locator('#v56-date').fill('2026-10-24');
   await page.locator('#v56-ship').fill('예시 선박');
   await page.locator('#v56-pier').fill('예시 접안 부두');
   await page.locator('#v56-deadline').fill('18:00');
   await page.locator('#v56-travel').fill('50');
   await page.locator('#v56-buffer').selectOption('60');
   await form.locator('button[type="submit"]').click();
   const result=await page.locator('#v56-return-result').innerText();
   if(!result.includes('16:10'))errors.push(width+'px: wrong time arithmetic: '+result.slice(0,100));
   if(!result.includes('예시 선박'))errors.push(width+'px: ship name not included');
   if(width===320||width===1440)await page.screenshot({path:dir+'/planner-'+width+'.png',fullPage:false});
   await page.locator('#v56-deadline').fill('01:00');
   await page.locator('#v56-travel').fill('80');
   await page.locator('#v56-buffer').selectOption('60');
   await form.locator('button[type="submit"]').click();
   const night=await page.locator('#v56-return-result').innerText();
   if(!night.includes('22:40 (전날)'))errors.push(width+'px: previous-day arithmetic failed: '+night.slice(0,100));
   checks.push({width,count,overflow:overflow.scroll,normal:'16:10',midnight:'22:40 (전날)',pass:true});
  }catch(e){errors.push(width+'px: '+String(e).slice(0,350))}
  finally{await page.close();}
 }
}finally{await browser.close();}
const report={at:new Date().toISOString(),checks,errors,passed:errors.length===0};
await writeFile(dir+'/return-planner-qa.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
if(errors.length)process.exitCode=1;
