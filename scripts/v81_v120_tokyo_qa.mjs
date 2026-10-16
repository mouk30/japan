import fs from 'node:fs';
import path from 'node:path';
import {chromium} from 'playwright';
const manifest=JSON.parse(fs.readFileSync('audit-reports/v81-v120/manifest.json','utf8'));
const entries=[{uri:'/',type:'home'},{uri:'/japan/',type:'region'},{uri:'/japan/tokyo/',type:'hub'},...manifest.articlesMeta.map(x=>({uri:x.path,type:'detail',...x}))];
const widths=[320,390,768,1440];
const report={checkedAt:new Date().toISOString(),pages:entries.length,newTokyoArticles:manifest.articles,checks:[],errors:[],warnings:[],photos:[],sourceLinks:[]};
const local=new Set(),sources=new Set();
const im='dist/images/venues/tokyo-city-night-real.webp';
if(!fs.existsSync(im)||fs.statSync(im).size<30000)report.errors.push('Missing authentic Tokyo city photograph');
const checkImages=['/','/japan/','/japan/tokyo/'];
for(const entry of entries){
 const file=path.join('dist',entry.uri,'index.html'),src=fs.existsSync(file)?fs.readFileSync(file,'utf8'):'';
 if(!src){report.errors.push('Built page not found '+entry.uri);continue}
 const canonical='https://www.nipponferry.com'+entry.uri;
 if(!src.includes(canonical))report.errors.push('Canonical absent '+entry.uri);
 if((src.match(/<h1\b/g)||[]).length!==1)report.errors.push('H1 count wrong '+entry.uri);
 if(entry.type==='detail'){
  if(!src.includes('application/ld+json'))report.errors.push('Missing Article schema '+entry.uri);
  for(const val of entry.sources)if(!src.includes(val))report.errors.push('Source missing '+entry.uri+' '+val);
  if(!src.includes('id="official"')||!src.includes('id="plan"'))report.errors.push('Missing direct source or travel route '+entry.uri);
 }
 for(const match of src.matchAll(/href=["']([^"']+)["']/g)){
  const u=match[1].split('#')[0].split('?')[0];
  if(u.startsWith('/')&&!u.startsWith('//'))local.add(u);
  if(u.startsWith('https://')&&!u.includes('nipponferry.com'))sources.add(u);
 }
}
for(const dest of local)if(dest&&!fs.existsSync('dist'+dest+'index.html')&&!fs.existsSync('dist'+dest))report.errors.push('Dead local href '+dest);
report.sourceLinks=[...sources].filter(x=>!x.includes('commons.wikimedia.org')&&!x.includes('creativecommons.org')).sort();
const sitemap=fs.readFileSync('dist/sitemap.xml','utf8');
for(const a of manifest.articlesMeta)if(!sitemap.includes('<loc>https://www.nipponferry.com'+a.path+'</loc>'))report.errors.push('Sitemap missing '+a.path);
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
try{
 for(const entry of entries)for(const width of widths){
  const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
  try{
   const resp=await page.goto('http://127.0.0.1:8757'+entry.uri,{waitUntil:'domcontentloaded',timeout:22000});
   const data=await page.evaluate(()=>{
     const h1=document.querySelector('h1');
     const brand=document.querySelector('.site-header .brand img');
     const imgs=[...document.querySelectorAll('main img, .tky-hub-photo img, .v65-tokyo img, .v81-tokyo img')];
     return{
      viewport:innerWidth,pageWidth:document.documentElement.scrollWidth,
      h1Count:document.querySelectorAll('h1').length,
      canonical:document.querySelector('link[rel=canonical]')?.getAttribute('href')||'',
      heading:h1?.textContent?.trim().slice(0,95)||'',
      logoWidth:brand?.getBoundingClientRect().width||0,
      images:imgs.length,brokenImages:imgs.filter(x=>x.complete&&x.naturalWidth===0).map(x=>x.getAttribute('src')),
      tokyoGuideCount:document.querySelectorAll('.tky-card').length,
      articleSectionCount:document.querySelectorAll('.tky-body .tky-block').length,
      officialCount:document.querySelectorAll('.tky-official a[href^="https://"]').length,
      url:location.pathname
     };
   });
   const errors=[];
   if(resp.status()!==200)errors.push('HTTP '+resp.status());
   if(data.pageWidth>width+2)errors.push('Horizontal overflow '+data.pageWidth+' > '+width);
   if(data.logoWidth>48)errors.push('Mascot over 48 px: '+data.logoWidth);
   if(data.h1Count!==1)errors.push('H1 count '+data.h1Count);
   if(data.canonical!=='https://www.nipponferry.com'+entry.uri)errors.push('Canonical mismatch '+data.canonical);
   if(entry.type==='hub'&&data.tokyoGuideCount!==40)errors.push('Tokyo hub grid count '+data.tokyoGuideCount);
   if(entry.type==='detail'&&(data.articleSectionCount<6||data.officialCount<2))errors.push('Missing specialist factual content '+data.articleSectionCount+'/'+data.officialCount);
   if(data.brokenImages.length)errors.push('Broken images '+data.brokenImages.join(','));
   if(['hub','home','region'].includes(entry.type)&&width===390)await page.screenshot({path:'audit-reports/v81-v120/'+entry.type+'-390.png',fullPage:false,timeout:12000});
   if(['tokyo-tower-tickets','tokyo-subway-route-map-korean','tokyo-disneyland-ticket-guide','tokyo-mega-donki-shibuya'].some(z=>entry.uri.endsWith('/'+z+'/'))&&width===390)
    await page.screenshot({path:'audit-reports/v81-v120/'+entry.slug+'-390.png',fullPage:false,timeout:12000});
   report.checks.push({path:entry.uri,type:entry.type,width,...data,errors});
   for(const e of errors)report.errors.push(entry.uri+' '+width+': '+e);
  }catch(e){report.errors.push(entry.uri+' '+width+': browser '+String(e).slice(0,180))}
  finally{await page.close()}
 }
}finally{await browser.close()}
report.passed=report.errors.length===0;
fs.writeFileSync('audit-reports/v81-v120/browser-qa.json',JSON.stringify(report,null,2));
console.log(JSON.stringify({passed:report.passed,articles:manifest.articles,viewportChecks:report.checks.length,internalLinks:local.size,sourceLinks:report.sourceLinks.length,errors:report.errors.slice(0,45)},null,2));
if(!report.passed)process.exitCode=1;
