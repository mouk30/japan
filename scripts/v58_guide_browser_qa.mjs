import { chromium } from 'playwright';
import {mkdir,stat,writeFile} from 'node:fs/promises';
import {join} from 'node:path';
const base='http://127.0.0.1:8758';
const out='audit-reports/v58';
await mkdir(out,{recursive:true});
const guides=[
 {key:'maeda',url:'/things-to-do/okinawa-cape-maeda/',need:['마에다곶·푸른동굴','청색','황색','적색','마에다곶 공식 한국어 안내'],image:'/images/editorial/okinawa-cape-maeda.webp',outLink:'https://www.maedamisaki.jp/ko/'},
 {key:'fujiq',url:'/practical/fujiq-highland-guide/',need:['무료 입장권','원데이패스','후지큐하이랜드역','공식 티켓 종류'],image:'/images/venues/fujiq-highland-panorama-ccby2.webp',outLink:'https://www.fujiq.jp/en/ticket/'},
 {key:'tsushima',url:'/japan/tsushima-food/',need:['아나고','돈짱','이리야키','로쿠베','대마도 관광물산협회'],image:null,outLink:'https://www.discover-nagasaki.com/en/featured-topics/about-tsushima'}
];
const errors=[],checks=[];
const browser=await chromium.launch({headless:true});
try {
 for(const g of guides)for(const width of [320,390,768,1440]){
  const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
  const name=g.key+'-'+width;
  try {
   await page.goto(base+g.url,{waitUntil:'domcontentloaded',timeout:24000});
   await page.waitForSelector('h1',{timeout:10000});
   const data=await page.evaluate(()=>({scrollWidth:document.documentElement.scrollWidth,innerWidth:window.innerWidth}));
   if(data.scrollWidth>data.innerWidth+2)errors.push(name+': overflow '+data.scrollWidth);
   const pageText=await page.locator('main').innerText();
   for(const text of g.need)if(!pageText.includes(text))errors.push(name+': missing text '+text);
   if(!await page.locator('a[href="'+g.outLink+'"]').count())errors.push(name+': missing official link '+g.outLink);
   if(g.image){
    const el=page.locator('img[src="'+g.image+'"]').first();
    if(!await el.count())errors.push(name+': wrong cover image');
    else{
     await el.scrollIntoViewIfNeeded();
     try{await el.evaluate(async x=>{if(!x.complete)await new Promise((resolve,reject)=>{x.addEventListener('load',resolve,{once:true});x.addEventListener('error',()=>reject(new Error('image error')),{once:true});setTimeout(()=>reject(new Error('image load timeout')),12000)});if(!x.naturalWidth)throw Error('image zero width')},{timeout:16000});}
     catch(e){errors.push(name+': cover image failed '+String(e).slice(0,100))}
    }
   }
   if(g.key==='tsushima'){
    for(const bad of ['/images/food.jpg','/images/local.jpg','/images/couple.jpg']){
      if(await page.locator('main img[src="'+bad+'"]').count())errors.push(name+': unrelated stock photo '+bad);
    }
    if(await page.locator('.v58-ts-dish').count()!==4)errors.push(name+': expected 4 actual dishes');
   }
   if(width===390||width===1440){
    await page.locator('h1').scrollIntoViewIfNeeded();
    await page.screenshot({path:out+'/'+g.key+'-'+width+'.png'});
   }
   checks.push({name,scrollWidth:data.scrollWidth,viewport:data.innerWidth});
  }catch(e){errors.push(name+': '+String(e).slice(0,250))}
  finally{await page.close()}
 }
}finally{await browser.close()}
const report={checkedAt:new Date().toISOString(),guides:guides.length,checks:checks.length,errors,passed:errors.length===0};
await writeFile(out+'/browser-qa.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));if(errors.length)process.exitCode=1;
