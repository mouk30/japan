const fs=require('fs');const{chromium}=require('playwright');
const slugs=['miyako','ishinomaki','toba','hachinohe'],widths=[390,768,945,1440],base='https://www.nipponferry.com',out='audit-output/v175-live';
fs.mkdirSync(out,{recursive:true});const rows=[];
(async()=>{const browser=await chromium.launch({headless:true,args:['--disable-dev-shm-usage']});try{
for(const slug of slugs)for(const width of widths){
const page=await browser.newPage({viewport:{width,height:1000},deviceScaleFactor:1});
try{
 const url=base+'/things-to-do/'+slug+'-cruise-port-day-trip/';
 const response=await page.goto(url+'?v175qa=1',{waitUntil:'domcontentloaded',timeout:28000});
 await page.locator('#nf-v175-'+slug).scrollIntoViewIfNeeded({timeout:9000});
 const m=await page.evaluate(async({slug})=>{
 const s=document.getElementById('nf-v175-'+slug),links=[...s.querySelectorAll('.nf-v175-card a')],img=document.querySelector('article header img');
 if(img){try{await Promise.race([img.decode(),new Promise(r=>setTimeout(r,5500))]);}catch(e){}}
 const disclosure=document.querySelector('article header figcaption')?.textContent||'';
 return{oneH1:document.querySelectorAll('h1').length===1,canonical:document.querySelector('link[rel="canonical"]')?.href,onePanel:document.querySelectorAll('#nf-v175-'+slug).length===1,cards:s.querySelectorAll('.nf-v175-card').length,actions:links.map(x=>x.dataset.nfV175Action),destinations:links.map(x=>x.href),heights:links.map(x=>Math.round(x.getBoundingClientRect().height)),oldGenericCTA:document.body.innerText.includes('입장·예약 운영기관 안내 확인 ↗'),photo:[img?.naturalWidth,img?.naturalHeight],aiPhoto:img?.alt?.includes('AI 생성 이미지'),aiDisclosure:disclosure.includes('AI 생성'),realLicense:!!document.querySelector('a[href*="commons.wikimedia.org"]'),scrollWidth:document.documentElement.scrollWidth,viewport:innerWidth,panelWidth:s.getBoundingClientRect().width};
 },{slug});
 const checks={HTTP200:response.status()===200,SEO:m.canonical===url&&m.oneH1,visibleCards:m.onePanel&&m.cards===3&&m.panelWidth>240,intents:JSON.stringify(m.actions)===JSON.stringify(['ticket','conditions','return'])&&m.destinations.every(x=>x.startsWith('https://')),noMisleadingPortalButton:!m.oldGenericCTA,CTA50:m.heights.every(x=>x>=50),realPhotoLoaded:m.photo[0]>=1000&&m.photo[1]>=700,creditHonest:slug==='toba'?m.realLicense:(m.aiPhoto&&m.aiDisclosure),noOverflow:m.scrollWidth<=width+6};
 const ok=Object.values(checks).every(Boolean);const shot=out+'/'+slug+'-'+width+'.png';
 await page.screenshot({path:shot,fullPage:false,animations:'disabled',timeout:17000});rows.push({slug,width,pass:ok,checks,metrics:m,shot});console.log(ok?'PASS':'FAIL',slug,width,JSON.stringify(checks));
}catch(e){rows.push({slug,width,pass:false,error:String(e)});console.log('FAIL',slug,width,String(e).slice(0,360));}finally{await page.close().catch(()=>{});}
}}finally{await browser.close();}
const report={version:'V175',expected:16,passed:rows.filter(r=>r.pass).length,rows};fs.writeFileSync(out+'/screens.json',JSON.stringify(report,null,2));console.log('SUMMARY',report.passed,'/',rows.length);if(report.passed!==16)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
