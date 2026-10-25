const fs=require('fs');const {chromium}=require('playwright');
const slugs=['himeji','tokoname','onahama','abashiri'],widths=[390,768,945,1440],base='https://www.nipponferry.com',dir='audit-output/v180-public';
fs.mkdirSync(dir,{recursive:true});const results=[];
(async()=>{const browser=await chromium.launch({headless:true,args:['--disable-dev-shm-usage']});
try{for(const slug of slugs)for(const width of widths){
const page=await browser.newPage({viewport:{width,height:1000},deviceScaleFactor:1});
try{
 const url=base+'/things-to-do/'+slug+'-cruise-port-day-trip/';
 const response=await page.goto(url+'?v180prodqa=1',{waitUntil:'domcontentloaded',timeout:30000});
 await page.locator('#nf-v180-'+slug).scrollIntoViewIfNeeded({timeout:11000});
 const m=await page.evaluate(async slug=>{
 const p=document.getElementById('nf-v180-'+slug),anchors=[...p.querySelectorAll('.nf-v180-card a')],img=document.querySelector('article header img');
 if(img){try{await Promise.race([img.decode(),new Promise(resolve=>setTimeout(resolve,6000))]);}catch(e){}}
 const text=document.querySelector('article header figcaption')?.textContent||'';
 return {h1:document.querySelectorAll('h1').length,canonical:document.querySelector('link[rel="canonical"]')?.href,
  panelCount:document.querySelectorAll('#nf-v180-'+slug).length,cards:p.querySelectorAll('.nf-v180-card').length,
  actions:anchors.map(a=>a.dataset.nfV180Action),targets:anchors.map(a=>a.href),tapHeights:anchors.map(a=>Math.round(a.getBoundingClientRect().height)),
  imageSize:[img?.naturalWidth,img?.naturalHeight],alt:img?.alt||'',aiDisclosure:text.includes('AI 생성'),hasCredit:!!document.querySelector('a[href*="commons.wikimedia.org"]'),
  documentWidth:document.documentElement.scrollWidth,viewport:innerWidth,panelWidth:p.getBoundingClientRect().width,
  genericMisleadingCTA:document.body.innerText.includes('입장·예약 운영기관 안내 확인 ↗')};
 },slug);
 const checks={HTTP200:response.status()===200,oneH1Canonical:m.h1===1&&m.canonical===url,onePanelThreeCards:m.panelCount===1&&m.cards===3,
  threeOfficialActions:JSON.stringify(m.actions)===JSON.stringify(['ticket','conditions','return'])&&m.targets.length===3&&m.targets.every(x=>x.startsWith('https://')),
  buttons50px:m.tapHeights.every(v=>v>=50),photoLoaded:m.imageSize[0]>=1200&&m.imageSize[1]>=830,
  photoRights:slug==='onahama'?m.alt.includes('AI 생성')&&m.aiDisclosure:m.hasCredit,documentNotWider:m.documentWidth<=width+6,panelVisible:m.panelWidth>260,
  oldGenericCTAReplaced:!m.genericMisleadingCTA};
 const passed=Object.values(checks).every(Boolean),shot=dir+'/'+slug+'-'+width+'.png';
 await page.screenshot({path:shot,animations:'disabled',fullPage:false,timeout:18000});
 results.push({slug,width,passed,checks,metrics:m,screenshot:shot});
 console.log(passed?'PASS':'FAIL',slug,width,JSON.stringify(checks));
}catch(e){results.push({slug,width,passed:false,error:String(e)});console.log('FAIL',slug,width,String(e).slice(0,450))}
finally{await page.close().catch(()=>{})}
}}finally{await browser.close()}
const report={version:'V180',screens:results.length,passed:results.filter(x=>x.passed).length,rows:results};
fs.writeFileSync(dir+'/screens.json',JSON.stringify(report,null,2));console.log('SUMMARY',report.passed,'/',report.screens);if(report.passed!==16)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
