import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import {createServer} from "node:http";
import {once} from "node:events";
import {chromium} from "playwright";
const root=path.resolve("site");
const manifest=JSON.parse(fs.readFileSync("audit-reports/v284/three-photo-first-cruise-ports.json","utf8"));
const dir=path.resolve("audit-reports/v284/browser-screens");
fs.mkdirSync(dir,{recursive:true});
const server=createServer((req,res)=>{
 let p;try{p=decodeURIComponent(new URL(req.url,"http://127.0.0.1").pathname)}catch{res.writeHead(400);res.end();return}
 const file=path.resolve(root,"."+(p.endsWith("/")?p+"index.html":p));
 if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return}
 fs.readFile(file,(err,b)=>{
  if(err){res.writeHead(404);res.end();return}
  const types={".html":"text/html; charset=utf-8",".css":"text/css; charset=utf-8",".js":"application/javascript",".webp":"image/webp",".jpg":"image/jpeg",".png":"image/png",".svg":"image/svg+xml"};
  res.writeHead(200,{"Content-Type":types[path.extname(file)]||"application/octet-stream"});res.end(b);
 });
});
server.listen(0,"127.0.0.1");await once(server,"listening");
const browser=await chromium.launch({headless:true});
const results=[];
try{
 for(const width of [320,390,768,1440]){
  for(const conf of manifest.changes){
   const context=await browser.newContext({viewport:{width,height:920}});
   const page=await context.newPage(),errors=[];
   page.on("pageerror",e=>errors.push(String(e)));
   const rel="/"+conf.path.replace(/^site\//,"").replace(/index\.html$/,"");
   const url="http://127.0.0.1:"+server.address().port+rel;
   try{
    const rsp=await page.goto(url,{waitUntil:"load"});assert.equal(rsp.status(),200);
    assert.equal(await page.locator("h1").count(),1);
    assert.ok(await page.locator(".nf-v284-hero").isVisible(),"Hero missing "+rel);
    assert.ok(await page.locator(".nf-v284-gallery").isVisible(),"Photo gallery missing "+rel);
    assert.ok(await page.locator(".nf-v284-warning").isVisible(),"Safety warning invisible "+rel);
    assert.equal(await page.locator("a.nf-v284-card").count(),3);
    const hero=page.locator(".nf-v284-photo-figure img");
    assert.ok(await hero.evaluate(async el=>{try{await el.decode();return el.complete&&el.naturalWidth>0}catch{return false}}),"Hero WebP not decoded "+rel);
    for(const item of conf.cards){
     const card=page.locator('a.nf-v284-card[href="#'+item.id+'"]');
     assert.equal(await card.count(),1);
     const img=card.locator("img");await img.scrollIntoViewIfNeeded();
     assert.ok(await img.evaluate(async el=>{try{await el.decode();return el.naturalWidth>0}catch{return false}}),"Original venue WebP failed "+item.id);
     await card.click();assert.equal(new URL(page.url()).hash,"#"+item.id,"Wrong destination "+item.title);
     const content=page.locator('[id="'+item.id+'"]');assert.equal(await content.count(),1);
     await content.scrollIntoViewIfNeeded();assert.ok(await content.isVisible());
     assert.ok((await content.innerText()).includes(item.title),"Destination is not about the card "+item.title);
     const pos=await content.evaluate(el=>el.getBoundingClientRect().top);
     assert.ok(pos>-100&&pos<1000,"Card details outside viewport "+item.id);
     await page.evaluate(()=>window.scrollTo({top:0,behavior:"instant"}));
    }
    const dims=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));
    assert.ok(dims.scroll<=dims.width+2,"Horizontal overflow "+rel+" "+width+" "+JSON.stringify(dims));
    assert.deepEqual(errors,[],"Uncaught JavaScript error "+rel);
    await page.goto(url,{waitUntil:"load"});
    await page.screenshot({path:path.join(dir,conf.path.split("/").slice(-2,-1)[0]+"-"+width+".png"),fullPage:false});
    results.push({page:conf.path,viewport:width,cards:3,passed:true});
   }finally{await context.close()}
  }
 }
}finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
fs.writeFileSync("audit-reports/v284/browser-qa-results.json",JSON.stringify({stage:"V284",scope:"Local Chromium, not authenticated Vercel preview",screens:results.length,directPhotoClicks:results.length*3,results},null,2)+"\n");
console.log("V284 BROWSER PASS "+results.length+" viewport/page tests and "+(results.length*3)+" direct attraction card clicks; saved 12 actual Chromium screenshots");
