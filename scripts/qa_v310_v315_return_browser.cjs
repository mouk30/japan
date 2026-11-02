"use strict";
/* V310-V315 — actual Chromium viewport QA of source-backed return steps. */
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),{chromium}=require("playwright");
const slugs=["fukuoka-busan-ferry","osaka-busan-ferry","shimonoseki-busan-ferry","tsushima-busan-ferry","busan-hitakatsu-ferry","busan-izuhara-ferry"];
const out="audit-output/v315";fs.mkdirSync(out,{recursive:true});
(async()=>{
 let browser=await chromium.launch({headless:true,args:["--no-sandbox"]}),result=[];
 try{
 for(const slug of slugs)for(const width of [390,768,1440]){
  const p=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
  try{
   const x=await p.goto("http://127.0.0.1:8765/guide/"+slug+"/",{waitUntil:"load",timeout:25000});
   assert.equal(x.status(),200,slug+" HTTP");
   let panel=p.locator("#nf310-verified-return");
   await panel.waitFor();
   const data=await p.evaluate(()=>{
    let el=document.querySelector("#nf310-verified-return"),r=el.getBoundingClientRect(),imgs=document.querySelectorAll("#nf310-verified-return img"),anchors=[...el.querySelectorAll("a")],cards=[...el.querySelectorAll(".nf310-return-card")];
    return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,rect:{x:r.x,w:r.width},links:anchors.map(a=>({url:a.getAttribute("href"),text:a.textContent.trim(),h:a.getBoundingClientRect().height})),cards:cards.length,h1:document.querySelectorAll("h1").length,grid:getComputedStyle(el.querySelector(".nf310-return-grid")).gridTemplateColumns,containsFakeBooking:el.textContent.includes("예약이 확정되었습니다"),text:el.textContent.slice(0,1900),images:imgs.length};
   });
   assert.equal(data.h1,1,"H1");
   assert.equal(data.cards,3,slug+" 3 practical cards");
   assert.ok(data.links.length>=5,slug+" missing official links");
   assert.ok(data.links.every(x=>x.url.startsWith("https://") && !x.url.includes("willer-travel")&&x.text.length>=6),slug+" wrong CTA");
   assert.ok(data.scrollWidth<=width+4,slug+" overflow: "+data.scrollWidth);
   assert.ok(data.rect.x>=-3&&data.rect.x+data.rect.w<=width+4,slug+" clipped panel");
   assert.equal(data.images,0,"unnecessary stock photo");
   assert.ok(!data.containsFakeBooking,"fake success");
   const col=data.grid.trim().split(/\s+/).length;
   if(width===390)assert.equal(col,1,"mobile should stack");
   if(width===1440)assert.equal(col,3,"desktop three-column");
   await panel.screenshot({path:path.join(out,slug+"-"+width+".png")});
   result.push({slug,width,links:data.links.length,grid:data.grid,scroll:data.scrollWidth});
   console.log("PASS",slug,width);
  }finally{await p.close()}
 }
 }finally{await browser.close()}
 fs.writeFileSync(path.join(out,"results.json"),JSON.stringify(result,null,2));
 console.log("V310–V315 PASS",result.length,"real-viewport screens");
})().catch(e=>{console.error(e);process.exitCode=1});
