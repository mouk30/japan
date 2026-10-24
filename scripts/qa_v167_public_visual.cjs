const fs=require('fs');
const {chromium}=require('playwright');
const sites=[
['hokkaido','/japan/hokkaido/','#highlights','#highlights .city-card img',3],
['osaka','/japan/osaka/','#cruise','#cruise .nf167-panstar-photo img',1],
['directory','/japan/','.dirgrid','a[href^="/japan/fukuoka"] img',19],
['busan','/busan-osaka-cruise/','.nf167-miracle-photo','.nf167-miracle-photo img',1]
];
const widths=[390,768,1440],out='audit-output/v167-browser';
fs.mkdirSync(out,{recursive:true});
(async()=>{
const b=await chromium.launch({headless:true,args:['--disable-dev-shm-usage']});
const rows=[];
for(const [name,path,area,selector,need] of sites){
for(const width of widths){
const p=await b.newPage({viewport:{width,height:850}});
try{
const r=await p.goto('https://www.nipponferry.com'+path,{waitUntil:'domcontentloaded',timeout:40000});
await p.locator(area).first().scrollIntoViewIfNeeded();
const report=await p.evaluate(async selector=>{
const elements=Array.from(document.querySelectorAll(selector));
await Promise.all(elements.map(x=>x.decode().catch(()=>null)));
return {screen:window.innerWidth,doc:document.documentElement.scrollWidth,images:elements.map(x=>({width:x.naturalWidth,height:x.naturalHeight,draw:Math.round(x.getBoundingClientRect().width),src:x.currentSrc,alt:x.alt}))};
},selector);
const check={
http:r.status()===200,
image_count:report.images.length>=need,
load:report.images.every(x=>x.width>0),
layout:report.doc<=report.screen+4,
large_photo:!['hokkaido','osaka','busan'].includes(name)||report.images.every(x=>x.width>=900),
no_upscale:name!=='hokkaido'||report.images.every(x=>x.width>=x.draw),
distinct:name!=='hokkaido'||new Set(report.images.map(x=>x.src)).size===3,
varied:name!=='directory'||new Set(report.images.map(x=>x.src)).size>=10
};
const file=out+'/'+name+'-'+width+'.png';
await p.locator(area).first().screenshot({path:file,animations:'disabled'});
rows.push({name,width,ok:Object.values(check).every(Boolean),check,photo:report.images,screenshot:file});
console.log(rows.at(-1).ok?'PASS':'FAIL',name,width,JSON.stringify(check));
}catch(e){rows.push({name,width,ok:false,error:String(e)});console.log('FAIL',name,width,String(e).slice(0,380));}
await p.close();
}}
await b.close();
const result={screens:rows.length,passed:rows.filter(x=>x.ok).length,rows};
fs.writeFileSync(out+'/live-390-768-1440.json',JSON.stringify(result,null,2));
console.log('SUMMARY',result.passed,'/',result.screens);
if(result.passed!==result.screens)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
