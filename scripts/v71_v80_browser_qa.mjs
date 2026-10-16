import fs from 'node:fs';
import path from 'node:path';
import {chromium} from 'playwright';
const dir='audit-reports/v71-v80',manifest=JSON.parse(fs.readFileSync(dir+'/manifest.json','utf8'));
const widths=[320,390,768,1440];
const report={versionRange:'V71-V80',time:new Date().toISOString(),articles:manifest.pages.length,counts:{},checks:[],errors:[],warnings:[],sourceTypes:{individual:0,portal:0}};
fs.mkdirSync(dir,{recursive:true});
for(const [v,x] of Object.entries(manifest.cohorts))report.counts[v]={pages:x.slugs.length,passed:0,failed:0};
let browser;
try{
browser=await chromium.launch({headless:true,args:['--no-sandbox']});
for(const [v,cohort] of Object.entries(manifest.cohorts)){
 let seq=0;
 for(const slug of cohort.slugs){
   const built=path.join('dist','things-to-do',slug,'index.html');
   if(!fs.existsSync(built)){report.errors.push(v+': '+slug+' missing dist file');continue}
   const html=fs.readFileSync(built,'utf8');
   const id='v'+v.slice(1)+'-verification';
   if((html.match(new RegExp('id="'+id+'"','g'))||[]).length!==1)report.errors.push(slug+' missing unique ID');
   if((html.match(/class="nf-q80-card"/g)||[]).length!==3)report.errors.push(slug+' must have three official-source cards');
   if(!html.includes('https://www.nipponferry.com/things-to-do/'+slug+'/'))report.errors.push(slug+' missing original Canonical');
   if(!html.includes('href="/v71-v80-quality.css"'))report.errors.push(slug+' missing shared CSS reference');
   if(html.includes('target="_blank" rel="noopener noreferrer"')===false)report.warnings.push(slug+' no external references');
   if(html.includes('AI 생성')&&!html.includes('AI 여행 참고 이미지'))report.warnings.push(slug+' check photo labeling');
   if(!manifest.pages.find(p=>p.slug===slug)?.originalExternalReference)report.sourceTypes.portal++;else report.sourceTypes.individual++;
   for(const width of widths){
      const page=await browser.newPage({viewport:{width,height:850},deviceScaleFactor:1});
      try{
        const url='http://127.0.0.1:8757/things-to-do/'+slug+'/';
        const response=await page.goto(url,{waitUntil:'domcontentloaded',timeout:22000});
        const panel=page.locator('#'+id);
        await panel.waitFor({timeout:12000});
        const data=await page.evaluate((id)=>{
         const el=document.getElementById(id),root=document.documentElement;
         const r=el.getBoundingClientRect(),cards=[...el.querySelectorAll('.nf-q80-card')],links=[...el.querySelectorAll('a')];
         const grid=el.querySelector('.nf-q80-grid');
         const logo=document.querySelector('a.brand img');
         return {
          viewport:innerWidth,pageWidth:root.scrollWidth,panelWidth:Math.round(r.width),
          panelVisible:r.width>150&&r.height>150,
          cards:cards.length,cardLinks:cards.filter(c=>c.querySelector('a[href]')).length,
          gridColumns:getComputedStyle(grid).gridTemplateColumns.split(' ').filter(Boolean).length,
          h1:document.querySelectorAll('h1').length,
          cssApplied:getComputedStyle(el).borderTopLeftRadius!=='0px',
          logoWidth:logo?.getBoundingClientRect().width||0,
          canonical:document.querySelector('link[rel="canonical"]')?.href||'',
          tooWideLinks:links.filter(a=>{const x=a.getBoundingClientRect();return x.left < -2||x.right>innerWidth+2}).slice(0,4).map(x=>x.href),
          overflowCandidates:root.scrollWidth>innerWidth+2?[...document.querySelectorAll('body *')].filter(n=>{const x=n.getBoundingClientRect();return x.right>innerWidth+2||x.left < -2}).slice(0,5).map(n=>({tag:n.tagName,class:String(n.className).slice(0,60),width:Math.round(n.getBoundingClientRect().width),right:Math.round(n.getBoundingClientRect().right)})):[]
         };
        },id);
        const issues=[];
        if(response?.status()!==200)issues.push('HTTP '+response?.status());
        if(data.pageWidth>width+2)issues.push('horizontal overflow '+data.pageWidth+' - '+width);
        if(!data.panelVisible||data.cards!==3||data.cardLinks!==3)issues.push('missing or unusable quality cards');
        if(!data.cssApplied)issues.push('quality stylesheet not loaded');
        if(data.gridColumns!==(width<=850?1:3))issues.push('incorrect responsive grid '+data.gridColumns);
        if(data.h1!==1)issues.push('invalid H1 count '+data.h1);
        if(data.logoWidth>46)issues.push('oversized logo '+data.logoWidth);
        if(data.tooWideLinks.length)issues.push('out-of-viewport links '+data.tooWideLinks.join(','));
        if(data.canonical!=='https://www.nipponferry.com/things-to-do/'+slug+'/')issues.push('changed canonical '+data.canonical);
        if(seq===0&&[320,1440].includes(width)){
          await panel.screenshot({path:path.join(dir,v+'-'+slug+'-'+width+'.png'),animations:'disabled',timeout:20000});
        }
        report.checks.push({version:v,slug,width,...data,issues});
        if(issues.length){report.counts[v].failed++;issues.forEach(x=>report.errors.push(v+' '+slug+' '+width+': '+x));}
        else report.counts[v].passed++;
      }catch(e){report.counts[v].failed++;report.errors.push(v+' '+slug+' '+width+': '+String(e).slice(0,260));}
      finally{await page.close()}
   }
   seq++;
 }
}
}catch(e){report.errors.push('Chromium failed '+String(e))}
finally{if(browser)await browser.close()}
report.passed=report.errors.length===0;
fs.writeFileSync(dir+'/browser-qa.json',JSON.stringify(report,null,2)+'\n');
for(const v of Object.keys(manifest.cohorts)){
 fs.writeFileSync(dir+'/qa-'+v.toLowerCase()+'.json',JSON.stringify({version:v,...report.counts[v],samples:report.checks.filter(x=>x.version===v&&x.issues.length).slice(0,12)},null,2)+'\n');
}
console.log(JSON.stringify({passed:report.passed,articles:report.articles,viewports:report.checks.length,passedByVersion:report.counts,errors:report.errors.slice(0,45),warnings:report.warnings.length},null,2));
if(!report.passed)process.exitCode=1;
