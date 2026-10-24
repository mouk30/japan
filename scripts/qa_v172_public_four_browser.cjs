const fs=require('fs');const{chromium}=require('playwright');
const base='https://www.nipponferry.com',names=["kure","fukuyama","sakaide","maizuru"],widths=[390,768,945,1440],output='audit-output/v172-public';
fs.mkdirSync(output,{recursive:true});let rows=[];
(async()=>{const browser=await chromium.launch({headless:true,args:['--disable-dev-shm-usage']});
try{for(const name of names)for(const width of widths){const page=await browser.newPage({viewport:{width,height:950},deviceScaleFactor:1});
try{const url=base+'/things-to-do/'+name+'-cruise-port-day-trip/';
const resp=await page.goto(url+'?v172_browser_qa=1',{waitUntil:'domcontentloaded',timeout:22000});
const panel=page.locator('#nf-v172-official-'+name);await panel.scrollIntoViewIfNeeded();
const x=await page.evaluate(async({name,url})=>{
const panel=document.querySelector('#nf-v172-official-'+name),imgs=[...document.querySelectorAll('article header img')],a=[...panel.querySelectorAll('.nf-v172-card a')],cards=[...panel.querySelectorAll('.nf-v172-card')],original=document.querySelector('article header img'),canon=document.querySelector('link[rel="canonical"]');
if(original){try{await Promise.race([original.decode(),new Promise(r=>setTimeout(r,5000))]);}catch(_){}}
return {viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,oneH1:document.querySelectorAll('h1').length===1,canonical:canon?.href,onePanel:document.querySelectorAll('#nf-v172-official-'+name).length===1,cardCount:cards.length,buttonHeights:a.map(x=>Math.round(x.getBoundingClientRect().height)),buttonSrc:a.map(x=>x.href),hasCredit:!!document.querySelector('a[href*="commons.wikimedia.org"]'),hasPhoto:!!original&&original.naturalWidth>=1000&&original.naturalHeight>=700,noticeVisible:panel.getBoundingClientRect().width>240}};
,{name,url});
const checks={http200:resp.status()===200,canonical:x.canonical===url,oneH1:x.oneH1,officialPanels:x.onePanel&&x.cardCount===3,officialLinks:x.buttonSrc.length===3&&x.buttonSrc.every(v=>v.startsWith('https://')),largeButtons:x.buttonHeights.every(h=>h>=50),originalPhoto:x.hasPhoto,licensedOriginal:x.hasCredit,noHorizontalOverflow:x.scrollWidth<=width+6,noticeVisible:x.noticeVisible};
const good=Object.values(checks).every(Boolean);const shot=output+'/'+name+'-'+width+'.png';await page.screenshot({path:shot,fullPage:false,animations:'disabled',timeout:13000});
rows.push({name,width,pass:good,checks,measure:x,shot});console.log(good?'PASS':'FAIL',name,width,JSON.stringify(checks));
}catch(e){rows.push({name,width,pass:false,error:String(e)});console.log('FAIL',name,width,String(e).slice(0,350));}finally{await page.close().catch(()=>{});}
}}finally{await browser.close();}
const result={version:'V172',count:rows.length,passed:rows.filter(r=>r.pass).length,rows};fs.writeFileSync(output+'/results.json',JSON.stringify(result,null,2));console.log('SUMMARY',result.passed,'/',result.count);if(result.passed!==result.count)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
