/* V302: browser check for four real-place ferry operator cards and official links. */
"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const {chromium}=require("playwright");
const out="audit-output/v302/browser";fs.mkdirSync(out,{recursive:true});
const expected=[
 ["/images/venues/nf-v85-osaka-dotonbori-licensed.webp","https://www.panstarcruise.com/"],
 ["/images/venues/fukuoka-ohori-park.webp","https://www.koreaferry.co.kr/rs/idv/reservation/calendar_index/1/2?country=2"],
 ["/images/venues/v62-karato-market-real.webp","https://www.kampuferry.co.jp/reserve/"],
 ["/images/venues/v62-izuhara-port-real.webp","https://www.panstarcruise.com/"]
];
(async()=>{
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});const results=[];
 try{
  for(const width of [390,768,1440]){
   const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
   const response=await page.goto("http://127.0.0.1:8765/ferry/",{waitUntil:"load"});
   assert.equal(response.status(),200,"ferry hub missing");
   const cards=page.locator("#nf91-direct-operators .nf91-direct-item");
   assert.equal(await cards.count(),4,"four operator cards");
   for(let i=0;i<4;i++){
    const img=cards.nth(i).locator("figure img");
    await img.scrollIntoViewIfNeeded();await img.evaluate(el=>el.decode());
   }
   const data=await page.evaluate(()=>{
    const box=e=>{const r=e?.getBoundingClientRect();return r?{x:r.x,y:r.y,width:r.width,height:r.height}:null};
    const cards=[...document.querySelectorAll("#nf91-direct-operators .nf91-direct-item")];
    return {h1:document.querySelectorAll("h1").length,overflow:document.documentElement.scrollWidth>innerWidth+1,
     cards:cards.map(c=>{const img=c.querySelector("figure img"),link=c.querySelector("a.nf91-direct-primary");return {
      card:box(c),photo:box(img),photoReady:!!img&&img.complete&&img.naturalWidth>0,
      photoSrc:img?.getAttribute("src"),photoAlt:img?.getAttribute("alt"),primary:link?.getAttribute("href"),cta:box(link)
     }})};
   });
   assert.equal(data.h1,1,"H1 changed");
   assert.ok(!data.overflow,"horizontal overflow");
   for(let i=0;i<4;i++){
    const c=data.cards[i];
    assert.ok(c.photoReady,"broken real place photo "+i);
    assert.equal(c.photoSrc,expected[i][0]);
    assert.equal(c.primary,expected[i][1]);
    assert.ok(c.photoAlt&&c.photoAlt.length>15,"missing place/ship disclaimer "+i);
    assert.ok(Math.abs(c.photo.width/c.photo.height-4/3)<0.06,"non 4:3 photo "+i);
    assert.ok(c.cta.height>=48,"too small booking CTA "+i);
   }
   if(width===390){
    for(let i=1;i<4;i++)assert.ok(data.cards[i].card.y>data.cards[i-1].card.y+20,"mobile cards must stack");
   }
   if(width===1440){
    assert.ok(data.cards[0].card.width>200,"desktop cards too narrow");
    assert.ok(Math.abs(data.cards[0].card.y-data.cards[3].card.y)<5,"desktop four-card row not aligned");
   }
   await page.evaluate(()=>{document.documentElement.style.scrollBehavior="auto";document.body.style.scrollBehavior="auto";window.scrollTo({top:0,left:0,behavior:"instant"});});
   await page.screenshot({path:path.join(out,"ferry-top-"+width+".png")});
   await page.locator("#nf91-direct-operators").screenshot({path:path.join(out,"ferry-cards-"+width+".png")});
   results.push({width,...data});console.log("PASS ferry cards",width);await page.close();
  }
 }finally{await browser.close();}
 fs.writeFileSync("audit-output/v302/browser-report.json",JSON.stringify(results,null,2));
 console.log("V302 PASS: 390/768/1440, four real-place photos and official booking CTAs");
})().catch(e=>{console.error(e);process.exitCode=1});
