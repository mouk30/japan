"use strict";
/* V304: Chromium at 390/768/1440 with Leaflet CDN intentionally unavailable.
 * Test actual guide navigation and layout without claiming operator availability.
 */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const {chromium}=require("playwright");
const widths=[390,768,1440],out="audit-output/v304";
fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
 const rows=[];
 try{
  for(const width of widths){
   const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
   try{
    await page.route("https://unpkg.com/**",route=>route.abort());
    const response=await page.goto("http://127.0.0.1:8765/explore/",{waitUntil:"load",timeout:30000});
    assert.equal(response.status(),200,"explore page not found");
    await page.locator("body.nf304-explore").waitFor();
    assert.equal(await page.locator(".nf304-place").count(),17,"17 direct links missing");
    assert.equal(await page.locator(".nf304-place-main").count(),17,"direct links not accessible");
    assert.match(await page.locator("#nf304-map-status").innerText(),/지도 서비스.*불러오지 못했습니다/);
    assert.equal(await page.locator(".nf304-place-map:disabled").count(),17,"broken map buttons must be disabled");
    assert.equal(await page.locator("body.nf304-map-unavailable").count(),1,"empty map canvas must be hidden");
    assert.equal(await page.locator("h1").count(),1);
    const links=await page.locator(".nf304-place-main").evaluateAll(els=>els.map(a=>a.getAttribute("href")));
    assert.equal(new Set(links).size,17,"duplicate city guide target");
    assert.ok(links.every(x=>x.startsWith("/")&&x.endsWith("/")),"nonlocal map destination");
    await page.locator('.regiontabs button[data-r="규슈"]').click();
    assert.equal(await page.locator(".nf304-place").count(),5,"Kyushu filtering failed");
    assert.equal(await page.locator('.regiontabs button[data-r="규슈"]').getAttribute("aria-pressed"),"true");
    await page.locator('.regiontabs button[data-r="전체"]').click();
    assert.equal(await page.locator(".nf304-place").count(),17,"all cities not restored");
    const data=await page.evaluate(()=>{
      const b=e=>{const r=e.getBoundingClientRect();return {x:r.x,w:r.width,h:r.height}};
      const a=document.querySelector(".nf304-place-main");
      const tab=document.querySelector(".regiontabs button");
      const map=document.querySelector("#exploreMap");
      const css=[...document.styleSheets].some(s=>s.href?.includes("nf-v304-explore-map.css"));
      return {viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,
       firstLink:b(a),tab:b(tab),map:b(map),css};
    });
    assert.ok(data.css,"new scoped stylesheet missing");
    assert.ok(data.scrollWidth<=width+3,"horizontal overflow "+width+" vs "+data.scrollWidth);
    assert.ok(data.firstLink.w>=140&&data.firstLink.h>=44,"guide link touch target too small");
    assert.ok(data.tab.h>=40,"region tab touch target too small");
    assert.equal(data.map.h,0,"offline blank map must not occupy screen");
    const top=await page.evaluate(()=>{document.documentElement.style.scrollBehavior="auto";document.body.style.scrollBehavior="auto";window.scrollTo({top:0,left:0,behavior:"instant"});return window.scrollY});
    assert.ok(top<2,"screenshot failed to return to page top: "+top);
    await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    await page.screenshot({path:path.join(out,"explore-"+width+".png")});
    rows.push({width,links:links.length,kyushu:5,leafletFallback:true,...data});
    console.log("PASS",width,"17 links, 5 Kyushu, offline map fallback, no overflow");
   }finally{await page.close()}
  }
 }finally{await browser.close()}
 fs.writeFileSync(path.join(out,"browser-report.json"),JSON.stringify(rows,null,2));
 console.log("V304 PASS: 3 responsive browser checks");
})().catch(e=>{console.error(e);process.exitCode=1});
