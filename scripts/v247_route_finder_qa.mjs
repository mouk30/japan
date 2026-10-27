/* V247 route explorer QA — static link, booking-trust and browser interactions */
import fs from 'node:fs';
import path from 'node:path';
import {chromium} from 'playwright';
const OUT='audit-reports/v247';
fs.mkdirSync(OUT,{recursive:true});
const report={checkedAt:new Date().toISOString(),routeCards:0,localLinks:0,viewports:[],errors:[],warnings:[]};
const distHtml=fs.readFileSync('dist/index.html','utf8');
const sourceHtml=fs.readFileSync('site/index.html','utf8');
const check=(condition,message)=>{if(!condition)report.errors.push(message)};
const val=(s,re)=>s.match(re)?.[1]||null;
check(val(sourceHtml,/<title>([^<]+)<\/title>/)===val(distHtml,/<title>([^<]+)<\/title>/),'SEO title changed during build');
check(val(sourceHtml,/<link rel="canonical" href="([^"]+)"/)===val(distHtml,/<link rel="canonical" href="([^"]+)"/),'canonical changed during build');
check(distHtml.includes('nf247-finder')&&distHtml.includes('data-nf247-finder'),'V247 section missing in published build');
check(distHtml.includes('href="#find-sea-route"'),'Hero route CTA not connected to finder');
check(distHtml.includes('href="/nf-v247-routes.css?v=20261027"'),'V247 CSS not loaded');
check(distHtml.includes('src="/nf-v247-routes.js?v=20261027"'),'V247 JS not loaded');
check(distHtml.includes('nf246-header')&&!distHtml.includes('data-nf301="v305"'),'V246 homepage header was overwritten');
check((distHtml.match(/<h1\b/g)||[]).length===1,'Homepage h1 count changed');
check(!/<input[^>]*(?:type=["']?(?:date|time)|name=["']?(?:seat|passengers))/i.test(distHtml.match(/<section class="nf247-finder"[\s\S]+?<\/section>/)?.[0]||''),'Finder must not impersonate a real booking engine');
const cards=[...distHtml.matchAll(/<article class="nf247-card"[^>]*data-nf247-from="([^"]+)" data-nf247-kind="([^"]+)"([^>]*)>([\s\S]*?)<\/article>/g)];
report.routeCards=cards.length;
check(cards.length===18,'Route-card total should be 18');
const expected={'busan/international':4,'japan/international':4,'japan/coastal':4,'busan/cruise':1,'japan/cruise':5};
const seen={};
for(const c of cards){
 const key=c[1]+'/'+c[2];
 seen[key]=(seen[key]||0)+1;
 const shouldStartHidden=key!=='busan/international';
 check(shouldStartHidden?c[3].includes(' hidden'):!c[3].includes(' hidden'),'Initial no-JS visibility incorrect '+key);
}
for(const [key,num] of Object.entries(expected))check(seen[key]===num,'Wrong route count '+key+': '+seen[key]);
for(const [key] of Object.entries(seen))check(Object.hasOwn(expected,key),'Unexpected type '+key);
const section=distHtml.match(/<section class="nf247-finder"[\s\S]+?<\/section>/)?.[0]||'';
const urls=new Set([...section.matchAll(/\bhref="([^"]+)"/g)].map(m=>m[1]));
for(const uri of urls){
 if(!uri.startsWith('/'))continue;
 const route=uri.split('#')[0].split('?')[0];
 if(route==='/')continue;
 let f=path.join('dist',route);
 if(!fs.existsSync(f)){
  f=path.join('dist',route.replace(/\/$/,'')+'/index.html');
  check(fs.existsSync(f),'Missing local route target: '+uri);
 }
 report.localLinks++;
}
check(section.includes('kampuferry.co.jp/news/20261027systemmaintenance.html'),'Current Kampu reservation resumption notice not linked');
check(!section.includes('kampuferry.co.jp/news/20261023systemmaintenance.html'),'Old Kampu suspension notice still linked');
for(const external of ['https://www.panstarcruise.com/product/osaka/info','https://www.panstarcruise.com/product/daemado/info'])check(section.includes(external),'Expected official operator guide missing '+external);
const widths=[320,375,390,768,1024,1440];
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
try{
 for(const width of widths){
  const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
  const issues=[];
  const assertion=(ok,msg)=>{if(!ok)issues.push(msg)};
  try{
   const response=await page.goto('http://127.0.0.1:8764/',{waitUntil:'domcontentloaded',timeout:30000});
   assertion(response?.status()===200,'HTTP '+response?.status());
   await page.locator('[data-nf247-finder]').waitFor();
   async function snapshot(){
    return page.evaluate(()=>{
     const section=document.querySelector('[data-nf247-finder]');
     const visible=[...section.querySelectorAll('[data-nf247-card]')].filter(e=>!e.hidden);
     const activeOrigin=[...section.querySelectorAll('[data-nf247-origin][aria-pressed="true"]')].map(e=>e.dataset.nf247Origin);
     const activeType=[...section.querySelectorAll('[data-nf247-type][aria-pressed="true"]')].map(e=>e.dataset.nf247Type);
     return {docWidth:document.documentElement.scrollWidth,screenWidth:innerWidth,
      count:visible.length,routeTitles:visible.map(e=>e.querySelector('h4')?.textContent),
      activeOrigin,activeType,unavailable:section.querySelector('[data-nf247-type="coastal"]').disabled,
      ariaStatus:section.querySelector('[data-nf247-status]').textContent,
      h1:document.querySelectorAll('h1').length,
      scrollWidth:section.scrollWidth,clientWidth:section.clientWidth};
    });
   }
   let v=await snapshot();
   assertion(v.docWidth<=width+2,'Horizontal page overflow '+v.docWidth);
   assertion(v.count===4&&v.activeOrigin[0]==='busan'&&v.activeType[0]==='international','Initial Busan state');
   assertion(v.unavailable,'Coastal fare option not disabled for Busan');
   assertion(v.h1===1,'Homepage main heading changed');
   await page.locator('[data-nf247-origin="japan"]').click();
   v=await snapshot();
   assertion(v.count===4&&v.activeOrigin[0]==='japan'&&!v.unavailable,'Japan state / reverse routes');
   await page.locator('[data-nf247-type="coastal"]').click();
   v=await snapshot();
   assertion(v.count===4&&v.routeTitles.some(t=>t.includes('자마미'))&&v.activeType[0]==='coastal','Domestic route choice / return');
   if(width===390||width===1440){
    await page.locator('[data-nf247-finder]').screenshot({path:OUT+'/route-finder-'+width+'.png',animations:'disabled'});
   }
   const guide=page.locator('[data-nf247-card]:not([hidden]) .nf247-guide').first();
   assertion(await guide.getAttribute('href')==='/okinawa/zamami-aka-ferry/','First domestic guide mismatch');
   await page.locator('[data-nf247-type="cruise"]').click();
   v=await snapshot();
   assertion(v.count===5&&v.activeType[0]==='cruise','Japan cruise ports count');
   await page.locator('[data-nf247-type="international"]').click();
   v=await snapshot();
   assertion(v.count===4&&v.routeTitles.some(t=>t.includes('→ 부산')),'Japan to Busan international guides');
   await page.locator('[data-nf247-type="cruise"]').click();
   await page.locator('[data-nf247-origin="busan"]').click();
   v=await snapshot();
   assertion(v.count===1&&v.activeType[0]==='cruise'&&v.unavailable,'Busan cruise planning not a false route');
   // A disabled domestic button never changes the selected Busan trip.
   assertion(await page.locator('[data-nf247-type="coastal"]').isDisabled(),'Busan domestic type should be disabled');
   // Keyboard must operate a selection and announce the new options.
   const international=page.locator('[data-nf247-type="international"]');
   await international.focus();await page.keyboard.press('Enter');
   v=await snapshot();
   assertion(v.count===4&&v.activeType[0]==='international'&&v.ariaStatus.includes('4개'),'Keyboard activation or aria-live status failed');
   assertion(v.docWidth<=width+2,'Overflow after switching '+v.docWidth);
   report.viewports.push({width,passed:issues.length===0,issues});
  }catch(err){issues.push(String(err).slice(0,500));report.viewports.push({width,passed:false,issues})}
  for(const issue of issues)report.errors.push(width+': '+issue);
  await page.close();
 }
}finally{await browser.close()}
report.passed=report.errors.length===0;
fs.writeFileSync(OUT+'/qa.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({passed:report.passed,routeCards:report.routeCards,localLinks:report.localLinks,screens:report.viewports.length,errors:report.errors.slice(0,35)},null,2));
if(!report.passed)process.exitCode=1;
