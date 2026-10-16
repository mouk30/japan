// V62 responsive browser and integrity QA: run with Playwright, local site on :8757.
import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';
const root = process.cwd();
const outDir = path.join(root, 'audit-reports/v62');
fs.mkdirSync(outDir, {recursive:true});
const widths = [320,390,768,1440];
const pages = [
 {slug:'home',uri:'/',expected:4, selector:'.d61-home-card', photoSelector:'.d61-home-card img'},
 {slug:'shimonoseki',uri:'/things-to-do/shimonoseki-one-day/',expected:2, selector:'.d61-spot',photoSelector:'.d61-spot img'},
 {slug:'tsushima',uri:'/things-to-do/tsushima-one-day/',expected:2,selector:'.d61-spot',photoSelector:'.d61-spot img'},
 {slug:'fukuoka',uri:'/things-to-do/fukuoka-one-day/',expected:3,selector:'.d61-spot',photoSelector:'.d61-spot img'},
 {slug:'osaka',uri:'/things-to-do/osaka-one-day/',expected:3,selector:'.d61-spot',photoSelector:'.d61-spot img'}
];
const expectedPhotoPaths=[
 '/images/venues/v62-karato-market-real.webp',
 '/images/venues/v62-izuhara-port-real.webp'
];
const report={generatedAt:new Date().toISOString(), widths, pages:[], errors:[], warnings:[], deployedUrl:'https://www.nipponferry.com/'};
for(const p of expectedPhotoPaths) {
 if(!fs.existsSync(path.join(root,'site',p))) report.errors.push('missing WebP: '+p);
}
let browser;
try {
 browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 for(const p of pages) for(const width of widths) {
  const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
  try {
   const response=await page.goto('http://127.0.0.1:8757'+p.uri,{waitUntil:'load',timeout:20000});
   await page.locator(p.selector).first().waitFor({timeout:10000});
   await page.evaluate(()=>{document.fonts?.ready});
   // Force offscreen lazy images to load before asserting naturalWidth.
   // The homepage regional section is below the fold at all viewport sizes.
   await page.locator(p.photoSelector).evaluateAll(async imgs=>{
     await Promise.all(imgs.map(async img=>{
       img.loading='eager';
       try { await img.decode(); } catch {}
     }));
   });
   const result=await page.evaluate(({selector,photoSelector})=>{
    const cards=[...document.querySelectorAll(selector)];
    const photos=[...document.querySelectorAll(photoSelector)];
    const isGoodLink=a=>a.getAttribute('href') && a.getAttribute('href')!=='#';
    const links=[...document.querySelectorAll(selector+' a')].filter(isGoodLink);
    const broken=photos.filter(img=>!img.complete||img.naturalWidth===0).map(img=>img.getAttribute('src'));
    const overflowing=links.filter(a=>{const box=a.getBoundingClientRect();return box.left< -1||box.right>window.innerWidth+1}).map(a=>a.getAttribute('href'));
    const canonical=document.querySelector('link[rel=canonical]')?.getAttribute('href')||'';
    return {cards:cards.length,broken,overflowing,viewport:window.innerWidth,scrollWidth:document.documentElement.scrollWidth,
     imagePaths:photos.map(img=>img.getAttribute('src')),canonical, hrefs:links.map(a=>a.getAttribute('href'))};
   }, {selector:p.selector,photoSelector:p.photoSelector});
   const errors=[];
   if(response.status()!==200) errors.push('HTTP status '+response.status());
   if(result.cards!==p.expected) errors.push('card count '+result.cards+' expected '+p.expected);
   if(result.scrollWidth>width+1) errors.push('horizontal overflow '+result.scrollWidth+' > '+width);
   if(result.overflowing.length) errors.push('overflowing buttons '+result.overflowing.join(','));
   if(result.broken.length) errors.push('broken images '+result.broken.join(','));
   if(!result.canonical.startsWith('https://www.nipponferry.com/')) errors.push('canonical invalid');
   if(p.slug==='home' && !result.imagePaths.includes(expectedPhotoPaths[0]))errors.push('Karato real photo not in homepage');
   if(p.slug==='home' && !result.imagePaths.includes(expectedPhotoPaths[1]))errors.push('Izuhara real photo not in homepage');
   for(const href of result.hrefs.filter(s=>s?.startsWith('/')&&!s.startsWith('//'))) {
     const pathname=href.split('#')[0].split('?')[0] || '/';
     const fsPath=path.join(root,'site',pathname);
     if(!fs.existsSync(path.join(fsPath,'index.html')) && !fs.existsSync(fsPath))errors.push('missing internal target '+href);
   }
   if(p.slug==='home')await page.locator('#v36-home').scrollIntoViewIfNeeded();
   else await page.locator('.d61-spot-head').scrollIntoViewIfNeeded();
   const png=path.join(outDir,p.slug+'-'+width+'.png');
   await page.screenshot({path:png,fullPage:false});
   const check={page:p.slug,width,...result,screenshot:path.relative(root,png),errors};
   report.pages.push(check);
   for(const e of errors)report.errors.push(p.slug+'-'+width+': '+e);
  } catch(e){report.errors.push(p.slug+'-'+width+': browser: '+String(e));}
  finally{await page.close();}
 }
} catch(e){report.errors.push('Browser launch failed: '+String(e));}
finally{if(browser)await browser.close();}
report.passed=report.errors.length===0;
fs.writeFileSync(path.join(outDir,'responsive-qa.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({passed:report.passed,checks:report.pages.length,errors:report.errors},null,2));
if(!report.passed)process.exitCode=1;
