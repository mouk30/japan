import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';

const SITE='https://www.nipponferry.com';
const OUT='audit-reports/v43';
await fs.mkdir(OUT,{recursive:true});
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
const results={site:SITE,checked_at:new Date().toISOString(),checks:[],screenshots:[],pass:false};

const cases=[{name:'mobile320',width:320,height:740},
             {name:'mobile390',width:390,height:844},
             {name:'tablet768',width:768,height:1024},
             {name:'desktop1440',width:1440,height:900}];
for(const viewport of cases){
 const page=await browser.newPage({viewport,deviceScaleFactor:1,hasTouch:viewport.width<=390,isMobile:viewport.width<=390});
 const name=viewport.name;
 const errors=[];
 page.on('pageerror',e=>errors.push(String(e).slice(0,200)));
 await page.goto(SITE+'/things-to-do/',{waitUntil:'domcontentloaded',timeout:90000});
 await page.locator('.v36-photo-card').first().scrollIntoViewIfNeeded();
 await page.locator('.v36-photo-card img').first().waitFor({state:'visible'});
 await page.waitForTimeout(1000);
 const probe=await page.evaluate(()=>{
  const cs=[...document.querySelectorAll('.v36-photo-card')];
  const first=cs[0],img=first.querySelector('img');
  const grid=first.closest('.v28-text-grid');
  const rect=first.getBoundingClientRect();
  const bounds=img.getBoundingClientRect();
  return {count:cs.length,screenWidth:innerWidth,documentWidth:document.documentElement.scrollWidth,
    columns:grid?.getBoundingClientRect().width,
    actualGridColumns:grid?getComputedStyle(grid).gridTemplateColumns.split(' ').filter(Boolean).length:null,
    firstCard:{left:rect.left,right:rect.right,width:rect.width,height:rect.height},
    firstPhoto:{width:bounds.width,height:bounds.height,naturalWidth:img.naturalWidth,naturalHeight:img.naturalHeight,
                objectFit:getComputedStyle(img).objectFit},
    loadedAboveFold:cs.slice(0,4).filter(c=>c.querySelector('img')?.naturalWidth>0).length};
 });
 const ok=(probe.count===152 && probe.documentWidth<=viewport.width+3 &&
   probe.firstCard.width>Math.min(220,viewport.width-55) &&
   probe.firstCard.left>=-2 && probe.firstCard.right<=viewport.width+3 &&
   probe.firstPhoto.naturalWidth>0 && probe.firstPhoto.height>=110 &&
   (viewport.width<=540?probe.actualGridColumns===1:true));
 const shot=path.join(OUT,name+'-culture-cards.png');
 await page.screenshot({path:shot});
 results.screenshots.push(shot);
 results.checks.push({kind:'culture-grid',viewport:name,ok,...probe,errors});
 await page.close();
}

for(const viewport of [cases[1],cases[3]]){
 const page=await browser.newPage({viewport,deviceScaleFactor:1});
 const name=viewport.name;
 await page.goto(SITE+'/',{waitUntil:'domcontentloaded',timeout:90000});
 const a=page.locator('.quick-grid a[href="/photo-spots/"]');
 const b=page.locator('a.theme-card[href="/photo-spots/"]');
 const homeLinks=(await a.count())===1&&(await b.count())===1;
 await a.click();
 await page.waitForURL('**/photo-spots/',{timeout:30000});
 await page.locator('.photo-card').first().waitFor({state:'visible',timeout:30000});
 await page.waitForTimeout(500);
 const probe=await page.evaluate(()=>{
  const cards=[...document.querySelectorAll('.photo-card')];
  return {url:location.pathname,title:document.title,
   count:cards.length,
   articleLinks:cards.map(x=>x.querySelector('a')?.getAttribute('href')),
   photoLoad:cards.map(x=>x.querySelector('img')?.naturalWidth>0),
   mapPresent:!!document.getElementById('exploreMap'),
   mapOptional:!!document.querySelector('.photo-map a[href="/explore/"]'),
   documentWidth:document.documentElement.scrollWidth,viewport:innerWidth};
 });
 const ok=homeLinks&&probe.url==='/photo-spots/'&&probe.count===4&&!probe.mapPresent&&probe.mapOptional&&
   probe.articleLinks.every(p=>/^\/japan\/[a-z-]+-photo\/$/.test(p))&&
   probe.photoLoad.every(Boolean)&&probe.documentWidth<=viewport.width+3;
 const shot=path.join(OUT,name+'-photo-spots.png');
 await page.screenshot({path:shot});
 results.screenshots.push(shot);
 results.checks.push({kind:'photo-spot-navigation',viewport:name,ok,homeLinks,...probe});
 await page.close();
}
await browser.close();
results.pass=results.checks.every(x=>x.ok);
await fs.writeFile(OUT+'/browser-qa.json',JSON.stringify(results,null,2)+'\n');
process.stdout.write(JSON.stringify({pass:results.pass,checks:results.checks.map(x=>({kind:x.kind,viewport:x.viewport,ok:x.ok,count:x.count,documentWidth:x.documentWidth}))},null,2)+'\n');
if(!results.pass)process.exit(1);
