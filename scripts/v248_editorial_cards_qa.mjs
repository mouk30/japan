/* V248 — destination/theme visual design and provenance regression.
   Run against built 'dist' via local HTTP server. */
import fs from 'node:fs';
import path from 'node:path';
import {chromium} from 'playwright';
const OUT='audit-reports/v248';
fs.mkdirSync(OUT,{recursive:true});
const source=fs.readFileSync('site/index.html','utf8');
const built=fs.readFileSync('dist/index.html','utf8');
const failures=[];
const assert=(ok,message)=>{if(!ok)failures.push(message)};
const textBetween=(html,start,end)=>{
 const from=html.indexOf(start);if(from<0)return '';
 const to=html.indexOf(end,from);return to<0?'':html.slice(from,to+end.length);
};
const sections=[
 {name:'destinations',selector:'.v65-destinations',marker:'<section class="section v65-destinations"',cards:'.v65-card',media:'.v65-photo',expected:8},
 {name:'themes',selector:'.v63-theme-section',marker:'<section class="section v63-theme-section"',cards:'.v63-card',media:'.v63-visual',expected:6}
];
assert(source.includes('<link rel="stylesheet" href="/nf-v248-editorial-cards.css?v=20261027">'),'V248 CSS not in homepage source');
assert(built.includes('<link rel="stylesheet" href="/nf-v248-editorial-cards.css?v=20261027">'),'V248 CSS not included in deployment build');
assert(built.includes('nf246-header'),'V246 homepage header overwritten');
assert(built.includes('data-nf247-finder'),'V247 interactive route finder lost');
assert((built.match(/<h1\b/g)||[]).length===1,'Homepage h1 changed');
const getMeta=(s,prop)=>s.match(prop)?.[1];
assert(getMeta(source,/<title>([^<]+)<\/title>/)===getMeta(built,/<title>([^<]+)<\/title>/),'SEO title changed');
assert(getMeta(source,/<link rel="canonical" href="([^"]+)"/)===getMeta(built,/<link rel="canonical" href="([^"]+)"/),'Canonical changed');
const report={generatedAt:new Date().toISOString(),sourceImages:0,internalLinks:0,imageFilesPresent:0,viewports:[],errors:[],warnings:[],artifacts:[]};
for(const sec of sections){
 const src=textBetween(source,sec.marker,'</section>'),dist=textBetween(built,sec.marker,'</section>');
 assert(src!==''&&dist!=='','Missing section '+sec.name);
 const srcImages=[...src.matchAll(/<img\b[^>]*>/g)].map(x=>x[0]);
 const distImages=[...dist.matchAll(/<img\b[^>]*>/g)].map(x=>x[0]);
 assert(srcImages.length===sec.expected&&distImages.length===sec.expected,sec.name+' images/card count mismatch');
 assert(JSON.stringify(srcImages)===JSON.stringify(distImages),sec.name+' build replaced photo/alt/credit');
 report.sourceImages+=srcImages.length;
 for(const im of srcImages){
  const srcUrl=im.match(/\bsrc="([^"]+)"/)?.[1]||'';
  const alt=im.match(/\balt="([^"]+)"/)?.[1]||'';
  assert(srcUrl.startsWith('/images/'),sec.name+' image not self-hosted');
  assert(alt.trim().length>=12,sec.name+' photo lacks informative alt');
  if(srcUrl.startsWith('/')){
   const file=path.join('dist',srcUrl.slice(1));
   assert(fs.existsSync(file),'Missing image file '+srcUrl);
   if(fs.existsSync(file))report.imageFilesPresent++;
  }
 }
 const allLinks=[...src.matchAll(/<a\b[^>]*href="([^"]+)"/g)].map(m=>m[1]);
 for(const url of allLinks){
  if(url.startsWith('#'))continue;
  if(!url.startsWith('/'))continue;
  const clean=url.split('#')[0].split('?')[0];
  const local=path.join('dist',clean.replace(/^\//,''));
  assert(fs.existsSync(local)||fs.existsSync(path.join(local,'index.html')),'Missing local link '+url);
  report.internalLinks++;
 }
 assert(src.includes('href="#nf-v148-photo-credits"'),sec.name+' missing attribution disclosure link');
 if(sec.name==='destinations'){
  assert((src.match(/data-nf248-index="\d\d"/g)||[]).length===8,'Missing image numeric overlays');
  assert(src.includes('여행 분위기 연출 이미지'),'Staged Hokkaido image label lost');
 }
 if(sec.name==='themes'){
  assert((src.match(/class="v63-photo-disclosure"/g)||[]).length>=3,'Theme staged-image disclosures lost');
 }
}
assert(source.includes('id="nf-v148-photo-credits"'),'Existing full photo credits disappeared');
const widths=[320,390,650,768,1024,1440];
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
try{
 for(const width of widths){
  const page=await browser.newPage({viewport:{width,height:950},deviceScaleFactor:1, reducedMotion:'reduce'});
  const issues=[];const check=(ok,msg)=>{if(!ok)issues.push(msg)};
  try{
   const response=await page.goto('http://127.0.0.1:8765/',{waitUntil:'domcontentloaded',timeout:30000});
   check(response?.status()===200,'HTTP '+response?.status());
   await page.locator('.v65-destinations .v65-card').first().waitFor();
   const metrics=await page.evaluate(()=>{
    const result={docWidth:document.documentElement.scrollWidth,innerWidth,sections:[]};
    for(const selector of ['.v65-destinations','.v63-theme-section']){
     const sec=document.querySelector(selector),cards=[...sec.querySelectorAll(selector.includes('v65')?'.v65-card':'.v63-card')];
     const isDest=selector.includes('v65'),images=[...sec.querySelectorAll('img')];
     const cardInfo=cards.map(el=>{const b=el.getBoundingClientRect(),cta=el.querySelector(isDest?'.v65-actions a:first-child':'.v63-cta');
      const ctaBox=cta?.getBoundingClientRect();
      const image=el.querySelector(isDest?'.v65-photo':'.v63-visual'),imBox=image?.getBoundingClientRect();
      return {width:b.width,height:b.height,ctaHeight:ctaBox?.height||0,photoRatio:(imBox?.width||0)/(imBox?.height||1),ctaVisible:!!(ctaBox?.width&&ctaBox?.height),
       title:el.querySelector('h3')?.textContent.trim(),num:el.querySelector('.v65-photo')?.dataset.nf248Index};
     });
     result.sections.push({name:isDest?'destinations':'themes',width:sec.getBoundingClientRect().width,
       cards:cardInfo,gridColumns:getComputedStyle(sec.querySelector(isDest?'.v65-grid':'.v63-grid')).gridTemplateColumns,
       originChip:isDest?!!sec.querySelector('.v104-photo-origin'):!!sec.querySelector('.v63-photo-disclosure'),
       creditVisible:!!sec.querySelector('.nf248-photo-note a')});
    }
    return result;
   });
   check(metrics.docWidth<=width+2,'Horizontal overflow '+metrics.docWidth);
   const [dest,theme]=metrics.sections;
   check(dest.cards.length===8&&theme.cards.length===6,'Unexpected card count');
   check(dest.cards.every(c=>c.width>225),'Destination card narrower than 225px');
   check(theme.cards.every(c=>c.width>225),'Theme card narrower than 225px');
   check(dest.cards.every(c=>c.ctaVisible&&c.ctaHeight>=43),'Destination guide CTA not touch accessible');
   check(theme.cards.every(c=>c.ctaVisible&&c.ctaHeight>=43),'Theme guide CTA not touch accessible');
   check(dest.cards.every(c=>c.photoRatio>1.45&&c.photoRatio<2.25),'Destination photos badly distorted');
   check(theme.cards.every(c=>c.photoRatio>1.65&&c.photoRatio<1.9),'Theme photo ratio inconsistent');
   check(dest.creditVisible&&theme.creditVisible&&dest.originChip&&theme.originChip,'Visible image credit not preserved');
   check(dest.cards.every((c,i)=>c.num===String(i+1).padStart(2,'0')),'Destination editorial index missing');
   if(width>=1200){
    check(dest.cards[0].width>dest.cards[2].width*1.3,'Featured destination cards not wider on desktop');
    check(Math.abs(theme.cards[0].width-theme.cards[1].width)<4,'Theme cards not aligned in desktop grid');
   }
   if(width<=650){
    check(Math.abs(dest.cards[0].width-dest.cards[2].width)<4,'Mobile destination card width inconsistent');
    check(Math.abs(theme.cards[0].width-theme.cards[1].width)<4,'Mobile theme card width inconsistent');
   }
   const focus=page.locator('.v65-destinations .v65-actions a:first-child').first();
   await focus.focus();
   check(await focus.evaluate(e=>document.activeElement===e),'Destination CTA cannot be keyboard focused');
   const themeLink=page.locator('.v63-theme-section .v63-cta').first();
   await themeLink.focus();
   check(await themeLink.evaluate(e=>document.activeElement===e),'Theme CTA cannot be keyboard focused');
   if([390,768,1440].includes(width)){
    for(const sec of sections){
     const target=page.locator(sec.selector);
     await target.scrollIntoViewIfNeeded();
     await target.screenshot({path:OUT+'/'+sec.name+'-'+width+'.png',animations:'disabled',timeout:30000});
     report.artifacts.push(sec.name+'-'+width+'.png');
    }
   }
   report.viewports.push({width,passed:issues.length===0,destinationCards:dest.cards.length,themeCards:theme.cards.length,featuredWidth:Math.round(dest.cards[0].width),regularWidth:Math.round(dest.cards[2].width),issues});
  }catch(err){issues.push('Browser: '+String(err).slice(0,600));report.viewports.push({width,passed:false,issues})}
  for(const issue of issues)failures.push(width+': '+issue);
  await page.close();
 }
}finally{await browser.close()}
report.errors=failures;report.passed=failures.length===0;
fs.writeFileSync(OUT+'/qa.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({passed:report.passed,sourceImages:report.sourceImages,imageFilesPresent:report.imageFilesPresent,internalLinks:report.internalLinks,screenWidths:report.viewports.length,screenshots:report.artifacts,errors:failures.slice(0,25)},null,2));
if(!report.passed)process.exitCode=1;
