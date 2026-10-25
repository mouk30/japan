const fs=require('fs');const {chromium}=require('playwright');
const slugs=['nagoya','kumamoto','yatsushiro','shingu'],widths=[390,768,945,1440],base='https://www.nipponferry.com',out='audit-output/v179-live';
fs.mkdirSync(out,{recursive:true});const records=[];
(async()=>{const browser=await chromium.launch({headless:true,args:['--disable-dev-shm-usage']});
try{for(const slug of slugs)for(const width of widths){
 const page=await browser.newPage({viewport:{width,height:950},deviceScaleFactor:1});
 try{
 const path='/things-to-do/'+slug+'-cruise-port-day-trip/';
 const response=await page.goto(base+path+'?v179browserqa=1',{waitUntil:'domcontentloaded',timeout:28000});
 await page.locator('#nf-v179-'+slug).scrollIntoViewIfNeeded({timeout:9000});
 const info=await page.evaluate(async slug=>{
 const panel=document.getElementById('nf-v179-'+slug),links=[...panel.querySelectorAll('.nf-v179-card a')],img=document.querySelector('article header img');
 if(img){try{await Promise.race([img.decode(),new Promise(r=>setTimeout(r,5000))]);}catch(e){}}
 return {h1:document.querySelectorAll('h1').length,canonical:document.querySelector('link[rel="canonical"]')?.href,
  panelCount:document.querySelectorAll('#nf-v179-'+slug).length,cardCount:panel.querySelectorAll('.nf-v179-card').length,
  actions:links.map(x=>x.dataset.nfV179Action),targets:links.map(x=>x.href),tapHeights:links.map(x=>Math.round(x.getBoundingClientRect().height)),
  imgDims:[img?.naturalWidth,img?.naturalHeight],imageCredit:!!document.querySelector('a[href*="commons.wikimedia.org"]'),
  docWidth:document.documentElement.scrollWidth,viewport:innerWidth,panelWidth:panel.getBoundingClientRect().width,
  badPortal:document.body.innerText.includes('입장·예약 운영기관 안내 확인 ↗')};
 },slug);
 const checks={HTTP200:response.status()===200,SEO:info.canonical===base+path&&info.h1===1,onePanelThreeCards:info.panelCount===1&&info.cardCount===3,threePurposes:JSON.stringify(info.actions)===JSON.stringify(['ticket','conditions','return'])&&info.targets.every(s=>s.startsWith('https://')),largeTapTargets:info.tapHeights.every(h=>h>=50),originalPhotoLoaded:info.imgDims[0]>=650&&info.imgDims[1]>=800,originalCredit:info.imageCredit,noHorizontalOverflow:info.docWidth<=width+6,visible:info.panelWidth>=250,oldPortalCorrected:!['yatsushiro','shingu'].includes(slug)||!info.badPortal};
 const pass=Object.values(checks).every(Boolean),image=out+'/'+slug+'-'+width+'.png';
 await page.screenshot({path:image,fullPage:false,animations:'disabled',timeout:17000});
 records.push({slug,width,pass,checks,metrics:info,image});
 console.log(pass?'PASS':'FAIL',slug,width,JSON.stringify(checks));
 }catch(e){records.push({slug,width,pass:false,error:String(e)});console.log('FAIL',slug,width,String(e).slice(0,380));}
 finally{await page.close().catch(()=>{});}
}}finally{await browser.close();}
const results={version:'V179',expected:16,screens:records.length,passed:records.filter(r=>r.pass).length,rows:records};
fs.writeFileSync(out+'/screens.json',JSON.stringify(results,null,2));
console.log('SUMMARY',results.passed,'/',results.screens);
if(results.passed!==16)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
