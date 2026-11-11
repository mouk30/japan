import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
const a=JSON.parse(fs.readFileSync('data/v253/stay-photo-audit.json','utf8'));
const dirs=fs.readdirSync('site/stay',{withFileTypes:true}).filter(x=>x.isDirectory()&&fs.existsSync(path.join('site/stay',x.name,'index.html'))).map(x=>x.name).sort();
const pages=['site/stay/index.html',...dirs.map(x=>path.join('site/stay',x,'index.html'))];
assert.equal(pages.length,28,'V253 has a locked 28-page scope; reconsider if pages were added');
assert.equal(a.existingStayPages,28);
assert.equal(a.findings.length,10);
const images=a.oldPhotoAssetPaths;
assert.equal(images.length,9);
let totalImageTags=0;
for(const file of pages){
 const html=fs.readFileSync(file,'utf8');
 const pathUrl='/'+path.dirname(file).replace(/^site\//,'')+'/';
 assert.match(html,/<meta name=['"]robots['"] content=['"]index,follow/i);
 assert.ok(html.includes('https://www.nipponferry.com'+pathUrl),'missing canonical destination '+file);
 assert.equal(html.split('class="nf-v253-photo-notice"').length-1,1,'missing or double photo notice '+file);
 assert.equal(html.split('id="nf-v253-image-audit-style"').length-1,1,'missing responsive audit style '+file);
 assert.ok(html.includes('해당 도시의 실제 호텔·객실을 촬영했다는 증빙이 없습니다'),'missing source uncertainty '+file);
 assert.ok(!/kids-stay\.com|kidsstay-v5\.vercel\.app/i.test(html),'Unverified KidsStay referral '+file);
 for(const m of html.matchAll(/<img\b[^>]*>/g)){
  const tag=m[0],img=tag.match(/\bsrc=['"](\/stay\/assets\/[^'"]+)['"]/);
  if(img){
   assert.ok(images.includes(img[1]),'Unknown source photo: '+img[1]);
   assert.ok(/alt=['"][^'"]*참고 이미지/.test(tag),'Original hotel photo presented as verified real '+file+' '+tag);
   totalImageTags++;
  }
 }
}
// V254 follow-up deliberately removes 10 unverified hotel.jpg card photos from five regions.
assert.ok(totalImageTags>=90,'Unexpected loss of audited legacy image references');
for(const slug of ['kagoshima','okinawa','nagoya','sendai','hiroshima']){
 const html=fs.readFileSync('site/stay/'+slug+'/index.html','utf8');
 assert.ok(!html.includes('/stay/assets/hotel.jpg'),'Unverified hotel photo still published '+slug);
}
const shaGroups=new Map();
const sizeRows=[];
function imageSize(buf){
 assert.equal(buf.readUInt16BE(0),0xffd8,'Not JPEG');
 let p=2;
 while(p+8<buf.length){
  if(buf[p]!==0xff){p++;continue}
  let marker=buf[p+1];p+=2;
  if(marker===0x00||marker===0x01||marker===0xd8||marker===0xd9||(marker>=0xd0&&marker<=0xd7))continue;
  if(p+2>buf.length)break;
  const len=buf.readUInt16BE(p);
  if(len<2||p+len>buf.length)throw Error('Corrupted JPEG marker length');
  if([0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf].includes(marker))
   return {width:buf.readUInt16BE(p+5),height:buf.readUInt16BE(p+3)};
  p+=len;
 }
 throw new Error('JPEG dimensions unavailable');
}
for(const img of images){
 const p='site'+img;
 assert.ok(fs.existsSync(p),'Missing referenced JPEG '+img);
 const data=fs.readFileSync(p);
 const hash=crypto.createHash('sha1').update(Buffer.from('blob '+data.length+'\0')).update(data).digest('hex');
 const dimensions=imageSize(data);
 assert.ok(dimensions.width>0&&dimensions.height>0,'bad JPEG size');
 const list=shaGroups.get(hash)||[];list.push(img);shaGroups.set(hash,list);
 sizeRows.push({asset:img,bytes:data.length,nativePixels:dimensions,gitBlobSha:hash});
}
assert.equal(shaGroups.size,7);
const duplicates=[...shaGroups.entries()].filter(([,p])=>p.length>1);
assert.equal(duplicates.length,1);
assert.equal(duplicates[0][0],a.duplicateAssetGroup.sha);
assert.deepEqual(duplicates[0][1].slice().sort(),a.duplicateAssetGroup.paths.slice().sort());
const small=sizeRows.filter(x=>x.nativePixels.width<1200||x.nativePixels.height<675);
const source=JSON.parse(fs.readFileSync(a.verifiedPlacePhotoReused.sourceMetadata,'utf8'));
assert.equal(source.photographer,'Lawsonstu');assert.equal(source.license,'CC0-1.0');
const h=fs.readFileSync('site/stay/hokkaido/index.html','utf8');
assert.ok(h.includes(a.verifiedPlacePhotoReused.src));
assert.ok(h.includes('노보리베쓰 온천 지역의 2015년 실제 지열 지형 사진'));
assert.ok(h.includes('commons.wikimedia.org/wiki/File:Noboribetsu_Onsen_hot_spring.jpg'));
assert.ok(h.includes('지열 지형 사진이며 숙박시설 객실 사진은 아닙니다'));
assert.ok(fs.existsSync('site'+a.verifiedPlacePhotoReused.src));
for(const item of a.findings)assert.ok(fs.existsSync('site'+item.page+'index.html'),'Missing risk page '+item.page);
console.log('V253 ACTUAL JPG IMAGE DATA '+JSON.stringify({files:sizeRows.length,distinctBlobSha:shaGroups.size,duplicates:duplicates.map(([,x])=>x),nativeBelow1200x675:small.map(x=>x.asset),nativeDimensions:sizeRows}));
console.log('V253 PASS: 28 pages, '+totalImageTags+' image alt corrections, explicit provenance notice, one Noboribetsu CC0 real-region photo, other photos NOT certified.');
