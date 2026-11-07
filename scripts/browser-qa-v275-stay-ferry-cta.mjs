/**
 * V275 local Chromium only. Verifies visible ferry CTA clarity and touch layout
 * at 320/390/768/1440; never substitutes for authenticated Vercel Preview.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {chromium} from 'playwright';
const root=path.resolve('site');
const files=['site/stay/index.html',...fs.readdirSync('site/stay',{withFileTypes:true})
 .filter(d=>d.isDirectory()&&fs.existsSync('site/stay/'+d.name+'/index.html'))
 .map(d=>'site/stay/'+d.name+'/index.html')].sort();
assert.equal(files.length,28);
const slugs=files.map(f=>'/'+f.replace(/^site\//,'').replace(/index\.html$/,''));
const server=createServer((req,res)=>{
 let pathname;try{pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname)}catch{res.writeHead(400);res.end();return}
 const file=path.resolve(root,'.'+(pathname.endsWith('/')?pathname+'index.html':pathname));
 if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return}
 fs.readFile(file,(err,data)=>{
  if(err){res.writeHead(404);res.end();return}
  const ext=path.extname(file).toLowerCase();
  res.writeHead(200,{'Content-Type':({'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8',
   '.js':'application/javascript','.jpg':'image/jpeg','.webp':'image/webp','.png':'image/png',
   '.svg':'image/svg+xml','.woff2':'font/woff2'}[ext]||'application/octet-stream')});res.end(data);
 });
});
server.listen(0,'127.0.0.1');await once(server,'listening');
const base='http://127.0.0.1:'+server.address().port;
const browser=await chromium.launch({headless:true});const observations=[];
try{
 for(const width of [320,390,768,1440]){
  const context=await browser.newContext({viewport:{width,height:900},deviceScaleFactor:1});
  const page=await context.newPage();
  await page.route('**/*',r=>r.request().url().startsWith(base)?r.continue():r.abort());
  try{
   for(const slug of slugs){
    const response=await page.goto(base+slug,{waitUntil:'load',timeout:30000});
    assert.equal(response?.status(),200,'Local page missing '+slug);
    const info=await page.evaluate(()=>{
     const a=document.querySelector('.stay-convert .buttons a.red');
     const note=document.querySelector('.stay-convert .stay-ferry-note');
     if(!a||!note)return null;
     const r=a.getBoundingClientRect(),style=getComputedStyle(a);
     return {label:a.textContent.trim(),href:a.getAttribute('href'),note:note.textContent.trim(),
      buttonWidth:r.width,buttonHeight:r.height,buttonLeft:r.left,buttonRight:r.right,
      visibility:style.visibility,display:style.display,
      horizontalOverflowPx:Math.max(0,document.documentElement.scrollWidth-innerWidth)};
    });
    assert.ok(info,'Ferry CTA/note missing '+slug+' @'+width);
    assert.equal(info.label,'크루즈·페리 예약 준비 가이드 →');
    assert.match(info.href,/^\/booking\/(?:[a-z0-9-]+\/)?$/);
    assert.ok(info.note.includes('숙소·객실 예약이 아닌 일본 국내 페리 항로 조회'));
    assert.ok(info.buttonHeight>=43,'Small touch target '+slug+' @'+width);
    assert.ok(info.buttonLeft>=-2&&info.buttonRight<=width+2,'CTA outside viewport '+slug+' @'+width);
    assert.ok(info.horizontalOverflowPx<=2,'Horizontal overflow '+slug+' @'+width);
    assert.notEqual(info.visibility,'hidden');
    observations.push({slug,width,...info});
   }
  }finally{await context.close()}
 }
}finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
assert.equal(observations.length,112);
const summary={pages:28,widths:[320,390,768,1440],localViewportChecks:112,ctaFailures:0,overflowFailures:0};
fs.writeFileSync('audit-reports/v275-stay-cta-viewport-generated.json',JSON.stringify({
 stage:'V275',generatedAt:new Date().toISOString(),kind:'LOCAL Chromium; not authenticated Preview',
 summary,observations,limitations:['Third-party resources intentionally blocked','External ferry availability not tested','Protected Vercel Preview 403 requires separate authenticated inspection']},null,2)+'\n');
console.log('V275 CHROMIUM PASS '+JSON.stringify(summary));