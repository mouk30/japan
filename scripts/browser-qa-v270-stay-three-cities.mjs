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
 fs.readFile(p,(err,data)=>{if(err){res.writeHead(404);res.end();return}
  const ext=path.extname(p).toLowerCase();
  res.writeHead(200,{'Content-Type':({'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'application/javascript','.jpg':'image/jpeg','.webp':'image/webp','.svg':'image/svg+xml'}[ext]||'application/octet-stream')});res.end(data);
 });
});
server.listen(0,'127.0.0.1');await once(server,'listening');
const browser=await chromium.launch({headless:true});
let checks=0;
try{
 for(const slug of ['kobe','yokohama','hiroshima'])for(const width of [320,390,768,1440]){
  const context=await browser.newContext({viewport:{width,height:900}}),page=await context.newPage();
  try{
   const res=await page.goto('http://127.0.0.1:'+server.address().port+'/stay/'+slug+'/',{waitUntil:'load'});
   assert.equal(res.status(),200,'HTTP '+slug+' '+width);
   assert.equal(await page.locator('h1').count(),1,'H1 '+slug+' '+width);
   assert.equal(await page.locator('.sv-card').count(),3,'cards '+slug+' '+width);
   assert.equal(await page.locator('.sv-photo-hold').count(),slug==='hiroshima'?2:4,'photo holds '+slug+' '+width);
   assert.ok(await page.locator('.sv-photo-hold').first().isVisible(),'hold hidden '+slug+' '+width);
   if(slug==='hiroshima')assert.ok(await page.locator('.nf-v254-verified-photo-credit').isVisible(),'licensed credits missing '+slug+' '+width);
   const hero=await page.locator('.sv-hero').evaluate(el=>getComputedStyle(el,'::before').backgroundImage);
   assert.ok(!hero.includes('/stay/assets/'),'legacy hero '+slug+' '+width);
   assert.ok(slug==='hiroshima'?hero.includes('/images/venues/'):hero.includes('gradient')&&!hero.includes('url('),'hero mismatch '+slug+' '+width);
   const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
   assert.ok(overflow<=2,'horizontal overflow '+slug+' '+width+' '+overflow);
   const broken=await page.locator('img').evaluateAll(nodes=>nodes.filter(el=>!el.complete||el.naturalWidth===0).map(el=>el.src));
   assert.deepEqual(broken,[],'broken image '+slug+' '+width);
   checks++;
  }finally{await context.close()}
 }
}finally{await browser.close();await new Promise(r=>server.close(r))}
console.log('V270 BROWSER PASS: '+checks+' local Chromium page/viewport checks at 320/390/768/1440; not authenticated Vercel Preview');
