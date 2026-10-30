import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
const registry=JSON.parse(fs.readFileSync('data/v254/stay-verified-region-photos.json','utf8'));
assert.equal(registry.version,'V254');
const pages=Object.keys(registry.pages), assets=Object.values(registry.images);
assert.deepEqual(pages.sort(),['hiroshima','kagoshima','nagoya','okinawa','sendai'].sort());
assert.equal(assets.length,8);
for(const a of assets){
  assert.ok(/^https:\/\/commons\.wikimedia\.org\/wiki\/File:/.test(a.source),'not a source file page');
  assert.ok(/^https:\/\/creativecommons\.org\//.test(a.licenseURL),'license URL required');
  assert.ok(a.author&&a.label&&a.gitBlobSha&&a.scene,'missing original photo evidence');
  const filepath='site'+a.src;
  assert.ok(fs.existsSync(filepath),'Missing real photo '+filepath);
  const data=fs.readFileSync(filepath);
  assert.ok(data.length>10000,'Invalid/tiny photo '+filepath);
  assert.equal(data.toString('ascii',0,4),'RIFF','Not RIFF WebP '+filepath);
  assert.equal(data.toString('ascii',8,12),'WEBP','Not WebP '+filepath);
  const sha=crypto.createHash('sha1').update(Buffer.from('blob '+data.length+'\0')).update(data).digest('hex');
  assert.equal(sha,a.gitBlobSha,'Image content changed without source review '+filepath);
}
for(const slug of pages){
 const p='site/stay/'+slug+'/index.html', html=fs.readFileSync(p,'utf8'), config=registry.pages[slug];
 assert.ok(html.includes('https://www.nipponferry.com/stay/'+slug+'/'),'Missing canonical '+slug);
 assert.ok(/<meta name=['"]robots['"] content=['"]index,follow/.test(html),'Missing robots '+slug);
 assert.equal((html.match(/class="nf-v253-photo-notice"/g)||[]).length,1);
 assert.equal((html.match(/nf-v254-verified-photo-credit/g)||[]).length,1);
 assert.ok(!/kids-stay\.com|kidsstay-v5\.vercel\.app/i.test(html),'Unapproved KidsStay reference');
 assert.ok(!/\/stay\/assets\/(?:fuji|fukuoka|tokyo|kyoto|ryokan)\.jpg/.test(html),'Known wrong-city image '+slug);
 assert.ok(html.includes('호텔·객실'),'Missing distinction between tourism and real hotel photo');
 assert.ok(!html.includes('해당 사진은 호텔 객실 실사입니다'),'Invalid accommodation certification');
 for(const key of config.photoKeys){
  const asset=registry.images[key];
  assert.ok(html.includes(asset.src),'Missing photo '+slug+' '+key);
  assert.ok(html.includes(asset.source),'Missing creator/source credit '+slug+' '+key);
  assert.ok(html.includes(asset.licenseURL),'Missing license credit '+slug+' '+key);
  const escaped=asset.src.replace(/[.*+?^$\{\}()|[\]\\]/g,'\\$&');
  assert.ok(new RegExp(escaped).test(html),'Image not attached');
 }
 const hero=html.match(/\.sv-hero:before\{[^}]*\}/)?.[0]??'';
 if(config.hero)assert.ok(hero.includes(registry.images[config.hero].src),'Hero location mismatch '+slug);
 else assert.ok(hero.includes('linear-gradient')&&!hero.includes('url('),'Low-res/outer-city hero must use neutral background '+slug);
 assert.ok(html.includes(registry.images[config.main].src),'Main image geography '+slug);
}
console.log('V254 VERIFIED-LOCAL-PHOTO QA PASS: '+pages.length+' stay pages, '+assets.length+' credited local photo assets; original bytes unchanged; incorrect-city imagery not presented.');
