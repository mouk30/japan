import {chromium} from 'playwright';
import {mkdir,writeFile} from 'node:fs/promises';
const slugs=['japan-bamboo-grove-ecology','taiko-japanese-drumming','japan-kyoto-gion-festival-floats','japan-jizo-roadside-statues','japanese-vending-machine-culture'];
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
const out='audit-reports/v34';await mkdir(out,{recursive:true});
let rows=[];
for(const slug of slugs){
 for(const [viewport,width,height] of [['mobile',390,844],['desktop',1365,900]]){
  const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
  let errors=[],data={};
  try{
   const resp=await page.goto('http://127.0.0.1:8765/things-to-do/'+slug+'/',{waitUntil:'domcontentloaded',timeout:30000});
   data=await page.evaluate(()=>{
    const pic=document.querySelector('main img[src*="/images/culture-verified/"]');
    const credit=document.querySelector('.v34-photo-credit');
    const rect=pic?.getBoundingClientRect();
    const hasLink=credit?.querySelector('a[href*="commons.wikimedia.org/wiki/File:"]');
    return {img:pic?.getAttribute('src'),complete:pic?.complete,naturalWidth:pic?.naturalWidth,
     photoWidth:Math.round(rect?.width||0),photoHeight:Math.round(rect?.height||0),credits:!!credit&&!!hasLink,
     og:document.querySelector('meta[property="og:image"]')?.content,
     canvasWidth:document.documentElement.scrollWidth,canonical:document.querySelector('link[rel="canonical"]')?.href};
   });
   if(resp?.status()!==200)errors.push('HTTP_'+resp?.status());
   if(!data.img||!data.complete||!data.naturalWidth)errors.push('PHOTO_NOT_LOADED');
   if(!data.credits)errors.push('ATTRIBUTION_MISSING');
   if(!data.og?.includes('/images/culture-verified/'+slug+'.webp'))errors.push('OG_NOT_UPDATED');
   if(data.canvasWidth>width+3)errors.push('MOBILE_OVERFLOW_'+data.canvasWidth);
   if(!data.canonical?.includes('/things-to-do/'+slug+'/'))errors.push('CANONICAL_WRONG');
   if(data.photoWidth<200||data.photoHeight<100)errors.push('HERO_TOO_SMALL');
   if(viewport==='mobile')await page.screenshot({path:out+'/'+slug+'-mobile.png',fullPage:false});
  }catch(e){errors.push('ERR_'+String(e).slice(0,180))}
  rows.push({slug,viewport,errors,data});
  await page.close();
 }
}
await browser.close();
const summary={views:rows.length,passed:rows.filter(x=>!x.errors.length).length,failed:rows.filter(x=>x.errors.length).length,issues:rows.filter(x=>x.errors.length).map(x=>({slug:x.slug,viewport:x.viewport,errors:x.errors}))};
await writeFile(out+'/render-qa.json',JSON.stringify({summary,rows},null,2));
console.log('V34_CULTURE_RENDER_QA '+JSON.stringify(summary));
if(summary.failed)process.exitCode=1;
