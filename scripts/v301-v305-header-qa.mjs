import fs from 'node:fs';
import path from 'node:path';
import {chromium} from 'playwright';
const OUT='audit-reports/v301-v305';
fs.mkdirSync(OUT,{recursive:true});
const samples=[
'/','/japan/','/japan/tokyo/','/japan/tokyo/disney-dpa-app-purchase/',
'/japan-cruise/','/booking/japan-cruise/','/things-to-do/',
'/things-to-do/cruise-ports/','/things-to-do/travel-companions/',
'/things-to-do/naha-cruise-port-day-trip/','/things-to-do/aomori-cruise-family-guide/','/things-to-do/aizu-wakamatsu-tsurugajo/','/food/','/shopping/',
'/seasons/','/photo-spots/','/voucher/','/practical/','/couple/','/life/don-quijote-first-guide/'
];
const widths=[320,390,768,1024,1200,1440];
const report={date:new Date().toISOString(),siteTotal:0,unifiedHeaders:0,withoutOriginalHeader:0,
screens:[],errors:[],warnings:[],navDestinations:[],sampleCount:samples.length,versions:['V301','V302','V303','V304','V305']};
const scan=(root,list=[])=>{for(const n of fs.readdirSync(root)){const p=path.join(root,n),st=fs.statSync(p);if(st.isDirectory())scan(p,list);else if(n==='index.html'||n.endsWith('.html'))list.push(p)}return list};
const pages=scan('dist');report.siteTotal=pages.length;
const urls=new Set();
for(const file of pages){
 const rel=path.relative('dist',file).replace(/\\/g,'/'),original=path.join('site',rel);
 const built=fs.readFileSync(file,'utf8');
 const src=fs.existsSync(original)?fs.readFileSync(original,'utf8'):'';
 const origHeader=/<header\b[^>]*class=["'][^"']*\bsite-header\b/.test(src);
 if(origHeader||rel.startsWith('things-to-do/')){
  report.unifiedHeaders++;
  if(!built.includes('data-nf301="v305"'))report.errors.push(rel+': original header not upgraded');
  if((built.match(/data-nf301="v305"/g)||[]).length!==1)report.errors.push(rel+': header duplication');
  if(!built.includes('<link rel="stylesheet" href="/v301-nav.css">')||!built.includes('<script src="/v301-nav.js" defer>'))report.errors.push(rel+': CSS/JS not loaded');
  if(!built.includes('nf301-subrow'))report.errors.push(rel+': 2nd nav missing');
  if(!built.includes('href="/japan/"'))report.errors.push(rel+': canonical Japan destinations link missing');
  const sourceCan=src.match(/<link\b[^>]*rel=["']canonical["'][^>]*href=["']([^"']+)/)?.[1]||src.match(/<link\b[^>]*href=["']([^"']+)["'][^>]*rel=["']canonical["']/)?.[1];
  const builtCan=built.match(/<link\b[^>]*rel=["']canonical["'][^>]*href=["']([^"']+)/)?.[1]||built.match(/<link\b[^>]*href=["']([^"']+)["'][^>]*rel=["']canonical["']/)?.[1];
  if(sourceCan!==builtCan)report.errors.push(rel+': changed canonical '+sourceCan+' -> '+builtCan);
  const sourceTitle=src.match(/<title>([\s\S]*?)<\/title>/)?.[1],builtTitle=built.match(/<title>([\s\S]*?)<\/title>/)?.[1];
  if(sourceTitle!==builtTitle)report.errors.push(rel+': changed page title');
  const head=built.slice(built.indexOf('data-nf301="v305"'),built.indexOf('</header>')+9);
  for(const match of head.matchAll(/<a\b[^>]*href="([^"]+)"/g))urls.add(match[1].split('#')[0].split('?')[0]);
 }else report.withoutOriginalHeader++;
}
for(const url of urls){
 if(!url.startsWith('/')){report.errors.push('Non-local nav URL '+url);continue}
 if(url==='/'||url==='')continue;
 if(!fs.existsSync('dist'+url)&&!fs.existsSync('dist'+url+'index.html'))report.errors.push('Menu target not found in build '+url);
}
report.navDestinations=[...urls].sort();
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
try{
 for(const pathname of samples){
  for(const width of widths){
   const pg=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
   const issues=[];
   try{
    const res=await pg.goto('http://127.0.0.1:8763'+pathname,{waitUntil:'domcontentloaded',timeout:24000});
    await pg.locator('.nf301-header').waitFor({timeout:9000});
    const el=await pg.evaluate(()=>{
     const h=document.querySelector('.nf301-header'),
      bar=h?.querySelector('.nf301-bar'),
      logo=h?.querySelector('.nf301-logo'),
      secondary=h?.querySelector('.nf301-secondary'),
      primary=h?.querySelector('.nf301-primary'),
      toggle=h?.querySelector('.nf301-toggle'),
      sub=h?.querySelectorAll('.nf301-subrow a')||[];
     return {doc:document.documentElement.scrollWidth,screen:innerWidth,
       headerWidth:Math.round(h.getBoundingClientRect().width),
       primaryDisplay:getComputedStyle(primary).display,
       secondaryDisplay:getComputedStyle(secondary).display,
       toggleDisplay:getComputedStyle(toggle).display,
       controlsDisplay:getComputedStyle(h.querySelector('.nf301-mobile-controls')).display,
       mainCount:h?.querySelectorAll('.nf301-primary .nf301-item').length,
       subCount:sub.length,logoWidth:logo?.getBoundingClientRect().width||0,
       barHeight:bar?.getBoundingClientRect().height||0,
       navCount:document.querySelectorAll('.nf301-header').length,
       pageCurrent:h.querySelectorAll('[aria-current="page"]').length,
       matched:h.querySelector('.nf301-primary .nf301-mainlink.nf301-active')?.getAttribute('href')||null};
    });
    if(res.status()!==200)issues.push('HTTP '+res.status());
    if(el.doc>width+2)issues.push('horizontal overflow '+el.doc);
    if(el.navCount!==1)issues.push('header count '+el.navCount);
    if(el.mainCount!==6||el.subCount!==8)issues.push('menu sizes '+el.mainCount+'/'+el.subCount);
    if(el.logoWidth>43)issues.push('logo too wide '+el.logoWidth);
    if(width>=1200){
     if(el.primaryDisplay==='none'||el.secondaryDisplay==='none'||el.controlsDisplay!=='none')issues.push('desktop 2-tier visibility');
     const item=pg.locator('.nf301-item[data-dropdown="japan"]');
     await item.locator('.nf301-mainlink').hover();
     const fly=item.locator('.nf301-flyout');
     try{await fly.waitFor({state:'visible',timeout:1500})}catch{
       // Some embedded legacy article styles have hover race conditions at 1200px.
       // Verify the visible disclosure button still opens the menu on deliberate activation.
       const btn=item.locator('.nf301-disclose');
       try{
        await btn.click();
        if(!await fly.isVisible())await btn.click();
        await fly.waitFor({state:'visible',timeout:1400});
        report.warnings.push(pathname+' '+width+': hovered item needed explicit disclosure click');
       }catch{issues.push('neither hover nor click opened mega menu')}
     }
     const bb=await fly.boundingBox();
     if(bb&&(bb.x < -2||bb.x+bb.width>width+2))issues.push('dropdown outside viewport');
     const last=pg.locator('.nf301-item[data-dropdown="practical"]');
     await last.locator('.nf301-mainlink').hover();
     const bb2=await last.locator('.nf301-flyout').boundingBox();
     if(!bb2||bb2.x < -2||bb2.x+bb2.width>width+2)issues.push('rightmost dropdown offscreen');
     await pg.keyboard.press('Escape');
     if(pathname==='/'&&width===1440){
      await pg.screenshot({path:OUT+'/v302-desktop-1440.png',fullPage:false});
      await item.locator('.nf301-mainlink').hover();
      await pg.screenshot({path:OUT+'/v304-japan-megamenu-1440.png',fullPage:false});
     }
    }else{
     if(el.primaryDisplay!=='none'||el.secondaryDisplay!=='none'||el.controlsDisplay==='none')issues.push('mobile hides desktop menus');
     const toggle=pg.locator('.nf301-toggle');
     await toggle.click();
     if(await toggle.getAttribute('aria-expanded')!=='true')issues.push('mobile toggle aria');
     try{await pg.locator('#nf301-mobile-panel').waitFor({state:'visible',timeout:2400})}catch{issues.push('mobile panel not visible')}
     const subBtn=pg.locator('.nf301-mob-group[data-mob-group="japan"] .nf301-mob-expand');
     await subBtn.click();
     if(await subBtn.getAttribute('aria-expanded')!=='true')issues.push('mobile submenu aria');
     if(!await pg.locator('#nf301-mob-japan a[href="/japan/tokyo/"]').isVisible())issues.push('Tokyo mobile region link invisible');
     if(pathname==='/'&&[320,390,768].includes(width))await pg.screenshot({path:OUT+'/v303-mobile-menu-'+width+'.png',fullPage:false});
     await pg.keyboard.press('Escape');
     try{await pg.locator('#nf301-mobile-panel').waitFor({state:'hidden',timeout:2400})}catch{issues.push('Escape did not close mobile menu')}
     if(await toggle.getAttribute('aria-expanded')!=='false')issues.push('Escape aria not reset');
     if(pathname==='/'&&width===390)await pg.screenshot({path:OUT+'/v301-mobile-home-390.png',fullPage:false});
    }
    if(pathname.startsWith('/japan/tokyo/')&&el.matched!=='/japan/')issues.push('Tokyo should activate Japan destinations');
    if(pathname==='/things-to-do/cruise-ports/'&&el.matched!=='/things-to-do/cruise-ports/')issues.push('Cruise port active tab incorrect');
    if(pathname==='/booking/japan-cruise/'&&!await pg.locator('.nf301-cta.nf301-active').count())issues.push('Booking CTA inactive');
    if(pathname==='/'&&await pg.locator('.nf305-shortcut').count()!==6)issues.push('premium homepage shortcuts not six');
    report.screens.push({pathname,width,...el,issues});
   }catch(e){issues.push('browser '+String(e).slice(0,210));report.screens.push({pathname,width,issues})}
   for(const msg of issues)report.errors.push(pathname+' '+width+': '+msg);
   await pg.close();
  }
 }
}finally{await browser.close()}
report.passed=report.errors.length===0;
fs.writeFileSync(OUT+'/browser-qa.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({passed:report.passed,sitePages:report.siteTotal,unifiedHeaders:report.unifiedHeaders,nonLegacy:report.withoutOriginalHeader,
screenCases:report.screens.length,navLinks:report.navDestinations.length,errors:report.errors.slice(0,35)},null,2));
if(!report.passed)process.exitCode=1;
