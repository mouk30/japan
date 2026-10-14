import { chromium } from 'playwright';
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';
const origin = process.env.LOCAL_BASE_URL || 'http://127.0.0.1:8765';
const suites=[
 {slug:'couple',url:'/couple/',cardSelector:'.dircard',expected:30,unique:30},
 {slug:'shopping',url:'/shopping/',cardSelector:'.dircard',expected:20,unique:20},
 {slug:'practical',url:'/practical/',cardSelector:'.dircard',expected:34,unique:34},
 {slug:'companions',url:'/things-to-do/travel-companions/',cardSelector:'.guide-card',expected:45,unique:0}
];
const out='audit-reports/v28';await mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
const all=[];
for(const t of suites){
 for(const [vp,width,height] of [['mobile',390,844],['tablet',768,1024],['desktop',1365,900]]){
  const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
  let status=0, errors=[],data={};
  try{
   const response=await page.goto(origin+t.url,{waitUntil:'domcontentloaded',timeout:30000});
   status=response?.status()??0;
   await page.evaluate(()=>document.querySelectorAll('img').forEach(img=>{img.loading='eager';}));
   await page.waitForFunction(()=>[...document.images].every(img=>img.complete),undefined,{timeout:18000}).catch(()=>{});
   await page.waitForTimeout(400);
   data=await page.evaluate((selector)=>{
    const cards=[...document.querySelectorAll(selector)];
    const thumbs=cards.map(card=>card.querySelector('img')).filter(Boolean);
    const pageImgs=[...document.querySelectorAll('img')];
    const broken=pageImgs.filter(x=>!x.complete||x.naturalWidth===0).map(x=>x.getAttribute('src'));
    const main=document.querySelectorAll('main').length;
    const grid=document.querySelector('.hub-main .dirgrid,.guide-grid');
    const heroCard=cards[0];
    const photo=heroCard?.querySelector('img');
    const rect=photo?.getBoundingClientRect();
    return {
      total:cards.length,photoCards:thumbs.length,uniqueSources:new Set(thumbs.map(img=>img.getAttribute('src'))).size,
      duplicates:thumbs.length-new Set(thumbs.map(img=>img.getAttribute('src'))).size,
      firstPhotoWidth:Math.round(rect?.width||0),firstPhotoHeight:Math.round(rect?.height||0),
      gridCols:grid?getComputedStyle(grid).gridTemplateColumns.split(' ').length:0,
      scrollWidth:document.documentElement.scrollWidth,viewport:innerWidth,
      mainCount:main,broken,emojiCards:document.querySelectorAll('.card-theme-icon').length,
      maxCardWidth:Math.round(Math.max(0,...cards.map(c=>c.getBoundingClientRect().width))),
    };
   },t.cardSelector);
   if(status!==200)errors.push('HTTP_'+status);
   if(data.total!==t.expected)errors.push('WRONG_CARD_COUNT');
   if(data.photoCards!==t.expected)errors.push('MISSING_CARD_PHOTO');
   if(t.unique&&data.uniqueSources!==t.unique)errors.push('DUPLICATE_CARD_IMAGES');
   if(data.broken.length)errors.push('BROKEN_IMAGES');
   if(data.scrollWidth>width+3)errors.push('HORIZONTAL_OVERFLOW');
   if(data.mainCount!==1)errors.push('MAIN_SEMANTICS');
   if(t.slug==='companions'&&data.emojiCards)errors.push('EMOJI_CARDS_REMAIN');
   if(data.firstPhotoWidth>width+3)errors.push('OVERSIZE_CARD_IMAGE');
   if(t.slug!=='companions'&&vp==='desktop'&&data.gridCols!==3)errors.push('MISSING_DESKTOP_GRID');
   if(t.slug!=='companions'&&vp==='mobile'&&data.gridCols!==1)errors.push('MISSING_MOBILE_GRID');
   if(vp!=='tablet')await page.screenshot({path:path.join(out,t.slug+'-'+vp+'.png'),fullPage:false});
  }catch(e){errors.push('EXCEPTION: '+String(e).slice(0,200))}
  all.push({page:t.slug,viewport:vp,width,status,data,errors});
  await page.close();
 }
 const file='dist'+t.url+'index.html';
 if(!existsSync(file))all.push({page:t.slug,viewport:'static',errors:['MISSING_BUILT_PAGE: '+file]});
 const s=await readFile('site'+t.url+'index.html','utf8');
 const links=[...s.matchAll(/<a\b[^>]*href="(\/[^"?#]+\/)"[^>]*>/g)].map(x=>x[1]);
 const missing=[...new Set(links)].filter(h=>!existsSync('dist'+h+'index.html'));
 if(missing.length)all.push({page:t.slug,viewport:'links',errors:['BROKEN_LOCAL_LINKS: '+missing.join(', ')]});
}
await browser.close();
let errors=all.filter(x=>x.errors?.length);let stats={cases:12,passed:12-errors.filter(x=>x.viewport!=='static'&&x.viewport!=='links').length,failed:errors.length,errors:errors.slice(0,30)};
await writeFile(path.join(out,'result.json'),JSON.stringify({stats,all},null,2));
console.log('V28_HUB_QA '+JSON.stringify(stats));
if(errors.length)process.exitCode=1;
