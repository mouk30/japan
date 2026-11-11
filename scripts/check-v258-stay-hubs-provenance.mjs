import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
import assert from 'node:assert/strict';
const m=JSON.parse(fs.readFileSync('data/v258/stay-hub-photo-rights.json','utf8'));
assert.equal(m.version,'V258');
assert.equal(m.changes.length,2);
const pages=['site/stay/index.html',...fs.readdirSync('site/stay',{withFileTypes:true}).filter(x=>x.isDirectory()&&fs.existsSync('site/stay/'+x.name+'/index.html')).map(x=>'site/stay/'+x.name+'/index.html')];
assert.equal(pages.length,28,'New articles forbidden, stay collection is 28');
let verifiedCards=0,withheldCards=0;
for(const [slug,config] of Object.entries(m.cardMapping)){
 const file='site/stay/'+(slug?slug+'/':'')+'index.html';
 const html=fs.readFileSync(file,'utf8');
 const pathname=slug?'/stay/'+slug+'/':'/stay/';
 assert.equal((html.match(/class="sv-v258-credits"/g)||[]).length,1,'One source notice per hub '+file);
 assert.ok(html.includes("rel='canonical' href='https://www.nipponferry.com"+pathname+"'"),'Canonical changed '+file);
 assert.match(html,/<meta name='robots' content='index,follow,max-image-preview:large'>/,'Robots changed '+file);
 assert.ok(html.includes("숙소·객실 예약이 아닌 일본 국내 페리 항로 조회"),'Ferry/hotel CTA distinction '+file);
 assert.equal((html.match(/href='https:\/\/willer-travel\.com\/ko\/ferry\/'/g)||[]).length,1,'Ferry source link changed '+file);
 assert.ok(!html.includes('/stay/assets/'),'No unproven JPG may be rendered on either hub '+file);
 assert.ok(!/kids-stay\.com|kidsstay-v5\.vercel\.app/i.test(html),'KidsStay not authorized '+file);
 const actualCards=[...html.matchAll(/<a class='sv-card' href='([^']+)'>([\s\S]*?)<\/a>/g)];
 assert.deepEqual(actualCards.map(x=>x[1]),Object.keys(config),'Original card order/URLs changed '+file);
 assert.ok((html.match(/class='sv-v258-safe-visual'/g)||[]).length>=Object.values(config).filter(x=>!x).length,'Expected withheld photo not neutral');
 const labels=(html.match(/class='sv-v258-photo-type'/g)||[]).length;
 assert.equal(labels,actualCards.length,'Each card needs explicit photo status');
 const display=html.match(/\.sv-hero:before\{[^}]*\}/)?.[0]||'';
 assert.ok(display.includes('linear-gradient')&&!display.includes('/stay/assets/'),'Hero must have verified image or neutral background '+file);
 for(const card of actualCards){
  const key=config[card[1]],body=card[2];
  if(key){
   const p=m.images[key];
   assert.ok(p,'Missing source record '+key);
   assert.ok(body.includes(p.src),'Incorrect region photo '+card[1]);
   assert.ok(body.includes('지역 관광 실사 · 호텔 사진 아님'),'Tourism versus hotel claim '+key);
   assert.ok(body.includes(p.place),'Exact photographed place not in ALT '+key);
   assert.ok(html.includes(p.author)&&html.includes(p.license)&&html.includes(p.source)&&html.includes(p.licenseURL),'License not publicly attributed '+key);
   const src='site'+p.src;assert.ok(fs.existsSync(src),'Missing sourced image '+src);
   const bytes=fs.readFileSync(src);
   assert.equal(bytes.toString('ascii',0,4),'RIFF','WebP RIFF missing '+key);
   assert.equal(bytes.toString('ascii',8,12),'WEBP','WebP format missing '+key);
   const sha=crypto.createHash('sha1').update(Buffer.from('blob '+bytes.length+'\0')).update(bytes).digest('hex');
   assert.equal(sha,p.blob,'Image bytes were changed without revalidating copyright/source '+key);
   verifiedCards++;
  }else {
   assert.ok(body.includes("class='sv-v258-safe-visual'")&&body.includes('검증 전 사진 미게시'),'Unknown photo must not be displayed '+card[1]);
   withheldCards++;
  }
 }
}
const root=fs.readFileSync('site/stay/index.html','utf8');
assert.equal((root.match(/class='sv-v258-safe-visual large'/g)||[]).length,1,'Unlicensed Mt Fuji room image withheld');
assert.equal(verifiedCards,14);assert.equal(withheldCards,12);
assert.equal((root.match(/class='sv-card'/g)||[]).length,12);
const area=fs.readFileSync('site/stay/area/index.html','utf8');
assert.equal((area.match(/class='sv-card'/g)||[]).length,14);
console.log('V258 PASS: 28 existing pages, 26 original linked cards, 14 place-licensed location photos, 12 withheld photo placeholders, 1 withheld Fuji feature, 2 neutral heroes; source byte SHA and existing booking/canonical/robots preserved.');
