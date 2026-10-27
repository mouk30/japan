/* V250: priority traveler journeys + representative responsive, keyboard and booking handoff QA. */
import fs from 'node:fs';
import {chromium} from 'playwright';
const OUT='audit-reports/v250';
fs.mkdirSync(OUT,{recursive:true});
const ORIGIN='http://127.0.0.1:8767';
const pages=[
 '/','/ferry/','/japan-cruise/','/booking/','/booking/japan-cruise/',
 '/guide/busan-osaka-ferry/','/guide/busan-fukuoka-ferry/','/guide/busan-shimonoseki-ferry/',
 '/guide/busan-tsushima-ferry/','/japan/tokyo/','/japan/osaka/','/japan/fukuoka/',
 '/okinawa/','/things-to-do/','/things-to-do/cruise-ports/','/things-to-do/travel-companions/'
];
const widths=[320,390,768,1199,1440];
const report={version:'V250',generatedAt:new Date().toISOString(),routes:pages,viewports:widths,checks:[],flows:[],screenshots:[],errors:[],warnings:[]};
const fail=(msg)=>report.errors.push(msg);
const check=(ok,msg)=>{if(!ok)fail(msg)};
const browser=await chromium.launch({headless:true,executablePath:process.env.NF250_BROWSER_PATH||undefined,args:['--no-sandbox']});
const runtimeEvents=[];
try{
 for(const pathname of pages){
  for(const width of widths){
   const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1,reducedMotion:'reduce'});
   const issues=[];const assert=(ok,s)=>{if(!ok)issues.push(s)};
   page.on('pageerror',err=>{if(runtimeEvents.length<35)runtimeEvents.push({pathname,width,error:String(err).slice(0,260)})});
   try{
    const res=await page.goto(ORIGIN+pathname,{waitUntil:'domcontentloaded',timeout:30000});
    assert(res?.status()===200,'HTTP '+res?.status());
    const state=await page.evaluate(()=>{
     const html=document.documentElement;
     const main=document.querySelector('main')||document.body;
     return {scrollWidth:html.scrollWidth,innerWidth,
      title:document.title,
      canonical:document.querySelector('link[rel=canonical]')?.href||'',
      h1:document.querySelectorAll('h1').length,
      bodyText:main?.textContent?.trim().length||0,
      hasHome:!!document.querySelector('.nf246-header'),
      hasShared:!!document.querySelector('.nf301-header'),
      styleCount:[...document.querySelectorAll('link[rel=stylesheet]')].filter(x=>x.href.includes('nf-v249-mobile-consistency.css')).length};
    });
    assert(state.scrollWidth<=width+2,'Horizontal overflow: '+state.scrollWidth);
    assert(state.title.length>=8,'Browser title missing');
    assert(state.canonical.includes('nipponferry.com/'),'Canonical absent');
    assert(state.bodyText>130,'Page body unexpectedly blank');
    assert(state.styleCount===1,'V249 CSS duplicate or missing');
    assert(pathname==='/'?state.hasHome:state.hasShared,'Wrong header type');
    if(pathname==='/' || pathname==='/guide/busan-shimonoseki-ferry/'||pathname==='/ferry/'||pathname==='/booking/japan-cruise/'){
     assert(state.h1===1,'Primary travel page H1 count '+state.h1);
    }
    if(pathname==='/guide/busan-shimonoseki-ferry/'||pathname==='/ferry/'||pathname==='/booking/japan-cruise/'){
     const booking=await page.evaluate(()=>{
      const h=document.documentElement.innerHTML;
      const all=[...document.querySelectorAll('a[href*="kampuferry.co.jp"]')];
      return {oldNotice:h.includes('20261023systemmaintenance.html'),
       newNotice:all.filter(a=>a.href.includes('20261027systemmaintenance.html')).length,
       official:all.some(a=>a.href.startsWith('https://www.kampuferry.co.jp/reserve/')),
       oldClaims:/온라인 예약 중단\(|재개일 미정|인터넷 예약 중단 중/.test(document.body.textContent),
       labels:all.filter(a=>a.href.includes('20261027systemmaintenance.html')).map(a=>a.textContent.trim()).slice(0,5)};
     });
     assert(!booking.oldNotice&&!booking.oldClaims,'Outdated suspended booking text persists');
     assert(booking.newNotice>=1,'Kampu restart notice missing');
     assert(booking.official,'Operator booking info link missing');
    }
    if([390,1440].includes(width)&&['/','/ferry/','/booking/japan-cruise/','/guide/busan-shimonoseki-ferry/','/japan/tokyo/'].includes(pathname)){
     const name=(pathname==='/'?'home':pathname.split('/').filter(Boolean).join('-'))+'-'+width+'.png';
     await page.screenshot({path:OUT+'/'+name,fullPage:false,animations:'disabled'});
     report.screenshots.push(name);
    }
    // Header interaction representative samples of both header implementations.
    if([390,768,1440].includes(width) &&
       ['/','/booking/japan-cruise/','/guide/busan-shimonoseki-ferry/','/japan/tokyo/','/things-to-do/cruise-ports/'].includes(pathname)){
     if(state.hasHome){
      const btn=page.locator('.nf246-header .menu-toggle');
      if(width<1200){
       await btn.click();
       assert(await btn.getAttribute('aria-expanded')==='true','Home mobile menu not expanded');
       const nav=page.locator('#nf-mobile-menu');
       assert(await nav.getAttribute('aria-hidden')==='false','Open home menu hidden');
       await page.keyboard.press('Escape');
       assert(await btn.getAttribute('aria-expanded')==='false','Home Escape does not close menu');
      }
     }else{
      const btn=page.locator('.nf301-header .nf301-toggle');
      if(width<1200){
       await btn.click();
       assert(await btn.getAttribute('aria-expanded')==='true','Shared menu not expanded');
       await page.keyboard.press('Escape');
       assert(await btn.getAttribute('aria-expanded')==='false','Shared Escape does not close menu');
      }else assert(!(await btn.isVisible()),'Shared mobile toggle visible desktop');
     }
    }
    report.checks.push({pathname,width,passed:issues.length===0,issues});
   }catch(e){issues.push('Browser exception '+String(e).slice(0,500));report.checks.push({pathname,width,passed:false,issues})}
   for(const item of issues)fail(pathname+' @ '+width+': '+item);
   await page.close();
  }
 }
 // Real connected journey: homepage CTA -> selector -> one original destination guide.
 const home=await browser.newPage({viewport:{width:390,height:850},reducedMotion:'reduce'});
 try{
  await home.goto(ORIGIN+'/',{waitUntil:'domcontentloaded',timeout:30000});
  const start=home.locator('.nf246-hero .nf-action-sub');
  check(await start.getAttribute('href')==='#find-sea-route','Hero CTA no longer scrolls to finder');
  await start.click();
  check(new URL(home.url()).hash==='#find-sea-route','Hero CTA anchor click broken');
  const finder=home.locator('[data-nf247-finder]');
  const first=await finder.locator('[data-nf247-card]:not([hidden])').count();
  check(first===4,'Default four Busan route cards not rendered');
  await finder.locator('[data-nf247-origin="japan"]').click();
  await finder.locator('[data-nf247-type="coastal"]').click();
  const coastal=await finder.locator('[data-nf247-card]:not([hidden])').count();
  check(coastal===4,'Japan coastal selection not working');
  const href=await finder.locator('.nf247-card:not([hidden]) .nf247-guide').first().getAttribute('href');
  check(href==='/okinawa/zamami-aka-ferry/','Japan coastal guide destination changed');
  await finder.locator('.nf247-card:not([hidden]) .nf247-guide').first().click();
  check(new URL(home.url()).pathname==='/okinawa/zamami-aka-ferry/','Domestic route card did not reach original guide');
  report.flows.push({name:'hero → selector → coastal ferry guide',passed:href==='/okinawa/zamami-aka-ferry/'});
 }catch(err){fail('Coastal booking/guide navigation flow '+String(err).slice(0,350))}
 await home.close();
 // International booking trust: go from route finder card to content, then existing official information handoff.
 const intPage=await browser.newPage({viewport:{width:390,height:850},reducedMotion:'reduce'});
 try{
  await intPage.goto(ORIGIN+'/',{waitUntil:'domcontentloaded'});
  const route=intPage.locator('.nf247-card[data-nf247-from="busan"][data-nf247-kind="international"]');
  const shimo=route.filter({hasText:'부산 → 시모노세키'});
  const href=await shimo.locator('.nf247-booking').getAttribute('href');
  check(href==='https://www.kampuferry.co.jp/news/20261027systemmaintenance.html','Outbound restart notice URL changed');
  check((await shimo.locator('.nf247-booking').textContent()).includes('재개'),'Restart button label inaccurate');
  await shimo.locator('.nf247-guide').click();
  check(new URL(intPage.url()).pathname==='/guide/busan-shimonoseki-ferry/','Busan international route guide broken');
  check(await intPage.locator('a[href="https://www.kampuferry.co.jp/reserve/"]').count()>0,'Guide lacks official booking information');
  report.flows.push({name:'Busan → Shimonoseki → official operator reservation guidance',passed:true});
 }catch(err){fail('Kampu official navigation flow '+String(err).slice(0,360))}
 await intPage.close();
 // Existing card image and link validity under new editorial treatment.
 const cards=await browser.newPage({viewport:{width:1440,height:950},reducedMotion:'reduce'});
 try{
  await cards.goto(ORIGIN+'/',{waitUntil:'domcontentloaded'});
  const count=await cards.locator('.v65-destinations .v65-card').count();
  const themes=await cards.locator('.v63-theme-section .v63-card').count();
  check(count===8&&themes===6,'Editorial cards 8/6 counts changed');
  const image=cards.locator('.v65-destinations .v65-photo img').first();
  await image.scrollIntoViewIfNeeded();
  await image.waitFor({state:'visible',timeout:15000});
  await image.evaluate(el=>{el.loading='eager'});
  const photoLoaded=await cards.waitForFunction(()=>{
   const el=document.querySelector('.v65-destinations .v65-photo img');
   return !!(el&&el.complete&&el.naturalWidth>0);
  },null,{timeout:15000}).then(()=>true).catch(()=>false);
  check(photoLoaded,'First editorial destination image failed to load after 15s');
  check((await cards.locator('.v65-destinations .nf248-photo-note a').getAttribute('href'))==='#nf-v148-photo-credits','Photo credit disclosure missing');
  report.flows.push({name:'V248 editorial cards + image credits',passed:count===8&&themes===6});
 }catch(err){fail('Destination/theme card image flow '+String(err).slice(0,360))}
 await cards.close();
}finally{await browser.close()}
if(runtimeEvents.length)report.warnings.push({kind:'page_runtime_exceptions_observed',count:runtimeEvents.length,examples:runtimeEvents.slice(0,8)});
report.passed=report.errors.length===0;
fs.writeFileSync(OUT+'/browser-audit.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({passed:report.passed,checks:report.checks.length,passedChecks:report.checks.filter(r=>r.passed).length,
 flowCount:report.flows.length,screenshots:report.screenshots.length,errors:report.errors.slice(0,35),runtimeWarnings:runtimeEvents.length},null,2));
if(!report.passed)process.exitCode=1;
