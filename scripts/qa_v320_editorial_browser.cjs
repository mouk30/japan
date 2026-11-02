"use strict";
/* V320 live browser test: 3 visual breakpoints, official links, valid calculator DOM. */
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),{chromium}=require("playwright");
const pages=[
 ["guide/busan-osaka-timetable","timetable"],
 ["guide/busan-tsushima-timetable","timetable"],
 ["guide/busan-fukuoka-timetable","timetable"],
 ["guide/japan-ferry-booking-passport","general"],
 ["guide/japan-ferry-seasickness","general"],
 ["booking/trip-cost-calculator","calculator"],
 ["guide/busan-osaka-ferry-price","timetable"],
 ["guide/busan-tsushima-ferry-price","timetable"],
 ["guide/busan-fukuoka-ferry-price","timetable"],
 ["guide/japan-ferry-fuel-surcharge","general"],
 ["guide/japan-ferry-checkin-time","general"]
];
const widths=[390,768,1440],out="audit-output/v320";fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
 let rows=[];
 try{
 for(const [slug,type] of pages)for(const width of widths){
  const p=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
  try{
   const r=await p.goto("http://127.0.0.1:8765/"+slug+"/",{waitUntil:"load",timeout:25000});
   assert.equal(r.status(),200,slug+" HTTP");
   await p.locator("h1").first().waitFor();
   let area;
   if(type==="timetable"){
    area=p.locator('section.booking#ferry');
    assert.equal(await area.count(),1,slug+" booking area");
    assert.equal(await area.locator('a[href*="willer-travel.com"]').count(),0);
    assert.ok((await area.locator('a').first().getAttribute("href")).startsWith("https://"),slug+" official outbound");
    const whole=await p.locator("main").innerText();
    if(slug.includes("osaka"))assert.ok(whole.includes("27,000원")&&whole.includes("2,700엔"));
    if(slug.includes("tsushima"))assert.ok(whole.includes("16,000원")&&whole.includes("27,000원")&&whole.includes("15:30"));
   }
   if(type==="general"){
    area=p.locator("#nf319-official-booking");
    assert.equal(await area.count(),1);
    assert.equal(await area.locator(".nf319-operator-grid a").count(),4);
    assert.equal(await p.locator('img[src="/images/ferry.jpg"]').count(),0);
    assert.equal(await p.locator(".nf319-visual-truth").count(),1);
   }
   if(type==="calculator"){
    area=p.locator("#calculator");
    await p.locator("#v26-people").fill("3");
    for(const [id,num] of Object.entries({fare:200000,cabin:120000,fees:45000,hotel:300000,transport:60000,food:90000,shopping:15000,extra:10000})){
     await p.locator("#v26-"+id).fill(String(num));
    }
    assert.equal(await p.locator("#v26-total").innerText(),"1,240,000원","wrong total");
    assert.ok((await p.locator("#v26-person").innerText()).includes("413,333원"),"per person wrong");
    assert.equal(await p.locator("#nf318-price-sources a").count(),4);
    assert.ok((await p.locator(".v26-note").innerText()).includes("환율"),"yen-to-KRW advice missing");
   }
   const data=await p.evaluate(()=>({scroll:document.documentElement.scrollWidth,viewport:innerWidth,h1:document.querySelectorAll("h1").length,htmlElements:document.querySelectorAll("html").length,bodies:document.querySelectorAll("body").length}));
   assert.ok(data.scroll<=width+4,slug+" horizontal overflow "+data.scroll+"/"+width);
   assert.equal(data.h1,1);assert.equal(data.htmlElements,1);assert.equal(data.bodies,1);
   await area.scrollIntoViewIfNeeded();
   await area.screenshot({path:path.join(out,slug.replaceAll("/","-")+"-"+width+".png")});
   rows.push({slug,type,width,...data});
   console.log("PASS",slug,width);
  }finally{await p.close()}
 }
 }finally{await browser.close()}
 fs.writeFileSync(path.join(out,"browser-screenshots-manifest.json"),JSON.stringify(rows,null,2));
 console.log("V320 33/33 browser breakpoint checks complete");
})().catch(e=>{console.error(e);process.exitCode=1});
