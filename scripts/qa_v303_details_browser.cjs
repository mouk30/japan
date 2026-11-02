"use strict";
/* V303: browser-level actual photo, centered page, CTA and 4:3 QA.
 * Existing pages only; do not infer real-time booking, bus, or return availability.
 */
const assert=require("node:assert/strict");
const fs=require("node:fs");const path=require("node:path");
const {chromium}=require("playwright");
const items=[
  ["things-to-do/naha-cruise-terminal-kokusai-dori","port"],
  ["things-to-do/hakata-port-hakata-station-access","port"],
  ["things-to-do/nagasaki-matsugae-glover-garden-cruise-access","port"],
  ["things-to-do/ishigaki-cruise-kabira-bay-bus-taxi","port"],
  ["guide/busan-osaka-ferry","ferry"],
  ["guide/busan-fukuoka-ferry","ferry"],
  ["guide/busan-shimonoseki-ferry","ferry"],
  ["things-to-do/yokohama-red-brick-warehouse","editorial"],
];
const widths=[390,768,1440],out="audit-output/v303";
fs.mkdirSync(out,{recursive:true});
(async()=>{
 const b=await chromium.launch({headless:true,args:["--no-sandbox"]});
 const rows=[];
 try{
 for(const [slug,kind] of items){
 for(const width of widths){
  const p=await b.newPage({viewport:{width,height:900},deviceScaleFactor:1});
  try{
   const url="http://127.0.0.1:8765/"+slug+"/";
   const res=await p.goto(url,{waitUntil:"load",timeout:30000});
   assert.equal(res.status(),200,slug+" missing page");
   await p.locator("body.nf303-"+kind+"-guide").waitFor();
   const selector=kind==="port"?"figure.nf303-hero-photo img.cover":kind==="ferry"?"figure.nf303-ferry-figure img.article-cover":".editorial-hero img";
   const hero=p.locator(selector);
   assert.equal(await hero.count(),1,slug+" original image missing");
   await hero.scrollIntoViewIfNeeded();
   await hero.evaluate(img=>img.decode());
   const data=await p.evaluate(sel=>{
    const box=el=>{if(!el)return null;const r=el.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}};
    const im=document.querySelector(sel),fig=im.closest("figure");
    const h1=document.querySelector("h1");
    const actions=[...document.querySelectorAll(".nf303-actions a")];
    const cards=[...document.querySelectorAll(".nf-q80-card")];
    const style=getComputedStyle(im);
    const head=document.querySelector("article>header,.page-hero>.wrap,main");
    return {
      h1Count:document.querySelectorAll("h1").length,
      imageReady:im.complete&&im.naturalWidth>0,
      imageSrc:im.getAttribute("src"),
      imageRatio:im.getBoundingClientRect().width/im.getBoundingClientRect().height,
      imageFit:style.objectFit,
      im:box(im),figure:box(fig),heading:box(h1),head:box(head),
      actions:actions.map(box),actionText:actions.map(a=>a.textContent.trim()),
      credit:fig.querySelector(".nf303-photo-caption a")?.getAttribute("href"),
      cards:cards.map(box),
      docWidth:document.documentElement.scrollWidth,viewportWidth:innerWidth,
      cssLoaded:[...document.styleSheets].some(ss=>ss.href?.includes("nf-v303-detail-photo-cta.css"))
    };
   },selector);
   assert.equal(data.h1Count,1,slug+" H1");
   assert.ok(data.cssLoaded,slug+" stylesheet missing");
   assert.ok(data.imageReady,slug+" image decode failure");
   assert.equal(data.imageFit,"contain",slug+" must not cut photograph");
   assert.ok(Math.abs(data.imageRatio-4/3)<0.035,slug+" not 4:3: "+data.imageRatio);
   assert.equal(data.credit,"#nf-v148-photo-credits",slug+" photo provenance jump lost");
   assert.equal(data.actions.length,2,slug+" expected two accessible actions");
   for(const a of data.actions)assert.ok(a.w>135&&a.h>=48,slug+" tiny CTA at "+width);
   assert.ok(data.docWidth<=width+3,slug+" horizontal overflow "+width+" vs "+data.docWidth);
   const center=data.heading.x+data.heading.w/2;
   // Page is centered in normal flow, and the headline fits within its viewport.
   assert.ok(data.heading.x>=0 && data.heading.x+data.heading.w<=width+2,slug+" heading overflow");
   if(kind==="port"&&width===1440&&data.cards.length===3){
    const heights=data.cards.map(x=>x.h);
    assert.ok(Math.max(...heights)-Math.min(...heights)<10,slug+" unequal practical cards");
   }
   await p.evaluate(()=>{document.documentElement.style.scrollBehavior="auto";document.body.style.scrollBehavior="auto";window.scrollTo({top:0,left:0,behavior:"instant"})});
   await p.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
   await p.screenshot({path:path.join(out,slug.replaceAll("/","-")+"-"+width+".png")});
   rows.push({slug,kind,width,...data});
   console.log("PASS",slug,width,"photo 4:3 + CTA + no overflow");
  }finally{await p.close()}
 }}
 }finally{await b.close()}
 fs.writeFileSync(path.join(out,"browser-report.json"),JSON.stringify(rows,null,2));
 console.log("V303 PASS",rows.length,"browser viewport checks");
})().catch(err=>{console.error(err);process.exitCode=1});
