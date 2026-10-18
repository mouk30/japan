const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const pages = JSON.parse(fs.readFileSync('audit-output/premium-80/pages.json','utf8'));
const widths=[390,768,1440], base='http://127.0.0.1:8765';
const out='audit-output/premium-80';fs.mkdirSync(path.join(out,'screenshots'),{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true});
 const results=[];
 for(const row of pages){
   for(const width of widths){
     const page=await browser.newPage({viewport:{width,height:850},deviceScaleFactor:1});
     const errors=[];
     page.on('pageerror',e=>errors.push(String(e)));
     let status=null,metrics=null;
     try{
       const response=await page.goto(base+row.url,{waitUntil:'domcontentloaded',timeout:25000});
       status=response?.status()??null;
       await page.locator('body').waitFor({timeout:8000});
       metrics=await page.evaluate(()=>{
         const html=document.documentElement;
         const images=[...document.images];
         const premium=document.querySelector('link[href*="nf-editorial-premium-v2.css"]');
         const box=document.querySelector('.nf-article-masthead');
         const computed=box?getComputedStyle(box):null;
         return {overflowPx:Math.max(0,html.scrollWidth-innerWidth),
             brokenImages:images.filter(x=>!x.complete||x.naturalWidth===0).map(x=>x.getAttribute('src')).slice(0,12),
             premiumCssLoaded:!![...document.styleSheets].find(x=>(x.href||'').includes('nf-editorial-premium-v2.css')),
             masthead:!!box, mastheadColor:computed?.backgroundImage,
             bookingCTA:!!document.querySelector('a[href="/booking/japan-cruise/"]'),
             h1Count:document.querySelectorAll('h1').length,
             horizontalScroll:html.scrollWidth>innerWidth+2};
       });
       const index=pages.indexOf(row);
       if([0,10,20,30,40,50,60,70].includes(index)){
         await page.screenshot({path:path.join(out,'screenshots',String(index+1).padStart(3,'0')+'-'+width+'.png'),fullPage:true});
       }
     }catch(e){errors.push(String(e))}
     results.push({url:row.url,width,status,...metrics,errors});
     await page.close();
   }
 }
 await browser.close();
 fs.writeFileSync(path.join(out,'browser-results.json'),JSON.stringify(results,null,2));
 const failures=results.filter(x=>x.status!==200||x.horizontalScroll||!x.premiumCssLoaded||!x.masthead||!x.bookingCTA||x.h1Count!==1||x.brokenImages?.length||x.errors?.length);
 const summary={pages:pages.length,combinations:results.length,pass:results.length-failures.length,fail:failures.length,failures:failures.slice(0,35)};
 fs.writeFileSync(path.join(out,'browser-summary.json'),JSON.stringify(summary,null,2));
 console.log(JSON.stringify({pages:summary.pages,combinations:summary.combinations,pass:summary.pass,fail:summary.fail},null,2));
 if(failures.length) process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
