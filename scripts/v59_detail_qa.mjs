import {chromium} from 'playwright';
import {mkdir,writeFile,stat} from 'node:fs/promises';
import path from 'node:path';
const base=process.env.V59_SITE_ORIGIN || 'http://127.0.0.1:8759';
const reports='audit-reports/v59';
await mkdir(reports,{recursive:true});
const slugs=[
'/things-to-do/beppu-port-onsen-day-trip/',
'/things-to-do/akita-nyuto-onsen-beech-forest/',
'/things-to-do/hanami-japanese-cherry-blossom-picnic/',
'/things-to-do/momijigari-japanese-autumn-leaves-culture/',
'/japan/shimonoseki-market/',
'/things-to-do/kyoto-nishiki-market-food-etiquette/',
'/things-to-do/japan-yakushima-ancient-cedars/',
'/things-to-do/japan-forest-bathing-shinrin-yoku/'
];
const errors=[],checks=[],broken=[];
const browser=await chromium.launch({headless:true});
try{
for(const slug of slugs){
 for(const width of [390,1440]){
  const page=await browser.newPage({viewport:{width,height:910},deviceScaleFactor:1});
  try{
   await page.goto(base+slug,{waitUntil:'domcontentloaded',timeout:25000});
   const root=page.locator('#v59-practical-guide');
   if(await root.count()!==1)errors.push(slug+': module missing/duplicated');
   const count=await root.locator('.v59-route li').count();
   if(count!==3)errors.push(slug+': expected 3 steps got '+count);
   const links=await root.locator('a[href]').evaluateAll(el=>el.map(x=>({href:x.getAttribute('href'),text:x.innerText})));
   const off=links.filter(x=>x.href?.startsWith('https://'));
   const inside=links.filter(x=>x.href?.startsWith('/'));
   if(!off.length||!inside.length)errors.push(slug+': missing official/internal sources');
   for(const entry of inside){
    const dest=entry.href.split('#')[0].split('?')[0];
    try{await stat(path.join('site',dest,'index.html'))}catch{broken.push({slug,href:entry.href})}
   }
   const size=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,width:innerWidth}));
   if(size.scroll>size.width+2)errors.push(slug+': horizontal overflow '+width+' '+size.scroll);
   const visible=await root.isVisible();
   if(!visible)errors.push(slug+': V59 details not visible '+width);
   if(width===390){
    await root.scrollIntoViewIfNeeded();
    await page.screenshot({path:path.join(reports,slug.split('/').filter(Boolean).at(-1)+'-mobile.png')});
   }
   const photo=page.locator('main img').first();
   if(await photo.count()){
    try{await photo.scrollIntoViewIfNeeded();await photo.evaluate(async el=>{
      if(!el.complete)await new Promise((resolve,reject)=>{el.addEventListener('load',resolve,{once:true});el.addEventListener('error',()=>reject(new Error('load error')),{once:true});setTimeout(()=>reject(new Error('timeout')),8000)});
      if(!el.naturalWidth)throw new Error('naturalWidth zero');
    });}catch(e){errors.push(slug+': primary image failed to render: '+String(e).slice(0,140))}
   }
   checks.push({slug,width,steps:count,official:off.length,internal:inside.length,scrollWidth:size.scroll});
  }catch(e){errors.push(slug+': '+String(e).slice(0,220))}
  finally{await page.close()}
 }
}
}finally{await browser.close()}
const summary={tested_at:new Date().toISOString(),pages:slugs.length,viewports:[390,1440],checks,broken_internal_links:broken,errors,passed:!broken.length&&!errors.length};
await writeFile(path.join(reports,'browser-qa.json'),JSON.stringify(summary,null,2)+'\n');
console.log(JSON.stringify({passed:summary.passed,pages:summary.pages,viewports:checks.length,broken,errors},null,2));
if(!summary.passed)process.exitCode=1;
