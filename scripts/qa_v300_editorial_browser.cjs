/* V300 Chromium screenshot + alignment gate for existing editorial pages. */
"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const {chromium}=require("playwright");
const pages=["","booking","booking/osaka","booking/fukuoka","booking/shimonoseki",
"booking/tsushima","booking/japan-cruise","japan-cruise","things-to-do/travel-companions"];
const widths=[390,768,1440],out="audit-output/v300/screenshots";
fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
 const report=[];
 try{
  for(const slug of pages)for(const width of widths){
   const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
   const res=await page.goto("http://127.0.0.1:8765/"+(slug?slug+"/":""),{waitUntil:"load"});
   assert.equal(res.status(),200,slug+" HTML missing");
   await page.locator("body.nf300-editorial").waitFor();
   // Trigger and verify the first six real lazy-loaded card images, not just the first.
   // Without this, a screenshot can show gray placeholders despite a passing gate.
   const thumbs=page.locator(".bk-case-card img,.nf247-route-photo img,.companion-main .guide-photo img,.jc-card .nf251-card-photo img");
   const checkedThumbs=Math.min(await thumbs.count(),6);
   for(let i=0;i<checkedThumbs;i++){
    const img=thumbs.nth(i);
    await img.scrollIntoViewIfNeeded();
    await img.evaluate(el=>el.decode());
   }
   const data=await page.evaluate(()=>{
    const box=e=>{const b=e?.getBoundingClientRect();return b?{x:b.x,y:b.y,width:b.width,height:b.height}:null};
    const hero=document.querySelector(".bk-hero>.bk-hi,.jc-hero>.jc-w");
    const first=document.querySelector(".bk-case-card img,.nf247-route-photo img,.companion-main .guide-photo img,.jc-card .nf251-card-photo img");
    const banner=document.querySelector(".nf298-banner-img");
    const styles=banner?getComputedStyle(banner):null;
    const cards=document.querySelectorAll(".bk-case-card").length;
    const routes=document.querySelectorAll(".nf247-route-photo").length;
    return {h1:document.querySelectorAll("h1").length,hero:box(hero),first:box(first),firstReady:!first||(first.complete&&first.naturalWidth>0),bannerReady:!banner||(banner.complete&&banner.naturalWidth>0),
      bannerFit:styles?.objectFit||"",cards,routes,viewport:innerWidth,
      bodyScrollWidth:document.documentElement.scrollWidth};
   });
   assert.equal(data.h1,1,slug+" h1");
   assert.ok(data.bannerReady,slug+" missing/corrupt hero image");
   assert.ok(data.firstReady,slug+" missing/corrupt thumbnail");
   if(data.hero){
    assert.ok(data.hero.width>0&&data.hero.width<=Math.min(1200,width+1),slug+" oversize text");
    const left=data.hero.x,right=width-data.hero.x-data.hero.width;
    assert.ok(Math.abs(left-right)<45,slug+" hero off-center at "+width+": "+left+"/"+right);
   }
   if(slug==="booking")assert.equal(data.cards,4,"all 4 ports");
   if(slug==="")assert.equal(data.routes,4,"4 real/AI contextual route thumbnails");
   if(slug==="things-to-do/travel-companions")assert.ok(data.first&&data.first.width>170,"guide images too small");
   assert.equal(data.bannerFit||"contain","contain",slug+" whole ship cropped");
   // Disable smooth scrolling for the QA capture; otherwise scrollTo(0,0)
   // can still be animating and screenshots misleadingly start halfway down.
   const scrollY=await page.evaluate(()=>{
    document.documentElement.style.scrollBehavior="auto";
    document.body.style.scrollBehavior="auto";
    window.scrollTo({top:0,left:0,behavior:"instant"});
    return window.scrollY;
   });
   assert.ok(scrollY<2,slug+" screenshot did not return to page top: "+scrollY);
   await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
   await page.screenshot({path:path.join(out,(slug||"home").replaceAll("/","-")+"-"+width+".png")});
   report.push({page:slug||"/",width,checkedThumbs,...data});
   await page.close();
   console.log("PASS",slug||"/",width);
  }
 }finally{await browser.close();}
 fs.mkdirSync("audit-output/v300",{recursive:true});
 fs.writeFileSync("audit-output/v300/browser-report.json",JSON.stringify(report,null,2));
 console.log("V300 PASS: "+report.length+" viewport cases");
})().catch(err=>{console.error(err);process.exitCode=1});
