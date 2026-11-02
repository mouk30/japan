/* V301: browser gate for the licensed Shikoku udon editorial card. */
"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const {chromium}=require("playwright");
const out="audit-output/v301/browser";
fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
 const results=[];
 try{
  for(const width of [390,768,1440]){
   const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
   const res=await page.goto("http://127.0.0.1:8765/things-to-do/food-experience/",{waitUntil:"load"});
   assert.equal(res.status(),200,"food page missing");
   const card=page.locator("#nf-v153-pilot-hub .nf-v153-pilot-card");
   assert.equal(await card.count(),1,"one original Shikoku feature");
   await card.scrollIntoViewIfNeeded();
   const img=card.locator("figure img");
   assert.equal(await img.count(),1,"single photo");
   await img.evaluate(el=>el.decode());
   const data=await page.evaluate(()=>{
    const b=e=>{const r=e?.getBoundingClientRect();return r?{x:r.x,y:r.y,width:r.width,height:r.height}:null};
    const c=document.querySelector("#nf-v153-pilot-hub .nf-v153-pilot-card");
    const f=c?.querySelector("figure"),photo=f?.querySelector("img"),copy=c?.querySelector(".nf-v153-pilot-copy"),cta=c?.querySelector("a.nf-v153-pilot-cta");
    return {h1:document.querySelectorAll("h1").length,card:b(c),figure:b(f),photo:b(photo),copy:b(copy),cta:b(cta),
     photoReady:!!photo&&photo.complete&&photo.naturalWidth>0,photoSrc:photo?.getAttribute("src"),photoAlt:photo?.getAttribute("alt"),
     ctaHref:cta?.getAttribute("href"),overflow:document.documentElement.scrollWidth>innerWidth+1};
   });
   assert.equal(data.h1,1,"single H1");
   assert.ok(data.photoReady,"broken licensed photo");
   assert.equal(data.photoSrc,"/images/culture-verified/japan-kagawa-udon-pilgrimage.webp");
   assert.ok(data.photoAlt&&data.photoAlt.length>10,"descriptive photo alt missing");
   assert.equal(data.ctaHref,"/things-to-do/takamatsu-cruise-udon-market-return/");
   assert.ok(!data.overflow,"horizontal overflow");
   assert.ok(data.card.width>width*0.7,"Shikoku card remains too narrow");
   assert.ok(Math.abs(data.photo.width/data.photo.height-4/3)<0.05,"4:3 image ratio lost");
   assert.ok(data.cta.height>=48,"CTA too small");
   if(width>800){
    assert.ok(Math.abs(data.figure.y-data.copy.y)<5,"desktop image and copy not aligned");
    const share=data.figure.width/data.card.width;
    assert.ok(share>0.45&&share<0.65,"desktop photo split is not balanced: "+share);
   }else{
    assert.ok(data.copy.y>=data.figure.y+data.figure.height-5,"mobile must stack image above text");
   }
   await page.evaluate(()=>{document.documentElement.style.scrollBehavior="auto";document.body.style.scrollBehavior="auto";window.scrollTo({top:0,left:0,behavior:"instant"});});
   await page.screenshot({path:path.join(out,"food-top-"+width+".png")});
   await card.screenshot({path:path.join(out,"food-card-"+width+".png")});
   results.push({width,...data});
   console.log("PASS Shikoku",width);
   await page.close();
  }
 }finally{await browser.close();}
 fs.writeFileSync("audit-output/v301/browser-report.json",JSON.stringify(results,null,2));
 console.log("V301 PASS: 390/768/1440, 4:3 photo, original CTA and no overflow");
})().catch(err=>{console.error(err);process.exitCode=1});
