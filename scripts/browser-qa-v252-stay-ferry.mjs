import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {once} from 'node:events';
import {chromium} from 'playwright';

const root=path.resolve('site');
const contentTypes={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.svg':'image/svg+xml','.webp':'image/webp','.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png'};
const server=http.createServer((req,res)=>{
 let pathname;
 try{pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname)}catch{res.writeHead(400);res.end();return}
 const p=path.resolve(root,'.'+(pathname.endsWith('/')?pathname+'index.html':pathname));
 if(!p.startsWith(root+path.sep)){res.writeHead(403);res.end();return}
 fs.readFile(p,(err,b)=>{
  if(err){res.writeHead(404);res.end();return}
  res.writeHead(200,{'Content-Type':contentTypes[path.extname(p)]||'application/octet-stream'});res.end(b);
 });
});
server.listen(0,'127.0.0.1');await once(server,'listening');
const browser=await chromium.launch({headless:true});
try{
 for(const width of [390,768,1440]){
  for(const url of ['/stay/','/stay/family/','/stay/ryokan/']){
   const ctx=await browser.newContext({viewport:{width,height:900}});
   const page=await ctx.newPage();
   const response=await page.goto('http://127.0.0.1:'+server.address().port+url,{waitUntil:'domcontentloaded'});
   assert.equal(response.status(),200);
   const cta=page.locator('section.stay-convert');
   assert.equal(await cta.count(),1,'missing CTA '+url);
   const notice=cta.locator('.stay-ferry-note');
   assert.equal(await notice.count(),1,'missing note '+url);
   assert.match(await notice.innerText(),/숙소·객실 예약이 아닌 일본 국내 페리 항로 조회/);
   const link=cta.getByRole('link',{name:/WILLER TRAVEL에서 일본 국내 페리 항로와 요금 조회/});
   assert.equal(await link.count(),1,'accessible target '+url);
   assert.equal(await link.getAttribute('href'),'https://willer-travel.com/ko/ferry/');
   assert.equal(await link.getAttribute('target'),'_blank');
   assert.match(await link.getAttribute('rel'),/noopener/);
   assert.match(await link.getAttribute('rel'),/noreferrer/);
   await cta.scrollIntoViewIfNeeded();
   const box=await link.boundingBox();
   assert.ok(box?.height>=44,'Touch target too small at '+width+'px '+url+' height '+box?.height);
   const style=await link.evaluate(el=>({height:getComputedStyle(el).minHeight,display:getComputedStyle(el).display}));
   assert.equal(style.height,'44px');
   assert.equal(style.display,'inline-flex');
   const ctaOverflow=await cta.evaluate(el=>el.scrollWidth-el.clientWidth);
   assert.ok(ctaOverflow<=2,'CTA horizontal overflow '+width+'px '+url+' '+ctaOverflow);
   await ctx.close();console.log('V252 browser PASS '+width+'px '+url);
  }
 }
}finally{await browser.close();await new Promise(done=>server.close(done))}
