/**
 * V272 evidence-only audit of 28 EXISTING /stay/ HTML guides on the current
 * main baseline. Image dimensions, byte size and SHA are computed from real
 * local files; this does not prove location, author, copyright or permission.
 * All findings are emitted to a downloadable CI artifact, not silently fixed.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const root=path.resolve('site');
const out='audit-reports/v272-stay-media-generated.json';
const old=JSON.parse(fs.readFileSync('data/v253/stay-photo-audit.json','utf8'));
const v254=JSON.parse(fs.readFileSync('data/v254/stay-verified-region-photos.json','utf8'));
const existing=['site/stay/index.html',...fs.readdirSync('site/stay',{withFileTypes:true})
 .filter(d=>d.isDirectory()&&fs.existsSync('site/stay/'+d.name+'/index.html'))
 .map(d=>'site/stay/'+d.name+'/index.html')].sort();
assert.equal(existing.length,28,'Scope must remain exactly 28 existing /stay/ guides');
assert.ok(fs.existsSync('site/sitemap.xml')&&fs.existsSync('site/robots.txt'),'SEO files missing');
const authorizedTourism=new Map(Object.values(v254.images).map(x=>[x.src,x]));
const cc0=old.verifiedPlacePhotoReused;
authorizedTourism.set(cc0.src,{src:cc0.src,author:cc0.photographer,source:cc0.sourcePage,license:cc0.license,gitBlobSha:null,scene:cc0.location});
const files=new Map();
const sha1=b=>crypto.createHash('sha1').update(Buffer.from('blob '+b.length+'\0')).update(b).digest('hex');
const sha256=b=>crypto.createHash('sha256').update(b).digest('hex');
function imageSize(b){
 if(b.length>=24&&b.subarray(0,8).equals(Buffer.from('89504e470d0a1a0a','hex')))
  return {format:'png',width:b.readUInt32BE(16),height:b.readUInt32BE(20)};
 if(b.length>=10&&b.toString('ascii',0,3)==='GIF')
  return {format:'gif',width:b.readUInt16LE(6),height:b.readUInt16LE(8)};
 if(b.length>=30&&b.toString('ascii',0,4)==='RIFF'&&b.toString('ascii',8,12)==='WEBP'){
  const kind=b.toString('ascii',12,16);
  if(kind==='VP8X')return {format:'webp-vp8x',width:1+b.readUIntLE(24,3),height:1+b.readUIntLE(27,3)};
  if(kind==='VP8L'&&b[20]===0x2f)return {format:'webp-vp8l',
   width:1+(b[21]|((b[22]&0x3f)<<8)),
   height:1+(((b[22]>>6)&3)|(b[23]<<2)|((b[24]&15)<<10))};
  if(kind==='VP8 '&&b[23]===0x9d&&b[24]===0x01&&b[25]===0x2a)
   return {format:'webp-vp8',width:b.readUInt16LE(26)&0x3fff,height:b.readUInt16LE(28)&0x3fff};
  return {format:'webp-unparsed',width:null,height:null};
 }
 if(b.length>4&&b[0]===0xff&&b[1]===0xd8){
  let i=2;
  while(i+3<b.length){
   if(b[i]!==0xff){i++;continue}
   while(b[i]===0xff)i++;
   const marker=b[i++];
   if(marker===0xd9||marker===0xda)break;
   if(marker===0xd8||marker===0x01||(marker>=0xd0&&marker<=0xd7))continue;
   if(i+2>b.length)break;
   const len=b.readUInt16BE(i);
   if(len<2||i+len>b.length)break;
   if([0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf].includes(marker)&&len>=7)
    return {format:'jpeg',width:b.readUInt16BE(i+5),height:b.readUInt16BE(i+3)};
   i+=len;
  }
  return {format:'jpeg-unparsed',width:null,height:null};
 }
 if(b.subarray(0,200).toString('utf8').includes('<svg')){
  const svg=b.toString('utf8');
  const box=svg.match(/\bviewBox\s*=\s*['"]\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)\s*['"]/i);
  return {format:'svg',width:box?Number(box[3]):null,height:box?Number(box[4]):null};
 }
 return {format:'unknown',width:null,height:null};
}
function resource(src){
 const cleaned=src.split(/[?#]/)[0];
 if(!cleaned.startsWith('/')||cleaned.startsWith('//'))return null;
 const full=path.resolve(root,'.'+decodeURIComponent(cleaned));
 assert.ok(full.startsWith(root+path.sep),'Invalid asset path '+src);
 return {cleaned,full};
}
function attr(tag,key){
 return tag.match(new RegExp('\\b'+key+'\\s*=\\s*["\x27]([^"\x27]*)["\x27]','i'))?.[1]??null;
}
function asset(src){
 const r=resource(src);
 if(!r)return null;
 assert.ok(fs.existsSync(r.full),'Broken local media reference '+src);
 if(!files.has(r.cleaned)){
  const b=fs.readFileSync(r.full),dim=imageSize(b),sha=sha1(b),isPhoto=/\.(?:jpe?g|webp|png|gif)(?:$)/i.test(r.cleaned)&&r.cleaned!=='/images/kakao-talk.jpg';
  const record=authorizedTourism.get(r.cleaned);
  if(record?.gitBlobSha)assert.equal(sha,record.gitBlobSha,'Verified tourism photo bytes changed '+r.cleaned);
  const originalPixels=record?.scene?.match(/원본\s*(\d+)\s*[×x]\s*(\d+)/);
  const originalWidth=originalPixels?Number(originalPixels[1]):null;
  const originalHeight=originalPixels?Number(originalPixels[2]):null;
  files.set(r.cleaned,{src:r.cleaned,bytes:b.length,gitBlobSha:sha,sha256:sha256(b),...dim,
   aspectRatio:dim.width&&dim.height?Number((dim.width/dim.height).toFixed(4)):null,
   role:r.cleaned.startsWith('/stay/assets/')?'UNVERIFIED_LEGACY_LODGING_REFERENCE':
    record?'SOURCED_TOURISM_NOT_HOTEL':r.cleaned==='/images/kakao-talk.jpg'?'UI_ICON':'OTHER_UNVERIFIED_MEDIA',
   author:record?.author??null,source:record?.source??null,license:record?.license??null,
   declaredOriginalWidth:originalWidth,declaredOriginalHeight:originalHeight,
   photo:isPhoto,
   risk:{
    smallForCard:isPhoto&&dim.width!==null&&(dim.width<720||dim.height<420),
    smallForLargeHero:isPhoto&&dim.width!==null&&(dim.width<1200||dim.height<500),
    unusualForLandscapeCard:isPhoto&&dim.width!==null&&(dim.width/dim.height<1.1||dim.width/dim.height>2.4),
    dimensionsUnparsed:isPhoto&&(dim.width===null||dim.height===null),
    largerThanDeclaredSourcePixels:isPhoto&&originalWidth!==null&&dim.width!==null&&(dim.width>originalWidth||dim.height>originalHeight)
   }});
 }
 return files.get(r.cleaned);
}
const pages=[];const counts=new Map();let imgCount=0,cssCount=0,legacyRefs=0;
for(const file of existing){
 const html=fs.readFileSync(file,'utf8');
 const slug=file==='site/stay/index.html'?'/stay/':'/stay/'+file.split('/')[2]+'/';
 assert.ok(html.includes("https://www.nipponferry.com"+slug),'Canonical URL missing '+file);
 assert.match(html,/<meta name=['"]robots['"] content=['"]index,follow/i,'Robots missing '+file);
 assert.match(html,/<h1\b/i,'H1 missing '+file);
 assert.doesNotMatch(html,/kids-stay\.com|kidsstay-v5\.vercel\.app/i,'KidsStay referral '+file);
 const images=[...html.matchAll(/<img\b[^>]*>/gi)].map(m=>{
  const src=attr(m[0],'src'),alt=attr(m[0],'alt');
  assert.ok(src&&alt!==null,'Image src/alt missing '+file);
  const a=asset(src);if(a)counts.set(a.src,(counts.get(a.src)||0)+1);
  return {src,alt,role:a?.role??'EXTERNAL',width:a?.width??null,height:a?.height??null};
 });
 const backgrounds=[...html.matchAll(/url\(\s*['"]?([^)'"]+)['"]?\s*\)/gi)].map(m=>{
  const src=m[1].trim(),a=asset(src);
  if(a)counts.set(a.src,(counts.get(a.src)||0)+1);
  return {src,role:a?.role??'EXTERNAL',width:a?.width??null,height:a?.height??null};
 });
 const refs=[...images,...backgrounds],legacy=refs.filter(x=>x.src.startsWith('/stay/assets/'));
 legacyRefs+=legacy.length;imgCount+=images.length;cssCount+=backgrounds.length;
 pages.push({page:slug,file,imgCount:images.length,cssBackgroundCount:backgrounds.length,
  legacyUnverifiedCount:legacy.length,images,cssBackgrounds:backgrounds,
  cardRule:html.match(/\.sv-card img\{[^}]+\}/)?.[0]??null,
  detailRule:html.match(/\.sv-img\{[^}]+\}/)?.[0]??null});
}
assert.equal(legacyRefs,143,'Main legacy reference baseline changed; refresh audit before proceeding');
assert.equal(old.declaredOriginalPhotoLicensesConfirmed,0,'V253 rights baseline changed');
for(const src of old.oldPhotoAssetPaths)assert.ok(files.has(src),'Legacy file no longer referenced '+src);
const groups=new Map();
for(const a of files.values())if(a.photo){
 const g=groups.get(a.sha256)||[];g.push(a.src);groups.set(a.sha256,g);
}
const duplicates=[...groups.entries()].filter(([,sources])=>sources.length>1)
 .map(([sha256,sources])=>({sha256,sources:sources.sort()})).sort((a,b)=>a.sha256.localeCompare(b.sha256));
const known=old.duplicateAssetGroup.paths.slice().sort();
assert.ok(duplicates.some(x=>JSON.stringify(x.sources)===JSON.stringify(known)),
 'Known Fuji/Hakone/Ryokan duplicate hash no longer matches baseline');
const heroCounts=new Map();
for(const p of pages){
 const html=fs.readFileSync(p.file,'utf8');
 const hero=html.match(/\.sv-hero:before\{[^}]+\}/)?.[0]??'';
 for(const m of hero.matchAll(/url\(\s*['\"]?([^)'\"]+)['\"]?\s*\)/gi)){
  const src=m[1].trim();heroCounts.set(src,(heroCounts.get(src)||0)+1);
 }
}
const assets=[...files.values()].sort((a,b)=>a.src.localeCompare(b.src)).map(a=>({
 ...a,references:counts.get(a.src)||0,heroUses:heroCounts.get(a.src)||0,
 risk:{...a.risk,smallForActualHero:(heroCounts.get(a.src)||0)>0&&a.risk.smallForLargeHero}
}));
const photos=assets.filter(a=>a.photo);
const report={
 stage:'V272',generatedAt:new Date().toISOString(),scope:'28 existing /stay/ HTML pages on main baseline',
 baselineCommit:'c17fec39626600b9b83c7890d8a0857ea19d661e',
 purpose:'Evidence-only duplicate SHA, native pixel dimensions, file bytes, aspect ratio, and HTML inline CSS image references.',
 thresholds:{cardNativeMinimum:'720x420 px heuristic',largeHeroNativeMinimum:'1200x500 px heuristic',
  landscapeCardAspect:'1.1 to 2.4 heuristic; object-fit cover may crop'},
 summary:{pages:pages.length,imgTags:imgCount,inlineCssUrlReferences:cssCount,
  legacyUnverifiedReferences:legacyRefs,uniqueMediaAssets:assets.length,uniquePhotoAssets:photos.length,
  duplicatedPhotoByteGroups:duplicates.length,smallForCard:photos.filter(a=>a.risk.smallForCard).length,
  smallForLargeHeroIfUsed:photos.filter(a=>a.risk.smallForLargeHero).length,
  smallForActualHero:photos.filter(a=>a.risk.smallForActualHero).length,
  largerThanDeclaredSourcePixels:photos.filter(a=>a.risk.largerThanDeclaredSourcePixels).length,
  unusualLandscapeRatio:photos.filter(a=>a.risk.unusualForLandscapeCard).length,
  unparsedPhotoDimensions:photos.filter(a=>a.risk.dimensionsUnparsed).length},
 duplicateSha256Groups:duplicates,assets,pages,
 limitations:['Git blob SHA and SHA-256 show byte identity, not copyright or scene identity.',
  'Tourism photos are NOT proof of a hotel or room; metadata is an existing registry claim, not fresh rights permission.',
  'Image size thresholds are review flags, not proof of a visually broken card.',
  'Declared source pixel dimensions are taken from existing V254 metadata, not freshly downloaded originals.',
  'CSS URL enumeration covers inline HTML; shared CSS computed display is audited separately in Chromium.',
  'Unmerged V258-V271 Draft PRs are not in main; compare before merge.',
  'This local audit is NOT authenticated Vercel Preview; deployment protection remains enforced.']
};
fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');
console.log('V272 STATIC AUDIT COMPLETE '+JSON.stringify(report.summary));
console.log('V272 duplicate groups '+JSON.stringify(duplicates));
console.log('V272 evidence artifact '+out+'; audit success does not clear image rights or Preview');
