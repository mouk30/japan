import { chromium } from 'playwright';
import {readdir,mkdir,writeFile,readFile} from 'node:fs/promises';
import path from 'node:path';
const root='site/things-to-do', folders=(await readdir(root,{withFileTypes:true})).filter(x=>x.isDirectory()&&x.name.includes('cruise'));
const base=process.env.LOCAL_BASE_URL||'http://127.0.0.1:8765';
const out='audit-reports/v23';await mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
const results=[];
for(const dir of folders){
  try{await readFile(path.join(root,dir.name,'index.html'))}catch{continue}
  if(dir.name==='cruise-ports')continue;
  const companion=/cruise-(family|couple|parents)-guide$/.test(dir.name);
  for(const [viewport,width,height] of [['mobile',390,844],['desktop',1365,900]]){
    const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
    const errors=[];let data=null;
    try{
      const response=await page.goto(base+'/things-to-do/'+dir.name+'/',{waitUntil:'domcontentloaded',timeout:22000});
      if(!response?.ok())errors.push('HTTP_'+response?.status());
      if(companion){await page.locator('#ct-topic-dashboard .ct-grid > .ct-card .ct-photo img').first().scrollIntoViewIfNeeded({timeout:9000}).catch(()=>{});}
      await page.evaluate(async()=>{await Promise.all([...document.querySelectorAll('main article img')].map(img=>img.complete?Promise.resolve():new Promise(resolve=>{img.addEventListener('load',resolve,{once:true});img.addEventListener('error',resolve,{once:true});setTimeout(resolve,3000)})));});
      data=await page.evaluate((companion)=>{
        const heading=document.querySelector('main article h1');
        const hero=document.querySelector('main article > header img.cover, main article > header img.hero-img, main article > header figure img[src*="/images/editorial/"]');
        const gallery=document.querySelector('#ct-topic-dashboard');
        const firstPhoto=gallery?.querySelector('.ct-grid > .ct-card .ct-photo img');
        const rect=x=>{const r=x?.getBoundingClientRect();return r?{top:r.top+scrollY,bottom:r.bottom+scrollY,width:r.width,height:r.height}:null};
        return {heading:rect(heading),hero:rect(hero),gallery:rect(gallery),firstPhoto:rect(firstPhoto),
          heroOk:!!hero&&hero.complete&&hero.naturalWidth>0,
          firstPhotoOk:!companion||(!!firstPhoto&&firstPhoto.complete&&firstPhoto.naturalWidth>0),
          imageCount:document.querySelectorAll('main article img').length,
          broken:[...document.querySelectorAll('main article img')].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.getAttribute('src')).slice(0,12),
          overflow:document.documentElement.scrollWidth>innerWidth+3,
          overflowNodes:[...document.querySelectorAll('main article *')].filter(e=>e.getBoundingClientRect().right>innerWidth+3).slice(0,5).map(e=>({tag:e.tagName,cls:String(e.className).slice(0,90),right:Math.round(e.getBoundingClientRect().right)}))
        };
      },companion);
      if(!data.heading||!data.hero||!data.heroOk)errors.push('HERO_MISSING_OR_BROKEN');
      if(data.hero&&data.heading&&data.hero.top<data.heading.bottom-3)errors.push('HERO_BEFORE_HEADING');
      if(data.hero&&(data.hero.width<100||data.hero.height<100))errors.push('HERO_TOO_SMALL');
      if(companion){
        if(!data.gallery||!data.firstPhoto||!data.firstPhotoOk)errors.push('COMPANION_PHOTO_MISSING_OR_BROKEN');
        if(data.gallery&&data.hero&&data.gallery.top<data.hero.bottom-3)errors.push('GALLERY_BEFORE_HERO');
      }
      if(data.broken.length)errors.push('BROKEN_IMAGE');
      if(data.overflow)errors.push('HORIZONTAL_OVERFLOW');
    }catch(e){errors.push('RUN_ERROR');data={message:String(e.message).slice(0,250)}}
    results.push({page:dir.name,viewport,errors,data});
    await page.close();
  }
}
await browser.close();
const report={pages:results.length/2,cases:results.length,passed:results.filter(x=>!x.errors.length).length,failed:results.filter(x=>x.errors.length).length,failures:results.filter(x=>x.errors.length).map(x=>({page:x.page,viewport:x.viewport,errors:x.errors,detail:x.data?.message,broken:x.data?.broken,overflowNodes:x.data?.overflowNodes}))};
await writeFile(path.join(out,'image-qa.json'),JSON.stringify(report,null,2)+'\n');
await writeFile(path.join(out,'details.json'),JSON.stringify(results,null,2)+'\n');
console.log('V23_IMAGE_QA',JSON.stringify(report));
if(report.failed)process.exitCode=1;
