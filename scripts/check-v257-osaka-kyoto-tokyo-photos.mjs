import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
const m=JSON.parse(fs.readFileSync('data/v257/stay-osaka-kyoto-tokyo-photo-rights.json','utf8'));
assert.equal(m.version,'V257');
const slugs=['osaka','kyoto','tokyo'];
assert.deepEqual(Object.keys(m.cityPhotos).sort(),slugs.slice().sort());
const existing=['site/stay/index.html',...fs.readdirSync('site/stay',{withFileTypes:true}).filter(x=>x.isDirectory()&&fs.existsSync('site/stay/'+x.name+'/index.html')).map(x=>'site/stay/'+x.name+'/index.html')];
assert.equal(existing.length,28,'The previously existing 28 stay articles must not grow or disappear');
for(const slug of slugs){
 const city=m.cityPhotos[slug],h=fs.readFileSync('site/stay/'+slug+'/index.html','utf8');
 assert.equal((h.match(/class="nf-v257-photo-provenance"/g)||[]).length,1,'Missing credits block '+slug);
 assert.equal((h.match(/class='sv-v257-photo-hold'/g)||[]).length,slug==='tokyo'?0:2,'Unverified card hidden '+slug);
 assert.equal((h.match(/<a class='sv-card'/g)||[]).length,3,'Stay regions changed '+slug);
 assert.equal((h.match(/<img class='sv-img'/g)||[]).length,1,'Hero main image changed '+slug);
 assert.ok(h.includes("https://www.nipponferry.com/stay/"+slug+"/"),'Canonical altered '+slug);
 assert.match(h,/<meta name='robots' content='index,follow,max-image-preview:large'>/,'Robots altered '+slug);
 assert.ok(!/\/stay\/assets\/[^'") >]+/.test(h),'Unverified location/photo still displayed '+slug);
 assert.ok(!/kids-stay\.com|kidsstay-v5\.vercel\.app/i.test(h),'Unauthorized KidsStay link '+slug);
 assert.ok(h.includes('실제 객실 사진·예약 시스템은 검증 전'),'Photo wrongly marketed as real hotel '+slug);
 for(const area of city.headings)assert.ok(h.includes('<h3>'+area+'</h3>'),'Original card removed '+slug+' '+area);
 for(const [key,p] of Object.entries(city.images)){
  const path='site'+p.src;assert.ok(fs.existsSync(path),'Image file missing '+path);
  const b=fs.readFileSync(path);assert.equal(b.toString('ascii',0,4),'RIFF','Not WebP RIFF '+slug+' '+key);
  assert.equal(b.toString('ascii',8,12),'WEBP','Not WebP '+slug+' '+key);
  const sha=crypto.createHash('sha1').update(Buffer.from('blob '+b.length+'\0')).update(b).digest('hex');
  assert.equal(sha,p.blob,'Image changed without provenance '+slug+' '+key);
  assert.ok(h.includes(p.src),'Image unused '+slug+' '+key);
  assert.ok(h.includes(p.source)&&h.includes(p.license_url)&&h.includes(p.author),'Original author or usage license missing '+slug+' '+key);
  assert.ok(h.includes(p.shot)&&h.includes(p.place),'Date/place missing '+slug+' '+key);
 }
 assert.ok(h.match(/\.sv-hero:before\{[^}]*\}/)[0].includes(city.images[city.primary].src),'City hero wrong '+slug);
}
console.log('PASS V257: 28 existing pages, licensed photo blobs 5, 4 unverified cards held, original city/card places, canonical/robots/KidsStay boundaries.');
