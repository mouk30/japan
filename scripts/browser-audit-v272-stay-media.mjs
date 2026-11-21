/**
 * V272 local Chromium rendering audit at 320/390/768/1440 for all 28 existing
 * /stay/ guides. Generates per-viewport measured card sizes, image upscaling,
 * broken image candidates, CSS hero backgrounds and horizontal overflow.
 * This is NOT an authenticated Vercel Preview inspection.
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
const slugs=files.map(f=>f==='site/stay/index.html'?'/stay/':'/stay/'+f.split('/')[2]+'/');
const server=createServer((req,res)=>{
 let pathname;
 try{pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname)}catch{res.writeHead(400);res.end();return}
 const file=path.resolve(root,'.'+(pathname.endsWith('/')?pathname+'index.html':pathname));
 if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return}
 fs.readFile(file,(err,data)=>{
  if(err){res.writeHead(404);res.end();return}
  const ext=path.extname(file).toLowerCase();
  res.writeHead(200,{'Content-Type':({
   '.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'application/javascript',
   '.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp','.png':'image/png','.svg':'image/svg+xml',
   '.gif':'image/gif','.woff2':'font/woff2'}[ext]||'application/octet-stream')});
  res.end(data);
 });
});
server.listen(0,'127.0.0.1');await once(server,'listening');
const base='http://127.0.0.1:'+server.address().port;
const browser=await chromium.launch({headless:true});
const observations=[];
try{
 for(const width of [320,390,768,1440]){
  const context=await browser.newContext({viewport:{width,height:900},deviceScaleFactor:1});
  const page=await context.newPage();
  // Deterministic local QA: block third-party scripts/fonts. Real Preview may differ.
  await page.route('**/*',route=>route.request().url().startsWith(base)?route.continue():route.abort());
  try{
   for(const slug of slugs){
    const response=await page.goto(base+slug,{waitUntil:'load',timeout:30000});
    assert.equal(response?.status(),200,'Local page failed '+slug+' @ '+width);
    const data=await page.evaluate(()=>{
     const images=[...document.querySelectorAll('img')].map(el=>{
      const rect=el.getBoundingClientRect(),cs=getComputedStyle(el);
      return {src:el.getAttribute('src'),naturalWidth:el.naturalWidth,naturalHeight:el.naturalHeight,
       renderedWidth:Number(rect.width.toFixed(2)),renderedHeight:Number(rect.height.toFixed(2)),
       objectFit:cs.objectFit,loaded:el.complete,
       upscaled:el.naturalWidth>0&&el.naturalHeight>0?
        Number(Math.max(rect.width/el.naturalWidth,rect.height/el.naturalHeight).toFixed(3)):null,
       inCard:!!el.closest('.sv-card'),inDetail:el.classList.contains('sv-img')};
     });
     const hero=document.querySelector('.sv-hero');
     const cards=[...document.querySelectorAll('.sv-card')].map(el=>{
      const rect=el.getBoundingClientRect();
      return {width:Number(rect.width.toFixed(2)),height:Number(rect.height.toFixed(2))};
     });
     return {h1Count:document.querySelectorAll('h1').length,canonical:document.querySelector('link[rel="canonical"]')?.href??null,
      cards:cards.length,cardRects:cards,images,
      heroBefore:hero?getComputedStyle(hero,'::before').backgroundImage:null,
      horizontalOverflowPx:Math.max(0,document.documentElement.scrollWidth-innerWidth),
      brokenLoadedImages:images.filter(x=>x.loaded&&x.naturalWidth===0).map(x=>x.src),
      upscaledCardImages:images.filter(x=>x.inCard&&x.upscaled!==null&&x.upscaled>1.5).map(x=>({src:x.src,scale:x.upscaled})),
      cardImageAspectDeviations:images.filter(x=>x.inCard&&x.renderedHeight>0&&Math.abs(x.renderedWidth/x.renderedHeight-4/3)>0.12).map(x=>({src:x.src,ratio:Number((x.renderedWidth/x.renderedHeight).toFixed(3))}))};
    });
    assert.equal(data.h1Count,1,'H1 changed '+slug+' '+width);
    assert.ok(data.canonical?.endsWith(slug),'Canonical changed '+slug+' '+width);
    assert.ok(data.cards>=3,'Missing card layout '+slug+' '+width);
    observations.push({slug,width,...data});
   }
  }finally{await context.close()}
 }
}finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
assert.equal(observations.length,112,'Expected 28 pages x 4 viewports');
const summary={pageCount:28,viewportWidths:[320,390,768,1440],checks:observations.length,
 overflowCases:observations.filter(x=>x.horizontalOverflowPx>2).length,
 brokenLoadedImageCases:observations.filter(x=>x.brokenLoadedImages.length).length,
 cardUpscaleCases:observations.filter(x=>x.upscaledCardImages.length).length,
 cardAspectDeviationCases:observations.filter(x=>x.cardImageAspectDeviations.length>0).length,
 cardImageAspectDeviations:observations.reduce((n,x)=>n+x.cardImageAspectDeviations.length,0)};
const report={stage:'V272',generatedAt:new Date().toISOString(),kind:'local Chromium only',
 summary,observations,
 caveats:['Third-party resources blocked for deterministic local rendering.',
  'An audit run finishing is not a claim that every image is sharp, correctly licensed or location-accurate.',
  'Loaded broken image candidates, horizontal overflow, upscaling and card image ratio deviations are recorded as review findings.',
  '4:3 ratio deviation uses rendered card IMAGE geometry, not the entire text+image card height; it is not an automatic failure.',
  'Vercel Preview still requires separate authenticated human-visible inspection before merge.']};
const output='audit-reports/v272-stay-viewport-generated.json';
fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
console.log('V272 CHROMIUM AUDIT COMPLETE '+JSON.stringify(summary));
console.log('V272 evidence artifact '+output+'; no production/Preview verification claimed');
