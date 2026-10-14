import { chromium } from 'playwright';
import { readFile,mkdir,writeFile } from 'node:fs/promises';
import path from 'node:path';
const spec=JSON.parse(await readFile('scripts/parents-port-v12-data.json','utf8'));
const ports=Object.keys(spec.cities);
const output='audit-reports/companion-port-v12-visual';await mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
const results=[];
const envs=[['build',process.env.LOCAL_BASE_URL||'http://127.0.0.1:8765'],['production',process.env.LIVE_BASE_URL||'https://www.nipponferry.com']];
const sizes=[['mobile',390,844],['desktop',1365,900]];
for(const [env,base] of envs)for(const [device,width,height] of sizes)for(const port of ports)for(const mode of ['family','couple']){
  const slug=port+'-cruise-'+mode+'-guide';
  const url=base.replace(/\/$/,'')+'/things-to-do/'+slug+'/';
  const page=await browser.newPage({viewport:{width,height},locale:'ko-KR',deviceScaleFactor:1});
  const errors=[];let content=null,http=null;
  try{
    const res=await page.goto(url,{waitUntil:'domcontentloaded',timeout:23000});
    http=res?.status();if(!res?.ok())throw Error('HTTP '+http);
    const panel=page.locator('#nf-shared-port-v12');
    await panel.waitFor({timeout:8000});
    content=await page.evaluate(()=>{
      const root=document.querySelector('#nf-shared-port-v12');
      const cards=[...root.querySelectorAll('.nf-share-route')];
      const links=[...root.querySelectorAll('.nf-share-route>a')];
      const photos=[...document.querySelectorAll('#ct-topic-dashboard .ct-grid .ct-card img')];
      return {
        cssPresent:!!document.querySelector('link[href*="companion-shared-port-v12.css"]'),
        mode:root.classList.contains('family')?'family':root.classList.contains('couple')?'couple':'unknown',
        hasReturn:!!root.querySelector('.nf-share-return'),
        hasFocus:!!root.querySelector('.nf-share-focus'),
        hasIntro:!!root.querySelector('.nf-share-concept'),
        noHorizontalOverflow:document.documentElement.scrollWidth<=innerWidth+3,
        sourceLinks:links.map(a=>a.getAttribute('href')),
        cards:cards.map(c=>({title:c.querySelector('h3')?.textContent?.trim(),value:c.querySelector('.nf-share-value')?.textContent?.trim(),height:Math.round(c.getBoundingClientRect().height),minHeight:getComputedStyle(c).minHeight})),
        cardGridAlign:getComputedStyle(root.querySelector('.nf-share-grid')).alignItems,
        topCards:document.querySelectorAll('#ct-topic-dashboard .ct-grid > .ct-card').length,
        photoCount:photos.length,
        photoRatios:photos.map(p=>{const r=p.getBoundingClientRect();return r.width>0 ? Number((r.height/r.width).toFixed(2)) : 0}),
      };
    });
    if(!content.cssPresent||!content.hasReturn||!content.hasFocus||!content.hasIntro)errors.push('MISSING_PORT_CONTENT_OR_CSS');
    if(!content.noHorizontalOverflow)errors.push('HORIZONTAL_OVERFLOW');
    if(content.mode!==mode)errors.push('WRONG_COMPANION_MODE');
    if(content.cardGridAlign!=='start')errors.push('CARD_HEIGHT_STRETCH');
    if(content.topCards!==3)errors.push('TOP3_CARD_COUNT_CHANGED');
    if(content.photoCount!==3)errors.push('MISSING_EXISTING_PHOTO');
    if(content.photoRatios.some(v=>v && Math.abs(v-.75)>.055))errors.push('PHOTO_4_3_RATIO_REGRESSION');
    if(content.cards.length!==spec.cities[port].routes.length)errors.push('SOURCE_SEGMENT_COUNT');
    for(let i=0;i<Math.min(spec.cities[port].routes.length,content.cards.length);i++){
       const row=spec.cities[port].routes[i];
       if(content.cards[i].title!==row[0]||content.cards[i].value!==row[2])errors.push('ROUTE_VALUE_MISMATCH_'+(i+1));
       if(content.sourceLinks[i]!==row[4])errors.push('SOURCE_URL_MISMATCH_'+(i+1));
       if(content.cards[i].minHeight!=='0px')errors.push('FORCED_HEIGHT_'+(i+1));
    }
    if(device==='mobile'&&['ishigaki','kagoshima','osaka','sasebo','yokohama'].includes(port)){
       await panel.screenshot({path:path.join(output,env+'-'+device+'-'+slug+'.png'),animations:'disabled',timeout:14000});
    }
  }catch(e){errors.push('PAGE_AUDIT_EXCEPTION');content={error:String(e.message).slice(0,220)}}
  results.push({env,device,port,mode,url,http,errors,content});
  console.log(env,device,slug,errors.length?'FAIL '+errors.join(','):'PASS');
  await page.close();
}
await browser.close();
const summary={pages:ports.length*2,cases:results.length,pass:results.filter(r=>!r.errors.length).length,failed:results.filter(r=>r.errors.length).length,failures:results.filter(r=>r.errors.length).map(r=>({env:r.env,device:r.device,port:r.port,mode:r.mode,errors:r.errors,reason:r.content?.error}))};
await writeFile(path.join(output,'summary.json'),JSON.stringify(summary,null,2));
await writeFile(path.join(output,'results.json'),JSON.stringify(results,null,2));
await writeFile(path.join(output,'report.csv'),['environment,viewport,port,mode,result,issues',...results.map(x=>[x.env,x.device,x.port,x.mode,x.errors.length?'FAIL':'PASS',x.errors.join(';')].map(y=>'"'+String(y).replaceAll('"','""')+'"').join(','))].join('\n')+'\n');
console.log('FINAL',JSON.stringify(summary));
if(summary.failed)process.exitCode=1;
