/* V309 traveler-first responsive 390 / 768 / 1440 Playwright QA.
   No fake booking/real-time labels; verify visible operator CTAs and safe return.
*/
"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path"),{chromium}=require("playwright");
const slugs=["booking","booking/osaka","booking/fukuoka","booking/shimonoseki","booking/tsushima","guide/busan-tsushima-ferry"];
const out="audit-output/v309";fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
 const record=[];
 try{
  for(const slug of slugs)for(const width of [390,768,1440]){
   const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
   try{
    const res=await page.goto("http://127.0.0.1:8765/"+slug+"/",{waitUntil:"load"});
    assert.equal(res.status(),200,slug+" served");
    const isGuide=slug.startsWith("guide/");
    let panel=page.locator(isGuide?".nf309-tsushima-review":slug==="booking"?"#nf309-before-return":"#nf309-booking-return");
    assert.equal(await panel.count(),1,slug+" factual area missing");
    await panel.scrollIntoViewIfNeeded();
    const data=await page.evaluate(([slug,isGuide])=>{
      const el=document.querySelector(isGuide?".nf309-tsushima-review":slug==="booking"?"#nf309-before-return":"#nf309-booking-return");
      const rect=el.getBoundingClientRect();
      const anchors=[...el.querySelectorAll("a")];
      const cards=[...el.querySelectorAll(slug==="booking"?".nf309-route":".nf309-journey__step")];
      const css=getComputedStyle(el);
      const links=anchors.map(a=>({href:a.getAttribute("href"),text:a.textContent.trim(),h:a.getBoundingClientRect().height}));
      const columns=slug==="booking"?getComputedStyle(el.querySelector(".nf309-compare")).gridTemplateColumns:!isGuide?getComputedStyle(el.querySelector(".nf309-journey__grid")).gridTemplateColumns:"";
      return {h1:document.querySelectorAll("h1").length,width:innerWidth,scroll:document.documentElement.scrollWidth,rect:{x:rect.x,w:rect.width},links,cardCount:cards.length,columns,body:el.textContent.trim().slice(0,2500)};
    },[slug,isGuide]);
    assert.equal(data.h1,1,slug+" main heading");
    assert.ok(data.scroll<=width+4,slug+" horizontal overflow "+data.scroll+"/"+width);
    assert.ok(data.rect.x>=-3&&data.rect.x+data.rect.w<=width+4,slug+" off-canvas factual panel");
    assert.ok(data.links.every(a=>a.text.length>=6&&a.href),slug+" broken text link");
    if(!isGuide){
      assert.equal(data.cardCount,slug==="booking"?4:3,slug+" number of steps");
      assert.ok(data.body.includes("실시간") || data.body.includes("좌석"),slug+" live-seat disclosure");
      if(slug!=="booking")assert.ok(data.body.includes("마지막")||data.body.includes("수속"),slug+" missing safe-return note");
      if(width===1440)assert.ok(data.columns.trim().split(/\s+/).length>=2,slug+" grid should be multi-column desktop");
      if(width===390)assert.equal(data.columns.trim().split(/\s+/).length,1,slug+" stacked cards on mobile");
    }else{
      assert.ok(data.body.includes("11월 15일")&&data.body.includes("15:30"),"Izuhara change missing");
      assert.ok(data.body.includes("90분")&&data.body.includes("30분"),"real check-in window absent");
    }
    await panel.screenshot({path:path.join(out,slug.replaceAll("/","-")+"-"+width+".png")});
    record.push({slug,width,links:data.links.length,cardCount:data.cardCount,columns:data.columns,scrollWidth:data.scroll});
    console.log("PASS",slug,width);
   }finally{await page.close()}
  }
 }finally{await browser.close()}
 fs.writeFileSync(path.join(out,"results.json"),JSON.stringify(record,null,2));
 console.log("V309 PASS "+record.length+" (6 existing pages x 3 viewport widths)");
})().catch(e=>{console.error(e);process.exitCode=1});
