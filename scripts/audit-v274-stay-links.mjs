/**
 * V274: evidence-gated route and intent audit for 28 EXISTING /stay/ guides.
 * Local GitHub Actions filesystem inspection only; never claims that an
 * external booking provider is live, available, or reachable.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const ROOT='site/stay';
const BASE='c17fec39626600b9b83c7890d8a0857ea19d661e';
const files=['site/stay/index.html',...fs.readdirSync(ROOT,{withFileTypes:true})
  .filter(d=>d.isDirectory()&&fs.existsSync(path.join(ROOT,d.name,'index.html')))
  .map(d=>path.posix.join(ROOT,d.name,'index.html'))].sort();
assert.equal(files.length,28,'Only the 28 existing /stay/ guides are in scope');
const stayPaths=new Set(files.map(f=>f==='site/stay/index.html'?'/stay/':'/stay/'+f.split('/')[2]+'/'));
const sitemap=fs.readFileSync('site/sitemap.xml','utf8');
const locs=[...sitemap.matchAll(/<loc>(https:\/\/www\.nipponferry\.com\/stay\/[^<]*)<\/loc>/g)].map(m=>m[1]);
assert.equal(locs.length,28,'Exactly 28 sitemap stay URLs required');
assert.deepEqual(new Set(locs),new Set([...stayPaths].map(x=>'https://www.nipponferry.com'+x)),
  'Stay sitemap and existing guides differ');
assert.ok(fs.readFileSync('site/robots.txt','utf8').includes('https://www.nipponferry.com/sitemap.xml'));
const cities=[['삿포로','sapporo'],['오타루','otaru'],['하코다테','hakodate'],['센다이','sendai'],
 ['요코하마','yokohama'],['나고야','nagoya'],['고베','kobe'],['히로시마','hiroshima'],
 ['시모노세키','shimonoseki'],['벳푸','beppu'],['나가사키','nagasaki'],['가고시마','kagoshima'],
 ['쓰시마','tsushima'],['대마도','tsushima'],['오키나와','okinawa'],['교토','kyoto'],
 ['오사카','osaka'],['도쿄','tokyo'],['후쿠오카','fukuoka']];
const external=new Map(), pages=[], review=[];
let totalAnchors=0,stayLinks=0,bookingLinks=0,hashLinks=0;
const clean=s=>s.replace(/<[^>]*>/g,' ').replace(/&nbsp;/g,' ').replace(/\s+/g,' ').trim();
for(const file of files){
 const html=fs.readFileSync(file,'utf8');
 const page=file==='site/stay/index.html'?'/stay/':'/stay/'+file.split('/')[2]+'/';
 assert.ok(html.includes('https://www.nipponferry.com'+page),'Canonical location absent '+file);
 assert.match(html,/<meta name=['"]robots['"] content=['"]index,follow/i,'Robots absent '+file);
 assert.doesNotMatch(html,/kids-stay\.com|kidsstay-v5\.vercel\.app/i,'KidsStay integration '+file);
 assert.match(html,/<section class=['"]stay-convert['"]>/,'Ferry conversion section absent '+file);
 assert.match(html,/<p class=['"]stay-ferry-note['"]>/,'Ferry vs lodging clarification absent '+file);
 assert.ok(html.includes('숙소·객실 예약이 아닌 일본 국내 페리 항로 조회'),
   'External ferry lookup must be clearly distinguished from lodging '+file);
 const ids=new Set([...html.matchAll(/\bid=['"]([^'"]+)['"]/gi)].map(m=>m[1]));
 const anchors=[...html.matchAll(/<a\b[^>]*\bhref=['"]([^'"]+)['"][^>]*>([\s\S]*?)<\/a>/gi)]
   .map(m=>({href:m[1],label:clean(m[2])}));
 assert.ok(anchors.length>0,'No anchors '+file);
 const pageRecord={page,file,anchors:anchors.length,stayLinks:[],bookingLinks:[],externalHosts:[],review:[]};
 for(const a of anchors){
  totalAnchors++;
  const u=a.href;
  if(u.startsWith('#')&&u.length>1){
   hashLinks++;const id=decodeURIComponent(u.slice(1));
   assert.ok(ids.has(id),'Broken in-page anchor '+page+' -> '+u);
  }
  if(u.startsWith('/stay/')){
   stayLinks++;const dest=u.split(/[?#]/)[0];
   assert.ok(stayPaths.has(dest),'Broken /stay/ guide route '+page+' -> '+u);
   pageRecord.stayLinks.push({href:u,label:a.label});
   for(const [city,slug] of cities){
    if(a.label.includes(city)&&dest!==('/stay/'+slug+'/')){
     const item={page,href:u,label:a.label,city,expectedCityGuide:'/stay/'+slug+'/',kind:'CROSS_TOPIC_INTENT_REVIEW_NOT_PROVEN_ERROR'};
     pageRecord.review.push(item);review.push(item);
    }
   }
  }
  if(u.startsWith('/booking/')){
   bookingLinks++;const dest=u.split(/[?#]/)[0];
   const target=path.posix.join('site',dest,'index.html');
   assert.ok(fs.existsSync(target),'Missing ferry/booking guide '+page+' -> '+u);
   pageRecord.bookingLinks.push({href:u,label:a.label,kind:'LOCAL_FERRY_GUIDE_NOT_HOTEL_BOOKING'});
   if(a.label==='예약 준비 가이드 →'){
    const item={page,href:u,label:a.label,kind:'AMBIGUOUS_CTA_TEXT_REVIEW_FERRY_CONTEXT_PRESENT'};
    pageRecord.review.push(item);review.push(item);
   }
  }
  if(/^https?:\/\//i.test(u)){
   const host=new URL(u).hostname;
   external.set(host,(external.get(host)||0)+1);
   if(!pageRecord.externalHosts.includes(host))pageRecord.externalHosts.push(host);
  }
 }
 const visible=clean(html.replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi,'').replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,''));
 assert.doesNotMatch(visible,/실시간\s*잔여\s*객실\s*확정|예약\s*확정\s*보장|즉시\s*객실\s*확정/i,
   'Unsubstantiated guaranteed room availability '+file);
 assert.ok(pageRecord.bookingLinks.length>0,'Ferry booking guide CTA missing '+page);
 pages.push(pageRecord);
}
const report={
 stage:'V274',generatedAt:new Date().toISOString(),baselineMain:BASE,
 scope:'28 existing /stay/ guides; local route and visible intent audit',
 summary:{pages:pages.length,anchorOccurrences:totalAnchors,stayGuideLinks:stayLinks,
  localBookingGuideLinks:bookingLinks,inPageHashLinks:hashLinks,
  distinctExternalHosts:external.size,reviewFlags:review.length,
  brokenStayOrBookingRoutes:0,brokenInPageHashes:0,
  ferryVersusHotelDisclosurePages:pages.length},
 externalHosts:[...external].map(([host,occurrences])=>({host,occurrences})),
 reviewFlags:review,pages,
 limitations:[
  'This verifies existing local /stay/, /booking/ and same-page hash targets, not HTTP 200 for all site routes.',
  'Cross-topic city-labelled links are review flags, not automatically broken or inaccurate.',
  'Generic 예약 준비 가이드 labels may be ambiguous even with the existing ferry disclaimer; V275 should decide wording.',
  'External host presence does not prove reachable, current pricing, availability, official booking, or safety.',
  'No photo provenance or rights are cleared by a link audit.',
  'V258-V273 Draft PRs are unmerged; main baseline may retain rights-unverified imagery.',
  'Vercel authenticated Preview is blocked by team scope 403; no merge or production deploy authorized.'
 ]
};
fs.mkdirSync('audit-reports',{recursive:true});
const out='audit-reports/v274-stay-links-generated.json';
fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');
console.log('V274 LINK AUDIT PASS '+JSON.stringify(report.summary));
console.log('V274 external hosts '+JSON.stringify(report.externalHosts));
console.log('V274 review flags '+review.length+'; generated '+out);
