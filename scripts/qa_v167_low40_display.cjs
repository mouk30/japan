const fs=require('fs');const{chromium}=require('playwright');
const src='audit-output/v167/v167-low-resolution-40-priorities.json';
const input=JSON.parse(fs.readFileSync(src,'utf8'));const limit=3;
const items=input.items;const pages=new Map();
function pageUrl(s){return '/'+s.replace(/^site\//,'').replace(/index\.html$/,'');}
for(const item of items){
 const seen=new Set();
 for(const u of item.example_html.slice(0,6)){
  const pg=pageUrl(u.page);if(seen.has(pg))continue;seen.add(pg);
  if(seen.size>limit)break;
  if(!pages.has(pg))pages.set(pg,new Set());
  pages.get(pg).add(item.url);
 }
}
const entries=[...pages].flatMap(([pg,urls])=>[390,1440].map(width=>({pg,width,urls:[...urls]})));
const rows=[];let next=0;
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--disable-dev-shm-usage']});
 async function worker(){
  while(next<entries.length){
   const item=entries[next++];let page;
   try{
    page=await browser.newPage({viewport:{width:item.width,height:900}});
    page.setDefaultTimeout(8500);page.setDefaultNavigationTimeout(12000);
    const r=await page.goto('https://www.nipponferry.com'+item.pg,{waitUntil:'domcontentloaded',timeout:12000});
    const obs=await page.evaluate(async urls=>{
     const imgs=[...document.querySelectorAll('img')].filter(x=>urls.includes(x.getAttribute('src')));
     for(const im of imgs){im.loading='eager';im.fetchPriority='high';}
     await Promise.race([Promise.all(imgs.map(x=>x.decode().catch(()=>null))),new Promise(ok=>setTimeout(ok,3000))]);
     return imgs.map(im=>{
      const b=im.getBoundingClientRect(),nW=im.naturalWidth,nH=im.naturalHeight,fit=getComputedStyle(im).objectFit;
      const base=fit==='contain'||fit==='scale-down'?Math.min(b.width/nW,b.height/nH):Math.max(b.width/nW,b.height/nH);
      return{src:im.getAttribute('src'),alt:im.alt,width:nW,height:nH,
       drawW:Math.round(b.width),drawH:Math.round(b.height),fit,scale:(nW&&nH)?Math.round(base*100)/100:null};
     });
    },item.urls);
    rows.push({page:item.pg,width:item.width,http:r.status(),observations:obs,missing:item.urls.filter(x=>!obs.some(y=>y.src===x))});
    console.log('CHECK',item.pg,item.width,obs.map(z=>z.src+':'+z.scale).join(' '));
   }catch(e){rows.push({page:item.pg,width:item.width,error:String(e).slice(0,220)});console.log('ERROR',item.pg,item.width,String(e).slice(0,130));}
   finally{if(page)await Promise.race([page.close().catch(()=>{}),new Promise(ok=>setTimeout(ok,2500))]);}
  }
 }
 try{await Promise.all([worker(),worker(),worker()]);}
 finally{await browser.close();}
 const indexed=new Map();
 for(const row of rows)for(const o of row.observations||[]){
  if(!indexed.has(o.src))indexed.set(o.src,[]);
  indexed.get(o.src).push({page:row.page,width:row.width,scale:o.scale,draw:[o.drawW,o.drawH],fit:o.fit,alt:o.alt});
 }
 const summary=items.map(item=>{
  const obs=indexed.get(item.url)||[];
  const up=obs.filter(o=>o.scale!==null&&o.scale>1.10);
  return{url:item.url,priority:item.priority,dimensions:item.dimensions,uses:item.html_uses,
   sample_count:obs.length,max_scale:obs.length?Math.max(...obs.map(x=>x.scale||0)):null,
   upscaled:up.length>0,upscaled_examples:up.slice(0,4),observations:obs.slice(0,7),
   review:up.length?'HIGH_RES_SOURCE_OR_NO_CROP_NEEDED':
    obs.length?'SAMPLED_NO_SIGNIFICANT_UPSCALING':'NOT_VISIBLE_IN_SAMPLED_HTML'};
 });
 const report={version:'V167',scope:'40 low-dimension candidates at 390 and 1440 on up to three original use pages each',browserChecks:rows.length,
  candidateCount:summary.length,withUpscaling:summary.filter(z=>z.upscaled).length,
  sampledNoUpscaling:summary.filter(z=>z.review==='SAMPLED_NO_SIGNIFICANT_UPSCALING').length,
  notVisible:summary.filter(z=>z.review==='NOT_VISIBLE_IN_SAMPLED_HTML').length,
  DISCLAIMER:'Image pixels and browser CSS only; this does not certify scene identity, license, current venue or all pages.',
  summary,pages:rows};
 const out='audit-output/v167-low40-visual';fs.mkdirSync(out,{recursive:true});
 fs.writeFileSync(out+'/display-pixel-scale-40-candidates.json',JSON.stringify(report,null,2));
 console.log('RESULT',JSON.stringify({checks:rows.length,upscaleAssets:report.withUpscaling,withoutUpscale:report.sampledNoUpscaling,unmeasured:report.notVisible}));
 for(const x of summary.filter(z=>z.upscaled))console.log('UPSCALED',JSON.stringify({url:x.url,priority:x.priority,px:x.dimensions,maxScale:x.max_scale,examples:x.upscaled_examples}));
})().catch(e=>{console.error(e);process.exitCode=1});
