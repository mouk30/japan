/* V252: all 220 Tokyo hub photos decoded in a real Chromium renderer,
   plus editorial-placeholder regression and responsive spot screenshots. */
import fs from 'node:fs';
import {chromium} from 'playwright';
const BASE='http://127.0.0.1:8772';
const DIR='audit-reports/v252';
fs.mkdirSync(DIR,{recursive:true});
const PHOTO_SELECTOR='.tky-card .tky-card-photo img';
const formerSvgSlugs=[
'donki-taxfree-passport','loft-stationery-gifts','muji-ginza-4f-taxfree',
'muji-ginza-food-b1','odaiba-kirakira-donki','sugamo-jizo-shopping',
'tokyo-drugstore-cosmetics','tokyo-drugstore-sun-care',
'tokyo-food-allergy-japanese','tokyo-hands-diy-gifts','tokyo-kbeauty-vs-jcosmetic',
'tokyo-kissaten-retro-cafe','tokyo-lastday-taxfree-baggage',
'tokyo-melonpan-bakery','tokyo-soba-vs-udon','tokyo-subway-ticket-24-48-72',
'tokyo-toddler-underfive','tokyo-winter-illumination-evening',
'disneysea-rapunzel-lantern','disneysea-soaring-flight','disney-fantasy-springs-hotel'];
const browser=await chromium.launch({headless:true,executablePath:process.env.NF252_BROWSER_PATH||undefined,args:['--no-sandbox']});
const reports=[],issues=[],screenshots=[];
try{
 for(const width of [390,1440]){
  const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
  const runtime=[];
  page.on('pageerror',error=>runtime.push(String(error)));
  try{
   const response=await page.goto(BASE+'/japan/tokyo/',{waitUntil:'domcontentloaded',timeout:60000});
   if(response?.status()!==200)issues.push('Tokyo HTTP '+response?.status());
   const result=await page.evaluate(async selector=>{
    const imgs=Array.from(document.querySelectorAll(selector));
    imgs.forEach(img=>img.loading='eager');
    const outcomes=await Promise.all(imgs.map(async (img,i)=>{
     try{
      await Promise.race([img.decode(),new Promise((_,reject)=>setTimeout(()=>reject(new Error('decode timeout')),25000))]);
      const rect=img.getBoundingClientRect();
      return {i,src:img.getAttribute('src'),ok:img.naturalWidth>0&&img.naturalHeight>0,
       width:img.naturalWidth,height:img.naturalHeight,alt:img.alt||'',renderedWidth:rect.width,
       parent:img.closest('a.tky-card')?.getAttribute('href')||''};
     }catch(e){return {i,src:img.getAttribute('src'),ok:false,error:String(e),parent:img.closest('a.tky-card')?.getAttribute('href')||''}}
    }));
    return {count:imgs.length,outcomes,overflow:document.documentElement.scrollWidth-innerWidth,
     title:document.title,canonical:document.querySelector('link[rel=canonical]')?.href,
     oldSVG:imgs.filter(img=>img.getAttribute('src')?.endsWith('.svg')).length};
   },PHOTO_SELECTOR);
   if(result.count!==220)issues.push(width+'px: '+result.count+' photos, expected 220');
   if(result.oldSVG)issues.push(width+'px: '+result.oldSVG+' SVG placeholders');
   if(result.overflow>2)issues.push(width+'px overflow '+result.overflow);
   if(!result.title||!result.canonical?.includes('/japan/tokyo/'))issues.push('Tokyo SEO head missing');
   const broken=result.outcomes.filter(o=>!o.ok||!o.alt||o.renderedWidth<20);
   if(broken.length)issues.push(width+'px: broken decoded photos '+JSON.stringify(broken.slice(0,20)));
   for(const slug of formerSvgSlugs){
    const photo=result.outcomes.find(x=>x.parent==='/japan/tokyo/'+slug+'/');
    if(!photo||!photo.ok||photo.src.endsWith('.svg'))issues.push(width+'px old SVG not corrected: '+slug);
   }
   for(const slug of [formerSvgSlugs[0],formerSvgSlugs[3],formerSvgSlugs[9],formerSvgSlugs[13],formerSvgSlugs[17],formerSvgSlugs[18],formerSvgSlugs[20]]){
    const card=page.locator('a.tky-card[href="/japan/tokyo/'+slug+'/"]');
    await card.scrollIntoViewIfNeeded();
    await card.locator('img').evaluate(async img=>{
     try{await img.decode()}catch(e){throw new Error('Card displayed without decoded photo: '+img.src)}
     await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
    });
    const dest=DIR+'/tokyo-'+slug+'-'+width+'.png';
    await card.screenshot({path:dest,animations:'disabled'});
    screenshots.push(dest);
   }
   if(runtime.length)issues.push(width+'px uncaught JavaScript '+runtime.slice(0,5));
   reports.push({width,count:result.count,decoded:result.outcomes.filter(o=>o.ok).length,
    oldSVG:result.oldSVG,horizontalOverflow:result.overflow,missingOrBroken:broken,consoleErrors:runtime});
   console.log('TOKYO_WIDTH',width,'decoded',result.outcomes.filter(o=>o.ok).length,'/',result.count,'broken',broken.length);
  }catch(e){issues.push(width+'px browser exception '+String(e).slice(0,550))}
  finally{await page.close()}
 }
}finally{await browser.close()}
const out={version:'V252',passed:!issues.length,checks:reports,replacedEditorialSlugs:formerSvgSlugs,
 screenshots,errors:issues};
fs.writeFileSync(DIR+'/tokyo-220-browser-photo-audit.json',JSON.stringify(out,null,2)+'\n');
console.log('V252_TOKYO_BROWSER',JSON.stringify({passed:out.passed,screenshots:screenshots.length,
 imageChecks:reports.map(r=>({width:r.width,total:r.count,decoded:r.decoded,svg:r.oldSVG})),issues:issues.slice(0,14)},null,2));
if(issues.length)process.exitCode=1;
