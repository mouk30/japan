/* V337: official international booking CTAs and two existing Wi-Fi/meal guides. */
const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require('playwright');
const slugs=['japan-ferry-wifi','japan-ferry-meals'];
const widths=[390,768,1440];
const operators=[
 'https://www.panstarcruise.com/product/osaka/info',
 'https://www.kampuferry.co.jp/reserve/',
 'https://www.koreaferry.kr/',
 'https://www.panstarcruise.com/product/daemado/info'
];
const source={
 'japan-ferry-wifi':['https://www.kampuferry.co.jp/service/starlink.html','2026년 7월 7일','성희(SEONG HEE)호','1,500엔/24시간','SMS 인증'],
 'japan-ferry-meals':['https://www.panstarcruise.com/product/osaka/price','https://www.kampuferry.co.jp/restaurant_shop/','2식 포함','19:00~21:00','오사카']
};
const covers={'japan-ferry-wifi':'/images/esim.jpg','japan-ferry-meals':'/images/ferry.jpg'};
const out='audit-reports/v337';
fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.NF337_BROWSER_PATH||undefined,args:['--no-sandbox']});
 const report={checkedAt:new Date().toISOString(),slugs,widths,checks:[],errors:[]};
 try{
  for(const slug of slugs)for(const width of widths){
   const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1,reducedMotion:'reduce'});
   const route='/guide/'+slug+'/';
   const fail=m=>report.errors.push(slug+' '+width+'px '+m);
   try{
    const response=await page.goto('http://127.0.0.1:8777'+route,{waitUntil:'domcontentloaded',timeout:30000});
    const data=await page.evaluate(()=>({
     h1:document.querySelectorAll('h1').length,
     canonical:document.querySelector('link[rel="canonical"]')?.href,
     description:document.querySelector('meta[name="description"]')?.content,
     robots:document.querySelector('meta[name="robots"]')?.content,
     overflow:document.documentElement.scrollWidth-innerWidth,
     willer:[...document.querySelectorAll('a')].filter(a=>a.href.includes('willer-travel.com')).length,
     links:[...document.querySelectorAll('.booking a')].map(a=>({href:a.href,text:a.textContent.trim(),rel:a.rel,target:a.target})),
     sidebar:document.querySelector('.sidebar .primary-btn')?.getAttribute('href'),
     bookingText:document.querySelector('.booking')?.textContent||'',
     articleText:document.querySelector('.article')?.textContent||'',
     articleLinks:[...document.querySelectorAll('.article-card a')].map(a=>a.href),
     cover:document.querySelector('.article-cover')?.getAttribute('src')
    }));
    if(response?.status()!==200)fail('HTTP '+response?.status());
    if(data.h1!==1||data.canonical!=='https://www.nipponferry.com'+route)fail('H1/canonical regression');
    if(!data.description||!data.robots?.includes('index'))fail('SEO meta/robots missing');
    if(data.overflow>2)fail('horizontal overflow '+data.overflow);
    if(data.willer)fail('WILLER domestic booking CTA remains');
    if(data.sidebar!=='/booking/')fail('sidebar handoff not internal');
    if(data.cover!==covers[slug])fail('original cover changed');
    if(!data.articleText.includes('공식 원문 대조일: 2026-11-03')||!data.articleText.includes('2026년 11월'))fail('source date/applicability missing');
    if(!data.bookingText.includes('실시간 운항·좌석 조회·결제·승선권 발권 기능이 없습니다'))fail('non-booking disclosure missing');
    if(!data.bookingText.includes('미확인 마지막 버스·열차 시각'))fail('last transport uncertainty missing');
    for(const required of source[slug]){
      if(!data.articleText.includes(required)&&!data.articleLinks.includes(required))fail('topical source/condition missing '+required);
    }
    if(data.links.length!==4)fail('expected 4 operator links, got '+data.links.length);
    for(const href of operators){
      const a=data.links.find(x=>x.href===href);
      if(!a||!a.text||a.target!=='_blank'||!a.rel.includes('noopener')||!a.rel.includes('noreferrer'))fail('missing/insecure official link '+href);
      const node=page.locator('.booking a[href="'+href+'"]');
      if(await node.count()){
        await node.scrollIntoViewIfNeeded();
        const rect=await node.boundingBox();
        if(!rect||rect.width<70||rect.height<18||rect.x < -2||rect.x+rect.width>width+2)fail('CTA geometry '+href+' '+JSON.stringify(rect));
      }
    }
    await page.screenshot({path:path.join(out,slug+'-'+width+'.png'),fullPage:true});
    report.checks.push({slug,width,status:response?.status(),bookingLinks:data.links.length,overflow:data.overflow});
   }catch(e){fail(String(e))}
   finally{await page.close()}
  }
 }finally{await browser.close()}
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));
 console.log(JSON.stringify({checks:report.checks.length,errors:report.errors},null,2));
 if(report.errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
