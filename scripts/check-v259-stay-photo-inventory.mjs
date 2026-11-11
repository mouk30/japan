/**
 * V259: evidence-only inventory against V254 main (the unmerged PRs are intentionally
 * not counted as live changes). This is not an independent copyright authorization.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const evidencePath='audit-reports/v259-stay-photo-provenance-evidence.json';
const outPath='audit-reports/v259-stay-photo-inventory.generated.json';
const e=JSON.parse(fs.readFileSync(evidencePath,'utf8'));
const v253=JSON.parse(fs.readFileSync('data/v253/stay-photo-audit.json','utf8'));
const v254=JSON.parse(fs.readFileSync('data/v254/stay-verified-region-photos.json','utf8'));
assert.equal(e.stage,'V259');
assert.equal(e.refCommit,'c17fec39626600b9b83c7890d8a0857ea19d661e');
assert.equal(e.pages.length,28);
const dirs=['site/stay/index.html',...fs.readdirSync('site/stay',{withFileTypes:true}).filter(x=>x.isDirectory()&&fs.existsSync('site/stay/'+x.name+'/index.html')).map(x=>'site/stay/'+x.name+'/index.html')];
assert.equal(dirs.length,28,'Do not add/remove existing stay pages');
const repoPaths=dirs.slice().sort(),expectedPaths=e.pages.map(x=>x.file).sort();
assert.deepEqual(repoPaths,expectedPaths);
const knownRegionSources=new Map(Object.values(v254.images).map(v=>[v.src,{
  status:'declared_original_source_in_v254',photographer:v.author,location:v.scene,source:v.source,license:v.license,licenseURL:v.licenseURL,gitBlobSha:v.gitBlobSha,
}]));
knownRegionSources.set(v253.verifiedPlacePhotoReused.src,{
  status:'declared_original_source_in_v253',photographer:v253.verifiedPlacePhotoReused.photographer,
  location:v253.verifiedPlacePhotoReused.location,source:v253.verifiedPlacePhotoReused.sourcePage,license:v253.verifiedPlacePhotoReused.license,
  metadata:v253.verifiedPlacePhotoReused.sourceMetadata,
});
function blobSha(buffer){return crypto.createHash('sha1').update(Buffer.from('blob '+buffer.length+'\0')).update(buffer).digest('hex')}
function safeSrc(src){const clean=src.split(/[?#]/)[0];if(!clean.startsWith('/')||clean.startsWith('//'))return null;const p=path.resolve('site','.'+clean);return p.startsWith(path.resolve('site')+path.sep)?p:null}
function typeOf(src) {
 if(src.startsWith('/stay/assets/'))return {status:'ORIGINAL_AUTHOR_LICENSE_LOCATION_UNVERIFIED',referenceType:'legacy_stay_JPG',copyrightVerified:false};
 if(src==='/images/kakao-talk.jpg')return {status:'UI_ICON_NOT_LODGING_PHOTO',referenceType:'ui_icon'};
 if(knownRegionSources.has(src))return {referenceType:'tourism_photograph_not_hotel_room',...knownRegionSources.get(src)};
 return {status:'EXACT_PHOTO_RIGHTS_NOT_VALIDATED_IN_V259',referenceType:'other_image'};
}
function attr(tag,key){return tag.match(new RegExp('\\b'+key+'\\s*=\\s*["\\x27]([^"\\x27]*)["\\x27]','i'))?.[1]??null}
const results=[],histogram=new Map();let allLegacy=0,totalImages=0,totalCssImages=0;
for(const row of e.pages) {
 const bytes=fs.readFileSync(row.file);const html=bytes.toString('utf8');
 assert.equal(blobSha(bytes),row.gitBlobSha,'Baseline main HTML file differs, re-run inventory with new base: '+row.file);
 assert.ok(html.includes("rel='canonical' href='https://www.nipponferry.com"+row.page+"'"),'Canonical changed');
 assert.match(html,/<meta name=['"]robots['"] content=['"]index,follow/i,'Robots changed');
 assert.match(html,/<h1\b/i,'Heading missing');
 assert.ok(!/kids-stay\.com|kidsstay-v5\.vercel\.app/i.test(html),'No KidsStay live booking referral');
 const imageTags=[...html.matchAll(/<img\b[^>]*>/gi)].map(m=>{
  const src=attr(m[0],'src'),alt=attr(m[0],'alt'),loading=attr(m[0],'loading');
  assert.ok(src,'Image missing src '+row.file);
  const resource=safeSrc(src);
  if(resource)assert.ok(fs.existsSync(resource),'Broken referenced image '+src+' '+row.file);
  const details=typeOf(src);
  if(src.startsWith('/stay/assets/')) {
   assert.ok((alt||'').includes('참고 이미지'),'Legacy image not correctly identified as reference '+row.file+' '+src);
  }
  return {src,alt,loading,photoAssessment:details};
 });
 const cssUrl=[...html.matchAll(/url\(\s*['"]?([^)'"]+)['"]?\s*\)/gi)].map(m=>({
  src:m[1],photoAssessment:typeOf(m[1])
 }));
 const all=[...imageTags.map(x=>x.src),...cssUrl.map(x=>x.src)];
 const legacy=all.filter(src=>src.startsWith('/stay/assets/'));
 assert.equal(legacy.length,row.unverifiedLegacyReferences,'Legacy image count changed at '+row.file);
 assert.deepEqual([...new Set(legacy)].sort(),row.legacyPhotoPaths.slice().sort(),'Legacy image sources differ at '+row.file);
 for(const src of legacy)histogram.set(src,(histogram.get(src)||0)+1);
 allLegacy+=legacy.length;totalImages+=imageTags.length;totalCssImages+=cssUrl.length;
 results.push({page:row.page,file:row.file,gitBlobSha:row.gitBlobSha,legacyCount:legacy.length,
 imageTags,cssImageReferences:cssUrl,legacyUniquePaths:[...new Set(legacy)],licensingStatusOfLegacy:'UNVERIFIED',sourceAssessment:'Sources labelled by earlier V253/V254 manifest only; not a hotel/room authorization'});
}
assert.equal(allLegacy,143);
assert.equal(histogram.size,9);
assert.deepEqual([...histogram.keys()].sort(),v253.oldPhotoAssetPaths.slice().sort());
const shaBlobs=new Map();
for(const src of v253.oldPhotoAssetPaths) {
 const b=fs.readFileSync('site'+src),hash=blobSha(b),arr=shaBlobs.get(hash)||[];
 arr.push(src);shaBlobs.set(hash,arr);
}
assert.equal(shaBlobs.size,7);
assert.deepEqual([...shaBlobs.values()].filter(x=>x.length>1)[0].slice().sort(),e.rights.duplicateImageGroup.slice().sort());
const output={
 stage:'V259',baselineCommit:e.refCommit,auditedPages:results.length,
 summary:{imageTagCount:totalImages,cssUrlReferenceCount:totalCssImages,
 legacyPhotoRefs:allLegacy,legacyUniquePaths:histogram.size,distinctLegacyGitBlobs:shaBlobs.size,
 originalLegacyImageRightsConfirmed:0,
 legacyRefsByPath:Object.fromEntries([...histogram].sort((a,b)=>a[0].localeCompare(b[0]))),
 duplicateOriginalPhotoHashes:[...shaBlobs.entries()].filter(([,arr])=>arr.length>1).map(([sha,paths])=>({sha,paths})),
 photographedHotelRoomsCertified:0,
 },
 claims:'This is only an HTML/CSS inventory as of the baseline commit, not copyright clearance, human image-place verification, actual browser display, or live Vercel preview proof.',
 pages:results
};
fs.writeFileSync(outPath,JSON.stringify(output,null,2)+'\n');
console.log('V259 PASS '+JSON.stringify(output.summary)+'; full per-page inventory artifact generated: '+outPath);
