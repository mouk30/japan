import assert from 'node:assert/strict';
import fs from 'node:fs';
const cases=[
 {slug:'hotel',h1:'일본 호텔 추천 | 도시별 숙소 위치 선택 가이드',cards:['/stay/tokyo/','/stay/osaka/','/stay/fukuoka/']},
 {slug:'ryokan',h1:'일본 료칸 추천 | 온천·가이세키·전통숙박 가이드',cards:['/stay/hakone/','/stay/kyoto/','/stay/fuji/']}
];
const sitemap=fs.readFileSync('site/sitemap.xml','utf8');
const robots=fs.readFileSync('site/robots.txt','utf8');
assert.match(robots,/Sitemap:\s*https:\/\/www\.nipponferry\.com\/sitemap\.xml/);
const report=JSON.parse(fs.readFileSync('audit-reports/v261-stay-hotel-ryokan-photo-hold.json','utf8'));
assert.equal(report.pages.length,2);
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
 assert.equal((html.match(/id="nf-v261-photo-hold-style"/g)||[]).length,1,'V261 CSS missing: '+file);
 assert.ok(html.includes('이 페이지의 숙박 예시 사진 4곳과 상단 배경 사진 1곳은 원본 저작자'),'truthful notice missing: '+file);
 const hero=html.match(/\.sv-hero:before\{[^}]+\}/)?.[0]||'';
 assert.ok(hero.includes('linear-gradient')&&!hero.includes('url('),'unverified hero image: '+file);
 const cards=[...html.matchAll(/<a class='sv-card' href='([^']+)'/g)].map(m=>m[1]);
 assert.deepEqual(cards,item.cards,'card destinations changed: '+file);
 assert.ok(html.includes("href='/booking/japan-cruise/'"),'original booking guide changed: '+file);
 assert.ok(html.includes('https://willer-travel.com/ko/ferry/'),'ferry CTA removed: '+file);
 assert.ok(html.includes('숙소·객실 예약이 아닌 일본 국내 페리 항로 조회'),'ferry/room booking distinction lost: '+file);
 assert.doesNotMatch(html,/kidsstay-v5\.vercel\.app|kids-stay\.com/i,'unverified KidsStay referral: '+file);
 assert.ok(html.includes('src="/images/kakao-talk.jpg"'),'existing Kakao contact missing: '+file);
 const e=report.pages.find(p=>p.path===file);
 assert.ok(e&&e.withheldImgPositions===4&&e.withheldCssHeroPositions===1,'audit evidence missing: '+file);
 console.log('V261 PASS '+url+' | 5 unverified photos withheld; card links and SEO/CTA preserved');
}
const paths=fs.readdirSync('site/stay',{withFileTypes:true}).filter(x=>x.isDirectory()&&fs.existsSync('site/stay/'+x.name+'/index.html'));
assert.equal(paths.length+1,28,'existing stay page count must remain 28');
console.log('V261 STATIC PASS: 2 existing guides, 10 unverified photo placements withheld; 28-page scope unchanged. No license or deployed-preview claim.');
