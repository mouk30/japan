/* V327: browser-check international ferry CTA integrity on two existing guides. */
const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require('playwright');
const origin='http://127.0.0.1:8777';
const slugs=['japan-ferry-first-timer','japan-ferry-cancellation-refund'];
const widths=[390,768,1440];
const expected=[
 'https://www.panstarcruise.com/',
 'https://www.kampuferry.co.jp/reserve/',
 'https://www.koreaferry.kr/',
 'https://www.panstarcruise.com/product/daemado/info'
];
const out='audit-reports/v327';
fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.NF327_BROWSER_PATH||undefined,args:['--no-sandbox']});
 const report={checkedAt:new Date().toISOString(),widths,slugs,checks:[],errors:[]};
 try {
  for(const slug of slugs) for(const width of widths){
   const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1,reducedMotion:'reduce'});
   const route='/guide/'+slug+'/';
   try {
    const response=await page.goto(origin+route,{waitUntil:'domcontentloaded',timeout:30000});
    const state=await page.evaluate(()=>({
     h1:document.querySelectorAll('h1').length,
     canonical:document.querySelector('link[rel="canonical"]')?.href,
     meta:document.querySelector('meta[name="description"]')?.content,
     robots:document.querySelector('meta[name="robots"]')?.content,
     overflow:document.documentElement.scrollWidth-innerWidth,
     willer:[...document.querySelectorAll('.booking a,.sidebar a')].filter(a=>a.href.includes('willer-travel.com')).length,
     links:[...document.querySelectorAll('.booking a')].map(a=>({href:a.href,text:a.textContent.trim(),rel:a.rel,target:a.target})),
     sidebar:document.querySelector('.sidebar .primary-btn')?.getAttribute('href'),
     disclosure:document.querySelector('.booking')?.textContent.includes('실시간 잔여 좌석 조회·결제·승선권 발권 기능을 제공하지 않습니다'),
     returnCheck:document.querySelector('.booking')?.textContent.includes('마지막 버스·열차'),
     h1Text:document.querySelector('h1')?.textContent.trim()
    }));
    const fail=msg=>report.errors.push(slug+' '+width+'px: '+msg);
    if(response?.status()!==200)fail('HTTP '+response?.status());
    if(state.h1!==1)fail('H1 count '+state.h1);
    if(state.canonical!=='https://www.nipponferry.com'+route)fail('canonical mismatch');
    if(!state.meta||!state.robots?.includes('index'))fail('meta/robots missing');
    if(state.overflow>2)fail('horizontal overflow '+state.overflow);
    if(state.willer)fail('misleading WILLER CTA remains');
    if(state.sidebar!=='/booking/')fail('sidebar handoff wrong');
    if(!state.disclosure||!state.returnCheck)fail('booking/return limitation notice missing');
    if(state.links.length!==4)fail('expected 4 operator links, got '+state.links.length);
    for(const href of expected){
     const link=state.links.find(x=>x.href===href);
     if(!link||!link.text||link.target!=='_blank'||!link.rel.includes('noopener')||!link.rel.includes('noreferrer'))fail('official operator link missing or insecure '+href);
    }
    for(const href of expected){
     const item=page.locator('.booking a[href="'+href+'"]');
     if(await item.count()){
      await item.scrollIntoViewIfNeeded();
      const rect=await item.boundingBox();
      if(!rect||rect.width<70||rect.height<18||rect.x< -2||rect.x+rect.width>width+2)fail('CTA geometry '+href+' '+JSON.stringify(rect));
     }
    }
    await page.screenshot({path:path.join(out,slug+'-'+width+'.png'),fullPage:true});
    report.checks.push({slug,width,status:response?.status(),h1:state.h1Text,links:state.links.length,overflow:state.overflow});
   } catch(e){report.errors.push(slug+' '+width+'px: '+String(e));}
   finally{await page.close();}
  }
 } finally {await browser.close();}
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));
 console.log(JSON.stringify({checks:report.checks.length,errors:report.errors},null,2));
 if(report.errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
