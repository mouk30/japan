const fs=require('fs');const{chromium}=require('playwright');
const BASE='https://www.nipponferry.com',slugs=["beppu","otaru","shimizu","hiroshima"],widths=[390,768,945,1440],out='audit-output/v173-live';
fs.mkdirSync(out,{recursive:true});
const rows=[];const browserGo=async()=>{
const browser=await chromium.launch({headless:true,args:['--disable-dev-shm-usage']});
try{for(const slug of slugs){for(const width of widths){const page=await browser.newPage({viewport:{width,height:950},deviceScaleFactor:1});
try{
 const path='/things-to-do/'+slug+'-cruise-port-day-trip/';
 const response=await page.goto(BASE+path+'?v173_live=1',{waitUntil:'domcontentloaded',timeout:25000});
 const panel=page.locator('#nf-v173-'+slug);await panel.scrollIntoViewIfNeeded({timeout:10000});
 const x=await page.evaluate(async({slug})=>{
  const p=document.querySelector('#nf-v173-'+slug);const links=[...p.querySelectorAll('.nf-v173-card a')];const photo=document.querySelector('article header img');
  if(photo){try{await Promise.race([photo.decode(),new Promise(r=>setTimeout(r,4500))]);}catch(_){}}
  return{canonical:document.querySelector('link[rel="canonical"]')?.href,h1:document.querySelectorAll('h1').length,panels:document.querySelectorAll('#nf-v173-'+slug).length,cards:p.querySelectorAll('.nf-v173-card').length,
  actions:links.map(a=>a.dataset.nfV173Action),links:links.map(a=>a.href),buttons:links.map(a=>Math.round(a.getBoundingClientRect().height)),
  photoSrc:photo?.getAttribute('src'),photoDimensions:[photo?.naturalWidth,photo?.naturalHeight],licensed:!!document.querySelector('a[href*="commons.wikimedia.org"]'),
  scrollWidth:document.documentElement.scrollWidth,viewport:innerWidth,visible:p.getBoundingClientRect().width>240,
  caption:slug==='otaru'?document.querySelector('article header figcaption')?.textContent?.trim():null};
 },{slug});
 const checks={
  http200:response.status()===200,
  correctCanonical:x.canonical===BASE+path&&x.h1===1,
  officialPanel:x.panels===1&&x.cards===3&&x.visible,
  threeIntentLinks:JSON.stringify(x.actions)===JSON.stringify(['ticket','conditions','return'])&&x.links.every(u=>u.startsWith('https://')),
  mobileFriendlyButtons:x.buttons.length===3&&x.buttons.every(y=>y>=50),
  originalPhotoLoaded:x.photoDimensions?.[0]>=1000&&x.photoDimensions?.[1]>=700,
  licensesPresent:x.licensed,
  noHorizontalOverflow:x.scrollWidth<=width+6,
  noFalseOtaruAI:slug!=='otaru'||(x.caption?.includes('실제')&&!x.caption.includes('AI 생성'))
 };
 const ok=Object.values(checks).every(Boolean),shot=out+'/'+slug+'-'+width+'.png';
 await page.screenshot({path:shot,animations:'disabled',fullPage:false,timeout:15000});
 rows.push({slug,width,ok,checks,measurement:x,screenshot:shot});console.log(ok?'PASS':'FAIL',slug,width,JSON.stringify(checks));
}catch(e){rows.push({slug,width,ok:false,error:String(e)});console.log('FAIL',slug,width,String(e).slice(0,400));}
finally{await page.close().catch(()=>{});}
}}}finally{await browser.close();}
const summary={version:'V173',screens:rows.length,passed:rows.filter(x=>x.ok).length,rows};
fs.writeFileSync(out+'/screens.json',JSON.stringify(summary,null,2));console.log('SUMMARY',summary.passed,'/',summary.screens);
if(summary.passed!==summary.screens)process.exitCode=1;
};browserGo().catch(e=>{console.error(e);process.exitCode=1;});
