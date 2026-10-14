import {chromium} from 'playwright';
import {readFile,writeFile,mkdir,stat} from 'node:fs/promises';
import path from 'node:path';
const base=process.env.LOCAL_BASE_URL||'http://127.0.0.1:8765',out='audit-reports/v29';
await mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
const report=[];
for(const [name,width,height,expectCols] of [['mobile',390,844,1],['tablet',768,1024,2],['desktop',1365,900,3]]){
 const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
 let issues=[],data={};
 try{
  let response=await page.goto(base+'/seasons/',{waitUntil:'domcontentloaded',timeout:30000});
  if(response?.status()!==200)issues.push('HTTP_'+response?.status());
  await page.evaluate(()=>[...document.querySelectorAll('.seasons-hub .dircard img')].forEach(x=>x.loading='eager'));
  await page.waitForFunction(()=>[...document.querySelectorAll('.seasons-hub .dircard img')].every(x=>x.complete),undefined,{timeout:26000}).catch(()=>{});
  data=await page.evaluate(()=>{
   const grid=document.querySelector('.seasons-hub .dirgrid');
   const cards=[...grid?.querySelectorAll('.dircard')||[]];
   const images=cards.map(x=>x.querySelector('img'));
   const styles=grid&&getComputedStyle(grid);
   const first=images[0]?.getBoundingClientRect();
   return {
    cards:cards.length,
    unique:new Set(images.map(x=>x?.getAttribute('src'))).size,
    broken:images.filter(x=>!x?.complete||x.naturalWidth===0).map(x=>x?.getAttribute('src')),
    width:document.documentElement.scrollWidth,
    columns:styles?styles.gridTemplateColumns.split(' ').filter(Boolean).length:0,
    main:document.querySelectorAll('main').length,
    firstImageWidth:Math.round(first?.width||0),
    firstImageRatio:first?.height?+(first.width/first.height).toFixed(2):0,
    winterPhotoCount:images.slice(0,28).filter(x=>x.getAttribute('src')?.includes('v29-season')).length,
    credits:document.querySelectorAll('.seasons-image-credits li').length,
    titles:cards.map(x=>x.querySelector('h2')?.textContent?.trim()||'')
   };
  });
  if(data.cards!==34)issues.push('CARD_COUNT_'+data.cards);
  if(data.unique!==34)issues.push('REPEATED_PHOTOS_'+data.unique);
  if(data.broken.length)issues.push('BROKEN_PHOTOS_'+JSON.stringify(data.broken));
  if(data.columns!==expectCols)issues.push('BAD_COLUMNS_'+data.columns);
  if(data.width>width+3)issues.push('HORIZONTAL_OVERFLOW_'+data.width);
  if(data.main!==1)issues.push('DUPLICATE_MAIN_'+data.main);
  if(data.firstImageWidth<120||data.firstImageWidth>width+3)issues.push('IMAGE_SIZE');
  if(data.winterPhotoCount<10)issues.push('TOO_FEW_WINTER_REAL_PHOTOS_'+data.winterPhotoCount);
  if(data.credits<11)issues.push('MISSING_LICENSE_CREDITS_'+data.credits);
  await page.screenshot({path:path.join(out,'seasons-'+name+'.png'),fullPage:false});
 }catch(e){issues.push('EXCEPTION_'+String(e).slice(0,200))}
 report.push({viewport:name,status:issues.length?'FAIL':'PASS',issues,data});
 await page.close();
}
await browser.close();
const original=await readFile('site/seasons/index.html','utf8');
const urls=[...original.matchAll(/<a class="dircard" href="(\/[^"]+)"/g)].map(x=>x[1]);
let broken=[];
for(const url of urls){try{await stat(path.join('dist',url,'index.html'))}catch{broken.push(url)}}
if(broken.length)report.push({viewport:'links',status:'FAIL',issues:['BROKEN_LINKS',...broken]});
const summary={cases:3,passed:report.filter(x=>x.status==='PASS').length,failed:report.filter(x=>x.status!=='PASS').length,results:report.map(x=>({viewport:x.viewport,issues:x.issues,columns:x.data?.columns,photos:x.data?.winterPhotoCount}))};
await writeFile(path.join(out,'visual.json'),JSON.stringify({summary,report},null,2));
console.log('V29_SEASONS_QA '+JSON.stringify(summary));
if(summary.failed)process.exitCode=1;
