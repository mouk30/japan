import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {once} from 'node:events';
import fs from 'node:fs';
import path from 'node:path';
import {chromium} from 'playwright';
const site=path.resolve('site');
const rootUrl='/things-to-do/yokohama-cruise-couple-guide/';
const cards=JSON.parse(fs.readFileSync('audit-reports/v281/photo-first-yokohama-pilot.json','utf8')).cards;
const screenshots=path.resolve('audit-reports/v281/screenshots');
fs.mkdirSync(screenshots,{recursive:true});
const server=createServer((req,res)=>{
 let url;try{url=new URL(req.url,'http://127.0.0.1')}catch{res.writeHead(400);res.end();return}
 const pathName=decodeURIComponent(url.pathname);
 const f=path.resolve(site,'.'+(pathName.endsWith('/')?pathName+'index.html':pathName));
 if(!f.startsWith(site+path.sep)){res.writeHead(403);res.end();return}
 fs.readFile(f,(err,buf)=>{if(err){res.writeHead(404);res.end('Not found '+pathName);return}
 const types={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'application/javascript','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml'};
 res.writeHead(200,{'Content-Type':types[path.extname(f)]||'application/octet-stream'});res.end(buf);
 });
});server.listen(0,'127.0.0.1');await once(server,'listening');
const browser=await chromium.launch({headless:true});const report=[];
try{
 for(const width of [320,390,768,1440]){
  const context=await browser.newContext({viewport:{width,height:950},deviceScaleFactor:1});
  const page=await context.newPage();const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  try{
   const response=await page.goto('http://127.0.0.1:'+server.address().port+rootUrl,{waitUntil:'load'});
   assert.equal(response.status(),200,'Page HTTP status');
   await page.evaluate(()=>document.fonts.ready);
   assert.equal(await page.locator('h1').count(),1);
   assert.ok(await page.locator('.nf-v281-hero').isVisible(),'Hero not visible');
   assert.ok(await page.locator('.nf-v281-preview').isVisible(),'Photo cards invisible');
   const firstImage=page.locator('.nf-v281-hero-figure img');
   assert.ok(await firstImage.evaluate(async img=>{try{await img.decode();return img.naturalWidth>0}catch{return false}}),'Hero photo broken');
   assert.equal(await page.locator('.nf-v281-card').count(),3);
   for(const c of cards){
    const card=page.locator('.nf-v281-card[href="#'+c.id+'"]');
    assert.equal(await card.count(),1,'Top card missing '+c.name);
    const img=card.locator('img');
    await img.scrollIntoViewIfNeeded();
    assert.ok(await img.evaluate(async img=>{try{await img.decode();return img.naturalWidth>0}catch{return false}}),'Failed licensed location photo '+c.name);
    assert.equal(await page.locator('#'+c.id).count(),1,'Original article target missing '+c.name);
    const ratio=await card.locator('.nf-v281-card-media').evaluate(el=>({width:el.getBoundingClientRect().width,height:el.getBoundingClientRect().height}));
    assert.ok(ratio.width>90&&ratio.height>90,'Card media collapsed '+c.name+' '+width);
   }
   const safety=page.locator('.nf-v281-safety-strip');
   assert.ok(await safety.isVisible(),'Visible return check not shown');
   assert.ok((await safety.innerText()).includes('귀선'));
   const details=page.locator('#nf-v281-safety');
   assert.ok(!(await details.evaluate(x=>x.open)),'Safety details should be concise by default');
   await details.locator('summary').click();
   assert.ok(await details.evaluate(x=>x.open),'Safety details cannot be expanded');
   assert.ok((await details.innerText()).includes('실제 하선 게이트'),'Missing operational safety when opened');
   await page.locator('#nf-v281-quick-decision summary').click();
   assert.ok(await page.locator('#nf-v281-quick-decision').evaluate(x=>x.open),'30-second full guide cannot be opened');
   await page.locator('a.nf-v281-card').first().click();
   assert.equal(new URL(page.url()).hash,'#nf-v281-stop-air-cabin','Visual card cannot reach its original details');
   const sizes=await page.evaluate(()=>({doc:document.documentElement.scrollWidth,window:window.innerWidth,hero:document.querySelector('.nf-v281-hero').getBoundingClientRect().width,cards:document.querySelector('.nf-v281-card-grid').getBoundingClientRect().width}));
   assert.ok(sizes.doc<=sizes.window+2,'Horizontal layout overflow '+width+': '+JSON.stringify(sizes));
   assert.ok(errors.length===0,'Browser JS errors: '+errors.join(';'));
   // Restore visual first screen before producing screenshot. Screenshot shows actual Chrome rendering.
   await page.goto('http://127.0.0.1:'+server.address().port+rootUrl,{waitUntil:'load'});
   await page.screenshot({path:path.join(screenshots,'yokohama-v281-'+width+'.png'),fullPage:false});
   report.push({viewport:width,passed:true,heading:await page.locator('h1').innerText(),photos:cards.length,documentWidth:sizes.doc});
  }finally{await context.close()}
 }
}finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
fs.writeFileSync('audit-reports/v281/browser-qa-result.json',JSON.stringify({version:'V281',screenshotReview:'Local CI Chromium only; Vercel protected preview separately required',report},null,2)+'\n');
console.log('V281 BROWSER PASS '+JSON.stringify(report));
