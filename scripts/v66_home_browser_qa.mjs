// NIPPONFERRY V66 browser QA: home components, navigation, SEO, and real render at four breakpoints.
import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';
const root=process.cwd();
const screenshots='audit-reports/v66';
fs.mkdirSync(screenshots,{recursive:true});
const widths=[320,390,768,1440];
const sections=[
 {name:'themes',css:'.v63-theme-section',card:'.v63-card',expected:6},
 {name:'practical',css:'.v64-practical',card:'.v64-card',expected:5},
 {name:'destinations',css:'.v65-destinations',card:'.v65-card',expected:7},
 {name:'port-day-trips',css:'.d61-home-region',card:'.d61-home-card',expected:4},
];
const report={createdAt:new Date().toISOString(),widths,results:[],errors:[],warnings:[],source:'site/index.html'};
const src=fs.readFileSync(path.join(root,'site/index.html'),'utf8');
const internalHref=/href="(\/[^"]*)"/g;
const allLinks=[...src.matchAll(internalHref)].map(m=>m[1]);
const seen=new Set();
for(const href of allLinks){
 if(href.startsWith('//'))continue;
 const clean=href.split('#')[0].split('?')[0]||'/';
 if(seen.has(clean))continue;seen.add(clean);
 if(clean==='/')continue;
 const target=path.join(root,'site',clean);
 if(!fs.existsSync(path.join(target,'index.html'))&&!fs.existsSync(target)){
  report.errors.push('Internal link missing: '+href);
 }
}
for(const pattern of ['<link rel="canonical" href="https://www.nipponferry.com/">','property="og:image"','type="application/ld+json"','href="/booking/japan-cruise/"']){
 if(!src.includes(pattern))report.errors.push('Required SEO / booking marker missing: '+pattern);
}
if(src.includes('href="https://willer-travel.com/ko/ferry/"'))report.errors.push('Generic offsite booking button persists');
for(const cls of ['v63-card','v64-card','v65-card','d61-home-card']){
 if(!src.includes('class="'+cls))report.errors.push('Missing component '+cls);
}
let browser;
try {
 browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 for(const width of widths){
  const page=await browser.newPage({viewport:{width,height:950},deviceScaleFactor:1});
  try{
   const response=await page.goto('http://127.0.0.1:8757/',{waitUntil:'load',timeout:30000});
   if(response.status()!==200)report.errors.push(width+'px HTTP '+response.status());
   for(const section of sections){
    const el=page.locator(section.css);
    await el.waitFor({timeout:15000});
    await el.locator('img').evaluateAll(async images=>{
      await Promise.all(images.map(async img=>{img.loading='eager';try{await img.decode()}catch{}}));
    });
    const result=await page.evaluate(({css,card})=>{
       const section=document.querySelector(css);
       const cards=[...section.querySelectorAll(card)];
       const imgs=[...section.querySelectorAll(card+' img')];
       const anchors=[...section.querySelectorAll('a')];
       const badAnchors=anchors.filter(a=>{
         const b=a.getBoundingClientRect();return b.width<1||b.height<1||b.left<-2||b.right>innerWidth+2;
       }).map(a=>a.getAttribute('href'));
       return {count:cards.length,images:imgs.map(x=>({src:x.getAttribute('src'),alt:x.alt,ready:x.complete&&x.naturalWidth>0})),
         linkCount:anchors.length,buttonsOverflow:badAnchors};
    },{css:section.css,card:section.card});
    const failures=[];
    if(result.count!==section.expected)failures.push('expected '+section.expected+' cards, got '+result.count);
    if(result.images.some(x=>!x.ready))failures.push('broken/non-loaded: '+result.images.filter(x=>!x.ready).map(x=>x.src).join(','));
    if(result.images.some(x=>!x.alt))failures.push('missing image alt');
    if(result.buttonsOverflow.length)failures.push('buttons overflow viewport: '+result.buttonsOverflow.join(','));
    const name=section.name+'-'+width+'.png';
    try{
      await el.screenshot({path:path.join(screenshots,name),animations:'disabled',timeout:18000});
    }catch(e){failures.push('screenshot failure: '+String(e).slice(0,200))}
    report.results.push({name:section.name,width,...result,failures,screenshot:name});
    failures.forEach(f=>report.errors.push(section.name+'-'+width+': '+f));
   }
   const widthData=await page.evaluate(()=>({window:innerWidth,document:document.documentElement.scrollWidth,booking:!!document.querySelector('a[href="/booking/japan-cruise/"]')}));
   if(widthData.document>width+1)report.errors.push(width+'px horizontal overflow: '+widthData.document);
   if(!widthData.booking)report.errors.push(width+'px booking CTA not found');
  }catch(e){report.errors.push(width+'px: '+String(e));}
  finally{await page.close()}
 }
} catch(e){report.errors.push('Chromium failed: '+String(e))}
finally{if(browser)await browser.close()}
const photos=[...new Set([...src.matchAll(/<img[^>]+src="([^"]+)"/g)].map(m=>m[1]))];
const scopedImages=[...src.matchAll(/class="v6[345]-(?:visual|photo)"[^>]*>\s*<img src="([^"]+)"/g)].map(m=>m[1]);
if(new Set(scopedImages).size!==scopedImages.length)report.warnings.push('Repeat hero image among V63-65: '+scopedImages.filter((x,i,a)=>a.indexOf(x)<i).join(','));
report.checkedInternalLinks=seen.size;
report.passed=report.errors.length===0;
fs.writeFileSync(path.join(screenshots,'report.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({passed:report.passed,checkCount:report.results.length,links:seen.size,errors:report.errors,warnings:report.warnings},null,2));
if(!report.passed)process.exitCode=1;
