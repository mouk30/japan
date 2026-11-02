"use strict";
/* V306: deterministically block Wikimedia to test the fallback at all 3 viewports. */
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const {chromium}=require("playwright");
const out="audit-output/v306";fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]}),results=[];
 try{
  for(const width of [390,768,1440]){
   const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
   try{
    await page.route("https://upload.wikimedia.org/**",route=>route.abort("failed"));
    const response=await page.goto("http://127.0.0.1:8765/food/",{waitUntil:"domcontentloaded",timeout:30000});
    assert.equal(response.status(),200);
    await page.evaluate(()=>document.querySelectorAll(".hub-main .dircard img").forEach(img=>img.loading="eager"));
    await page.waitForFunction(()=>document.querySelectorAll(".hub-main .dircard.nf-v306-photo-failed").length===9,{timeout:15000});
    const data=await page.evaluate(()=>{
     const grid=document.querySelector(".hub-main .dirgrid");
     const cards=[...grid.querySelectorAll(":scope > .dircard")];
     const fallbacks=cards.filter(c=>c.classList.contains("nf-v306-photo-failed"));
     const sizes=fallbacks.map(c=>{const r=c.querySelector(".nf-v306-image-fallback").getBoundingClientRect();return r.width/r.height});
     return {
      cards:cards.length,failed:fallbacks.length,
      originalExternal:cards.filter(c=>c.querySelector('img[src^="https://upload.wikimedia.org/"]')).length,
      fallbackElements:document.querySelectorAll(".nf-v306-image-fallback").length,
      notices:fallbacks.filter(c=>c.querySelector(".v36-food-photo-note")?.textContent.includes("로딩 실패")).length,
      fallbackHidden:fallbacks.every(c=>getComputedStyle(c.querySelector("img")).display==="none"),
      ratios:sizes,
      columns:getComputedStyle(grid).gridTemplateColumns.split(" ").filter(Boolean).length,
      overflow:document.documentElement.scrollWidth>innerWidth+2,
      canonical:document.querySelector('link[rel="canonical"]')?.getAttribute("href"),
      title:document.querySelectorAll("h1").length,
      pilotPhoto:document.querySelector("#nf-v153-pilot-hub figure img")?.getAttribute("src"),
      cssLoaded:[...document.styleSheets].some(s=>s.href?.includes("nf-v305-food.css"))
     };
    });
    assert.equal(data.cards,16);
    assert.equal(data.originalExternal,9);
    assert.equal(data.failed,9);
    assert.equal(data.fallbackElements,9);
    assert.equal(data.notices,9);
    assert.ok(data.fallbackHidden);
    assert.ok(data.ratios.every(r=>Math.abs(r-4/3)<0.04));
    assert.equal(data.columns,width===390?1:width===768?2:3);
    assert.ok(!data.overflow);
    assert.ok(data.cssLoaded);
    assert.equal(data.canonical,"https://www.nipponferry.com/food/");
    assert.equal(data.title,1);
    assert.equal(data.pilotPhoto,"/images/culture-verified/japan-kagawa-udon-pilgrimage.webp");
    await page.locator(".hub-main .dirgrid").screenshot({path:path.join(out,"food-fallback-"+width+".png")});
    results.push({width,...data});
    console.log("V306 PASS",width,"9 failed hotlinks handled, 4:3 retained");
   }finally{await page.close()}
  }
 }finally{await browser.close()}
 fs.writeFileSync(path.join(out,"report.json"),JSON.stringify(results,null,2));
})().catch(e=>{console.error(e);process.exitCode=1});
