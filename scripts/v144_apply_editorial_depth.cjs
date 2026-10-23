/* V144: rewrite only 24 + 27 exact identified existing thin articles.
   Preserve every SEO field, URL, source references and booking. Replace stock
   hero photographs with transparent topic-specific editorial info boards.
   Stock photo provenance queue is explicitly retained; no fake documentary photo.
*/
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),site=path.join(root,'site');
const inv=JSON.parse(fs.readFileSync(path.join(root,'audit-reports/v144/repetition-inventory.json'),'utf8'));
const season=JSON.parse(fs.readFileSync(path.join(__dirname,'v144_season_specifics.json'),'utf8')).rows;
const practical=JSON.parse(fs.readFileSync(path.join(__dirname,'v144_practical_specifics.json'),'utf8')).rows;
const expected={season:24,practical:27};
const generic={
 season:'계절 이벤트는 날짜와 날씨 변수의 영향을 크게 받습니다.',
 practical:'서비스·교통·시설은 노선, 기기, 날짜와 지역에 따라 조건이 달라질 수 있습니다.'
};
function escapeHtml(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}
function matchPart(x,r){return x.match(r)?.[0]||null}
function topicFigure(title,rows,group,slug){
const name=group==='season'?'FOUR SEASONS · LOCAL PLANNING':'TRAVEL PRACTICAL · STEP BY STEP';
const sub=group==='season'?'계절별 현장 확인·교통·준비를 한눈에':'여행 전 확인·예약·현장 이용을 한눈에';
const badges=rows.slice(0,3).map((r,i)=>
  '<div class="v144-visual-panel"><span class="v144-panel-num">0'+(i+1)+'</span><b>'+escapeHtml(r[0])+'</b></div>').join('');
return '<figure class="v144-topic-visual" data-v144-visual="'+escapeHtml(slug)+'" role="group" aria-label="'+escapeHtml(title)+' 핵심 확인 순서">'
 +'<div class="v144-visual-header"><small>'+name+'</small><strong>'+escapeHtml(title)+'</strong><p>'+sub+'</p></div>'
 +'<div class="v144-visual-items">'+badges+'</div>'
 +'<figcaption>기존 공통 대표사진 대신 페이지별 핵심 정보로 구성한 자체 제작 안내 도식입니다. 실제 관광지·차량·시설 촬영 사진이 아닙니다.</figcaption>'
 +'</figure>';
}
function details(title,descr,rows,group){
const icons=rows.map((r,i)=>'<section class="v144-action"><span class="v144-action-id">0'+(i+1)+'</span><div><h3>'+escapeHtml(r[0])+'</h3><p>'+escapeHtml(r[1])+'</p></div></section>').join('');
const official=group==='season'
 ?'https://www.japan.travel/en/see-and-do/festivals-and-events/'
 :'https://www.japan.travel/en/faq/';
const claim=group==='season'
 ?'행사 개최일·기상·입장권·교통편은 당해연도 주최 측과 운송사 원문에서 다시 확인하세요. 아래 링크는 일본의 계절·행사 전체를 안내하는 공식 참고자료로, 개별 행사 확정 정보가 아닙니다.'
 :'운임·예약·서비스·운행일·환불조건은 실제 운영사 및 판매자 약관을 우선 확인하세요. 아래 링크는 일본 여행 교통·이용의 공식 일반 참고자료이며 개별 업체 운영을 보증하지 않습니다.';
return '<section class="article-card v144-detailed-guide" data-v144-detail="true">'
 +'<div class="v144-guide-eyebrow">'+(group==='season'?'SEASONAL TRAVEL CHECKLIST':'PRACTICAL DECISION GUIDE')+'</div>'
 +'<h2>'+escapeHtml(title)+' — 실제 준비 순서</h2>'
 +'<p class="v144-guide-desc">'+escapeHtml(descr)+'</p>'
 +'<div class="v144-guide-grid">'+icons+'</div>'
 +'<div class="v144-source-caution"><strong>공식 정보 확인</strong><p>'+escapeHtml(claim)+'</p>'
 +'<a href="'+official+'" target="_blank" rel="noopener noreferrer">일본정부관광국 공식 참고자료 확인 ↗</a></div>'
 +'</section>';
}
function sha(s){return crypto.createHash('sha256').update(s).digest('hex')}
const report={version:'V144',date:'2026-10-23',intended_pages:51,edited_pages:[],image_followups:[],
  preserved:{seo:true,canonical:true,booking:true,new_articles:0,original_images_retained_in_repository:true},
  note:'51 covers become explicitly labeled self-authored informative visuals. Real location-verified photos remain a separate follow-up; unverified photos not passed off as location documentary.'};
const prepared=[];
for(const [group,expectedCount] of Object.entries(expected)){
 const sample=inv.targets[group];const db=group==='season'?season:practical;
 if(sample.length!==expectedCount||Object.keys(db).length!==expectedCount)throw Error(group+' count discrepancy');
 for(const item of sample){
  const source=path.join(site,group,item.slug,'index.html');
  if(!fs.existsSync(source))throw Error('missing source '+source);
  const original=fs.readFileSync(source,'utf8'),rows=db[item.slug];
  if(!rows||rows.length!==3)throw Error('editorial data missing '+item.slug);
  if(!original.includes(generic[group]))throw Error('generic text already removed on '+item.slug);
  const t=original.match(/<h1[^>]*>([^<]+)<\/h1>/)?.[1]?.trim();
  const desc=original.match(/<meta name="description" content="([^"]+)"/)?.[1]?.trim()||'';
  if(t!==item.title||item.image!==(original.match(/<img class="article-cover" src="([^"]+)"/)||[])[1])
   throw Error('source changed since baseline: '+item.slug);
  const oldBlock=/<section class="article-card">[\s\S]*?<\/section>/.exec(original);
  const cover=/<img class="article-cover" src="[^"]+"[^>]*>/.exec(original);
  if(!oldBlock||!cover)throw Error('unexpected source structure '+item.slug);
  let updated=original.replace(oldBlock[0],details(t,desc,rows,group))
    .replace(cover[0],topicFigure(t,rows,group,item.slug));
  if(updated===original)throw Error('no change '+item.slug);
  const css='<link rel="stylesheet" href="/nf-v144-topic-depth.css?v=20261023">';
  if(updated.includes(css))throw Error('duplicate V144 stylesheet');
  updated=updated.replace('<link rel="stylesheet" href="/style.css">','<link rel="stylesheet" href="/style.css">'+css);
  for(const re of [/<title>[\s\S]*?<\/title>/,/<meta name="description"[^>]*>/,/<link rel="canonical"[^>]*>/,/<script type="application\/ld\+json">[\s\S]*?<\/script>/]){
   if(matchPart(original,re)!==matchPart(updated,re))throw Error('SEO regression: '+item.slug);
  }
  for(const sample of ['https://willer-travel.com/ko/ferry/','<section class="booking"','<section class="article-card related"']){
   if(original.includes(sample)&&!updated.includes(sample))throw Error('lost booking/related: '+item.slug);
  }
  if(updated.includes(generic[group]))throw Error('generic phrase still present '+item.slug);
  if(updated.split('data-v144-detail').length!==2||updated.split('data-v144-visual').length!==2)throw Error('visual/detail count '+item.slug);
  const route='/'+group+'/'+item.slug+'/';
  prepared.push({source,updated,original,route,cover:item.image,slug:item.slug,group,title:t});
 }
}
if(prepared.length!==51)throw Error('wrong update count');
for(const p of prepared){
 fs.writeFileSync(p.source,p.updated,'utf8');
 report.edited_pages.push({url:p.route,title:p.title,old_cover:p.cover,new_visual:'v144-topic-visual; per-page information diagram',detail_step_count:3,seo_unchanged:true,old_sha256:sha(p.original),new_sha256:sha(p.updated)});
 report.image_followups.push({url:p.route,old_cover:p.cover,
  provenance:'Not verified as a photograph of page-specific attraction/scene; keep file in repository and prioritize actual source/license search',
  rephotograph_priority:/city|hokkaido|couple|transport/.test(p.cover)?'high':'medium'});
}
report.images_replaced_with_diagrams=report.edited_pages.length;
const dir=path.join(root,'audit-reports/v144');fs.mkdirSync(dir,{recursive:true});
fs.writeFileSync(path.join(dir,'editorial-image-provenance-report.json'),JSON.stringify(report,null,2)+'\n','utf8');
console.log(JSON.stringify({modified:prepared.length,by_type:{season:24,practical:27},
  old_photo_counts:report.image_followups.reduce((a,o)=>(a[o.old_cover]=(a[o.old_cover]||0)+1,a),{}),
  new_articles:0},null,2));
