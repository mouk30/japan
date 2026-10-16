import fs from 'node:fs';
import path from 'node:path';
import {chromium} from 'playwright';
const slugs=[
'life/japan-cash-how-much','practical/japan-atm-cash-guide','life/japan-card-payment-error',
'practical/japan-ic-card-guide','japan/fukuoka-transport','practical/japan-airport-bus-guide',
'practical/japan-esim-setup','practical/japan-esim-vs-sim-wifi','practical/japan-data-usage',
'life/japan-convenience-shopping-list','life/japan-convenience-atm','life/japan-supermarket-discount-time',
'shopping/japan-souvenir-buying-guide','shopping/japan-food-bring-korea','shopping/korea-customs-return',
'couple/kyoto-romantic-date','couple/japan-onsen-couple-trip','japan/fukuoka-photo',
'stay/hakone','season/japan-summer-festival-guide'
];
const widths=[320,390,768,1440],output='audit-reports/v68';
fs.mkdirSync(output,{recursive:true});
const report={time:new Date().toISOString(),slugs,widths,checks:[],errors:[],warnings:[],officialLinks:[],internalLinks:[],noNewArticles:true};
const official=new Set(),local=new Set();
for(const slug of slugs){
 const file='site/'+slug+'/index.html',html=fs.readFileSync(file,'utf8');
 if((html.match(/id="v68-precision"/g)||[]).length!==1)report.errors.push(slug+' v68 block missing or duplicate');
 const canonical='https://www.nipponferry.com/'+slug+'/';
 const match=html.match(/<link\s+rel=["']canonical["']\s+href=["']([^"']+)/);
 if(match?.[1]!==canonical)report.errors.push(slug+' canonical changed: '+(match?.[1]||'missing'));
 for(const a of [...html.matchAll(/href=["']([^"']+)["']/g)]){
  const href=a[1];
  if(href.startsWith('/'))local.add(href.split(/[?#]/)[0]||'/');
 }
 const panel=(html.match(/<section class="v68-precision"[\s\S]*?<\/section>/)||[])[0]||'';
 if((panel.match(/class="v68-fact"/g)||[]).length!==3)report.errors.push(slug+' expected 3 source cards');
 for(const a of panel.matchAll(/href=["'](https?:\/\/[^"']+)/g))official.add(a[1]);
}
for(const link of local){
 const clean=link.split('?')[0];
 if(clean==='/'||clean.startsWith('//'))continue;
 const full='site'+clean;
 if(!fs.existsSync(path.join(full,'index.html'))&&!fs.existsSync(full))report.errors.push('Internal target missing '+link);
}
report.officialLinks=[...official].sort();report.internalLinks=[...local].sort();
let browser;
try{
 browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 for(const slug of slugs)for(const width of widths){
  const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
  try{
   const res=await page.goto('http://127.0.0.1:8757/'+slug+'/',{waitUntil:'domcontentloaded',timeout:30000});
   await page.locator('#v68-precision').waitFor({timeout:12000});
   const x=await page.evaluate(()=>{
     const root=document.querySelector('#v68-precision');
     const cards=[...root.querySelectorAll('.v68-fact')],links=[...root.querySelectorAll('a')];
     return {
      count:cards.length,visible:root.getBoundingClientRect().width>180,
      viewportWidth:innerWidth,pageWidth:document.documentElement.scrollWidth,
      headings:document.querySelectorAll('h1').length,
      links:links.length,emptyLinks:links.filter(x=>!x.getAttribute('href')||x.getAttribute('href')==='#').map(x=>x.textContent.trim()),
      overflowLinks:links.filter(a=>{const r=a.getBoundingClientRect();return r.right>innerWidth+1||r.left < -1}).map(a=>a.getAttribute('href')),
      canonical:document.querySelector('link[rel=canonical]')?.getAttribute('href')||''
     };
   });
   const failures=[];
   if(res.status()!==200)failures.push('status '+res.status());
   if(x.count!==3)failures.push('source card count '+x.count);
   if(!x.visible)failures.push('hidden panel');
   if(x.pageWidth>width+1)failures.push('horizontal overflow '+x.pageWidth);
   if(x.overflowLinks.length)failures.push('overflowing CTA '+x.overflowLinks.join(','));
   if(x.emptyLinks.length)failures.push('empty links');
   if(x.headings!==1)failures.push('page H1 count '+x.headings);
   if(x.canonical!=='https://www.nipponferry.com/'+slug+'/')failures.push('canonical mismatch');
   if([320,390,768,1440].includes(width)&&['life/japan-cash-how-much','shopping/korea-customs-return','couple/kyoto-romantic-date','stay/hakone'].includes(slug)){
     await page.locator('#v68-precision').screenshot({path:path.join(output,slug.split('/').at(-1)+'-'+width+'.png'),animations:'disabled',timeout:15000});
   }
   report.checks.push({slug,width,...x,failures});
   failures.forEach(f=>report.errors.push(slug+' '+width+': '+f));
  }catch(e){report.errors.push(slug+' '+width+': '+String(e).slice(0,230))}
  finally{await page.close()}
 }
}catch(e){report.errors.push('browser: '+String(e))}
finally{if(browser)await browser.close()}
report.passed=report.errors.length===0;
fs.writeFileSync(path.join(output,'details-qa.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({passed:report.passed,pages:slugs.length,checks:report.checks.length,internal:local.size,official:official.size,errors:report.errors.slice(0,55)},null,2));
if(!report.passed)process.exitCode=1;
