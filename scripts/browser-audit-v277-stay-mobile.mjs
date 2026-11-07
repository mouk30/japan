/**
 * V277: 28 EXISTING /stay/ guides x 320/390px, LOCAL Chromium audit.
 * Evidence-only. Touch-target and accessibility findings are review candidates;
 * passing this script does not mean every control meets WCAG or that Vercel
 * Preview was inspected. No photos, booking links or HTML are changed.
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
assert.equal(files.length,28,'Only 28 existing /stay/ guides may be audited');
assert.ok(fs.existsSync('site/robots.txt')&&fs.existsSync('site/sitemap.xml'));
const slugs=files.map(f=>'/'+f.replace(/^site\//,'').replace(/index\.html$/,''));
const server=createServer((req,res)=>{
 let pathname;
 try{pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname)}
 catch{res.writeHead(400);res.end();return}
 const file=path.resolve(root,'.'+(pathname.endsWith('/')?pathname+'index.html':pathname));
 if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return}
 fs.readFile(file,(err,data)=>{
  if(err){res.writeHead(404);res.end();return}
  const ext=path.extname(file).toLowerCase();
  res.writeHead(200,{'Content-Type':({
   '.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8',
   '.js':'application/javascript','.jpg':'image/jpeg','.jpeg':'image/jpeg',
   '.webp':'image/webp','.png':'image/png','.svg':'image/svg+xml',
   '.gif':'image/gif','.woff2':'font/woff2'}[ext]||'application/octet-stream')});
  res.end(data);
 });
});
server.listen(0,'127.0.0.1');await once(server,'listening');
const base='http://127.0.0.1:'+server.address().port;
const browser=await chromium.launch({headless:true});
const observations=[];
try{
 for(const width of [320,390]){
  const context=await browser.newContext({viewport:{width,height:900},deviceScaleFactor:1});
  const page=await context.newPage();
  await page.route('**/*',r=>r.request().url().startsWith(base)?r.continue():r.abort());
  try{
   for(const slug of slugs){
    const response=await page.goto(base+slug,{waitUntil:'load',timeout:30000});
    assert.equal(response?.status(),200,'Local HTTP error '+slug+' @'+width);
    // Force local lazy images to resolve; no remote resource is fetched.
    await page.evaluate(async()=>{
     const local=[...document.images].filter(i=>i.src.startsWith(location.origin));
     for(const img of local)img.loading='eager';
     await Promise.all(local.map(img=>img.decode().catch(()=>null)));
    });
    const data=await page.evaluate(()=>{
     const visible=el=>{
      const cs=getComputedStyle(el),r=el.getBoundingClientRect();
      return cs.display!=='none'&&cs.visibility!=='hidden'&&r.width>0&&r.height>0;
     };
     const name=el=>(el.getAttribute('aria-label')||el.innerText||el.getAttribute('title')||
      el.querySelector('img')?.getAttribute('alt')||'').trim().replace(/\s+/g,' ').slice(0,110);
     const clickable=[...document.querySelectorAll('a[href],button,[role="button"]')]
      .filter(visible).map(el=>{
       const r=el.getBoundingClientRect(),cs=getComputedStyle(el);
       const primary=!!el.closest('.stay-convert .buttons,.sv-ct');
       return {tag:el.tagName.toLowerCase(),href:el.getAttribute('href'),
        label:name(el),selector:el.className?.toString().slice(0,80)||'',
        primary,width:+r.width.toFixed(1),height:+r.height.toFixed(1),
        left:+r.left.toFixed(1),right:+r.right.toFixed(1),
        touchUnder44:r.width<43.5||r.height<43.5,
        focusable:el.tabIndex>=0,outlineStyle:cs.outlineStyle};
      });
     const images=[...document.images].filter(i=>i.src.startsWith(location.origin)).map(i=>({
      src:i.getAttribute('src'),alt:i.getAttribute('alt'),
      loaded:i.complete,naturalWidth:i.naturalWidth
     }));
     const cards=[...document.querySelectorAll('.sv-card')].filter(visible);
     const hero=document.querySelector('.sv-hero');
     return {
      title:document.title,
      canonical:document.querySelector('link[rel="canonical"]')?.href||null,
      robots:document.querySelector('meta[name="robots"]')?.content||null,
      h1Count:document.querySelectorAll('h1').length,
      horizontalOverflowPx:Math.max(0,document.documentElement.scrollWidth-innerWidth),
      cardCount:cards.length,
      heroVisible:!!hero&&visible(hero),
      controls:clickable.length,
      unnamedControls:clickable.filter(x=>!x.label),
      under44:clickable.filter(x=>x.touchUnder44),
      primaryUnder44:clickable.filter(x=>x.primary&&x.touchUnder44),
      nonFocusableLinks:clickable.filter(x=>x.tag==='a'&&!x.focusable),
      brokenLocalImages:images.filter(x=>x.loaded&&x.naturalWidth===0),
      missingImageAlts:images.filter(x=>x.alt===null),
      imageCount:images.length,
      mainFerryCta:document.querySelector('.stay-convert .buttons a.red')?.getAttribute('href')||null
     };
    });
    await page.keyboard.press('Tab');
    const keyboardFocus=await page.evaluate(()=>({
     tag:document.activeElement?.tagName||null,
     label:(document.activeElement?.getAttribute('aria-label')||document.activeElement?.textContent||'').trim().slice(0,100)
    }));
    assert.equal(data.h1Count,1,'H1 count changed '+slug+' @'+width);
    assert.equal(data.canonical,'https://www.nipponferry.com'+slug,'Canonical changed '+slug+' @'+width);
    assert.match(data.robots,/index,follow/i,'Robots changed '+slug+' @'+width);
    assert.ok(data.cardCount>=3,'Stay cards missing '+slug+' @'+width);
    assert.ok(data.heroVisible,'Hero hidden '+slug+' @'+width);
    assert.ok(data.mainFerryCta?.startsWith('/booking/'),'Ferry CTA missing '+slug+' @'+width);
    assert.ok(data.horizontalOverflowPx<=2,'Horizontal overflow '+slug+' @'+width);
    assert.equal(data.brokenLocalImages.length,0,'Broken local image '+slug+' @'+width);
    assert.equal(data.missingImageAlts.length,0,'Missing local image alt '+slug+' @'+width);
    observations.push({slug,width,keyboardFocus,...data});
   }
  }finally{await context.close()}
 }
}finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
assert.equal(observations.length,56);
const summary={
 pages:28,viewports:[320,390],checks:56,
 overflowCases:observations.filter(x=>x.horizontalOverflowPx>2).length,
 brokenLocalImageCases:observations.filter(x=>x.brokenLocalImages.length>0).length,
 missingAltCases:observations.filter(x=>x.missingImageAlts.length>0).length,
 missingControlNameCases:observations.filter(x=>x.unnamedControls.length>0).length,
 touchTargetUnder44Cases:observations.filter(x=>x.under44.length>0).length,
 touchTargetUnder44Total:observations.reduce((n,x)=>n+x.under44.length,0),
 primaryTargetUnder44Cases:observations.filter(x=>x.primaryUnder44.length>0).length,
 nonFocusableLinkCases:observations.filter(x=>x.nonFocusableLinks.length>0).length,
 keyboardFocusNoTabCases:observations.filter(x=>!['A','BUTTON','INPUT'].includes(x.keyboardFocus.tag)).length
};
const report={
 stage:'V277',generatedAt:new Date().toISOString(),
 scope:'28 EXISTING /stay/ pages, 320px and 390px',
 kind:'LOCAL Chromium measurement only; NOT authenticated Vercel Preview',
 summary,observations,
 limitations:[
  'Only local origin assets are loaded; third-party scripts/fonts are blocked.',
  'Sub-44px targets are measured findings, not automatic WCAG failures; adjacent target spacing not evaluated.',
  'An accessible-name approximation is used, not a full accessibility-tree or screen-reader audit.',
  'The first Tab key tests initial keyboard navigation, not full focus order.',
  'Image presence and alt do not prove original author, exact shooting location, copyright or permissions.',
  'Draft PRs for earlier V260-V276 stages are unmerged; their HTML is not represented in this main-based audit.',
  'Protected Vercel Preview is not verified; no merge or deployment is authorized.'
 ]
};
fs.mkdirSync('audit-reports',{recursive:true});
fs.writeFileSync('audit-reports/v277-stay-mobile-generated.json',JSON.stringify(report,null,2)+'\n');
console.log('V277 LOCAL MOBILE AUDIT '+JSON.stringify(summary));
console.log('V277 report audit-reports/v277-stay-mobile-generated.json; findings need separate remediation');
