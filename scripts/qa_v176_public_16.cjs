const fs=require('fs');const {chromium}=require('playwright');
const names=['tomakomai','nanao','miyazaki','imabari'],widths=[390,768,945,1440],base='https://www.nipponferry.com',dest='audit-output/v176-public';
fs.mkdirSync(dest,{recursive:true});const results=[];
(async()=>{const browser=await chromium.launch({headless:true,args:['--disable-dev-shm-usage']});
try{for(const slug of names)for(const width of widths){
 const page=await browser.newPage({viewport:{width,height:950},deviceScaleFactor:1});
 try{
 const url=base+'/things-to-do/'+slug+'-cruise-port-day-trip/';
 const response=await page.goto(url+'?v176qa=1',{waitUntil:'domcontentloaded',timeout:28000});
 await page.locator('#nf-v176-'+slug).scrollIntoViewIfNeeded({timeout:10000});
 const m=await page.evaluate(async(slug)=>{
  const p=document.getElementById('nf-v176-'+slug),links=[...p.querySelectorAll('.nf-v176-card a')],img=document.querySelector('article header img');
  if(img){try{await Promise.race([img.decode(),new Promise(resolve=>setTimeout(resolve,5000))]);}catch(e){}}
  return{
   canonical:document.querySelector('link[rel="canonical"]')?.href,
   h1:document.querySelectorAll('h1').length,
   panelCount:document.querySelectorAll('#nf-v176-'+slug).length,
   cardCount:p.querySelectorAll('.nf-v176-card').length,
   actions:links.map(a=>a.dataset.nfV176Action),
   urls:links.map(a=>a.href),
   buttonHeights:links.map(a=>Math.round(a.getBoundingClientRect().height)),
   photoDims:[img?.naturalWidth,img?.naturalHeight],
   credit:!!document.querySelector('a[href*="commons.wikimedia.org"]'),
   viewport:innerWidth,documentWidth:document.documentElement.scrollWidth,
   panelWidth:p.getBoundingClientRect().width,
   outdatedCTA:document.body.innerText.includes('입장·예약 운영기관 안내 확인 ↗')
  };
 },slug);
 const checks={HTTP200:response.status()===200,canonicalH1:m.canonical===url&&m.h1===1,onePanelAndThreeCards:m.panelCount===1&&m.cardCount===3,threePurposeLinks:JSON.stringify(m.actions)===JSON.stringify(['booking','conditions','return'])&&m.urls.every(s=>s.startsWith('https://')),largeButtons:m.buttonHeights.length===3&&m.buttonHeights.every(h=>h>=50),originalWebPDecoded:m.photoDims[0]>=1000&&m.photoDims[1]>=700,photoOriginalCredit:m.credit,noHorizontalOverflow:m.documentWidth<=width+6,panelVisible:m.panelWidth>240,noPortalAsTicket:!['nanao','imabari'].includes(slug)||!m.outdatedCTA};
 const pass=Object.values(checks).every(Boolean),shot=dest+'/'+slug+'-'+width+'.png';
 await page.screenshot({path:shot,fullPage:false,animations:'disabled',timeout:15000});
 results.push({slug,width,pass,checks,metrics:m,screenshot:shot});
 console.log(pass?'PASS':'FAIL',slug,width,JSON.stringify(checks));
 }catch(err){results.push({slug,width,pass:false,error:String(err)});console.log('FAIL',slug,width,String(err).slice(0,350));}
 finally{await page.close().catch(()=>{});}
}}finally{await browser.close();}
const report={version:'V176',screenCount:results.length,passed:results.filter(x=>x.pass).length,rows:results};
fs.writeFileSync(dest+'/screens.json',JSON.stringify(report,null,2));console.log('SUMMARY',report.passed,'/',report.screenCount);if(report.passed!==16)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
