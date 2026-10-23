#!/usr/bin/env node
'use strict';
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const {compactPhotoAttribution}=require('./v139_photo_credits.cjs');
const cases=[
 'index.html',
 'things-to-do/cruise-ports/index.html',
 'things-to-do/index.html',
 'japan/index.html',
 'guide/busan-fukuoka-ferry/index.html',
 'guide/busan-osaka-ferry/index.html',
 'guide/busan-shimonoseki-ferry/index.html',
];
const errors=[],pages=[];
const exact=(s,rx)=>s.match(rx)?.[0]||null;
for(const name of cases){
 const beforePath=path.join(root,'site',name),afterPath=path.join(root,'dist',name);
 if(!fs.existsSync(beforePath)||!fs.existsSync(afterPath)){errors.push(name+': missing source or build');continue}
 const source=fs.readFileSync(beforePath,'utf8'),built=fs.readFileSync(afterPath,'utf8');
 const check=compactPhotoAttribution(source);
 const panelCount=(built.match(/<details class="nf-photo-credits-panel"/g)||[]).length;
 const originalCount=(source.match(/<(?:p|figcaption|div|a|small)\b[^>]*\bclass="[^"]*(?:nf-v\d+-credit|nf\d+-credit|photo-credit|nf84-home__meta|v65-note)[^"]*"/gi)||[]).length;
 const sourceImageCount=(source.match(/<img\b/gi)||[]).length;
 const buildImageCount=(built.match(/<img\b/gi)||[]).length;
 const sourceSourceLinks=(source.match(/href="https:\/\/(?:commons\.wikimedia\.org|creativecommons\.org)[^"]*"/gi)||[]).length;
 const builtSourceLinks=(built.match(/href="https:\/\/(?:commons\.wikimedia\.org|creativecommons\.org)[^"]*"/gi)||[]).length;
 for(const [key,regex] of [['title',/<title>[^<]*<\/title>/],['canonical',/<link rel="canonical"[^>]*>/],['meta description',/<meta name="description"[^>]*>/]]){
  if(exact(source,regex)!==exact(built,regex))errors.push(name+': SEO '+key+' changed');
 }
 if(buildImageCount<sourceImageCount)errors.push(name+': image tags removed during build');
 if(sourceSourceLinks!==builtSourceLinks)errors.push(name+': CC/source hyperlink count changed');
 if(originalCount>0&&!panelCount)errors.push(name+': expected compact attribution details missing');
 if(panelCount>1)errors.push(name+': duplicated global attribution panel');
 if(panelCount>0&&!built.includes('/nf-v139-photo-credits.css'))errors.push(name+': attribution stylesheet missing');
 if(panelCount>0&&(!built.includes('<summary>사진 출처·저작권</summary>')||built.indexOf('nf-photo-credits-panel')>built.indexOf('<footer')))errors.push(name+': inaccessible or misplaced disclosure');
 if(name==='index.html'){
  if(/<p class="nf84-home__meta"/.test(built))errors.push('home: long image caption remains visible');
  if(/<p class="nf-v79-photo-credit"/.test(built))errors.push('home: maritime photo credit remains visible');
  if(!built.includes('Kristoffer Trolle')||!built.includes('creativecommons.org/licenses/by/2.0/'))errors.push('home: missing photographer/license');
 }
 pages.push({page:name,original_candidates:originalCount,compiled_credits:check.credits,panelCount,links_preserved:sourceSourceLinks,imageCount:sourceImageCount});
}
const synthetic='<html><head><title>Example</title></head><body><p class="nf-v135-photo-credit">선박 사진 · 촬영자 Alice · <a href="https://commons.wikimedia.org/wiki/File:Boat.jpg">원본</a> · <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></p><p class="nf89-review__meta">수속 마감 확인 필요</p><footer>FOOTER</footer></body></html>';
const once=compactPhotoAttribution(synthetic),twice=compactPhotoAttribution(once.html);
if(once.credits!==1||twice.credits!==0||twice.html!==once.html)errors.push('transform not idempotent');
if(!once.html.includes('수속 마감 확인 필요'))errors.push('operational info incorrectly moved');
if(!once.html.includes('Alice')||!once.html.includes('creativecommons.org'))errors.push('photographic rights data missing');
const report={version:'V139',generated_at:new Date().toISOString(),passed:errors.length===0,pages,errors,principles:['SEO unchanged','image tags preserved','original photographer/license/source links preserved','real-world operation information kept visible','photos free of long attribution banners']};
fs.mkdirSync(path.join(root,'audit-reports/v139'),{recursive:true});
fs.writeFileSync(path.join(root,'audit-reports/v139/report.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({passed:report.passed,pages,errors},null,2));
if(errors.length)process.exitCode=1;
