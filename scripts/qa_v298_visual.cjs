#!/usr/bin/env node
/* V298: Local Chromium desktop/mobile checks for the exact approved ship image. */
"use strict";
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const {chromium}=require("playwright");
const items=[
 "japan-cruise","booking","booking/japan-cruise","booking/osaka",
 "booking/fukuoka","booking/shimonoseki","booking/tsushima"
];
const widths=[390,768,1440];
const out="audit-output/v298/screenshots";
fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
 const results=[];
 try{
  for(const slug of items){
   for(const width of widths){
    const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
    const response=await page.goto("http://127.0.0.1:8765/"+slug+"/",{waitUntil:"domcontentloaded",timeout:30000});
    // Third-party widgets and fonts may never finish the load event. Validate the actual local hero image instead.
    await page.waitForFunction(()=>{const img=document.querySelector(".jc-hero .nf298-banner-img,.bk-hero .nf298-banner-img");return !!img&&img.complete&&img.naturalWidth>200&&img.naturalHeight>100;},undefined,{timeout:20000});
    assert.equal(response.status(),200,slug+" HTTP status");
    const data=await page.evaluate(()=>{
     const hero=document.querySelector(".jc-hero,.bk-hero");
     const img=hero?.querySelector(".nf298-banner-img");
     const title=hero?.querySelector("h1");
     const content=hero?.querySelector(".jc-w,.bk-hi");
     const caption=hero?.querySelector(".nf298-caption");
     if(!hero||!img||!title||!content||!caption)return {missing:true};
     const a=img.getBoundingClientRect(),b=content.getBoundingClientRect();
     const t=title.getBoundingClientRect(),f=hero.getBoundingClientRect();
     return {missing:false,src:img.getAttribute("src"),naturalWidth:img.naturalWidth,
      naturalHeight:img.naturalHeight,htmlWidth:Number(img.getAttribute('width')),htmlHeight:Number(img.getAttribute('height')),photoWidth:a.width,photoHeight:a.height,
      separate:a.bottom<=b.top+2,objectFit:getComputedStyle(img).objectFit,
      imageInsideViewport:a.left>=-2&&a.right<=innerWidth+2,
      titleInsideViewport:t.left>=-2&&t.right<=innerWidth+2,
      horizontalScroll:document.documentElement.scrollWidth>innerWidth+3,
      captionCount:caption.textContent.trim().length,h1:document.querySelectorAll("h1").length};
    });
    assert(!data.missing,slug+": missing image, caption, heading or content");
    assert(data.naturalWidth>200&&data.naturalHeight>100,slug+": image not loaded");
    assert(data.htmlWidth===data.naturalWidth&&data.htmlHeight===data.naturalHeight,slug+": intrinsic size attributes mismatch");
    assert(data.separate,slug+": photo overlaps booking title/CTA");
    assert.equal(data.objectFit,"contain",slug+": photograph must never crop");
    assert(data.imageInsideViewport&&data.titleInsideViewport,slug+": image/title out of viewport");
    assert(!data.horizontalScroll,slug+": horizontal page overflow");
    assert.equal(data.h1,1,slug+": H1 count");
    assert(data.captionCount>8,slug+": caption missing");
    if(data.src.endsWith("panstar-cruise-clean-2048.webp")){
     assert.equal(data.naturalWidth,2048,slug+": wrong approved image width");
     assert.equal(data.naturalHeight,682,slug+": wrong approved image height");
    }
    const name=slug.replaceAll("/","-")+"-"+width+".png";
    await page.screenshot({path:path.join(out,name),fullPage:false});
    results.push({page:slug,width,...data,pass:true});
    console.log("PASS",slug,width,"image",data.naturalWidth+"x"+data.naturalHeight);
    await page.close();
   }
  }
  fs.mkdirSync("audit-output/v298",{recursive:true});
  fs.writeFileSync("audit-output/v298/visual-qa.json",JSON.stringify(results,null,2));
  console.log("V298 VISUAL PASS",results.length,"viewport checks; full image and readable separate booking content");
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
