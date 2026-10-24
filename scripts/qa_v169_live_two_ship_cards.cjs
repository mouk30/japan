const fs=require('fs'),{chromium}=require('playwright');
const BASE='https://www.nipponferry.com',SHIP='/images/venues/nf-v134-new-camellia-busan-2026-real.webp';
const sites=[
 {id:'fukuoka',url:'/japan/fukuoka/',selector:'section#ferry img.fk-photo--new-camellia'},
 {id:'busan-fukuoka',url:'/busan-fukuoka-cruise/',selector:'img.nf169-camellia'}
];
const sizes=[390,768,1440],out='audit-output/v169-public';fs.mkdirSync(out,{recursive:true});
const results=[];
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--disable-dev-shm-usage']});
 try{
  for(const item of sites){
   for(const width of sizes){
    const p=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
    p.setDefaultTimeout(8000);p.setDefaultNavigationTimeout(20000);
    try{
     const resp=await p.goto(BASE+item.url+'?v169_photo_qa=1',{waitUntil:'domcontentloaded',timeout:20000});
     const loc=p.locator(item.selector).first();await loc.scrollIntoViewIfNeeded({timeout:8000});
     const obj=await p.evaluate(async({selector,SHIP,id})=>{
      let el=document.querySelector(selector);
      if(!el)return {error:'target photo missing'};
      el.loading='eager';try{await Promise.race([el.decode(),new Promise(r=>setTimeout(r,7000))]);}catch(e){}
      let box=el.getBoundingClientRect(),cs=getComputedStyle(el),hero=document.querySelector('.h');
      return {src:el.getAttribute('src'),naturalWidth:el.naturalWidth,naturalHeight:el.naturalHeight,
       visible:box.width>200&&box.height>150,fit:cs.objectFit,alt:el.alt,
       wrongOldImageUsed:[...document.images].some(x=>x.getAttribute('src')==='/images/ferry.jpg'),
       credit:document.body.textContent.includes('Midnight cadet')&&[...document.querySelectorAll('a')].some(x=>x.href.includes('creativecommons.org/licenses/by/4.0')),
       hero:hero?getComputedStyle(hero,'::before').backgroundImage:'',
       documentWidth:document.documentElement.scrollWidth,viewport:innerWidth,
       shippingCardContent:id!=='fukuoka'||document.querySelector('#ferry')?.textContent.includes('뉴카멜리아'),
       actualPhotoMatches:el.getAttribute('src')===SHIP};
     },{selector:item.selector,SHIP,id:item.id});
     const rules={html200:resp.status()===200,targetFound:!obj.error,
      correctActual2026Ship:obj.actualPhotoMatches===true,
      nativeSize:obj.naturalWidth>=1200&&obj.naturalHeight>=800,
      uncroppedAndNotStretched:obj.fit==='contain',
      imageVisible:obj.visible===true,noWrongPanStar:obj.wrongOldImageUsed===false,
      visibleRightsAndAuthor:obj.credit===true,correctCardContext:obj.shippingCardContent===true,
      noMajorHorizontalOverflow:obj.documentWidth<=width+5,
      heroAlsoNewCamellia:item.id==='fukuoka'||obj.hero.includes(SHIP)};
     const shot=out+'/'+item.id+'-'+width+'.png';
     await p.screenshot({path:shot,fullPage:false,animations:'disabled',timeout:12000});
     const row={site:item.id,width,pass:Object.values(rules).every(Boolean),rules,observed:obj,screenshot:shot};
     results.push(row);
     console.log(row.pass?'PASS':'FAIL',item.id,width,JSON.stringify(rules));
    }catch(e){results.push({site:item.id,width,pass:false,error:String(e)});console.log('FAIL',item.id,width,String(e).slice(0,280));}
    finally{await p.close().catch(()=>{})}
   }
  }
  const webp=await browser.newPage();
  try{
    const r=await webp.request.get(BASE+SHIP);
    const buf=await r.body();
    const ok=r.status()===200&&buf.slice(0,4).toString()==='RIFF'&&buf.slice(8,12).toString()==='WEBP';
    results.push({site:'original-high-res-webp',width:0,pass:ok,http:r.status(),bytes:buf.length});
    console.log(ok?'PASS':'FAIL','original WebP response',r.status(),buf.length);
  }catch(e){results.push({site:'original-high-res-webp',pass:false,error:String(e)})}
  finally{await webp.close().catch(()=>{})}
 }finally{await browser.close()}
 const report={version:'V169',screens:6,checked:results.length,passed:results.filter(x=>x.pass).length,rows:results};
 fs.writeFileSync(out+'/real-camellia-not-panstar-report.json',JSON.stringify(report,null,2));
 console.log('SUMMARY',report.passed,'/',report.checked);
 if(report.passed!==report.checked)process.exitCode=1;
})().catch(err=>{console.error(err);process.exitCode=1});
