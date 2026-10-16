import fs from 'node:fs';
import path from 'node:path';
import {chromium} from 'playwright';
const slugs=['yokohama','nagasaki','hakata','naha','ishigaki','osaka','kobe','hakodate','aomori','kagoshima','beppu','sasebo','shimonoseki','shimizu','kanazawa','sendai','kochi','niigata','matsuyama','sakaiminato'];
const sizes=[320,390,768,1440],out='audit-reports/v69';
fs.mkdirSync(out,{recursive:true});
const report={timestamp:new Date().toISOString(),version:'69',noNewPages:true,articles:slugs.length,sizes,results:[],errors:[],warnings:[],officialSourceLinks:[]};
const links=new Set();
for(const slug of slugs){
 const name='dist/things-to-do/'+slug+'-cruise-port-day-trip/index.html';
 if(!fs.existsSync(name)){report.errors.push('Missing built page '+name);continue}
 const html=fs.readFileSync(name,'utf8');
 if((html.match(/id="v69-berth-qa"/g)||[]).length!==1)report.errors.push(slug+': V69 section missing or duplicate');
 if((html.match(/class="v69-fact"/g)||[]).length!==3)report.errors.push(slug+': three fact cards required');
 if(!html.includes('https://www.nipponferry.com/things-to-do/'+slug+'-cruise-port-day-trip/'))report.errors.push(slug+': canonical changed');
 const excerpt=html.match(/<section class="v69-port"[\s\S]*?<\/section>/)?.[0]||'';
 for(const m of excerpt.matchAll(/href="(https?:\/\/[^"]+)"/g))links.add(m[1]);
 for(const m of excerpt.matchAll(/href="(\/[^"]+)"/g)){
  const t=m[1].split(/[?#]/)[0];
  if(!fs.existsSync('dist'+t+'index.html')&&!fs.existsSync('dist'+t))report.errors.push(slug+': dead internal target '+t);
 }
 if(excerpt.includes('**해당 항차'))report.errors.push(slug+': markdown leaked in live HTML');
}
report.officialSourceLinks=[...links].sort();
let browser;
try{
 browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 for(const slug of slugs){
  for(const width of sizes){
   const page=await browser.newPage({viewport:{width,height:860},deviceScaleFactor:1});
   try{
    const response=await page.goto('http://127.0.0.1:8757/things-to-do/'+slug+'-cruise-port-day-trip/',{waitUntil:'domcontentloaded',timeout:28000});
    await page.locator('#v69-berth-qa').waitFor({timeout:12000});
    const p=await page.evaluate(()=>{
     const sec=document.querySelector('#v69-berth-qa'),box=sec.getBoundingClientRect(),cards=[...sec.querySelectorAll('.v69-fact')],sources=[...sec.querySelectorAll('.v69-fact a')],logo=document.querySelector('.site-header .brand img')||document.querySelector('a.brand img');
     const out=sources.filter(a=>{const r=a.getBoundingClientRect();return r.left< -1||r.right>innerWidth+1}).map(a=>a.href);
     const hero=document.querySelector('main article>header h1'),image=document.querySelector('main article>header img.cover, main article>header figure img');
     return{docWidth:document.documentElement.scrollWidth,width:innerWidth,cardCount:cards.length,sourceCount:sources.length,logoWidth:logo?.getBoundingClientRect().width||0,heroTitle:hero?.textContent?.trim()||'',heroImage:!!image&&image.complete&&image.naturalWidth>0,sectionWidth:Math.round(box.width),overflowingLinks:out,firstCardWidth:Math.round(cards[0]?.getBoundingClientRect().width||0),canonical:document.querySelector('link[rel=canonical]')?.href||''};
    });
    const errors=[];
    if(response.status()!==200)errors.push('HTTP '+response.status());
    if(p.docWidth>width+2)errors.push('horizontal overflow '+p.docWidth+' > '+width);
    if(p.cardCount!==3)errors.push('V69 card count '+p.cardCount);
    if(p.sourceCount!==3)errors.push('Source links '+p.sourceCount);
    if(p.logoWidth>45)errors.push('Oversized mascot '+p.logoWidth);
    if(!p.heroTitle)errors.push('Missing H1');
    if(!p.heroImage)errors.push('Broken hero image');
    if(p.overflowingLinks.length)errors.push('Overflowing source links '+p.overflowingLinks.join(','));
    if(p.canonical!=='https://www.nipponferry.com/things-to-do/'+slug+'-cruise-port-day-trip/')errors.push('Incorrect canonical '+p.canonical);
    if(['yokohama','nagasaki','hakata','naha','ishigaki'].includes(slug)){
      await page.locator('#v69-berth-qa').screenshot({path:path.join(out,slug+'-'+width+'.png'),animations:'disabled',timeout:20000});
    }
    report.results.push({slug,width,...p,errors});
    errors.forEach(e=>report.errors.push(slug+'-'+width+': '+e));
   }catch(e){report.errors.push(slug+'-'+width+': '+String(e).slice(0,230))}
   finally{await page.close()}
  }
 }
}catch(e){report.errors.push('Chromium launch: '+String(e))}
finally{if(browser)await browser.close()}
report.passed=report.errors.length===0;
fs.writeFileSync(path.join(out,'browser-qa.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({passed:report.passed,articles:slugs.length,checks:report.results.length,sources:report.officialSourceLinks.length,errors:report.errors.slice(0,55)},null,2));
if(!report.passed)process.exitCode=1;
