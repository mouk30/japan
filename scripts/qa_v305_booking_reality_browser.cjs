"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const {chromium}=require("playwright");
const cases=[["","home",".nf247-route-photo"],["booking","booking",".bk-case-photo"],["guide/busan-osaka-ferry","guide",null]];
const widths=[390,768,1440];
const out="audit-output/v305";fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
 const report=[];
 try{
  for(const [slug,kind,sel] of cases)for(const width of widths){
   const page=await browser.newPage({viewport:{width,height:950},deviceScaleFactor:1});
   try{
    const url="http://127.0.0.1:8765/"+(slug?slug+"/":"");
    const r=await page.goto(url,{waitUntil:"load",timeout:30000});
    assert.equal(r.status(),200,slug+" http");
    await page.locator("h1").first().waitFor();
    if(sel){
     assert.equal(await page.locator(sel).count(),4,slug+" route card quantity");
     for(const el of await page.locator(sel+" img").all()){
      await el.scrollIntoViewIfNeeded();
      await el.evaluate(img=>img.decode());
     }
     const a=await page.locator(sel+" img").evaluateAll(imgs=>imgs.map(img=>{
      const css=getComputedStyle(img),r=img.getBoundingClientRect(),parent=img.parentElement.getBoundingClientRect();
      return {src:img.getAttribute("src"),ready:img.complete&&img.naturalWidth>0,fit:css.objectFit,frameRatio:parent.width/parent.height,alt:img.alt};
     }));
     for(const x of a){
      assert.ok(x.ready,slug+" missing photo "+x.src);
      assert.equal(x.fit,"cover",slug+" must fill 4:3 photo card without dark-letterbox");
      assert.ok(Math.abs(x.frameRatio-4/3)<0.035,slug+" not 4:3 image card "+JSON.stringify(x));
      assert.ok(!x.src.includes("panstar-cruise-clean-2048.webp"),slug+" AI still primary");
      assert.ok(x.alt?.length>=20,slug+" photo identity alt too short");
     }
     const credits=await page.locator(".nf305-photo-rights").count();
     if(kind==="home")assert.equal(credits,4,"4 visible source links");
     await page.locator(sel).first().scrollIntoViewIfNeeded();
    }else{
     const t=await page.locator("main").innerText();
     assert.ok(t.includes("27,000원")&&t.includes("2,700엔"),"Nov 2026 fees missing");
     assert.ok(t.includes("11월 1일"),"effective date missing");
    }
    const doc=await page.evaluate(()=>({scrollWidth:document.documentElement.scrollWidth,viewport:innerWidth,h1:document.querySelectorAll("h1").length}));
    assert.equal(doc.h1,1,"unexpected h1 count");
    assert.ok(doc.scrollWidth<=width+4,slug+" horizontal clipping "+doc.scrollWidth+"/"+width);
    await page.evaluate(()=>{document.documentElement.style.scrollBehavior="auto";document.body.style.scrollBehavior="auto"});
    await page.screenshot({path:path.join(out,(slug||"home").replaceAll("/","-")+"-"+width+".png")});
    report.push({slug:slug||"/",width,...doc});
    console.log("PASS",slug||"/",width);
   }finally{await page.close()}
  }
 }finally{await browser.close()}
 fs.writeFileSync(path.join(out,"results.json"),JSON.stringify(report,null,2));
 console.log("V305 PASS 9 responsive snapshots; no letterboxed AI booking cards");
})().catch(e=>{console.error(e);process.exitCode=1});
