/* V338: official booking CTA and source integrity for existing seniors/kids guides. */
const fs=require('node:fs'),path=require('node:path');
const {chromium}=require('playwright');
const slugs=['japan-ferry-seniors','japan-ferry-with-kids'];
const widths=[390,768,1440];
const operators=[
 'https://www.panstarcruise.com/product/osaka/info',
 'https://www.kampuferry.co.jp/reserve/',
 'https://www.koreaferry.kr/',
 'https://www.panstarcruise.com/product/daemado/info'
];
const topical={
 'japan-ferry-seniors':[
 'https://www.panstarcruise.com/product/osaka/price',
 'https://www.kampuferry.co.jp/fare/basic/',
 'https://www.panstarcruise.com/product/osaka/info'
 ],
 'japan-ferry-with-kids':[
 'https://www.kampuferry.co.jp/yoyaku/en/pricelist202510.html',
 'https://www.kampuferry.co.jp/yoyaku/en/reservation.html',
 'https://www.panstarcruise.com/product/osaka/price'
 ]
};
const out='audit-reports/v338';fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.NF338_BROWSER_PATH||undefined,args:['--no-sandbox']});
 const report={checkedAt:new Date().toISOString(),checks:[],errors:[]};
 try{
  for(const slug of slugs)for(const width of widths){
   const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1,reducedMotion:'reduce'});
   const route='/guide/'+slug+'/';
   const fail=m=>report.errors.push(slug+' '+width+'px '+m);
   try{
    const response=await page.goto('http://127.0.0.1:8777'+route,{waitUntil:'domcontentloaded',timeout:30000});
    const d=await page.evaluate(()=>({
      h1:document.querySelectorAll('h1').length,
      canonical:document.querySelector('link[rel="canonical"]')?.href,
      description:document.querySelector('meta[name="description"]')?.content,
      robots:document.querySelector('meta[name="robots"]')?.content,
      overflow:document.documentElement.scrollWidth-innerWidth,
      willer:[...document.querySelectorAll('a')].filter(a=>a.href.includes('willer-travel.com')).length,
      booking:[...document.querySelectorAll('.booking a')].map(a=>({href:a.href,text:a.textContent.trim(),target:a.target,rel:a.rel})),
      bookingText:document.querySelector('.booking')?.textContent||'',
      articleText:document.querySelector('.article')?.textContent||'',
      articleLinks:[...document.querySelectorAll('.article-card a')].map(a=>a.href),
      sidebar:document.querySelector('.sidebar .primary-btn')?.getAttribute('href'),
      cover:document.querySelector('.article-cover')?.getAttribute('src')
    }));
    if(response?.status()!==200)fail('HTTP '+response?.status());
    if(d.h1!==1||d.canonical!=='https://www.nipponferry.com'+route)fail('H1/canonical regression');
    if(!d.description||!d.robots?.includes('index'))fail('SEO metadata missing');
    if(d.overflow>2)fail('horizontal overflow '+d.overflow);
    if(d.willer)fail('misleading WILLER booking link remains');
    if(d.sidebar!=='/booking/')fail('sidebar is not internal booking handoff');
    if(d.cover!=='/images/ferry.jpg')fail('original cover changed');
    if(!d.articleText.includes('공식 원문 대조일: 2026-11-03')||!d.articleText.includes('2026년 11월'))fail('dated applicability missing');
    if(!d.bookingText.includes('실시간 운항·좌석 조회·결제·승선권 발권 기능이 없습니다'))fail('non-booking disclosure missing');
    if(!d.bookingText.includes('미확인 마지막 버스·열차 시각'))fail('last transport uncertainty missing');
    for(const u of topical[slug])if(!d.articleLinks.includes(u))fail('official topical source missing '+u);
    if(d.booking.length!==4)fail('expected four international operator links');
    for(const u of operators){
      const a=d.booking.find(x=>x.href===u);
      if(!a||!a.text||a.target!=='_blank'||!a.rel.includes('noopener')||!a.rel.includes('noreferrer'))fail('missing/insecure operator link '+u);
      const node=page.locator('.booking a[href="'+u+'"]');
      if(await node.count()){
        await node.scrollIntoViewIfNeeded();
        const r=await node.boundingBox();
        if(!r||r.width<70||r.height<18||r.x< -2||r.x+r.width>width+2)fail('CTA geometry '+u+' '+JSON.stringify(r));
      }
    }
    await page.screenshot({path:path.join(out,slug+'-'+width+'.png'),fullPage:true});
    report.checks.push({slug,width,status:response?.status(),operatorLinks:d.booking.length,overflow:d.overflow});
   }catch(e){fail(String(e))}
   finally{await page.close()}
  }
 }finally{await browser.close()}
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));
 console.log(JSON.stringify({checks:report.checks.length,errors:report.errors},null,2));
 if(report.errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
