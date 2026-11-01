import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {chromium} from 'playwright';
const root=path.resolve('site');
const report=JSON.parse(fs.readFileSync('audit-reports/v283/photo-card-targets-and-legacy-qa.json','utf8'));
const server=createServer((req,res)=>{
 let requestUrl;try{requestUrl=new URL(req.url,'http://127.0.0.1')}catch{res.writeHead(400);res.end();return}
 const p=decodeURIComponent(requestUrl.pathname),f=path.resolve(root,'.'+(p.endsWith('/')?p+'index.html':p));
 if(!f.startsWith(root+path.sep)){res.writeHead(403);res.end();return}
 fs.readFile(f,(err,b)=>{if(err){res.writeHead(404);res.end();return}const types={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'application/javascript','.webp':'image/webp','.jpg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml'};
 res.writeHead(200,{'Content-Type':types[path.extname(f)]||'application/octet-stream'});res.end(b)});
});
server.listen(0,'127.0.0.1');await once(server,'listening');
const browser=await chromium.launch({headless:true});
let total=0;
const saved=[];
try{
 for(const width of [320,390,768,1440]){
  for(const config of report.pages){
   const context=await browser.newContext({viewport:{width,height:880}}),page=await context.newPage();
   try{
    const url='http://127.0.0.1:'+server.address().port+'/'+config.path.replace(/^site\//,'').replace(/index\.html$/,'');
    const r=await page.goto(url,{waitUntil:'load'});assert.equal(r.status(),200);
    assert.equal(await page.locator('a.nf-v282-card').count(),3);
    const hero=page.locator('h1');assert.ok(await hero.isVisible());
    const safety=page.locator('.nf-v282-warning');assert.ok(await safety.isVisible());
    for(const t of config.targets){
     const card=page.locator('a.nf-v282-card[href="#'+t.id+'"]');assert.equal(await card.count(),1);
     const img=card.locator('img');await img.scrollIntoViewIfNeeded();
     assert.ok(await img.evaluate(async el=>{try{await el.decode();return el.naturalWidth>0}catch{return false}}),'Photo broken '+t.id);
     await card.click();
     assert.equal(new URL(page.url()).hash,'#'+t.id,'Not navigated to direct detail '+t.id);
     const dest=page.locator('[id="'+t.id+'"]');assert.equal(await dest.count(),1);
     assert.ok(await dest.isVisible(),'Clicked destination not visible '+t.id);
     const text=await dest.innerText();
     assert.ok(text.includes(t.mustInclude),'Destination content mismatch '+t.id);
     await page.waitForFunction(id=>{const el=document.getElementById(id);if(!el)return false;const rect=el.getBoundingClientRect();return rect.top>-70&&rect.top<innerHeight-10;},t.id,{timeout:7000});
     const pos=await dest.evaluate(el=>el.getBoundingClientRect().top);
     assert.ok(pos>-70&&pos<880,'Clicked destination outside scroll position '+width+' '+t.id+' top='+pos);
     await page.evaluate(()=>window.scrollTo(0,0));
    }
    const dimensions=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,width:innerWidth}));
    assert.ok(dimensions.scroll<=dimensions.width+2,'Horizontal overflow '+config.path+' '+width);
    saved.push({path:config.path,width,passed:true,cardTargets:config.targets.map(t=>t.id)});
    total++;
   }finally{await context.close()}
  }
 }
}finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
fs.mkdirSync('audit-reports/v283',{recursive:true});
fs.writeFileSync('audit-reports/v283/browser-card-navigation-results.json',JSON.stringify({screens:total,cardsPerScreen:3,checks:total*3,result:saved},null,2)+'\n');
console.log('V283 BROWSER PASS '+total+' page-width screen tests, '+(total*3)+' exact card→destination click checks');
