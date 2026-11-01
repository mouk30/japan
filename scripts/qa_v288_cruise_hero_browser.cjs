#!/usr/bin/env node
// V288: browser evidence only. A screenshot is NOT proof of image rights or real-world accuracy.
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const {chromium}=require('playwright');
const BASE='http://127.0.0.1:8765';
const ASSET='site/images/panstar-cruise-clean-2048.webp';
const EXPECTED='bbcfa65a0e670060b5ce6fe79b2a9ea3272874b4d96f96799800ec9ccb631bdd';
const ROUTES=['/japan-cruise/','/booking/','/booking/japan-cruise/','/booking/fukuoka/','/booking/osaka/','/booking/shimonoseki/','/booking/tsushima/'];
const WIDTHS=[390,768,1440,1920];
const OUT='audit-output/v288-browser';
fs.mkdirSync(OUT,{recursive:true});
const assetVerified=fs.existsSync(ASSET)&&crypto.createHash('sha256').update(fs.readFileSync(ASSET)).digest('hex')===EXPECTED;
// The CSS can reference a nonexistent file and still pass layout checks; verify the actual decoded image.
(async()=>{
 const browser=await chromium.launch({headless:true});
 const results=[];
 try{
  for(const route of ROUTES){
   for(const width of WIDTHS){
    const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
    const entry={route,width,checks:{},errors:[]};
    try{
     const response=await page.goto(BASE+route,{waitUntil:'domcontentloaded',timeout:30000});
     entry.checks.page200=Boolean(response&&response.status()===200);
     const hero=page.locator('.bk-hero,.jc-hero').first();
     entry.checks.heroExists=await hero.count()===1;
     if(entry.checks.heroExists){
      entry.layout=await page.evaluate(()=>{
       const el=document.querySelector('.bk-hero,.jc-hero');
       const photo=getComputedStyle(el,'::before');
       const bandHeight=parseFloat(photo.height);
       const r=el.getBoundingClientRect();
       const content=el.querySelector('.bk-hi,.jc-w');
       const c=content&&content.getBoundingClientRect();
       const h=el.querySelector('h1');
       const hr=h&&h.getBoundingClientRect();
       const links=[...el.querySelectorAll('a[href]')].map(a=>{const b=a.getBoundingClientRect();return {text:a.textContent.trim().slice(0,45),href:a.getAttribute('href'),left:b.left,right:b.right,width:b.width};});
       return {
        bandHeight,heroTop:r.top,contentTop:c&&c.top,
        background:photo.backgroundImage,backgroundSize:photo.backgroundSize,
        pageOverflow:document.documentElement.scrollWidth-innerWidth,
        headingOverflow:h?h.scrollWidth-h.clientWidth:null,
        headingLeft:hr&&hr.left,headingRight:hr&&hr.right,
        links
       };
      });
      const l=entry.layout;
      entry.checks.photoNotCropped=l.backgroundSize.includes('contain');
      entry.checks.correctImage=l.background.includes('panstar-cruise-clean-2048.webp');
      entry.checks.photoDecoded=await page.evaluate(async()=>{
       const image=new Image();
       image.src='/images/panstar-cruise-clean-2048.webp';
       try{await image.decode();return image.naturalWidth===2048&&image.naturalHeight===682;}catch{return false;}
      });
      entry.checks.approvedImageHash=assetVerified;
      entry.checks.photoBandPositive=l.bandHeight>80;
      entry.checks.textBelowPhoto=l.contentTop!==null&&l.contentTop>=l.heroTop+l.bandHeight-3;
      entry.checks.noHorizontalOverflow=l.pageOverflow<=3;
      entry.checks.headingFits=l.headingOverflow!==null&&l.headingOverflow<=3&&l.headingLeft>=-2&&l.headingRight<=width+2;
      entry.checks.ctaFits=l.links.length>0&&l.links.every(a=>a.width>0&&a.left>=-2&&a.right<=width+2);
      const name=route.replace(/^\/|\/$/g,'').replaceAll('/','-')||'root';
      await hero.screenshot({path:path.join(OUT,name+'-'+width+'.png'),timeout:15000});
     }
    }catch(err){entry.errors.push(String(err).slice(0,500));}
    entry.pass=entry.errors.length===0&&Object.values(entry.checks).every(Boolean);
    results.push(entry);
    console.log((entry.pass?'PASS':'FAIL')+' '+route+' '+width+' '+JSON.stringify(entry.checks));
    await page.close();
   }
  }
 }finally{await browser.close();}
 const report={scope:'V288 desktop/mobile responsive hero screenshot QA',assetVerified,assetExpectedSha256:EXPECTED,imagesChecked:ROUTES.length,viewports:WIDTHS,passed:results.filter(x=>x.pass).length,total:results.length,results,limitations:['Photo rights not proven','Image identity and route relevance require human verification','No live booking availability tested']};
 fs.writeFileSync(path.join(OUT,'report.json'),JSON.stringify(report,null,2));
 if(!assetVerified)console.error('BLOCK: approved PanStar WebP absent or SHA-256 mismatch; 28 CSS-only screenshots are not evidence of a rendered photograph.');
 if(!assetVerified||report.passed!==report.total)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
