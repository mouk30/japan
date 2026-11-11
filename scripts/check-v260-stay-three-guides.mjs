import assert from 'node:assert/strict';
import fs from 'node:fs';
const cases=[
 {slug:'family',h1:'일본 가족여행 숙소 추천 | 가족호텔·온천·료칸 선택 가이드',cards:['/stay/hotel/','/stay/ryokan/','/stay/fuji/'],booking:'/booking/family/'},
 {slug:'couple',h1:'일본 커플 숙소 추천 | 료칸·온천·야경 좋은 호텔',cards:['/stay/tokyo/','/stay/ryokan/','/stay/fuji/'],booking:'/booking/couple/'},
 {slug:'first-trip',h1:'첫 일본여행 숙소 추천 | 어디에 묵어야 편할까?',cards:['/stay/fukuoka/','/stay/osaka/','/stay/tokyo/'],booking:'/booking/first-timer/'}
];
const sitemap=fs.readFileSync('site/sitemap.xml','utf8');
const robots=fs.readFileSync('site/robots.txt','utf8');
assert.match(robots,/Sitemap:\s*https:\/\/www\.nipponferry\.com\/sitemap\.xml/);
for(const item of cases){
 const file='site/stay/'+item.slug+'/index.html',html=fs.readFileSync(file,'utf8'),url='/stay/'+item.slug+'/';
 assert.equal(html.match(/<h1>([^<]+)<\/h1>/)?.[1],item.h1,'H1 changed: '+file);
 assert.match(html,/<title>[^<]{20,}<\/title>/,'title missing: '+file);
 assert.match(html,/<meta name=['"]description['"] content=['"][^'"]{30,}['"]/,'description missing: '+file);
 assert.ok(html.includes("rel='canonical' href='https://www.nipponferry.com"+url+"'"),'canonical changed: '+file);
 assert.match(html,/<meta name=['"]robots['"] content=['"]index,follow/,'robots changed: '+file);
 assert.ok(sitemap.includes('<loc>https://www.nipponferry.com'+url+'</loc>'),'sitemap missing: '+file);
 assert.doesNotMatch(html,/\/stay\/assets\//,'unverified hotel photo still referenced: '+file);
 assert.equal((html.match(/role='img' aria-label='숙박 예시 사진 게시 보류/g)||[]).length,4,'4 image positions must be withheld: '+file);
 assert.equal((html.match(/class='sv-photo-hold sv-photo-hold--card'/g)||[]).length,3,'3 cards must have neutral image panels: '+file);
 assert.equal((html.match(/class='sv-img sv-photo-hold sv-photo-hold--feature'/g)||[]).length,1,'main guide image must be withheld: '+file);
 assert.equal((html.match(/id="nf-v260-photo-hold-style"/g)||[]).length,1,'V260 CSS missing: '+file);
 assert.equal((html.match(/class="nf-v253-photo-notice"/g)||[]).length,1,'original notice missing: '+file);
 assert.ok(html.includes('원본 저작자·촬영 장소·사용 허가가 확인되지 않아 게시를 보류했습니다'),'truthful notice missing: '+file);
 const hero=html.match(/\.sv-hero:before\{[^}]+\}/)?.[0]||'';
 assert.ok(hero.includes('linear-gradient')&&!hero.includes('url('),'unverified hero image: '+file);
 const cards=[...html.matchAll(/<a class='sv-card' href='([^']+)'/g)].map(m=>m[1]);
 assert.deepEqual(cards,item.cards,'card destinations changed: '+file);
 assert.ok(html.includes("href='"+item.booking+"'"),'original booking guide changed: '+file);
 assert.ok(html.includes('https://willer-travel.com/ko/ferry/'),'ferry CTA removed: '+file);
 assert.ok(html.includes('숙소·객실 예약이 아닌 일본 국내 페리 항로 조회'),'ferry/room booking distinction lost: '+file);
 assert.doesNotMatch(html,/kidsstay-v5\.vercel\.app|kids-stay\.com/i,'unverified KidsStay referral: '+file);
 assert.ok(html.includes('src="/images/kakao-talk.jpg"'),'existing Kakao contact missing: '+file);
 console.log('V260 PASS '+url+' | 5 unverified photos withheld (4 img + 1 CSS), 3 card links and SEO/CTA preserved');
}
const paths=fs.readdirSync('site/stay',{withFileTypes:true}).filter(x=>x.isDirectory()&&fs.existsSync('site/stay/'+x.name+'/index.html'));
assert.equal(paths.length+1,28,'existing stay page count must remain 28');
console.log('V260 STATIC PASS: 3 existing guides, 15 unverified photo placements withheld; 28-page scope unchanged. No license or deployed-preview claim.');
