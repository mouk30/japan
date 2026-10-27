/* V249 responsive nav/tap/readability regression: real built homepage + V301 pages. */
import fs from 'node:fs';
import path from 'node:path';
import {chromium} from 'playwright';
const OUT='audit-reports/v249';
fs.mkdirSync(OUT,{recursive:true});
const source=fs.readFileSync('site/index.html','utf8');
const built=fs.readFileSync('dist/index.html','utf8');
const errors=[], warnings=[];
const check=(ok,msg)=>{if(!ok)errors.push(msg)};
const href='<link rel="stylesheet" href="/nf-v249-mobile-consistency.css?v=20261027">';
const script='<script src="/nf-v249-mobile-consistency.js?v=20261027" defer></script>';
check(source.includes(href)&&built.includes(href),'Homepage CSS missing');
check(source.includes(script)&&built.includes(script),'Homepage JS missing');
check((built.match(/nf-v249-mobile-consistency.css\?v=20261027/g)||[]).length===1,'Homepage CSS included more than once');
check(built.includes('class="site-header nf246-header"'),'V246 header overwritten in build');
check(built.includes('data-nf247-finder'),'V247 route finder missing');
check((built.match(/<article class="v65-card/g)||[]).length===8,'V248 destination cards missing');
check((built.match(/<article class="v63-card/g)||[]).length===6,'V248 theme cards missing');
check((built.match(/<h1\b/g)||[]).length===1,'Homepage h1 changed');
function get(h,re){return h.match(re)?.[1]||''}
for(const [name,re] of [['title',/<title>([^<]+)<\/title>/],['canonical',/<link rel="canonical" href="([^"]+)"/],['description',/<meta name="description" content="([^"]+)"/]]){
 check(get(source,re)===get(built,re),name+' changed by build');
}
const navPages=[];
function scan(d){
 for(const e of fs.readdirSync(d,{withFileTypes:true})){
  const p=path.join(d,e.name);
  if(e.isDirectory())scan(p);
  else if(e.name.endsWith('.html')){
   const html=fs.readFileSync(p,'utf8');
   if(html.includes('class="site-header nf301-header"')){
    navPages.push(path.relative('dist',p).replace(/\\/g,'/'));
    const n=(html.match(/nf-v249-mobile-consistency.css\?v=20261027/g)||[]).length;
    if(n!==1)errors.push('V301 CSS count '+n+' at '+p);
   }
  }
 }
}
scan('dist');
check(navPages.length>=900,'Expected production shared headers missing: '+navPages.length);
const samples=['/','/japan/tokyo/','/ferry/','/guide/busan-shimonoseki-ferry/','/things-to-do/cruise-ports/','/booking/japan-cruise/'];
const widths=[320,360,390,430,650,768,1024,1150,1199,1200,1440];
const report={generatedAt:new Date().toISOString(),homepageCases:[],sharedCases:[],navPages:navPages.length,checks:{v246:true,v247:true,v248:true},screenshots:[],errors:[],warnings};
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
try{
 for(const width of widths){
  const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1,reducedMotion:'reduce'});
  const issues=[];const assert=(x,why)=>{if(!x)issues.push(why)};
  try{
   const response=await page.goto('http://127.0.0.1:8766/',{waitUntil:'domcontentloaded',timeout:30000});
   assert(response?.status()===200,'Homepage HTTP '+response?.status());
   const metrics=await page.evaluate(()=>{
    const header=document.querySelector('.nf246-header'),
      toggle=header.querySelector('.menu-toggle'),menu=header.querySelector('#nf-mobile-menu'),
      photo=document.querySelector('.v65-destinations .v65-photo'),
      p=document.querySelector('.v65-destinations .v65-info p');
    return {doc:document.documentElement.scrollWidth,viewport:innerWidth,
     btnVisible:getComputedStyle(toggle).display!=='none',
     navVisible:getComputedStyle(header.querySelector('.desktop-nav')).display!=='none',
     btnRect:toggle.getBoundingClientRect().toJSON(),btnLabel:toggle.getAttribute('aria-label'),
     descriptionSize:parseFloat(getComputedStyle(p).fontSize),
     cardCount:document.querySelectorAll('.v65-destinations .v65-card').length,
     themeCount:document.querySelectorAll('.v63-theme-section .v63-card').length,
     photoWidth:photo.getBoundingClientRect().width};
   });
   assert(metrics.doc<=width+2,'Homepage horizontal overflow '+metrics.doc);
   assert(metrics.cardCount===8&&metrics.themeCount===6,'Editorial card counts');
   const toggle=page.locator('.nf246-header .menu-toggle');
   const menu=page.locator('#nf-mobile-menu');
   if(width<=1150){
    assert(metrics.btnVisible&&!metrics.navVisible,'Mobile header/nav visibility');
    assert(metrics.btnRect.width>=47&&metrics.btnRect.height>=47,'Mobile toggle below 48px');
    assert(await menu.getAttribute('aria-hidden')==='true','Closed nav not aria-hidden');
    await toggle.click();
    assert(await toggle.getAttribute('aria-expanded')==='true','Toggle did not expand');
    assert(await toggle.getAttribute('aria-label')==='메뉴 닫기','Toggle aria did not update');
    assert(await page.locator('.nf246-toggle-label').innerText()==='닫기','Visible close label missing');
    assert(await menu.getAttribute('aria-hidden')==='false','Open menu aria-hidden');
    assert(await menu.locator('a[href="/booking/japan-cruise/"]').isVisible(),'Booking guide not visible');
    assert(await menu.locator('a[href="/kids/"]').isVisible(),'Kids menu not visible');
    assert(await page.evaluate(()=>document.documentElement.classList.contains('nf249-menu-open')),'Body scroll lock absent');
    const layout=await menu.evaluate(el=>{
     const links=[...el.querySelectorAll('a')];
     const box=el.getBoundingClientRect();
     return {columns:getComputedStyle(el).gridTemplateColumns,
      box:{top:box.top,bottom:box.bottom,width:box.width},
      linkMin:Math.min(...links.map(x=>x.getBoundingClientRect().height)),
      linkWidths:links.map(x=>x.getBoundingClientRect().width),
      allUrls:links.map(x=>x.getAttribute('href')),
      focused:el.contains(document.activeElement)};
    });
    assert(layout.linkMin>=47,'Mobile link target below 48px: '+layout.linkMin);
    assert(layout.focused,'Mobile opening did not focus first link');
    assert(layout.box.width<=width+2,'Menu wider than screen');
    assert(layout.allUrls.includes('/booking/japan-cruise/')&&layout.allUrls.includes('/ferry/'),'Route/menu links changed');
    const countColumns=layout.columns.split(' ').filter(Boolean).length;
    if(width<=650)assert(countColumns===1,'Small mobile must use single-column menu: '+layout.columns);
    else assert(countColumns>=2,'Tablet menu should use two columns: '+layout.columns);
    if([390,768].includes(width)){
     await page.screenshot({path:OUT+'/home-menu-open-'+width+'.png',fullPage:false});
     report.screenshots.push('home-menu-open-'+width+'.png');
    }
    // Tab cycles in the open mobile menu instead of entering the obscured page.
    await menu.locator('a').last().focus();
    await page.keyboard.press('Tab');
    assert(await toggle.evaluate(e=>document.activeElement===e),'Tab did not loop to toggle');
    await page.keyboard.press('Shift+Tab');
    assert(await menu.locator('a').last().evaluate(e=>document.activeElement===e),'Shift+Tab did not loop to last menu item');
    await page.keyboard.press('Escape');
    assert(await toggle.getAttribute('aria-expanded')==='false','Escape did not close menu');
    assert(await menu.getAttribute('aria-hidden')==='true','Escape left menu exposed');
    assert(await toggle.evaluate(e=>document.activeElement===e),'Escape did not restore toggle focus');
    assert(!await page.evaluate(()=>document.documentElement.classList.contains('nf249-menu-open')),'Escape left body scroll locked');
    assert((await page.locator('.nf246-toggle-label').innerText())==='메뉴','Closed toggle label missing');
    if(width<=650){
     assert(metrics.descriptionSize>=15.5,'Destination paragraphs too small: '+metrics.descriptionSize);
     const targets=await page.evaluate(()=>{
      const selectors=['.nf246-hero .nf-hero-actions a','.nf247-finder .nf247-links a',
       '.v65-destinations .v65-actions a:first-child','.v63-theme-section .v63-cta','.d61-home-region .d61-home-cta',
       '.v64-practical .v64-primary'];
      return Object.fromEntries(selectors.map(s=>[s,[...document.querySelectorAll(s)].slice(0,12).map(el=>Math.round(el.getBoundingClientRect().height))]));
     });
     for(const [key,heights] of Object.entries(targets)){
      assert(heights.length>0,'Missing touch buttons '+key);
      assert(heights.every(h=>h>=47),'Touch button <48px in '+key+': '+heights);
     }
    }
   }else{
    assert(!metrics.btnVisible&&metrics.navVisible,'Desktop header/nav visibility');
    if(width===1440){
     await page.screenshot({path:OUT+'/home-desktop-1440.png',fullPage:false});
     report.screenshots.push('home-desktop-1440.png');
    }
   }
   report.homepageCases.push({width,passed:issues.length===0,issues});
  }catch(err){issues.push('Browser error '+String(err).slice(0,450));report.homepageCases.push({width,passed:false,issues})}
  for(const issue of issues)errors.push('home '+width+': '+issue);
  await page.close();
 }
 // The production build replaces every non-home source header with V301.
 for(const pathname of samples.slice(1)){
  for(const width of [320,390,768,1024,1199,1200,1440]){
   const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1,reducedMotion:'reduce'});
   const issues=[];const assert=(x,why)=>{if(!x)issues.push(why)};
   try{
    const response=await page.goto('http://127.0.0.1:8766'+pathname,{waitUntil:'domcontentloaded',timeout:30000});
    assert(response?.status()===200,'HTTP '+response?.status());
    const sizes=await page.evaluate(()=>{
     const el=document.querySelector('.nf301-header');
     const toggle=el?.querySelector('.nf301-toggle');
     const cta=el?.querySelector('.nf301-mobile-cta');
     return {doc:document.documentElement.scrollWidth,
      headerCount:document.querySelectorAll('.nf301-header').length,
      toggleDisplay:toggle?getComputedStyle(toggle).display:'',
      toggleSize:toggle?.getBoundingClientRect().height||0,
      toggleWidth:toggle?.getBoundingClientRect().width||0,
      ctaSize:cta?.getBoundingClientRect().height||0};
    });
    assert(sizes.headerCount===1,'Unified header missing');
    assert(sizes.doc<=width+2,'Shared page horizontal overflow '+sizes.doc);
    if(width<1200){
     assert(sizes.toggleSize>=47&&sizes.toggleWidth>=47,'Shared toggle below 48px');
     assert(sizes.ctaSize>=47,'Shared booking CTA below 48px');
     const toggle=page.locator('.nf301-toggle'),menu=page.locator('#nf301-mobile-panel');
     await toggle.click();
     assert(await toggle.getAttribute('aria-expanded')==='true','Shared nav aria');
     assert(await menu.getAttribute('data-open')==='true','Shared nav not opened');
     if(pathname==='/japan/tokyo/'&&width===390){
      await page.screenshot({path:OUT+'/shared-tokyo-menu-390.png',fullPage:false});
      report.screenshots.push('shared-tokyo-menu-390.png');
     }
     await page.keyboard.press('Escape');
     assert(await toggle.getAttribute('aria-expanded')==='false','Shared Escape fails');
     assert(await menu.getAttribute('data-open')==='false','Shared nav stays open');
    }else{
     assert(sizes.toggleDisplay==='none','Desktop shared toggle visible');
    }
    report.sharedCases.push({pathname,width,passed:issues.length===0,issues});
   }catch(err){issues.push('Browser error '+String(err).slice(0,400));report.sharedCases.push({pathname,width,passed:false,issues})}
   for(const issue of issues)errors.push('shared '+pathname+' '+width+': '+issue);
   await page.close();
  }
 }
}finally{await browser.close()}
report.errors=errors;report.passed=errors.length===0;
fs.writeFileSync(OUT+'/qa.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({passed:report.passed,productionSharedHeaders:report.navPages,
 homepageWidths:report.homepageCases.length,sharedCases:report.sharedCases.length,
 screenshots:report.screenshots,errors:errors.slice(0,30)},null,2));
if(!report.passed)process.exitCode=1;
