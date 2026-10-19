// Three commercial long-tail pages: browser, basic SEO, and event-contract QA.
const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const routes = [
  'busan-hakata-ferry-reservation',
  'bukan-ferry-shimonoseki-price',
  'panstar-miracle-osaka-cabin-types'
];
const widths=[390,768,1440];
const base='http://127.0.0.1:8765';
const out='audit-output/longtail-3';
fs.mkdirSync(out,{recursive:true});
(async()=>{
  const browser=await chromium.launch({headless:true});
  const rows=[];
  try {
    for(const slug of routes) {
      for(const width of widths) {
        const ctx=await browser.newContext({viewport:{width,height:900},deviceScaleFactor:1});
        await ctx.addInitScript(()=>{
          window.__nfQAEvents=[];
          window.gtag=(...args)=>window.__nfQAEvents.push(args);
        });
        const page=await ctx.newPage(),errors=[];
        page.on('pageerror',e=>errors.push(String(e.message)));
        const url='/japan-cruise/'+slug+'/';
        let response=null;
        try {response=await page.goto(base+url,{waitUntil:'networkidle',timeout:30000});}
        catch(e){errors.push('navigation '+e.message);}
        let state={};
        try{
          state=await page.evaluate(()=>{
            const brokenImgs=[...document.images].filter(x=>!x.complete||x.naturalWidth===0).map(x=>x.src);
            const structured=[...document.querySelectorAll('script[type="application/ld+json"]')].map(x=>{try{return JSON.parse(x.textContent)}catch(e){return null}});
            const external=[...document.querySelectorAll('a[href]')].filter(a=>/^https?:/.test(a.href)&&new URL(a.href).origin!==location.origin);
            const internal=[...document.querySelectorAll('a[href]')].filter(a=>new URL(a.href).pathname==='/booking/japan-cruise/');
            return {
              title:document.title,description:document.querySelector('meta[name="description"]')?.content,
              canonical:document.querySelector('link[rel="canonical"]')?.href,
              h1:document.querySelectorAll('h1').length,
              structuredCount:structured.length,
              structuredParseOK:structured.length>0&&structured.every(x=>x!==null),
              isOverflow:document.documentElement.scrollWidth>window.innerWidth+1,
              brokenImgs,externalCount:external.length,internalBookingCount:internal.length,
              trackingScript:!!document.querySelector('script[src="/nf-longtail-clicks.js"]')
            };
          });
          const link=page.locator('a[href^="https://"]').first();
          await link.evaluate(a=>{
            a.addEventListener('click',e=>e.preventDefault(),{once:true});
            a.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}));
          });
          state.trackResult=await page.evaluate(()=>window.__nfQAEvents);
        }catch(e){errors.push('browser evaluation '+e.message);}
        const expected='https://www.nipponferry.com'+url;
        const checks={
          status200:response?.status()===200,
          title:!!state.title&&state.title.includes('NIPPONFERRY'),
          canonical:state.canonical===expected,
          description:!!state.description,
          oneH1:state.h1===1,
          jsonld:state.structuredParseOK===true,
          responsive:state.isOverflow===false,
          images:state.brokenImgs?.length===0,
          officialLinks:state.externalCount>0,
          internalBooking:state.internalBookingCount>0,
          trackingLoaded:state.trackingScript===true,
          clickEvent:state.trackResult?.some(x=>x[0]==='event'&&x[1]==='nf_travel_link_click')===true,
          noJsErrors:errors.length===0
        };
        const pass=Object.values(checks).every(Boolean);
        rows.push({slug,width,pass,checks,errors,brokenImages:state.brokenImgs||[]});
        if(width===390||width===1440)await page.screenshot({path:path.join(out,slug+'-'+width+'.png'),fullPage:true});
        console.log((pass?'PASS':'FAIL')+' '+slug+' '+width+'px '+JSON.stringify(checks));
        await ctx.close();
      }
    }
  }finally {await browser.close();}
  const summary={pages:routes.length,combinations:rows.length,pass:rows.filter(x=>x.pass).length,fail:rows.filter(x=>!x.pass).length,scope:'local static browser QA; not live ranking, external link availability, or reservations'};
  fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(rows,null,2));
  fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(summary,null,2));
  console.log(JSON.stringify(summary,null,2));
  if(summary.fail)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
