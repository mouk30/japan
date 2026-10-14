import { chromium } from 'playwright';
import { readFile,mkdir,writeFile } from 'node:fs/promises';
import path from 'node:path';

const manifest=JSON.parse(await readFile('scripts/v16-gate-venue-transport.json','utf8'));
const ports=Object.keys(manifest.ports);
const dir='audit-reports/v16/visual';
await mkdir(dir,{recursive:true});
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
const environments=[['build',process.env.LOCAL_BASE_URL||'http://127.0.0.1:8765'],['production',process.env.LIVE_BASE_URL||'https://www.nipponferry.com']];
const viewports=[['mobile',390,844],['desktop',1365,900]];
const rows=[];
for(const [environment,base] of environments)for(const [viewport,width,height] of viewports)
for(const port of ports)for(const audience of ['family','couple','parents']){
  const slug=port+'-cruise-'+audience+'-guide';
  const page=await browser.newPage({viewport:{width,height},locale:'ko-KR',deviceScaleFactor:1});
  const url=base.replace(/\/$/,'')+'/things-to-do/'+slug+'/';
  let state=null,http=null;const errors=[];
  try{
    const response=await page.goto(url,{waitUntil:'domcontentloaded',timeout:26000});
    http=response?.status();if(!response?.ok())throw Error('HTTP '+http);
    await page.locator('#ct-topic-dashboard .ct-grid>.ct-card').first().waitFor({timeout:9000});
    await page.waitForFunction(()=>{
      const loaded=[...document.styleSheets].map(x=>x.href||'');
      return loaded.some(x=>x.includes('companion-gate-v16.css'))&&loaded.some(x=>x.includes('companion-card-standard.css'));
    },null,{timeout:15000});
    for(const photo of await page.locator('#ct-topic-dashboard .ct-grid>.ct-card .ct-photo img').all()){
      await photo.scrollIntoViewIfNeeded({timeout:5000});
      await photo.evaluate(async image=>{try{await image.decode()}catch{}});
    }
    state=await page.evaluate(()=>{
      const root=document.querySelector('#ct-topic-dashboard');
      const cards=[...root.querySelectorAll('.ct-grid > article.ct-card')];
      const brief=root.querySelector('#nf-v16-brief');
      const entries=cards.map(card=>{
        const title=card.querySelector('h3')?.textContent.trim();
        const details=card.querySelector('details.nf-v16-route');
        const img=card.querySelector('.ct-photo img');
        const r=img?.getBoundingClientRect();
        const links=details?[...details.querySelectorAll('.nf-v16-evidence a')].map(a=>a.getAttribute('href')):[];
        return {title,detailsPresent:!!details,detailsInitiallyClosed:details?!details.open:false,
           hasGate:!!details?.textContent.includes('실제 출발점'),
           hasAccess:!!details?.textContent.includes('접근'),
           hasLastReturn:!!details?.textContent.includes('귀선'),
           hasShuttle:!!details?.textContent.includes('셔틀'),
           noInventedExactDistance:!!details?.textContent.includes('실측 미확인'),
           links,
           alt:img?.alt||'',imageLoaded:!!img&&img.complete&&img.naturalWidth>0,
           aspectRatio:r?.width ? +(r.height/r.width).toFixed(3) : null,
           minHeight:getComputedStyle(card).minHeight,
           sourceInline:[...card.querySelectorAll('figcaption a')].every(a=>getComputedStyle(a).display==='inline')
        };
      });
      return {cssLinked:!!document.querySelector('link[href*="companion-gate-v16.css"]'),
        visibleBrief:!!brief,portSource:brief?.querySelector('a')?.getAttribute('href'),
        overflow:document.documentElement.scrollWidth>innerWidth+4,
        entries,
        summaryText:brief?.textContent.slice(0,360)};
    });
    if(!state.visibleBrief||!state.cssLinked)errors.push('PORT_BRIEF_MISSING');
    if(state.overflow)errors.push('HORIZONTAL_OVERFLOW');
    if(state.portSource!==manifest.ports[port].url)errors.push('PORT_OFFICIAL_SOURCE_MISMATCH');
    if(state.entries.length!==3)errors.push('THREE_VENUE_CARDS_NOT_FOUND');
    state.entries.forEach((x,i)=>{
      if(!x.detailsPresent||!x.hasGate||!x.hasAccess||!x.hasLastReturn||!x.hasShuttle||!x.noInventedExactDistance)errors.push('ROUTE_STEP_MISSING_'+(i+1));
      if(x.links[0]!==manifest.ports[port].url||!x.links[1]?.startsWith('https://'))errors.push('SOURCE_LINK_INVALID_'+(i+1));
      if(!x.detailsInitiallyClosed)errors.push('ACCORDION_INIT_OPEN_'+(i+1));
      if(x.imageLoaded && (x.aspectRatio===null || Math.abs(x.aspectRatio-.75)>.045))errors.push('PHOTO_RATIO_'+(i+1));
      if(x.aspectRatio!==null&&!x.imageLoaded)errors.push('BROKEN_PHOTO_'+(i+1));
      if(!x.sourceInline)errors.push('PHOTO_CREDIT_AS_BUTTON_'+(i+1));
      if(x.minHeight!=='0px')errors.push('FORCED_CARD_HEIGHT_'+(i+1));
    });
    const summary=page.locator('#ct-topic-dashboard details.nf-v16-route').first().locator('summary');
    await summary.focus();await page.keyboard.press('Enter');
    const expanded=await page.locator('#ct-topic-dashboard details.nf-v16-route').first().evaluate(x=>x.open);
    if(!expanded)errors.push('KEYBOARD_ACCORDION_FAILED');
    if(environment==='production'&&viewport==='mobile'&&['ishigaki','naha','osaka','hakodate','yokohama'].includes(port)){
      await page.locator('#ct-topic-dashboard').screenshot({path:path.join(dir,'production-mobile-'+slug+'.png'),timeout:17000,animations:'disabled'});
    }
  }catch(e){errors.push('BROWSER_CHECK_EXCEPTION');state={error:String(e.message).slice(0,250)}}
  rows.push({environment,viewport,port,audience,url,http,errors,state});
  console.log(environment,viewport,slug,errors.length?'FAIL '+errors.join(';'):'PASS');
  await page.close();
}
await browser.close();
const summary={pages:45,venueCards:135,cases:rows.length,pass:rows.filter(x=>!x.errors.length).length,fail:rows.filter(x=>x.errors.length).length,failures:rows.filter(x=>x.errors.length).map(x=>({env:x.environment,view:x.viewport,port:x.port,audience:x.audience,issues:x.errors,detail:x.state?.error}))};
await writeFile(path.join(dir,'summary.json'),JSON.stringify(summary,null,2));
await writeFile(path.join(dir,'results.json'),JSON.stringify(rows,null,2));
await writeFile(path.join(dir,'report.csv'),['environment,viewport,port,audience,result,issues',...rows.map(x=>[x.environment,x.viewport,x.port,x.audience,x.errors.length?'FAIL':'PASS',x.errors.join(';')].map(s=>'"'+String(s).replaceAll('"','""')+'"').join(','))].join('\n')+'\n');
console.log('V16_FINAL',JSON.stringify(summary));
if(summary.fail)process.exitCode=1;
