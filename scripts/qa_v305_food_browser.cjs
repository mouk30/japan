"use strict";
/* V305: visual layout assertions at 390 / 768 / 1440, no external image success assumed. */
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const {chromium}=require("playwright");
const out="audit-output/v305";
fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]}),rows=[];
 try{
  for(const width of [390,768,1440]){
   const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
   try{
    const response=await page.goto("http://127.0.0.1:8765/food/",{waitUntil:"domcontentloaded",timeout:30000});
    assert.equal(response.status(),200,"food hub missing");
    assert.equal(await page.locator("h1").count(),1);
    assert.equal(await page.locator(".hub-main .dirgrid > a.dircard").count(),16);
    assert.equal(await page.locator('#nf-v153-pilot-hub .nf-v153-pilot-card').count(),1);
    const shikoku=page.locator('#nf-v153-pilot-hub figure img');
    await shikoku.scrollIntoViewIfNeeded();
    await shikoku.evaluate(el=>el.decode());
    const data=await page.evaluate(()=>{
     const rect=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}};
     const grid=document.querySelector(".hub-main .dirgrid");
     const cards=[...grid.querySelectorAll(":scope > a.dircard")];
     const img=cards[2].querySelector("img");
     const hero=document.querySelector(".page-hero h1");
     const feature=document.querySelector("#nf-v153-pilot-hub .nf-v153-pilot-card");
     const photo=feature.querySelector("figure img");
     const copy=feature.querySelector(".nf-v153-pilot-copy");
     const cta=feature.querySelector("a.nf-v153-pilot-cta");
     return {overflow:document.documentElement.scrollWidth>innerWidth+2,
      columns:getComputedStyle(grid).gridTemplateColumns.split(" ").filter(Boolean).length,
      css:[...document.styleSheets].some(s=>s.href?.includes("nf-v305-food.css")),
      hero:rect(hero),card:rect(cards[2]),cardPhoto:rect(img),feature:rect(feature),
      photo:rect(photo),copy:rect(copy),cta:rect(cta),
      featurePhotoReady:photo.complete&&photo.naturalWidth>0,
      featurePhotoSrc:photo.getAttribute("src"),featureLink:cta.getAttribute("href"),
      photoNotes:cards.filter(c=>c.querySelector(".v36-food-photo-note")).length};
    });
    assert.ok(data.css,"scoped CSS not loaded");
    assert.ok(!data.overflow,"horizontal overflow at "+width);
    assert.equal(data.columns,width===390?1:width===768?2:3,"food card columns incorrect");
    assert.equal(data.photoNotes,16,"original image disclosure labels missing");
    assert.ok(data.featurePhotoReady,"verified Shikoku image not decoded");
    assert.equal(data.featurePhotoSrc,"/images/culture-verified/japan-kagawa-udon-pilgrimage.webp");
    assert.equal(data.featureLink,"/things-to-do/takamatsu-cruise-udon-market-return/");
    assert.ok(Math.abs(data.cardPhoto.w/data.cardPhoto.h-4/3)<0.04,"food thumbnail not 4:3");
    assert.ok(Math.abs(data.photo.w/data.photo.h-4/3)<0.04,"Shikoku photo not 4:3");
    assert.ok(data.cta.h>=48,"CTA too small");
    if(width===1440){
     assert.ok(Math.abs(data.photo.y-data.copy.y)<5,"desktop feature not side-by-side");
     assert.ok(data.photo.w>data.feature.w*.45,"feature photo still too narrow");
    }else assert.ok(data.copy.y>=data.photo.y+data.photo.h-5,"mobile feature not stacked");
    await page.evaluate(()=>{document.documentElement.style.scrollBehavior="auto";window.scrollTo(0,0)});
    await page.screenshot({path:path.join(out,"food-top-"+width+".png")});
    await page.locator(".hub-main .dirgrid").screenshot({path:path.join(out,"food-grid-"+width+".png")});
    rows.push({width,...data});
    console.log("V305 PASS",width,"columns",data.columns);
   }finally{await page.close()}
  }
 }finally{await browser.close()}
 fs.writeFileSync(path.join(out,"browser-report.json"),JSON.stringify(rows,null,2));
 console.log("V305 responsive QA passed");
})().catch(e=>{console.error(e);process.exitCode=1});
