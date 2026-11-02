/* V336: existing overnight and bicycle guides, official international CTA + browser QA. */
const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require('playwright');
const slugs=['japan-ferry-overnight-tips','japan-ferry-bicycle'];
const widths=[390,768,1440];
const expected=[
 'https://www.panstarcruise.com/product/osaka/info',
 'https://www.kampuferry.co.jp/reserve/',
 'https://www.koreaferry.kr/',
 'https://www.panstarcruise.com/product/daemado/info'
];
const topical={
 'japan-ferry-overnight-tips':['https://www.panstarcruise.com/product/osaka/info','https://www.panstarcruise.com/product/osaka/procedure','https://www.panstarcruise.com/support/notice/265','https://www.panstarcruise.com/product/osaka/price','https://www.kampuferry.co.jp/reserve/'],
 'japan-ferry-bicycle':['https://www.panstarcruise.com/product/osaka/baggage','https://www.panstarcruise.com/product/osaka/procedure','https://www.kampuferry.co.jp/lang_kor/fare/basic/','https://www.kampuferry.co.jp/reserve/']
};
const out='audit-reports/v336';
fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.NF336_BROWSER_PATH||undefined,args:['--no-sandbox']});
 const report={checkedAt:new Date().toISOString(),slugs,widths,checks:[],errors:[]};
 try{
  for(const slug of slugs)for(const width of widths){
   const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1,reducedMotion:'reduce'});
   const route='/guide/'+slug+'/';
   const fail=msg=>report.errors.push(slug+' '+width+'px: '+msg);
   try{
    const response=await page.goto('http://127.0.0.1:8777'+route,{waitUntil:'domcontentloaded',timeout:30000});
    const state=await page.evaluate(()=>({
     h1:document.querySelectorAll('h1').length,
     canonical:document.querySelector('link[rel="canonical"]')?.href,
     meta:document.querySelector('meta[name="description"]')?.content,
     robots:document.querySelector('meta[name="robots"]')?.content,
     overflow:document.documentElement.scrollWidth-innerWidth,
     willer:[...document.querySelectorAll('a')].filter(a=>a.href.includes('willer-travel.com')).length,
     booking:[...document.querySelectorAll('.booking a')].map(a=>({href:a.href,rel:a.rel,target:a.target,text:a.textContent.trim()})),
     sidebar:document.querySelector('.sidebar .primary-btn')?.getAttribute('href'),
     disclaimer:document.querySelector('.booking')?.textContent.includes('실시간 운항·좌석 조회·결제·승선권 발권 기능이 없습니다'),
     returnNote:document.querySelector('.booking')?.textContent.includes('미확인'),
     articleText:document.querySelector('.article-card')?.textContent||'',
     articleLinks:[...document.querySelectorAll('.article-card a')].map(a=>a.href),
     cover:document.querySelector('img.article-cover')?.getAttribute('src'),
     h1Text:document.querySelector('h1')?.textContent.trim()
    }));
    if(response?.status()!==200)fail('HTTP '+response?.status());
    if(state.h1!==1)fail('H1 count '+state.h1);
    if(state.canonical!=='https://www.nipponferry.com'+route)fail('canonical mismatch');
    if(!state.meta||!state.robots?.includes('index'))fail('meta/robots missing');
    if(state.overflow>2)fail('horizontal overflow '+state.overflow);
    if(state.willer)fail('WILLER domestic booking CTA remains');
    if(state.sidebar!=='/booking/')fail('sidebar handoff mismatch');
    if(!state.disclaimer||!state.returnNote)fail('booking/return limitations missing');
    if(!state.articleText.includes('공식 원문 대조일: 2026-11-03'))fail('official source date missing');
    if(!state.articleText.includes('2026년 11월'))fail('November applicability missing');
    if(state.cover!==(slug==='japan-ferry-bicycle'?'/images/car.jpg':'/images/ferry.jpg'))fail('original article cover mismatch');
    if(slug==='japan-ferry-overnight-tips'&&(!state.articleText.includes('2026년 4월 1일')||!state.articleText.includes('오사카 국제페리터미널')))fail('overnight source/applicability/return port missing');
    if(slug==='japan-ferry-bicycle'&&(!state.articleText.includes('40,000원')||!state.articleText.includes('현금 결제')||!state.articleText.includes('적재 공간')))fail('bicycle fare/payment/capacity conditions missing');
    for(const href of topical[slug])if(!state.articleLinks.includes(href))fail('official topical source missing '+href);
    if(state.booking.length!==4)fail('expected 4 operator links, got '+state.booking.length);
    for(const href of expected){
     const link=state.booking.find(x=>x.href===href);
     if(!link||!link.text||link.target!=='_blank'||!link.rel.includes('noopener')||!link.rel.includes('noreferrer'))fail('official operator link missing/insecure '+href);
     const a=page.locator('.booking a[href="'+href+'"]');
     if(await a.count()){
      await a.scrollIntoViewIfNeeded();
      const rect=await a.boundingBox();
      if(!rect||rect.width<70||rect.height<18||rect.x< -2||rect.x+rect.width>width+2)fail('CTA geometry '+href+' '+JSON.stringify(rect));
     }
    }
    await page.screenshot({path:path.join(out,slug+'-'+width+'.png'),fullPage:true});
    report.checks.push({slug,width,status:response?.status(),h1:state.h1Text,bookingLinks:state.booking.length,overflow:state.overflow});
   }catch(e){fail(String(e))}
   finally{await page.close()}
  }
 }finally{await browser.close()}
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));
 console.log(JSON.stringify({checks:report.checks.length,errors:report.errors},null,2));
 if(report.errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});