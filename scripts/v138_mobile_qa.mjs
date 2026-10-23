// V138 mobile home QA. Requires locally served /site at 127.0.0.1:8757 and Playwright.
import fs from 'node:fs';
import path from 'node:path';
import {chromium} from 'playwright';
const root=process.cwd(), out=path.join(root,'audit-reports/v138');
fs.mkdirSync(out,{recursive:true});
const widths=[320,360,390,430,768,1440];
const src=fs.readFileSync(path.join(root,'site/index.html'),'utf8');
const report={version:'V138',generated_at:new Date().toISOString(),viewports:[],errors:[],source:'site/index.html',image_policy:'existing images unchanged'};
const markers=[
 '<link rel="canonical" href="https://www.nipponferry.com/">',
 '<link rel="stylesheet" href="/nf-v137-mobile-readability.css?v=20261023a">',
 '<link rel="stylesheet" href="/nf-v138-mobile-polish.css?v=20261023a">',
 '<title>일본크루즈 여행 | 가격·일정·기항지 | 일본페리</title>',
 'href="/booking/japan-cruise/"',
 'href="/things-to-do/"',
 'src="/images/kimono.jpg"',
 'id="nf-premium-title"'
];
for(const m of markers)if(!src.includes(m))report.errors.push('source marker missing: '+m);
for(const file of ['/nf-v137-mobile-readability.css','/nf-v138-mobile-polish.css','/images/kimono.jpg']){
 if(!fs.existsSync(path.join(root,'site',file)))report.errors.push('asset missing: '+file);
}
let browser;
try{
 browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 for(const width of widths){
  const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
  const problems=[];
  try{
   const res=await page.goto('http://127.0.0.1:8757/',{waitUntil:'load',timeout:45000});
   if(res.status()!==200)problems.push('http status '+res.status());
   await page.locator('.discovery-v33 .v34-feature img').evaluate(async img=>{
     img.loading='eager';try{await img.decode()}catch{}
   });
   const data=await page.evaluate(()=>{
     const rect=selector=>{
       const el=document.querySelector(selector);if(!el)return null;
       const b=el.getBoundingClientRect();return {x:b.x,y:b.y,w:b.width,h:b.height,right:b.right};
     };
     const $=s=>document.querySelector(s);
     const hero=$('.nf-premium-hero'),heading=$('#nf-premium-title'),card=$('.discovery-v33 .v34-feature');
     const photo=card?.querySelector('img');
     const nav=$('.site-header .mobile-menu');
     const navButton=$('.site-header .menu-toggle');
     return {
       viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,
       hero:{rect:rect('.nf-premium-hero'),titleRect:rect('#nf-premium-title'),
          titleFont:parseFloat(getComputedStyle(heading).fontSize),
          titleText:heading?.innerText||'',background:getComputedStyle(hero).backgroundImage,
          mainLink:hero?.querySelector('a.nf-action-main')?.getAttribute('href')},
       menu:{buttonVisible:getComputedStyle(navButton).display!=='none',
         buttonRect:rect('.site-header .menu-toggle'),navDisplay:getComputedStyle(nav).display,
         navMaxHeight:getComputedStyle(nav).maxHeight},
       content:{cardDisplay:getComputedStyle(card).display,cardDirection:getComputedStyle(card).flexDirection,
         cardRect:rect('.discovery-v33 .v34-feature'),
         photoRect:rect('.discovery-v33 .v34-feature img'),photoFit:getComputedStyle(photo).objectFit,
         photoNaturalWidth:photo?.naturalWidth||0,
         photoAlt:photo?.alt||'', cardHeading:card?.querySelector('h3')?.textContent||''},
       maritime:{columns:getComputedStyle($('.nf-v79-maritime-grid')).gridTemplateColumns,
         cardRect:rect('.nf-v79-maritime-grid .nf-maritime-card')},
       kakao:rect('.kakao-float'),
       bookingExists:!!$('a[href="/booking/japan-cruise/"]'),
       desktopNavVisible:getComputedStyle($('.desktop-nav')).display!=='none'
     };
   });
   if(data.scrollWidth>width+1)problems.push('horizontal document overflow: '+data.scrollWidth);
   if(!data.bookingExists)problems.push('booking link missing');
   if(!data.content.photoNaturalWidth)problems.push('editorial photo not loaded');
   if(!data.content.photoAlt)problems.push('editorial image alt missing');
   if(!data.hero.mainLink)problems.push('hero navigation missing');
   if(width<=650){
     if(data.hero.titleFont>41)problems.push('mobile hero title too large: '+data.hero.titleFont);
     if(data.hero.titleRect?.right>width+2)problems.push('hero title overflows screen');
     if(data.hero.rect?.h>850)problems.push('hero unexpectedly too tall: '+data.hero.rect.h);
   }
   if(width<=900){
     if(data.content.cardDisplay!=='flex'||data.content.cardDirection!=='column')problems.push('card did not switch to stacked mobile design');
     const c=data.content.cardRect,p=data.content.photoRect;
     if(!c||!p||Math.abs(c.w-p.w)>6)problems.push('photo not full width of card');
     if(!data.menu.buttonVisible)problems.push('mobile menu toggle hidden');
   }
   if(width>900&&data.content.cardDisplay!=='grid')problems.push('desktop card layout unexpectedly changed');
   if(width<=1150){
     await page.locator('.site-header .menu-toggle').click();
     const opened=await page.locator('.site-header .menu-toggle').getAttribute('aria-expanded');
     const menuOpen=await page.locator('.site-header .mobile-menu').evaluate(el=>getComputedStyle(el).display!=='none');
     if(opened!=='true'||!menuOpen)problems.push('mobile menu failed to open and sync aria-expanded');
     await page.keyboard.press('Escape');
     const closed=await page.locator('.site-header .menu-toggle').getAttribute('aria-expanded');
     if(closed!=='false')problems.push('mobile menu failed to close on Escape');
   }
   if([320,390,768,1440].includes(width)){
     await page.locator('.nf-premium-hero').screenshot({path:path.join(out,'hero-'+width+'.png'),animations:'disabled',timeout:30000});
     await page.locator('.discovery-v33 .v34-feature').screenshot({path:path.join(out,'enjoy-'+width+'.png'),animations:'disabled',timeout:30000});
   }
   report.viewports.push({width,...data,problems});
  }catch(e){problems.push('browser exception: '+String(e).slice(0,260));report.viewports.push({width,problems});}
  for(const p of problems)report.errors.push(width+'px: '+p);
  await page.close();
 }
}catch(e){report.errors.push('chromium launch: '+String(e));}
finally{if(browser)await browser.close();}
report.passed=report.errors.length===0;
fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n','utf8');
console.log(JSON.stringify({passed:report.passed,viewport_count:report.viewports.length,errors:report.errors,stats:report.viewports.map(x=>({width:x.width,title_px:x.hero?.titleFont,hero_height:x.hero?.rect?.h,photo_width:x.content?.photoRect?.w,body_scroll_width:x.scrollWidth,menu:x.menu?.buttonVisible}))},null,2));
if(!report.passed)process.exitCode=1;
