import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {chromium} from 'playwright';
const root=path.resolve('site');
const photos=JSON.parse(fs.readFileSync('data/v256/stay-kobe-yokohama-sapporo-photos.json','utf8')).images;
const server=createServer((req,res)=>{
 let pathname;try{pathname=decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname)}catch{res.writeHead(400);res.end();return}
 const file=path.resolve(root,'.'+(pathname.endsWith('/')?pathname+'index.html':pathname));
 if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return}
 fs.readFile(file,(err,b)=>{if(err){res.writeHead(404);res.end();return}
 res.writeHead(200,{'Content-Type':({'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'application/javascript','.webp':'image/webp','.jpg':'image/jpeg','.svg':'image/svg+xml'}[path.extname(file)]||'application/octet-stream')});res.end(b)
 });
});server.listen(0,'127.0.0.1');await once(server,'listening');
const browser=await chromium.launch({headless:true});let checked=0;
try{
 for(const width of [320,390,768,1440])for(const slug of Object.keys(photos)){
  const context=await browser.newContext({viewport:{width,height:920}});
  const page=await context.newPage();
  try{
   const r=await page.goto('http://127.0.0.1:'+server.address().port+'/stay/'+slug+'/',{waitUntil:'load'});
   assert.equal(r.status(),200);
   assert.equal(await page.locator('h1').count(),1,'Missing primary heading');
   assert.equal(await page.locator('.nf-v256-region-photo-credit').count(),1,'Missing license attribution');
   const img=page.locator('img.sv-img');
   assert.ok(await img.evaluate(el=>el.complete&&el.naturalWidth>0&&el.naturalHeight>0),'Real region photo broken '+slug);
   assert.equal(await page.locator('.sv-v256-photo-placeholder').count(),3,'Unsafe photograph displayed '+slug);
   assert.ok(await page.locator('.sv-v256-photo-placeholder').first().isVisible(),'Placeholder hidden '+slug);
   assert.equal(await page.locator('img[src^="/stay/assets/"]').count(),0,'Unverified JPG shown '+slug);
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth)<=2,'Horizontal overflow '+slug+' '+width);
   checked++;
  }finally{await context.close()}
 }
}finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
console.log('V256 PASS: '+checked+' browser page/viewport combinations including verified source images and safe card placeholders.');
