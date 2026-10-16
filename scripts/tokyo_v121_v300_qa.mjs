import fs from 'node:fs';
import path from 'node:path';
import {chromium} from 'playwright';
const manifest=JSON.parse(fs.readFileSync('audit-reports/v121-v300/editorial-manifest.json','utf8'));
const articles=manifest.topics, sizes=[320,390,768,1440];
const report={time:new Date().toISOString(),articles:articles.length,versions:'V121-V300',screensizes:sizes,checks:[],errors:[],warnings:[],byBatch:{},sources:[],internalLinks:[],siteHub:{},passed:false};
for(const b of manifest.groups)report.byBatch['V'+b.versionStart+'-V'+b.versionEnd]={target:80,checked:0,errors:0};
const targetDirs=new Set(articles.map(t=>t.path));
if(articles.length!==180||manifest.groups.length!==9)report.errors.push('180 guides and 9×20 required');
const all=[
{slug:'city-hub',url:'/japan/tokyo/',kind:'hub',version:0},
{slug:'home-popular',url:'/',kind:'homepage',version:0},
{slug:'japan-destinations',url:'/japan/',kind:'region',version:0},
...articles.map(t=>({slug:t.slug,url:t.path,version:t.version,kind:'guide',source:t.source}))
];
const urls=new Set();
for(const obj of all){
 const filename=path.join('dist',obj.url,'index.html');
 if(!fs.existsSync(filename)){report.errors.push('Missing built page '+filename);continue}
 const h=fs.readFileSync(filename,'utf8');
 if((h.match(/<h1\b/g)||[]).length!==1)report.errors.push(obj.url+' has invalid H1');
 if(!h.includes('href="https://www.nipponferry.com'+obj.url+'"'))report.errors.push('Missing exact canonical '+obj.url);
 for(const m of h.matchAll(/href=["'](\/[^"']+)["']/g)){
  const target=m[1].split(/[?#]/)[0];
  if(!target||target.startsWith('//'))continue;
  urls.add(target);
 }
 if(obj.kind==='guide'){
  if(!h.includes(obj.source))report.errors.push('Page lost official source '+obj.url);
  const schemas=[...h.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)];
  if(!schemas.length)report.errors.push('Missing JSONLD '+obj.url);
  for(const s of schemas){try{JSON.parse(s[1])}catch(e){report.errors.push('Invalid JSONLD '+obj.url)}}
  if((h.match(/class="tky-block/g)||[]).length<6)report.errors.push('Page thin or missing facts '+obj.url);
 }
 if(obj.kind==='hub'){
  const packs=(h.match(/class="tky-exp-group"/g)||[]).length;
  const cards=(h.match(/class="tky-card"/g)||[]).length;
  report.siteHub={packs,cards,bytes:Buffer.byteLength(h,'utf8')};
  if(packs!==9||cards!==220)report.errors.push('Hub 9 sets or 220 cards incorrect '+packs+'/'+cards);
 }
}
for(const u of urls)if(u!=='/'&&!fs.existsSync('dist'+u)&&!fs.existsSync('dist'+u+'index.html')){
 report.errors.push('Internal path unavailable '+u);
}
report.internalLinks=[...urls].sort();
const map=fs.readFileSync('dist/sitemap.xml','utf8');
for(const a of articles)if(!map.includes('<loc>https://www.nipponferry.com'+a.path+'</loc>'))report.errors.push('Not in sitemap '+a.path);
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
try{
 for(const obj of all)for(const width of sizes){
  const page=await browser.newPage({viewport:{width,height:820},deviceScaleFactor:1});
  try{
   const response=await page.goto('http://127.0.0.1:8757'+obj.url,{waitUntil:'domcontentloaded',timeout:26000});
   const q=await page.evaluate(()=>{
    const logo=document.querySelector('a.brand img');
    const list=[...document.querySelectorAll('main img,.tky-hub-photo img,.v81-tokyo img')];
    return {
      width:innerWidth,documentWidth:document.documentElement.scrollWidth,
      headingCount:document.querySelectorAll('h1').length,
      logoWidth:logo?.getBoundingClientRect().width||0,
      heroImages:list.length,broken:list.filter(x=>x.complete&&x.naturalWidth===0).map(x=>x.getAttribute('src')),
      blocks:document.querySelectorAll('.tky-body .tky-block').length,
      official:document.querySelectorAll('.tky-body #official a[href^="https://"]').length,
      details:document.querySelectorAll('.tky-exp-group').length,
      cards:document.querySelectorAll('.tky-card').length,
      canonical:document.querySelector('link[rel=canonical]')?.href||'',
      title:document.title
    };
   });
   const fails=[];
   if(response.status()!==200)fails.push('HTTP '+response.status());
   if(q.documentWidth>width+2)fails.push('horizontal overflow '+q.documentWidth);
   if(q.headingCount!==1)fails.push('H1 count '+q.headingCount);
   if(q.logoWidth>45)fails.push('Mascot logo width '+q.logoWidth);
   if(q.broken.length)fails.push('broken images '+q.broken.join(','));
   if(q.canonical!=='https://www.nipponferry.com'+obj.url)fails.push('Canonical '+q.canonical);
   if(obj.kind==='guide'&&(q.blocks<6||q.official!==1))fails.push('Facts or official links '+q.blocks+'/'+q.official);
   if(obj.kind==='hub'&&(q.details!==9||q.cards!==220))fails.push('Hub categories or article cards '+q.details+'/'+q.cards);
   if(obj.kind==='homepage'&&!await page.locator('.v81-tokyo').count())fails.push('Tokyo popular city card missing');
   if(obj.kind==='region'&&!await page.locator('a[href="/japan/tokyo/"]').count())fails.push('Tokyo region link missing');
   if(obj.kind==='guide'){
     const start=121+Math.floor((obj.version-121)/20)*20;
     const group=report.byBatch['V'+start+'-V'+(start+19)];
     group.checked++;
     group.errors+=fails.length;
     if((obj.version-121)%20===0&&[320,1440].includes(width))
      await page.screenshot({path:'audit-reports/v121-v300/v'+start+'-'+obj.slug+'-'+width+'.png',fullPage:false,timeout:16000});
   }else if(width===390)await page.screenshot({path:'audit-reports/v121-v300/'+obj.slug+'-390.png',fullPage:false,timeout:16000});
   report.checks.push({type:obj.kind,slug:obj.slug,width,...q,errors:fails});
   for(const f of fails)report.errors.push(obj.slug+' '+width+': '+f);
  }catch(e){report.errors.push(obj.slug+' '+width+' browser '+String(e).slice(0,230))}
  finally{await page.close()}
 }
}finally{await browser.close()}
report.passed=report.errors.length===0;
fs.writeFileSync('audit-reports/v121-v300/browser-qa.json',JSON.stringify(report,null,2));
console.log(JSON.stringify({passed:report.passed,articles:articles.length,viewports:report.checks.length,hub:report.siteHub,internalTargets:report.internalLinks.length,groups:report.byBatch,errors:report.errors.slice(0,38)},null,2));
if(!report.passed)process.exitCode=1;
