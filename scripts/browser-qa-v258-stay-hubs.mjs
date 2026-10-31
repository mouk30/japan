import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {chromium} from 'playwright';
const root=path.resolve('site');
const map=JSON.parse(fs.readFileSync('data/v258/stay-hub-photo-rights.json','utf8')).cardMapping;
const server=createServer((req,res)=>{
 let pathname;try{pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname)}catch{res.writeHead(400);res.end();return}
 const f=path.resolve(root,'.'+(pathname.endsWith('/')?pathname+'index.html':pathname));
 if(!f.startsWith(root+path.sep)){res.writeHead(403);res.end();return}
 fs.readFile(f,(err,b)=>{if(err){res.writeHead(404);res.end();return}
 res.writeHead(200,{'Content-Type':({'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'application/javascript','.webp':'image/webp','.jpg':'image/jpeg','.svg':'image/svg+xml'}[path.extname(f)]||'application/octet-stream')});res.end(b);
 });
});
server.listen(0,'127.0.0.1');await once(server,'listening');
const browser=await chromium.launch({headless:true});let count=0,photos=0;
try{for(const width of [320,390,768,1440])for(const slug of ['','area']){
 const context=await browser.newContext({viewport:{width,height:900}}),page=await context.newPage();
 try{
  const r=await page.goto('http://127.0.0.1:'+server.address().port+'/stay/'+(slug?slug+'/':''),{waitUntil:'load'});
  assert.equal(r.status(),200);
  assert.equal(await page.locator('h1').count(),1);
  assert.equal(await page.locator('.sv-v258-credits').count(),1);
  assert.equal(await page.locator('img[src^="/stay/assets/"]').count(),0);
  const cards=page.locator('a.sv-card');
  assert.equal(await cards.count(),Object.keys(map[slug]).length);
  const actualPhoto=page.locator('a.sv-card img');
  assert.equal(await actualPhoto.count(),Object.values(map[slug]).filter(Boolean).length);
  for(const index of Array.from({length:await actualPhoto.count()},(_,i)=>i)){
   const img=actualPhoto.nth(index);
   assert.ok(await img.evaluate(el=>el.complete&&el.naturalWidth>0&&el.naturalHeight>0),'Broken copyright-verified photo '+slug+' '+width+' #'+index);
   photos++;
  }
  const hold=page.locator('.sv-v258-safe-visual:not(.large)');
  assert.equal(await hold.count(),Object.values(map[slug]).filter(v=>!v).length);
  assert.ok(await hold.first().isVisible(),'Withheld photo info not visible '+slug+' '+width);
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth)<=2,'Page overflow '+slug+' '+width);
  count++;
 }finally{await context.close()}
}}finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
console.log('V258 PASS '+count+' browser screens with '+photos+' total decoded/visible photo references at 320,390,768,1440.');
