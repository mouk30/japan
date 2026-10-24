const fs=require('fs');
const {chromium}=require('playwright');
const BASE='https://www.nipponferry.com';
const targets=[
 {name:'things-to-do',url:'/things-to-do/'},
 {name:'cruise-ports',url:'/things-to-do/cruise-ports/'}
];
const sizes=[390,768,945,1440];
const expected=[
 '/images/editorial/v146-naoshima-miyanoura-ferry-terminal-2025.webp',
 '/images/editorial/v146-teshima-art-museum-exterior-2013.webp',
 '/images/culture-verified/japan-kagawa-udon-pilgrimage.webp'
];
const out='audit-output/v170-public';fs.mkdirSync(out,{recursive:true});
const rows=[];
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--disable-dev-shm-usage']});
 try{
  for(const site of targets){
   for(const width of sizes){
    const page=await browser.newPage({viewport:{width,height:950},deviceScaleFactor:1});
    page.setDefaultTimeout(9500);page.setDefaultNavigationTimeout(21000);
    try{
     const r=await page.goto(BASE+site.url+'?v170_photoQA=1',{waitUntil:'domcontentloaded',timeout:21000});
     const selector='#nf-v153-pilot-hub .nf-v153-pilot-card';
     const cards=page.locator(selector);
     await cards.first().scrollIntoViewIfNeeded({timeout:7000});
     for(const img of await page.locator(selector+' .nf-v170-wide-media > img').all()){
       await img.scrollIntoViewIfNeeded({timeout:6500});
     }
     const result=await page.evaluate(async({expected})=>{
       const cards=[...document.querySelectorAll('#nf-v153-pilot-hub .nf-v153-pilot-card')];
       const ims=cards.map(card=>card.querySelector('.nf-v170-wide-media > img'));
       await Promise.race([Promise.all(ims.filter(Boolean).map(async img=>{
         img.loading='eager';try{await img.decode();}catch(_){}
       })),new Promise(ok=>setTimeout(ok,7000))]);
       const detail=cards.map((card,i)=>{
         const wrap=card.querySelector('.nf-v170-wide-media');
         const img=card.querySelector('.nf-v170-wide-media > img');
         const link=card.querySelector('a.nf-v153-pilot-cta');
         const caption=card.querySelector('.nf-v153-pilot-photo-credit');
         const w=wrap?.getBoundingClientRect(),b=img?.getBoundingClientRect(),c=card.getBoundingClientRect();
         return {
           src:img?.getAttribute('src'),photoNatural:[img?.naturalWidth,img?.naturalHeight],
           photoDraw:[Math.round(b?.width||0),Math.round(b?.height||0)],
           boxRatio:w&&w.height?Math.round(1000*w.width/w.height)/1000:null,
           drawnRatio:b&&b.height?Math.round(1000*b.width/b.height)/1000:null,
           cardWidth:Math.round(c.width),cardHeight:Math.round(c.height),
           imageFit:img?getComputedStyle(img).objectFit:null,
           imgPosition:img?getComputedStyle(img).position:null,
           captionCredit:caption?.innerText?.slice(0,150),
           creditLinks:caption?.querySelectorAll('a').length||0,
           actionHeight:Math.round(link?.getBoundingClientRect().height||0),
           actionHref:link?.getAttribute('href'),alt:img?.alt
         };
       });
       const title=document.querySelector('#nf-v153-pilot-heading')?.innerText;
       return{width:innerWidth,scrollWidth:document.documentElement.scrollWidth,heading:title,
        details:detail,
        uniquePhotos:new Set(detail.map(x=>x.src)).size,
        expectedPhotos:detail.every((x,i)=>x.src===expected[i])
       };
     },{expected});
     const pass={
       http200:r.status()===200,threeCards:result.details.length===3,
       photosCorrectAndDistinct:result.expectedPhotos&&result.uniquePhotos===3,
       photoImagesDecode:result.details.every(x=>x.photoNatural?.[0]>=1100&&x.photoNatural?.[1]>=800),
       landscapeSlots:result.details.every(x=>x.boxRatio>=1.30&&x.boxRatio<=1.36),
       imageRenderedLandscape:result.details.every(x=>x.drawnRatio>=1.30&&x.drawnRatio<=1.36&&x.photoDraw[1]<x.photoDraw[0]),
       noForcedVerticalStretch:result.details.every(x=>x.imageFit==='cover'&&x.imgPosition==='absolute'),
       originalAuthorLicenseCaptions:result.details.every(x=>x.creditLinks===2&&x.captionCredit?.includes('실제 사진')),
       cardActionsUsable:result.details.every(x=>x.actionHeight>=50&&x.actionHref?.startsWith('/things-to-do/')),
       readableMobileNoOverflow:result.scrollWidth<=width+5
     };
     await page.locator('#nf-v153-pilot-hub').scrollIntoViewIfNeeded({timeout:6000});
     const shot=out+'/'+site.name+'-'+width+'.png';
     await page.screenshot({path:shot,fullPage:false,animations:'disabled',timeout:12000});
     const row={site:site.name,width,pass:Object.values(pass).every(Boolean),tests:pass,measure:result,screenshot:shot};rows.push(row);
     console.log(row.pass?'PASS':'FAIL',site.name,width,JSON.stringify(pass));
    }catch(e){rows.push({site:site.name,width,pass:false,error:String(e)});console.log('FAIL',site.name,width,String(e).slice(0,500));}
    finally{await Promise.race([page.close().catch(()=>{}),sleep(3000)])}
   }
  }
 }finally{await browser.close()}
 const obj={title:'V170 two existing hubs, three real licensed photos, 390/768/945/1440',
  count:rows.length,passed:rows.filter(x=>x.pass).length,rows};
 fs.writeFileSync(out+'/eight-screen-landscape-cards.json',JSON.stringify(obj,null,2));
 console.log('SUMMARY',obj.passed,'/',obj.count);
 if(obj.passed!==obj.count)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
