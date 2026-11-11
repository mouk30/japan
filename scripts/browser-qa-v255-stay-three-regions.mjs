import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {chromium} from 'playwright';
const root=path.resolve('site');
const registry=JSON.parse(fs.readFileSync('data/v255/stay-three-regions-photo-origin.json','utf8')).photos;
const server=createServer((req,res)=>{
 let pathname; try{pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname)}catch{res.writeHead(400);res.end();return}
 const p=path.resolve(root,'.'+(pathname.endsWith('/')?pathname+'index.html':pathname));
 if(!p.startsWith(root+path.sep)){res.writeHead(403);res.end();return}
 fs.readFile(p,(err,b)=>{if(err){res.writeHead(404);res.end();return}
  res.writeHead(200,{'Content-Type':({'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'application/javascript','.webp':'image/webp','.jpg':'image/jpeg','.svg':'image/svg+xml'}[path.extname(p)]||'application/octet-stream')});res.end(b)
 });
});server.listen(0,'127.0.0.1');await once(server,'listening');
const browser=await chromium.launch({headless:true});let checked=0;
try{for(const width of [320,390,768,1440])for(const slug of Object.keys(registry)){
 const context=await browser.newContext({viewport:{width,height:900}}),page=await context.newPage();
 try{
  const response=await page.goto('http://127.0.0.1:'+server.address().port+'/stay/'+slug+'/',{waitUntil:'load'});
  assert.equal(response.status(),200);
  assert.equal(await page.locator('h1').count(),1);
  assert.equal(await page.locator('.nf-v255-real-location-credit').count(),1);
  const img=page.locator('img.sv-img');
  assert.ok(await img.evaluate(el=>el.complete&&el.naturalWidth>0&&el.naturalHeight>0),'Local photo broken '+slug);
  assert.equal(await page.locator('img[src^="/stay/assets/"]').count(),0,'Legacy image remains '+slug);
  assert.equal(await page.locator('.sv-v255-unverified-photo').count(),slug==='nagasaki'?3:2);
  assert.ok(await page.locator('.sv-v255-unverified-photo').first().isVisible(),'Hold display hidden '+slug);
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth)<=2,'Horizontal overflow '+slug+' '+width);
  checked++;
 }finally{await context.close()}
}}finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
console.log('V255 PASS '+checked+' real-browser responsive route checks at four widths.');
