const fs=require('fs');
const {chromium}=require('playwright');
const BASE='https://www.nipponferry.com';
const targets=[
{name:'naoshima',url:'/things-to-do/naoshima-art-ferry-return/',note:'naoshima-2027-closure',must:'2027년 1월 12일~3월 19일',source:'https://www.benesse-artsite.jp/news/20260525-3518.html',photo:'/images/editorial/v146-naoshima-miyanoura-ferry-terminal-2025.webp'},
{name:'teshima',url:'/things-to-do/teshima-art-ferry-return/',note:'teshima-winter-days',must:'화~목요일',source:'https://www.benesse-artsite.jp/news/20260630-3558.html',photo:'/images/editorial/v146-teshima-art-museum-exterior-2013.webp'},
{name:'shikoku-food',url:'/things-to-do/takamatsu-cruise-udon-market-return/',note:'marche-date-vs-postponement',must:'2027년 1월 17일',source:'https://www.kensanpin.org/ko/marche/schedule/',photo:'/images/culture-verified/japan-kagawa-udon-pilgrimage.webp'}
];
const widths=[390,768,945,1440],out='audit-output/v171-browser';
fs.mkdirSync(out,{recursive:true});
const rows=[];
const nap=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--disable-dev-shm-usage']});
 try{
  for(const target of targets)for(const width of widths){
   const page=await browser.newPage({viewport:{width,height:930},deviceScaleFactor:1});
   page.setDefaultNavigationTimeout(23000);page.setDefaultTimeout(9000);
   try{
    const response=await page.goto(BASE+target.url+'?v171_live_screen=1',{waitUntil:'domcontentloaded',timeout:23000});
    const notice=page.locator('[data-nf-v171-note="'+target.note+'"]');
    await notice.scrollIntoViewIfNeeded({timeout:8500});
    const measure=await page.evaluate(async(target)=>{
      const panel=document.querySelector('[data-nf-v171-note="'+target.note+'"]');
      const hero=document.querySelector('img[src="'+target.photo+'"]');
      if(hero){hero.loading='eager';try{await Promise.race([hero.decode(),new Promise(r=>setTimeout(r,5000))]);}catch(_){}}
      const rect=panel?.getBoundingClientRect();
      const c=document.querySelector('link[rel="canonical"]')?.getAttribute('href');
      const actions=[...document.querySelectorAll('#nf-v154-depart-book-return .nf-v154-step a')];
      return {
        scrollWidth:document.documentElement.scrollWidth,viewport:innerWidth,
        mainTitle:document.querySelector('h1')?.innerText,
        canonical:c,
        panelVisible:!!rect&&rect.width>220&&rect.height>40&&getComputedStyle(panel).display!=='none',
        panelWidth:Math.round(rect?.width||0),panelHeight:Math.round(rect?.height||0),
        panelText:panel?.innerText?.slice(0,600)||'',
        officialLink:!!panel?.querySelector('a[href="'+target.source+'"]'),
        steps:document.querySelectorAll('#nf-v154-depart-book-return .nf-v154-step').length,
        stepLinkCount:actions.length,
        smallestLinkHeight:Math.min(...actions.map(a=>a.getBoundingClientRect().height),999),
        photoSrc:hero?.getAttribute('src'),photoSize:[hero?.naturalWidth||0,hero?.naturalHeight||0],
        originalAttribution:document.body.textContent.includes('CC BY')&&!!document.querySelector('a[href*="commons.wikimedia.org"]')
      };
    },target);
    const checks={
     HTTP200:response.status()===200,
     exact_2027_or_march_notice:measure.panelText.includes(target.must),
     official_notice_link:measure.officialLink,
     one_h1_and_original_canonical:!!measure.mainTitle&&measure.canonical===BASE+target.url,
     notice_visible_and_readable:measure.panelVisible,
     three_official_journey_steps:measure.steps===3&&measure.stepLinkCount>=3,
     original_authentic_photo_loaded:measure.photoSrc===target.photo&&measure.photoSize[0]>=1000&&measure.photoSize[1]>=700,
     author_license_credit_preserved:measure.originalAttribution,
     no_horizontal_scroll:measure.scrollWidth<=width+6
    };
    const shot=out+'/'+target.name+'-'+width+'.png';
    await page.screenshot({path:shot,fullPage:false,animations:'disabled',timeout:14000});
    const good=Object.values(checks).every(Boolean);
    rows.push({name:target.name,width,pass:good,checks,measure,screenshot:shot});
    console.log(good?'PASS':'FAIL',target.name,width,JSON.stringify(checks));
   }catch(e){console.log('FAIL',target.name,width,String(e));rows.push({name:target.name,width,pass:false,error:String(e)});}
   finally{await Promise.race([page.close().catch(()=>{}),nap(3000)])}
  }
 }finally{await browser.close()}
 const result={version:'V171',screens:rows.length,pass:rows.filter(r=>r.pass).length,viewport_widths:widths,existing_pages:targets.length,new_articles:0,screenshots:rows.map(r=>r.screenshot).filter(Boolean),rows};
 fs.writeFileSync(out+'/twelve-guide-screens.json',JSON.stringify(result,null,2));
 console.log('SUMMARY',result.pass,'/',result.screens);
 if(result.pass!==result.screens)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
