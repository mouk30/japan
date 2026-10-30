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
  res.writeHead(200,{'Content-Type':({'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'application/javascript','.jpg':'image/jpeg','.webp':'image/webp','.svg':'image/svg+xml'}[ext]||'application/octet-stream')});res.end(b);
 });
});
server.listen(0,'127.0.0.1');await once(server,'listening');
const browser=await chromium.launch({headless:true});
let checks=0;
try{
 for(const width of [320,390,768,1440])for(const slug of ['kagoshima','okinawa','nagoya','sendai','hiroshima']){
  const context=await browser.newContext({viewport:{width,height:900}}),page=await context.newPage();
  try{
   const res=await page.goto('http://127.0.0.1:'+server.address().port+'/stay/'+slug+'/',{waitUntil:'load'});
   assert.equal(res.status(),200);
   assert.equal(await page.locator('h1').count(),1);
   assert.equal(await page.locator('.nf-v254-verified-photo-credit').count(),1);
   assert.ok((await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth))<=2,'Horizontal overflow at '+slug+' '+width);
   const first=page.locator('img.sv-img');
   assert.equal(await first.count(),1);
   assert.ok(await first.evaluate(el=>el.complete&&el.naturalWidth>0&&el.naturalHeight>0),'Broken real photo '+slug);
   const bg=await page.locator('.sv-hero').evaluate(el=>getComputedStyle(el,'::before').backgroundImage);
   assert.ok(!bg.includes('/stay/assets/tokyo.jpg')&&!bg.includes('/stay/assets/fuji.jpg')&&!bg.includes('/stay/assets/kyoto.jpg'),'Old false-location hero '+slug);
   checks++;
  }finally{await context.close()}
 }
}finally{await browser.close();await new Promise(r=>server.close(r))}
console.log('V254 responsive region-photo QA PASS: '+checks+' pages/viewports');
