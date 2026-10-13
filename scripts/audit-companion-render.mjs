// Browser-based visual QA of the deployed NIPPONFERRY companion guides.
// Run: npm install --no-save playwright; npx playwright install chromium;
//      node scripts/audit-companion-render.mjs
// LOCAL_BASE_URL=http://127.0.0.1:8765, LIVE_BASE_URL=https://www.nipponferry.com
import { chromium } from 'playwright';
import { readdir, mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
const sourceDir='site/things-to-do', outputDir='audit-reports/visual-v10';
const local=(process.env.LOCAL_BASE_URL || 'http://127.0.0.1:8765').replace(/\/$/,'');
const live=(process.env.LIVE_BASE_URL || 'https://www.nipponferry.com').replace(/\/$/,'');
await mkdir(outputDir,{recursive:true});
const files=await readdir(sourceDir,{withFileTypes:true});
const slugs=files.filter(f=>f.isDirectory()&&/-cruise-(family|couple)-guide$/.test(f.name)).map(f=>f.name).sort();
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
const results=[];
async function checkPage(base,slug,kind,viewport,label) {
  const url=base+'/things-to-do/'+slug+'/';
  const page=await browser.newPage({viewport,deviceScaleFactor:1,locale:'ko-KR',isMobile:label==='mobile',hasTouch:label==='mobile'});
  const failedRequests=[];
  page.on('requestfailed',r=>{if(r.url().startsWith(base)) failedRequests.push({url:r.url(),error:r.failure()?.errorText})});
  let httpStatus=null,loadError=null;
  try {
    // DOM and images are checked in Chromium, not inferred from GitHub file paths.
    const response=await page.goto(url,{waitUntil:'domcontentloaded',timeout:22000});
    httpStatus=response?.status()??null;
    if(httpStatus<200||httpStatus>=400) throw new Error('HTTP '+httpStatus);
    await page.locator('#ct-topic-dashboard .ct-grid > article.ct-card').first().waitFor({timeout:8000});
    await page.locator('#ct-topic-dashboard .ct-card img').last().scrollIntoViewIfNeeded({timeout:5000});
    await page.evaluate(async()=>{
      const imgs=[...document.querySelectorAll('#ct-topic-dashboard .ct-grid > article.ct-card img')];
      await Promise.all(imgs.map(img=>new Promise(done=>{
        if(img.complete)return done();
        const t=setTimeout(done,7000);img.addEventListener('load',()=>{clearTimeout(t);done()},{once:true});
        img.addEventListener('error',()=>{clearTimeout(t);done()},{once:true});
      })));
    });
  }catch(e){loadError=String(e.message).slice(0,250)}
  let data=null;
  if(!loadError){
    data=await page.evaluate(()=>{
      const cards=[...document.querySelectorAll('#ct-topic-dashboard .ct-grid > article.ct-card')];
      const blocks=['.ct-tag','h3','.ct-photo','.ct-distance','a:last-child'];
      return {
        title:document.title, cards:cards.map((card,i)=>{
          const img=card.querySelector('.ct-photo img'),fig=card.querySelector('figcaption');
          const r=card.getBoundingClientRect(), cs=getComputedStyle(card);
          const boxes=blocks.map(s=>card.querySelector(s)).filter(Boolean).map(el=>el.getBoundingClientRect());
          let maxGap=0;
          for(let j=1;j<boxes.length;j++) maxGap=Math.max(maxGap, Math.max(0,boxes[j].top-boxes[j-1].bottom));
          const figLinks=fig?[...fig.querySelectorAll('a')].map(a=>a.href):[];
          return {index:i+1, title:card.querySelector('h3')?.textContent?.trim()||'',
            imageSrc:img?.getAttribute('src')||null,imageLoaded:!!img&&img.complete&&img.naturalWidth>0,
            imageWidth:img?.naturalWidth??0,imageHeight:img?.naturalHeight??0,
            alt:img?.alt||'',captionPresent:!!fig&&fig.textContent.trim().length>=12,
            sourceLink:figLinks.some(x=>/commons\.wikimedia\.org/.test(x)),
            licenseLink:figLinks.some(x=>/creativecommons\.org|commons\.wikimedia\.org/.test(x)),
            caption:fig?.textContent?.trim().slice(0,140)||'',
            cardHeight:Math.round(r.height),forcedMinHeight:cs.minHeight,
            maxGap:Math.round(maxGap)
          };
        }),
        horizontalOverflow:document.documentElement.scrollWidth>innerWidth+4,
        viewportWidth:innerWidth,
        cssLinks:[...document.querySelectorAll('link[rel=stylesheet]')].map(l=>l.href)
      };
    });
    try {
      const root=page.locator('#ct-topic-dashboard');
      await root.screenshot({path:path.join(outputDir,kind+'-'+label+'-'+slug+'.png'),animations:'disabled',timeout:14000});
    }catch(e){data.screenshotError=String(e.message).slice(0,180)}
  }
  const issues=[];
  if(loadError)issues.push('PAGE_LOAD_FAILED');
  if(data){
    if(data.cards.length!==3) issues.push('CARD_COUNT_'+data.cards.length);
    if(data.horizontalOverflow)issues.push('HORIZONTAL_OVERFLOW');
    data.cards.forEach(c=>{
      if(!c.imageLoaded)issues.push('BROKEN_IMAGE_'+c.index);
      if(!c.captionPresent)issues.push('MISSING_CREDIT_'+c.index);
      if(!c.sourceLink)issues.push('MISSING_SOURCE_LINK_'+c.index);
      if(!c.licenseLink)issues.push('MISSING_LICENSE_LINK_'+c.index);
      if(c.maxGap>140)issues.push('OVERSIZED_CARD_GAP_'+c.index);
      if(c.imageLoaded&&!c.alt)issues.push('MISSING_ALT_'+c.index);
    });
  }
  const row={environment:kind,mode:label,page:slug,url,httpStatus,loadError,failedRequests,data,issues};
  results.push(row);
  console.log(kind,label,slug,issues.length?'ISSUES '+issues.join(','):'PASS');
  await page.close();
}
for(const env of [{name:'build-preview',base:local},{name:'live',base:live}]){
  for(const slug of slugs){
    await checkPage(env.base,slug,env.name,{width:390,height:844},'mobile');
    // Desktop test for every page; screenshots only mobile by default to bound artifacts.
    const desktop=await browser.newPage({viewport:{width:1365,height:900},locale:'ko-KR'});
    let row={environment:env.name,mode:'desktop',page:slug,url:env.base+'/things-to-do/'+slug+'/',issues:[]};
    try {
      const res=await desktop.goto(row.url,{waitUntil:'domcontentloaded',timeout:16000});
      row.httpStatus=res?.status()??null;
      if(!res?.ok())throw new Error('HTTP '+row.httpStatus);
      await desktop.locator('#ct-topic-dashboard .ct-grid > article.ct-card').first().waitFor({timeout:7000});
      row.data=await desktop.evaluate(()=>{
        const grid=document.querySelector('#ct-topic-dashboard .ct-grid');
        const cards=[...grid.querySelectorAll(':scope > article.ct-card')];
        return {gridColumns:getComputedStyle(grid).gridTemplateColumns,cardHeights:cards.map(x=>Math.round(x.getBoundingClientRect().height)),
        hasHorizontalOverflow:document.documentElement.scrollWidth>innerWidth+4,
        cardImages:cards.map(x=>{const img=x.querySelector('img');return {url:img?.getAttribute('src'),loaded:!!img&&img.complete&&img.naturalWidth>0}})};
      });
      // Wait for image readiness rather than treating lazy-load at offscreen coordinates as broken.
      await desktop.locator('#ct-topic-dashboard .ct-card img').last().scrollIntoViewIfNeeded({timeout:5000});
      await desktop.evaluate(async()=>{const imgs=[...document.querySelectorAll('#ct-topic-dashboard .ct-card img')];await Promise.all(imgs.map(img=>new Promise(resolve=>{if(img.complete)return resolve();img.addEventListener('load',resolve,{once:true});img.addEventListener('error',resolve,{once:true});setTimeout(resolve,6000)})))});
      row.data.cardImages=await desktop.evaluate(()=>[...document.querySelectorAll('#ct-topic-dashboard .ct-card img')].map(img=>({url:img.getAttribute('src'),loaded:img.complete&&img.naturalWidth>0})));
      if(row.data.cardImages.length!==3||row.data.cardImages.some(x=>!x.loaded))row.issues.push('DESKTOP_BROKEN_IMAGES');
      if(row.data.hasHorizontalOverflow)row.issues.push('DESKTOP_HORIZONTAL_OVERFLOW');
      if(slugs.indexOf(slug)<3)await desktop.locator('#ct-topic-dashboard').screenshot({path:path.join(outputDir,env.name+'-desktop-'+slug+'.png'),animations:'disabled'});
    }catch(e){row.issues.push('DESKTOP_LOAD_FAILED');row.loadError=String(e.message).slice(0,200)}
    results.push(row);console.log(env.name,'desktop',slug,row.issues.length?row.issues.join(','):'PASS');
    await desktop.close();
  }
}
await browser.close();
const summary={checkedAt:new Date().toISOString(),pageCount:slugs.length,
  environments:Object.fromEntries(['build-preview','live'].map(name=>{
    const list=results.filter(r=>r.environment===name);
    return [name,{cases:list.length,pass:list.filter(r=>!r.issues.length).length,failed:list.filter(r=>r.issues.length>0).length,loadFailures:list.filter(r=>r.issues.includes('PAGE_LOAD_FAILED')||r.issues.includes('DESKTOP_LOAD_FAILED')).length,
      brokenImages:list.filter(r=>r.issues.some(s=>s.includes('BROKEN_IMAGE'))).length,
      missingCredit:list.filter(r=>r.issues.some(s=>s.includes('MISSING_CREDIT'))).length}];
  }))};
await writeFile(path.join(outputDir,'summary.json'),JSON.stringify({summary,results},null,2));
const lines=['environment,mode,page,status,issues,url',...results.map(r=>[r.environment,r.mode,r.page,r.issues.length?'FAIL':'PASS',r.issues.join(';'),r.url].map(x=>'"'+String(x??'').replaceAll('"','""')+'"').join(','))];
await writeFile(path.join(outputDir,'report.csv'),lines.join('\n')+'\n');
console.log('AUDIT_SUMMARY',JSON.stringify(summary));
