const fs=require('fs');const{chromium}=require('playwright');
const base='https://www.nipponferry.com',slugs=["yokohama","kanazawa","akita","kushiro"],widths=[390,768,945,1440],dest='audit-output/v174-live';fs.mkdirSync(dest,{recursive:true});const rows=[];
(async()=>{const browser=await chromium.launch({headless:true,args:['--disable-dev-shm-usage']});
try{for(const slug of slugs)for(const width of widths){
 const page=await browser.newPage({viewport:{width,height:1000},deviceScaleFactor:1});try{
  const url=base+'/things-to-do/'+slug+'-cruise-port-day-trip/';
  const response=await page.goto(url+'?v174_browser_qa=1',{waitUntil:'domcontentloaded',timeout:25000});
  const loc=page.locator('#nf-v174-'+slug);await loc.scrollIntoViewIfNeeded({timeout:10000});
  const x=await page.evaluate(async({slug})=>{
   const panel=document.getElementById('nf-v174-'+slug),as=[...panel.querySelectorAll('.nf-v174-card a')],img=document.querySelector('article header img');
   if(img)try{await Promise.race([img.decode(),new Promise(r=>setTimeout(r,5000))]);}catch(e){}
   return {canonical:document.querySelector('link[rel="canonical"]')?.href,h1:document.querySelectorAll('h1').length,
    panels:document.querySelectorAll('#nf-v174-'+slug).length,cards:panel.querySelectorAll('.nf-v174-card').length,
    actions:as.map(a=>a.dataset.nfV174Action),hrefs:as.map(a=>a.href),buttons:as.map(a=>Math.round(a.getBoundingClientRect().height)),
    photoDims:[img?.naturalWidth,img?.naturalHeight],photoLicense:!!document.querySelector('a[href*="commons.wikimedia.org"]'),
    scrollWidth:document.documentElement.scrollWidth,viewport:innerWidth,panelWidth:panel.getBoundingClientRect().width};
  },{slug});
  const checks={http200:response.status()===200,canonical:x.canonical===url&&x.h1===1,
  exactPanel:x.panels===1&&x.cards===3,threePurposeButtons:JSON.stringify(x.actions)===JSON.stringify(['booking','conditions','return'])&&x.hrefs.every(h=>h.startsWith('https://')),
  clickableLarge:x.buttons.length===3&&x.buttons.every(h=>h>=50),originalImage:x.photoDims[0]>=1000&&x.photoDims[1]>=700,license:x.photoLicense,noOverflow:x.scrollWidth<=width+6,visible:x.panelWidth>240};
  const ok=Object.values(checks).every(Boolean);
  const filename=dest+'/'+slug+'-'+width+'.png';await page.screenshot({path:filename,animations:'disabled',timeout:15000,fullPage:false});
  rows.push({slug,width,ok,checks,metrics:x,screenshot:filename});console.log(ok?'PASS':'FAIL',slug,width,JSON.stringify(checks));
 }catch(e){rows.push({slug,width,ok:false,error:String(e)});console.log('FAIL',slug,width,String(e).slice(0,400));}finally{await page.close().catch(()=>{});}
 }}finally{await browser.close();}
 const result={version:'V174',screens:rows.length,passed:rows.filter(x=>x.ok).length,rows};fs.writeFileSync(dest+'/metrics.json',JSON.stringify(result,null,2));console.log('SUMMARY',result.passed,'/',result.screens);if(result.passed!==result.screens)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
