const fs=require('fs');const {chromium}=require('playwright');
const base='https://www.nipponferry.com',slugs=['muroran','mojiko','sakata','sendai'],widths=[390,768,945,1440],dir='audit-output/v177-live';
fs.mkdirSync(dir,{recursive:true});const rows=[];
(async()=>{const browser=await chromium.launch({headless:true,args:['--disable-dev-shm-usage']});
try{for(const slug of slugs)for(const width of widths){
 const page=await browser.newPage({viewport:{width,height:1000},deviceScaleFactor:1});
 try{
 const path='/things-to-do/'+slug+'-cruise-port-day-trip/';
 const response=await page.goto(base+path+'?v177publicqa=1',{waitUntil:'domcontentloaded',timeout:28000});
 await page.locator('#nf-v177-'+slug).scrollIntoViewIfNeeded({timeout:10000});
 const m=await page.evaluate(async slug=>{
  const p=document.getElementById('nf-v177-'+slug),links=[...p.querySelectorAll('.nf-v177-card a')],img=document.querySelector('article header img');
  if(img){try{await Promise.race([img.decode(),new Promise(r=>setTimeout(r,5500))]);}catch(e){}}
  return{h1:document.querySelectorAll('h1').length,canonical:document.querySelector('link[rel="canonical"]')?.href,panels:document.querySelectorAll('#nf-v177-'+slug).length,cards:p.querySelectorAll('.nf-v177-card').length,
   linkIntents:links.map(a=>a.dataset.nfV177Action),linkTargets:links.map(a=>a.href),buttonHeights:links.map(a=>Math.round(a.getBoundingClientRect().height)),
   photoDimensions:[img?.naturalWidth,img?.naturalHeight],credit:!!document.querySelector('a[href*="commons.wikimedia.org"]'),
   viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,panelWidth:p.getBoundingClientRect().width,misleadingCTA:document.body.innerText.includes('입장·예약 운영기관 안내 확인 ↗')};
 },slug);
 const checks={HTTP200:response.status()===200,canonicalAndOneH1:m.canonical===base+path&&m.h1===1,onePanelThreeCards:m.panels===1&&m.cards===3,actions:['ticket','conditions','return'].every((x,i)=>m.linkIntents[i]===x)&&m.linkTargets.length===3&&m.linkTargets.every(x=>x.startsWith('https://')),buttonHeight50:m.buttonHeights.every(x=>x>=50),decodedOriginalPhoto:m.photoDimensions[0]>=1000&&m.photoDimensions[1]>=700,sourceLicense:m.credit,noOverflow:m.scrollWidth<=width+6,visiblePanel:m.panelWidth>240,oldBadCTAReplaced:slug==='sendai'||!m.misleadingCTA};
 const passed=Object.values(checks).every(Boolean),shot=dir+'/'+slug+'-'+width+'.png';
 await page.screenshot({path:shot,animations:'disabled',fullPage:false,timeout:18000});
 rows.push({slug,width,passed,checks,metrics:m,shot});console.log(passed?'PASS':'FAIL',slug,width,JSON.stringify(checks));
 }catch(e){rows.push({slug,width,passed:false,error:String(e)});console.log('FAIL',slug,width,String(e).slice(0,400));}
 finally{await page.close().catch(()=>{});}
}}finally{await browser.close();}
const report={version:'V177',screens:rows.length,passed:rows.filter(x=>x.passed).length,rows};fs.writeFileSync(dir+'/screens.json',JSON.stringify(report,null,2));console.log('SUMMARY',report.passed,'/',report.screens);if(report.passed!==16)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
