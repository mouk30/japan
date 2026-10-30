import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {chromium} from 'playwright';
const root=path.resolve('site');
const server=createServer((req,res)=>{
 let pathname;
 try{pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname)}catch{res.writeHead(400);res.end();return}
 const p=path.resolve(root,'.'+(pathname.endsWith('/')?pathname+'index.html':pathname));
 if(!p.startsWith(root+path.sep)){res.writeHead(403);res.end();return}
 fs.readFile(p,(err,b)=>{if(err){res.writeHead(404);res.end();return}
 const ext=path.extname(p).toLowerCase();
 const ct={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'application/javascript','.jpg':'image/jpeg','.webp':'image/webp','.svg':'image/svg+xml'}[ext]||'application/octet-stream';
 res.writeHead(200,{'Content-Type':ct});res.end(b)});
});
server.listen(0,'127.0.0.1');await once(server,'listening');
const b=await chromium.launch({headless:true});
try{for(const width of [320,390,768,1440]){
 for(const route of ['/stay/','/stay/kagoshima/','/stay/okinawa/','/stay/hokkaido/']){
 const ctx=await b.newContext({viewport:{width,height:900}}),page=await ctx.newPage();
 const res=await page.goto('http://127.0.0.1:'+server.address().port+route,{waitUntil:'domcontentloaded'});
 assert.equal(res.status(),200);
 const disclosure=page.locator('.nf-v253-photo-notice');
 assert.equal(await disclosure.count(),1);
 assert.match(await disclosure.innerText(),/실제 호텔·객실을 촬영했다는 증빙이 없습니다/);
 assert.equal(await page.locator('h1').count(),1);
 assert.ok((await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth))<=2,'Page horizontal scroll '+width+' '+route);
 if(route==='/stay/hokkaido/'){
  const im=page.locator('img[src="/images/v167/noboribetsu-onsen-lawsonstu-cc0-2015.webp"]');
  assert.equal(await im.count(),1);
  await im.scrollIntoViewIfNeeded();
  await page.waitForFunction(()=>{const i=document.querySelector('img[src="/images/v167/noboribetsu-onsen-lawsonstu-cc0-2015.webp"]');return !!i&&i.complete&&i.naturalWidth>=1200;});
  assert.ok((await page.locator('.nf-v253-photo-credit a').count())>=2);
 }
 console.log('V253 browser PASS '+width+'px '+route);
 await ctx.close();
 }
}}finally{await b.close();await new Promise(resolve=>server.close(resolve))}
