const fs=require('fs');const {chromium}=require('playwright');
const names=['ofunato','tsuruga','sakaiminato','shimonoseki'],widths=[390,768,945,1440],base='https://www.nipponferry.com',dir='audit-output/v178-live';
fs.mkdirSync(dir,{recursive:true});const results=[];
(async()=>{const browser=await chromium.launch({headless:true,args:['--disable-dev-shm-usage']});
try{for(const slug of names)for(const width of widths){
 const page=await browser.newPage({viewport:{width,height:1000},deviceScaleFactor:1});
 try{
 const path='/things-to-do/'+slug+'-cruise-port-day-trip/';
 const response=await page.goto(base+path+'?v178publicqa=1',{waitUntil:'domcontentloaded',timeout:30000});
 await page.locator('#nf-v178-'+slug).scrollIntoViewIfNeeded({timeout:9000});
 const x=await page.evaluate(async slug=>{
  const guide=document.getElementById('nf-v178-'+slug),anchors=[...guide.querySelectorAll('.nf-v178-card a')],img=document.querySelector('article header img');
  if(img){try{await Promise.race([img.decode(),new Promise(resolve=>setTimeout(resolve,5000))]);}catch(e){}}
  const caption=document.querySelector('article header figcaption')?.textContent||'';
  return {canonical:document.querySelector('link[rel="canonical"]')?.href,h1:document.querySelectorAll('h1').length,
   panelCount:document.querySelectorAll('#nf-v178-'+slug).length,cards:guide.querySelectorAll('.nf-v178-card').length,
   actions:anchors.map(a=>a.dataset.nfV178Action),urls:anchors.map(a=>a.href),
   buttons:anchors.map(a=>Math.round(a.getBoundingClientRect().height)),
   photoDims:[img?.naturalWidth,img?.naturalHeight],photoIsAI:img?.alt?.includes('AI 생성 이미지'),aiCaption:caption.includes('AI 생성'),credit:!!document.querySelector('a[href*="commons.wikimedia.org"]'),
   docWidth:document.documentElement.scrollWidth,viewport:innerWidth,panelWidth:guide.getBoundingClientRect().width,
   badPortalCTA:document.body.innerText.includes('입장·예약 운영기관 안내 확인 ↗')};
 },slug);
 const checks={HTTP200:response.status()===200,SEO:x.canonical===base+path&&x.h1===1,threeCards:x.panelCount===1&&x.cards===3,purposeLinks:JSON.stringify(x.actions)===JSON.stringify(['ticket','conditions','return'])&&x.urls.length===3&&x.urls.every(u=>u.startsWith('https://')),
  tapTargets:x.buttons.every(z=>z>=50),imageDecoded:x.photoDims[0]>=1000&&x.photoDims[1]>=700,photoRights:slug==='ofunato'?x.photoIsAI&&x.aiCaption:x.credit,noOverflow:x.docWidth<=width+6,panelVisible:x.panelWidth>240,portalCTAFixed:!['ofunato','tsuruga'].includes(slug)||!x.badPortalCTA};
 const ok=Object.values(checks).every(Boolean),shot=dir+'/'+slug+'-'+width+'.png';
 await page.screenshot({path:shot,fullPage:false,animations:'disabled',timeout:18000});
 results.push({slug,width,pass:ok,checks,metrics:x,screenshot:shot});console.log(ok?'PASS':'FAIL',slug,width,JSON.stringify(checks));
 }catch(e){results.push({slug,width,pass:false,error:String(e)});console.log('FAIL',slug,width,String(e).slice(0,370));}
 finally{await page.close().catch(()=>{});}
}}finally{await browser.close();}
const result={version:'V178',pages:4,screens:results.length,passed:results.filter(r=>r.pass).length,rows:results};
fs.writeFileSync(dir+'/screens.json',JSON.stringify(result,null,2));console.log('SUMMARY',result.passed,'/',result.screens);
if(result.passed!==16)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
