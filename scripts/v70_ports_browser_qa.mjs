// V70: audit exactly 20 existing port pages in the built production tree.
import fs from 'node:fs';
import path from 'node:path';
import {chromium} from 'playwright';
const manifest=JSON.parse(fs.readFileSync('audit-reports/v70/upgraded-ports.json','utf8'));
const slugs=manifest.results.map(x=>x.slug);
const widths=[320,390,768,1440];
const out='audit-reports/v70',portLinks=new Set(),internal=new Set();
const qa={version:70,createdAt:new Date().toISOString(),noNewPages:true,articles:slugs.length,widths,checks:[],errors:[],warnings:[],officialLinks:[]};
if(slugs.length!==20||new Set(slugs).size!==20)qa.errors.push('Exactly twenty unique port articles required');
for(const slug of slugs){
 const file=path.join('dist','things-to-do',slug+'-cruise-port-day-trip','index.html');
 if(!fs.existsSync(file)){qa.errors.push('Missing built article '+file);continue}
 const html=fs.readFileSync(file,'utf8');
 if((html.match(/id="v70-port-official"/g)||[]).length!==1)qa.errors.push(slug+' no unique V70 section');
 if((html.match(/class="v70-panel"/g)||[]).length!==3)qa.errors.push(slug+' card count !=3');
 if(!html.includes('https://www.nipponferry.com/things-to-do/'+slug+'-cruise-port-day-trip/'))qa.errors.push(slug+' changed canonical URL');
 const excerpt=html.match(/<section class="v70-verified"[\s\S]*?<\/section>/)?.[0]||'';
 for(const m of excerpt.matchAll(/href="(https?:\/\/[^"]+)"/g))portLinks.add(m[1]);
 for(const m of excerpt.matchAll(/href="(\/[^"]+)"/g)){
  const t=m[1].split(/[?#]/)[0]||'/';
  internal.add(t);
  if(!fs.existsSync(path.join('dist',t,'index.html'))&&!fs.existsSync(path.join('dist',t)))qa.errors.push(slug+' broken internal destination '+t);
 }
}
qa.officialLinks=[...portLinks].sort();
let browser;
try{
 browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 for(const slug of slugs){
  for(const width of widths){
   const page=await browser.newPage({viewport:{width,height:850},deviceScaleFactor:1});
   try{
    const url='http://127.0.0.1:8757/things-to-do/'+slug+'-cruise-port-day-trip/';
    const response=await page.goto(url,{waitUntil:'domcontentloaded',timeout:25000});
    await page.locator('#v70-port-official').waitFor({timeout:12000});
    const data=await page.evaluate(()=>{
     const root=document.querySelector('#v70-port-official');
     const cards=[...root.querySelectorAll('.v70-panel')],links=[...root.querySelectorAll('a')];
     const logo=document.querySelector('.site-header .brand img')||document.querySelector('a.brand img');
     const hero=document.querySelector('main article > header img.cover, main article > header figure img, main article > header img.hero-img');
     const h1=document.querySelector('main article h1');
     return {
      viewport:innerWidth,documentWidth:document.documentElement.scrollWidth,
      cardCount:cards.length,officialCardLinks:cards.filter(c=>c.querySelector('a[href^="https://"]')).length,
      panelWidth:Math.round(root.getBoundingClientRect().width),
      logoWidth:logo?.getBoundingClientRect().width||0,heroOk:!!hero&&hero.complete&&hero.naturalWidth>0,h1:!!h1,
      overflowLinks:links.filter(a=>{const r=a.getBoundingClientRect();return r.left< -1||r.right>innerWidth+1}).map(x=>x.getAttribute('href')),
      canonical:document.querySelector('link[rel="canonical"]')?.getAttribute('href')||''
     };
    });
    const errs=[];
    if(response?.status()!==200)errs.push('HTTP status '+response?.status());
    if(data.documentWidth>width+2)errs.push('horizontal overflow '+data.documentWidth);
    if(data.cardCount!==3||data.officialCardLinks!==3)errs.push('missing one of three official reference cards');
    if(data.logoWidth>46)errs.push('oversized shared logo '+data.logoWidth);
    if(!data.h1||!data.heroOk)errs.push('missing heading or broken hero');
    if(data.overflowLinks.length)errs.push('links outside viewport '+data.overflowLinks.join(','));
    if(data.canonical!=='https://www.nipponferry.com/things-to-do/'+slug+'-cruise-port-day-trip/')errs.push('wrong canonical');
    if(['hiroshima','nagoya','kumamoto','kumamoto-misumi','yakushima-miyanoura'].includes(slug))
      await page.locator('#v70-port-official').screenshot({path:path.join(out,slug+'-'+width+'.png'),animations:'disabled',timeout:20000});
    qa.checks.push({slug,width,...data,errors:errs});
    errs.forEach(e=>qa.errors.push(slug+'/'+width+': '+e));
   }catch(e){qa.errors.push(slug+'/'+width+': browser '+String(e).slice(0,260))}
   finally{await page.close()}
  }
 }
}catch(e){qa.errors.push('Chromium launch '+String(e))}
finally{if(browser)await browser.close()}
qa.checkedInternalLinks=[...internal].sort();
qa.passed=qa.errors.length===0;
fs.writeFileSync(path.join(out,'browser-qa.json'),JSON.stringify(qa,null,2));
console.log(JSON.stringify({passed:qa.passed,articles:slugs.length,screenChecks:qa.checks.length,officialLinks:qa.officialLinks.length,internalLinks:internal.size,errors:qa.errors.slice(0,35)},null,2));
if(!qa.passed)process.exitCode=1;
