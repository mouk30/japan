import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
const manifest=JSON.parse(fs.readFileSync('audit-reports/v281/photo-first-yokohama-pilot.json','utf8'));
const h=fs.readFileSync('site'+manifest.baseline.url+'index.html','utf8');
const css=fs.readFileSync('site/v281-magazine.css','utf8');
assert.equal(manifest.version,'V281');
assert.equal((h.match(/<h1\b/gi)||[]).length,1,'Keep one H1');
assert.equal((h.match(/class="nf-v281-card"/g)||[]).length,3,'Three large travel cards');
assert.equal((h.match(/class="nf-v281-disclosure"/g)||[]).length,2,'All original safety and 30s sections available');
assert.equal((h.match(/id="nf-v281-stop-/g)||[]).length,3,'Every top card links to original guide');
assert.equal((h.match(/class="nf-v281-safety-strip"/g)||[]).length,1,'Short safety note must remain visible');
assert.equal((h.match(/class="nf-v281-hero-copy"/g)||[]).length,1,'Hero copy absent');
assert.match(h,/class="nf-v281-magazine"/,'Design scoped to page');
assert.match(h,/href="\/v281-magazine\.css\?v=20261101"/,'Missing scoped styles');
assert.ok(css.includes('aspect-ratio:4/3')&&css.includes('max-width:620px')&&css.includes('prefers-reduced-motion'),'Responsive, image crops or reduced motion missing');
const b=manifest.baseline;
assert.ok(h.includes('<title>'+b.title+'</title>'),'SEO title modified');
assert.ok(h.includes('name="description" content="'+b.description+'"'),'Meta description modified');
assert.ok(h.includes('rel="canonical" href="'+b.canonical+'"'),'Canonical changed');
assert.ok(h.includes('content="index,follow,max-image-preview:large"'),'Robots changed');
assert.ok(h.includes('property="og:url" content="'+b.canonical+'"'),'OG changed');
const jsonLd=[...h.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)];
assert.ok(jsonLd.length>0,'Original Article/Breadcrumb schema removed');
const structured=jsonLd.flatMap(x=>{const z=JSON.parse(x[1]);return Array.isArray(z)?z:[z]});
assert.ok(structured.some(x=>x['@type']==='Article'&&x.mainEntityOfPage===b.canonical),'Original structured article removed');
assert.ok(structured.some(x=>x['@type']==='BreadcrumbList'),'Breadcrumb schema removed');
const ids=new Set([...h.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]));
for(const c of manifest.cards){
 assert.ok(ids.has(c.id),'Target card missing '+c.id);
 assert.ok(h.includes('href="#'+c.id+'"'),'Top photo card broken '+c.id);
 assert.ok(h.includes('href="'+c.original+'"'),'Wikimedia source link lost '+c.original);
 assert.ok(h.includes('href="'+c.licenseUrl+'"')||h.includes("href='"+c.licenseUrl+"'"),'License URL lost '+c.licenseUrl);
 assert.ok(h.includes(c.author),'Source credited creator missing '+c.author);
 const p='site'+c.src;assert.ok(fs.existsSync(p),'Original photo file missing');
 const buffer=fs.readFileSync(p);
 assert.equal(buffer.toString('ascii',0,4),'RIFF');
 assert.equal(buffer.toString('ascii',8,12),'WEBP');
 const sha=crypto.createHash('sha1').update(Buffer.from('blob '+buffer.length+'\0')).update(buffer).digest('hex');
 assert.equal(sha,c.sha,'Original licensed photo blob unexpectedly replaced '+c.name);
 assert.ok(h.includes('<img src="'+c.src+'"')||h.includes('<img class="'), 'Image absent from original guide');
}
for(const id of ['v80-verification','nf-intent-summary','ct-experience-booking','ct-topic-dashboard','route','hours','photo','history','checks','nf-v148-photo-credits']){
 assert.ok(ids.has(id),'Lost original content anchor '+id)
}
for(const token of ['오산바시','신코','다이코쿠','최종 승객 귀선 마감','실시간 확인된 정보가 아닙니다','날짜별 재고','https://yokohama-air-cabin.jp/','https://cosmoworld.jp/']){
 assert.ok(h.includes(token),'Booking/safety information accidentally removed '+token);
}
for(const link of [...h.matchAll(/\bhref="#([^"]+)"/g)]){
 assert.ok(ids.has(link[1]),'Broken hash jump #'+link[1]);
}
assert.equal((h.match(/<img\b/g)||[]).length,7,'Lost original photo or invented extra sources');
assert.equal((h.match(/<section id="v80-verification"/g)||[]).length,1);
assert.equal((h.match(/<section id="nf-intent-summary"/g)||[]).length,1);
assert.ok(!h.includes('kids-stay.com')&&!h.includes('kidsstay-v5.vercel.app'));
console.log('V281 STATIC PASS: original SEO+JSON-LD, source image SHA/CC credits, 3 visual jump cards, existing 3 safety chapters, official booking links, all hash targets.');
