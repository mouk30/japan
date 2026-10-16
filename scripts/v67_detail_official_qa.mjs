import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';
const root=process.cwd(), base='http://127.0.0.1:8757';
const pagePaths=[
'/japan/fukuoka-food/','/things-to-do/fukuoka-one-day/','/japan/shimonoseki-market/',
'/things-to-do/shimonoseki-one-day/','/things-to-do/tsushima-one-day/',
'/things-to-do/osaka-one-day/','/practical/fujiq-highland-guide/',
'/shopping/japan-tax-free-2026/','/life/japan-tax-free-2026/',
'/life/don-quijote-first-guide/','/life/don-quijote-tax-free/',
'/things-to-do/activity/','/things-to-do/food-experience/','/japan/tsushima-food/'
];
const breakpoints=[320,390,768,1440];
const report={generatedAt:new Date().toISOString(),version:'V67',noNewPages:true,checks:[],errors:[],sourceUrls:[],scope:pagePaths};
const output=path.join(root,'audit-reports/v67');
fs.mkdirSync(output,{recursive:true});
const internal=new Set(),official=new Set();
let browser;
try{
 browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 for(const slug of pagePaths){
  const file=path.join(root,'site',slug,'index.html');
  const original=fs.readFileSync(file,'utf8');
  const canonical='https://www.nipponferry.com'+slug;
  if(!original.includes(canonical))report.errors.push('No canonical on '+slug);
  if((original.match(/id="v67-official-info"/g)||[]).length!==1)report.errors.push('V67 block duplicated or absent '+slug);
  for(const tag of [...original.matchAll(/<a[^>]*href=["']([^"']+)["']/g)]){
   const href=tag[1].trim();
   if(href.startsWith('http')){
     try{const host=new URL(href).hostname;if(['karatoichiba.com','gofukuoka.jp','www.fujiq.jp','www.kaiyukan.com','www.discover-nagasaki.com','tsushima-gbt.com','www.nta.go.jp','www.japan.travel','www.kanmon-kisen.co.jp','www.fujikyu-railway.jp','www.usj.co.jp'].some(h=>host===h)){official.add(href)}}
     catch{}
   } else if(href.startsWith('/')&&!href.startsWith('//')){
    const abs=href.split(/[?#]/)[0]||'/';
    internal.add(abs);
   }
  }
  for(const width of breakpoints){
   const tab=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
   try{
    const response=await tab.goto(base+slug,{waitUntil:'domcontentloaded',timeout:22000});
    await tab.locator('#v67-official-info').waitFor({timeout:12000});
    const summary=await tab.evaluate(()=>{
      const panel=document.querySelector('#v67-official-info');
      const panelRect=panel.getBoundingClientRect();
      const cards=[...panel.querySelectorAll('.v67-block')];
      const officialLinks=[...panel.querySelectorAll('a[href^="http"]')];
      const empty=[...panel.querySelectorAll('a')].filter(a=>!a.getAttribute('href')||a.getAttribute('href')==='#');
      const overflowing=[...panel.querySelectorAll('a')].filter(a=>{const r=a.getBoundingClientRect();return r.right>innerWidth+1||r.left < -1}).map(a=>a.getAttribute('href'));
      return {cards:cards.length,officialLinkCount:officialLinks.length,panelWidth:Math.round(panelRect.width),panelRight:Math.round(panelRect.right),pageScrollWidth:document.documentElement.scrollWidth,emptyLinks:empty.length,overflowingLinks:overflowing,canonical:document.querySelector('link[rel=canonical]')?.getAttribute('href')||''};
    });
    const issues=[];
    if(response.status()!==200)issues.push('HTTP '+response.status());
    if(summary.cards!==3)issues.push('Expected 3 fact cards, found '+summary.cards);
    if(summary.officialLinkCount<1)issues.push('No official source in panel');
    if(summary.emptyLinks)issues.push('Blank links: '+summary.emptyLinks);
    if(summary.overflowingLinks.length)issues.push('Overflowing clickable links: '+summary.overflowingLinks.join(','));
    if(summary.pageScrollWidth>width+1)issues.push('Horizontal overflow '+summary.pageScrollWidth+' > '+width);
    if(summary.canonical!==canonical)issues.push('Canonical changed '+summary.canonical);
    if(['320','390','768','1440'].includes(String(width))&&['/things-to-do/osaka-one-day/','/japan/shimonoseki-market/','/life/japan-tax-free-2026/','/things-to-do/activity/'].includes(slug)){
      await tab.locator('#v67-official-info').screenshot({path:path.join(output,slug.split('/').filter(Boolean).pop()+'-'+width+'.png'),animations:'disabled',timeout:18000});
    }
    report.checks.push({slug,width,...summary,issues});
    issues.forEach(x=>report.errors.push(slug+' '+width+': '+x));
   }catch(ex){report.errors.push(slug+' '+width+': '+String(ex))}
   finally{await tab.close()}
  }
 }
}catch(e){report.errors.push('Browser error '+String(e))}
finally{if(browser)await browser.close()}
for(const href of internal){
 const item=path.join(root,'site',href);
 if(!fs.existsSync(path.join(item,'index.html'))&&!fs.existsSync(item))report.errors.push('Internal link target missing: '+href);
}
report.officialSources=Array.from(official).sort();
report.checkedInternalPaths=internal.size;
report.passed=report.errors.length===0;
fs.writeFileSync(path.join(output,'detail-qa.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({passed:report.passed,checks:report.checks.length,updatedPages:pagePaths.length,officialSources:official.size,internalPaths:internal.size,errors:report.errors.slice(0,45)},null,2));
if(!report.passed)process.exitCode=1;
