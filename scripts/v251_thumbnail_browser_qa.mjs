/* V251: actual decoded image, mobile layout, link and runtime checks. */
import fs from 'node:fs';
import {chromium} from 'playwright';
const BASE='http://127.0.0.1:8768';
const OUT='audit-reports/v251';
fs.mkdirSync(OUT,{recursive:true});
const hubs=[
 ['/japan/tokyo/','.tky-card .tky-card-photo img',220],
 ['/japan-cruise/','.jc-card .nf251-card-photo img',12],
 ['/okinawa/','.oc .nf251-card-photo img',12],
 ['/japan/osaka/','.os-card img',9],
 ['/japan/fukuoka/','.fk-card img',9],
 ['/japan/','.dircard img',23],
 ['/things-to-do/','.v36-photo-card img',152]
];
const errors=[],results=[],screenshots=[];
const browser=await chromium.launch({headless:true,executablePath:process.env.NF251_BROWSER_PATH||undefined,args:['--no-sandbox']});
try{
 for(const [path,selector,expected] of hubs){
  for(const width of [390,1440]){
   const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
   const cases=[], runtime=[];
   page.on('pageerror',e=>runtime.push(String(e).slice(0,280)));
   try{
    const response=await page.goto(BASE+path,{waitUntil:'domcontentloaded',timeout:30000});
    if(response?.status()!==200)cases.push('HTTP status '+response?.status());
    const state=await page.evaluate(()=>({title:document.title,canonical:document.querySelector('link[rel="canonical"]')?.href||'',
      overflow:document.documentElement.scrollWidth-innerWidth}));
    if(!state.title||!state.canonical.includes('nipponferry.com/'))cases.push('missing title/canonical');
    if(state.overflow>2)cases.push('horizontal overflow '+state.overflow);
    const imgs=page.locator(selector);
    const n=await imgs.count();
    if(n!==expected)cases.push('card thumbnail count '+n+' expected '+expected);
    const samples=[...new Set([0,1,2,Math.floor(expected/4),Math.floor(expected/2),Math.floor(expected*3/4),expected-1])].filter(x=>x<n);
    for(const i of samples){
     const img=imgs.nth(i);
     await img.evaluate(el=>{el.loading='eager';});
     const ok=await img.evaluate(async el=>{
      if(el.complete&&el.naturalWidth>0)return true;
      return Promise.race([new Promise(resolve=>{
       el.addEventListener('load',()=>resolve(el.naturalWidth>0),{once:true});
       el.addEventListener('error',()=>resolve(false),{once:true});
      }),new Promise(resolve=>setTimeout(()=>resolve(false),12000))]);
     });
     if(!ok)cases.push('image '+i+' failed decode '+await img.getAttribute('src'));
     if(!(await img.getAttribute('alt')))cases.push('image '+i+' missing meaningful alt');
    }
    if(runtime.length)cases.push('uncaught page errors: '+JSON.stringify(runtime.slice(0,3)));
    // One screenshot per hub and viewport for human visual QA.
    const name=path.replaceAll('/','-').replace(/^-|-$/g,'')+'-'+width+'.png';
    await page.screenshot({path:OUT+'/'+name,fullPage:false,animations:'disabled'});
    screenshots.push(name);
    results.push({path,width,pictured:n,expected,samples_checked:samples.length,passed:cases.length===0,issues:cases});
    for(const x of cases)errors.push(path+' @ '+width+': '+x);
   }catch(e){errors.push(path+' @ '+width+': browser exception '+String(e).slice(0,380));results.push({path,width,passed:false,issues:[String(e)]})}
   finally{await page.close()}
  }
 }
}finally{await browser.close()}
const report={version:'V251',passed:errors.length===0,checks:results.length,results,screenshots,errors};
fs.writeFileSync(OUT+'/thumbnail-browser.json',JSON.stringify(report,null,2)+'\n');
console.log('V251_BROWSER',JSON.stringify({passed:report.passed,checks:results.length,screenshots:screenshots.length,errors:errors.slice(0,12)},null,2));
if(errors.length)process.exitCode=1;
