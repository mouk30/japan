import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {chromium} from 'playwright';
const root=path.resolve('site'), photos=JSON.parse(fs.readFileSync('data/v257/stay-osaka-kyoto-tokyo-photo-rights.json','utf8')).cityPhotos;
const server=createServer((req,res)=>{
 let pathname;try{pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname)}catch{res.writeHead(400);res.end();return}
 const p=path.resolve(root,'.'+(pathname.endsWith('/')?pathname+'index.html':pathname));
 if(!p.startsWith(root+path.sep)){res.writeHead(403);res.end();return}
 fs.readFile(p,(err,b)=>{if(err){res.writeHead(404);res.end();return}
 res.writeHead(200,{'Content-Type':({'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'application/javascript','.webp':'image/webp','.jpg':'image/jpeg','.svg':'image/svg+xml'}[path.extname(p)]||'application/octet-stream')});res.end(b)
 });
});server.listen(0,'127.0.0.1');await once(server,'listening');
const browser=await chromium.launch({headless:true});let tested=0;
try{for(const width of [320,390,768,1440])for(const [slug,c] of Object.entries(photos)){
 const context=await browser.newContext({viewport:{width,height:900}});
 const page=await context.newPage();
 try{
  const response=await page.goto('http://127.0.0.1:'+server.address().port+'/stay/'+slug+'/',{waitUntil:'load'});
  assert.equal(response.status(),200);
  assert.equal(await page.locator('h1').count(),1);
  assert.equal(await page.locator('.nf-v257-photo-provenance').count(),1);
  assert.equal(await page.locator('.sv-v257-photo-hold').count(),slug==='tokyo'?0:2);
  assert.equal(await page.locator('img[src^="/stay/assets/"]').count(),0);
  for(const key of Object.values(c.images)){
   const photo=page.locator('img[src="'+key.src+'"]').first();
   assert.ok(await photo.count(),'Photo missing '+slug+' '+key.src);
   assert.ok(await photo.evaluate(el=>el.complete&&el.naturalWidth>0&&el.naturalHeight>0),'Photo broken '+slug+' '+key.src);
  }
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth)<=2,'Overflow '+slug+' at '+width);
  tested++;
 }finally{await context.close()}
}}finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
console.log('V257 PASS '+tested+' 3-city × 4-device browser screens; image decoding, source credit and safe cards.');
