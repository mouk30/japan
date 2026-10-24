const fs=require('fs');
const {chromium}=require('playwright');
// Each selector is intentionally specific to the V167 corrected region.
const sites=[
 ['hokkaido','/japan/hokkaido/','#highlights','#highlights .city-card img',3],
 ['osaka','/japan/osaka/','#cruise','#cruise .nf167-panstar-photo img',1],
 ['directory','/japan/','.dirgrid','a[href^="/japan/fukuoka"] img',19],
 ['busan','/busan-osaka-cruise/','.nf167-miracle-photo','.nf167-miracle-photo img',1]
];
const widths=[390,768,1440],out='audit-output/v167-browser';
fs.mkdirSync(out,{recursive:true});
const sleep=(ms)=>new Promise(resolve=>setTimeout(resolve,ms));
(async()=>{
 const b=await chromium.launch({headless:true,args:['--disable-dev-shm-usage']});
 const rows=[];
 try{
  for(const [name,path,area,selector,need] of sites){
   for(const width of widths){
    const p=await b.newPage({viewport:{width,height:850}});
    p.setDefaultTimeout(9000);
    p.setDefaultNavigationTimeout(18000);
    try{
     const r=await p.goto('https://www.nipponferry.com'+path,{waitUntil:'domcontentloaded',timeout:18000});
     // A tall responsive directory should never block the entire suite while
     // waiting for scrolling to settle, decoding lazy images, or whole-grid screenshots.
     await p.locator(area).first().scrollIntoViewIfNeeded({timeout:8000});
     const report=await p.evaluate(async selector=>{
      const elements=Array.from(document.querySelectorAll(selector));
      for(const img of elements){img.loading='eager';img.fetchPriority='high';}
      const completed=Promise.all(elements.map(async img=>{
       try{await img.decode();}catch(e){/* quality result will fail if missing */ }
      }));
      await Promise.race([completed,new Promise(done=>setTimeout(done,5000))]);
      return {screen:window.innerWidth,doc:document.documentElement.scrollWidth,
       images:elements.map(img=>({width:img.naturalWidth,height:img.naturalHeight,
        draw:Math.round(img.getBoundingClientRect().width),src:img.currentSrc,alt:img.alt}))};
     },selector);
     const check={
      http:r.status()===200,
      image_count:report.images.length>=need,
      load:report.images.length>0 && report.images.every(img=>img.width>0),
      layout:report.doc<=report.screen+4,
      large_photo:!['hokkaido','osaka','busan'].includes(name)||report.images.every(img=>img.width>=900),
      no_upscale:name!=='hokkaido'||report.images.every(img=>img.width>=img.draw),
      distinct:name!=='hokkaido'||new Set(report.images.map(img=>img.src)).size===3,
      varied:name!=='directory'||new Set(report.images.map(img=>img.src)).size>=10
     };
     const file=out+'/'+name+'-'+width+'.png';
     // Bounded viewport screenshot prevents an unbounded 19-card
     // document from stalling Playwright for the entire 25-minute job.
     await p.screenshot({path:file,animations:'disabled',fullPage:false,timeout:12000});
     const row={name,width,ok:Object.values(check).every(Boolean),check,photo:report.images,screenshot:file};
     rows.push(row);
     console.log(row.ok?'PASS':'FAIL',name,width,JSON.stringify(check));
    }catch(e){
     rows.push({name,width,ok:false,error:String(e)});
     console.log('FAIL',name,width,String(e).slice(0,350));
    }finally{
     await Promise.race([p.close().catch(()=>{}),sleep(3000)]);
    }
   }
  }
 }finally{await Promise.race([b.close().catch(()=>{}),sleep(6000)]);}
 const result={screens:rows.length,passed:rows.filter(x=>x.ok).length,rows};
 fs.writeFileSync(out+'/live-390-768-1440.json',JSON.stringify(result,null,2));
 console.log('SUMMARY',result.passed,'/',result.screens);
 if(result.passed!==result.screens)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
