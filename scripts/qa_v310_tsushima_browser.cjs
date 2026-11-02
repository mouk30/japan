"use strict";
// V310: real page screenshots and usable operator links, no phantom ticket booking.
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const {chromium}=require("playwright");
const slugs=["busan-tsushima-ferry-price"];
const widths=[390,768,1440],out="audit-output/v310";fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
 const report=[];
 try{
  for(const slug of slugs)for(const width of widths){
   const pg=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
   try{
    const res=await pg.goto("http://127.0.0.1:8765/guide/"+slug+"/",{waitUntil:"load",timeout:30000});
    assert.equal(res.status(),200,slug+" HTTP");
    const panel=pg.locator("#nf310-travel-check");await panel.waitFor();
    assert.equal(await panel.count(),1,"one panel");
    await panel.scrollIntoViewIfNeeded();
    const data=await pg.evaluate(()=>{
      const p=document.querySelector("#nf310-travel-check"),rect=p.getBoundingClientRect();
      const cards=[...p.querySelectorAll(".nf310-step")],ctas=[...p.querySelectorAll(".nf310-links a")];
      const columns=getComputedStyle(p.querySelector(".nf310-steps")).gridTemplateColumns.split(/\s+/).filter(Boolean).length;
      const cover=document.querySelector("img.article-cover");
      return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,h1:document.querySelectorAll("h1").length,
       rect:{x:rect.x,y:rect.y,w:rect.width,h:rect.height},
       steps:cards.length,columns,buttons:ctas.map(a=>({href:a.href,h:a.getBoundingClientRect().height,w:a.getBoundingClientRect().width,txt:a.textContent.trim()})),
       firstImg:cover?{src:cover.getAttribute("src"),alt:cover.alt}:null,
       sourceOk:[...ctas].every(a=>a.href.startsWith("https://www.panstarcruise.com/")),
       disclosure:p.textContent.includes("실시간")&&p.textContent.includes("예약증")};
    });
    assert.equal(data.h1,1,slug+" h1");
    assert.ok(data.scrollWidth<=width+4,slug+" horizontal overflow "+data.scrollWidth+"/"+width);
    assert.ok(data.rect.x>=-4&&data.rect.x+data.rect.w<=width+4,slug+" panel outside viewport");
    assert.equal(data.steps,3,slug+" decision cards");
    assert.equal(data.buttons.length,2,"two distinct official operator CTAs");
    assert.ok(data.sourceOk&&data.disclosure,"operator truthful routes/disclosure");
    for(const a of data.buttons)assert.ok(a.h>=48&&a.w>=140,slug+" small CTA");
    if(width===390)assert.equal(data.columns,1,slug+" mobile not stacked");
    if(width===1440)assert.equal(data.columns,3,slug+" desktop not 3 columns");
    await panel.screenshot({path:path.join(out,slug+"-"+width+".png")});
    report.push({slug,width,columns:data.columns,steps:data.steps,buttons:data.buttons.length});
    console.log("PASS",slug,width,"official CTAs & card grid");
   }finally{await pg.close();}
  }
 }finally{await browser.close();}
 fs.writeFileSync(path.join(out,"results.json"),JSON.stringify(report,null,2));
 console.log("V310 PASS",report.length,"viewports for unchanged-layout price guide");
})().catch(e=>{console.error(e);process.exitCode=1});
