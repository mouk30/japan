import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {once} from 'node:events';
import {createServer} from 'node:http';
import {chromium} from 'playwright';
const base=path.resolve('site'),registry=JSON.parse(fs.readFileSync('audit-reports/v282/photo-first-pilot-registry.json','utf8'));
const reportDir=path.resolve('audit-reports/v282/browser-screens');
fs.mkdirSync(reportDir,{recursive:true});
const server=createServer((req,res)=>{
 let url;try{url=new URL(req.url,'http://127.0.0.1')}catch{res.writeHead(400);res.end();return}
 const reqPath=decodeURIComponent(url.pathname);
 const local=path.resolve(base,'.'+(reqPath.endsWith('/')?reqPath+'index.html':reqPath));
 if(!local.startsWith(base+path.sep)){res.writeHead(403);res.end();return}
 fs.readFile(local,(e,buffer)=>{if(e){res.writeHead(404);res.end();return}
 const mime={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'application/javascript','.webp':'image/webp','.jpg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml'};
 res.writeHead(200,{'Content-Type':mime[path.extname(local)]||'application/octet-stream'});res.end(buffer);
 });
});server.listen(0,'127.0.0.1');await once(server,'listening');
const browser=await chromium.launch({headless:true});
const results=[];
try{
 for(const width of [320,390,768,1440]){
  for(const conf of registry.modified){
   const pathname='/'+conf.path.replace(/^site\//,'').replace(/index\.html$/,'');
   const context=await browser.newContext({viewport:{width,height:920}});
   const page=await context.newPage(),errors=[];
   page.on('pageerror',e=>errors.push(String(e)));
   try{
    const rsp=await page.goto('http://127.0.0.1:'+server.address().port+pathname,{waitUntil:'load'});
    assert.equal(rsp.status(),200);
    assert.equal(await page.locator('h1').count(),1);
    assert.ok(await page.locator('.nf-v282-gallery').isVisible(),'Three guide cards not visible');
    assert.equal(await page.locator('a.nf-v282-card').count(),3);
    assert.ok(await page.locator('.nf-v282-warning').isVisible(),'Visible berth/return safety missing');
    for(const c of conf.cards){
     const link=page.locator('a.nf-v282-card[href="'+c.href+'"]').filter({hasText:c.title});
     assert.equal(await link.count(),1,'Card incorrect target '+c.href);
     const img=link.locator('img');await img.scrollIntoViewIfNeeded();
     const decoded=await img.evaluate(async el=>{try{await el.decode();return el.naturalWidth>0&&el.naturalHeight>0}catch{return false}});
     assert.ok(decoded,'Source image broken '+c.src);
     assert.equal(await page.locator(c.href).count(),1,'Target section not found '+c.href);
     const size=await link.locator('.nf-v282-card-media').evaluate(el=>({w:el.getBoundingClientRect().width,h:el.getBoundingClientRect().height}));
     assert.ok(size.w>90&&size.h>90,'Visual subject collapsed '+width+' '+conf.path);
    }
    if(conf.path.includes('things-to-do')){
     const d=page.locator('details.nf-v282-archive');
     assert.ok(!(await d.evaluate(el=>el.open)),'Long historical ferry notices should default collapsed');
     await d.locator('summary').click();
     assert.ok(await d.evaluate(el=>el.open),'Can not expand original operating information');
     assert.ok((await d.innerText()).includes('운항'),'Original history missing');
    }else{
     const hero=page.locator('.city-hero.nf-v282-cityhero');
     assert.ok(await hero.isVisible(),'Verified port tower hero invisible');
     assert.ok((await hero.evaluate(el=>getComputedStyle(el,'::before').backgroundImage)).includes('nf-v140-kobe-port-tower-2025-real.webp'),'City hero still unknown photo');
    }
    assert.ok(errors.length===0,'JS errors '+errors.join("; "));
    const dimensions=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,inner:innerWidth}));
    assert.ok(dimensions.scroll<=dimensions.inner+2,'Horizontal overflow '+width+' '+conf.path+' '+JSON.stringify(dimensions));
    await page.goto('http://127.0.0.1:'+server.address().port+pathname,{waitUntil:'load'});
    await page.screenshot({path:path.join(reportDir,conf.path.replace(/[^a-z0-9-]/gi,'-')+'-'+width+'.png'),fullPage:false});
    results.push({path:conf.path,viewport:width,images:3,passed:true});
   }finally{await context.close()}
  }
 }
}finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
fs.writeFileSync('audit-reports/v282/browser-qa-result.json',JSON.stringify({tested:results.length,preview:"Local CI Chromium only; independent authenticated Vercel inspection remains required",results},null,2)+'\n');
console.log('V282 BROWSER PASS '+results.length+' real responsive pages with decoded photos, clickable section anchors and expandable old operational data.');
