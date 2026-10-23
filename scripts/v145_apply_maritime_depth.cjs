/* V145: refine exactly ten EXISTING NIPPONFERRY articles without adding routes.
 * Dedicated source-verified editorial guidance, no invented departure/return times.
 * Preserve title/meta/OG/JSON-LD, original documentary image and rights caption.
 */
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),site=path.join(root,'site');
const catalogue=JSON.parse(fs.readFileSync(path.join(__dirname,'v145_maritime_content.json'),'utf8'));
const entries=catalogue.entries;
const slugs=Object.keys(entries);
if(slugs.length!==10||catalogue.target_count!==10)throw Error('V145 manifest mismatch');
const esc=x=>String(x).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const protect=[
 ['title',/<title>[\s\S]*?<\/title>/i],
 ['meta-description',/<meta name="description"[^>]+>/i],
 ['canonical',/<link rel="canonical"[^>]+>/i],
 ['og-title',/<meta property="og:title"[^>]+>/i],
 ['og-description',/<meta property="og:description"[^>]+>/i],
 ['og-image',/<meta property="og:image"[^>]+>/i],
 ['json-ld',/<script type="application\/ld\+json">[\s\S]*?<\/script>/i]
];
const origSet=fs.readdirSync(path.join(site,'things-to-do'),{withFileTypes:true}).filter(x=>x.isDirectory()).length;
function pageURL(slug){return '/things-to-do/'+slug+'/'}
function linkExists(url){
 if(!/^\/[a-z]/.test(url)||url.includes('..'))return false;
 const target=path.join(site,url.replace(/^\//,''));
 return fs.existsSync(path.join(target,'index.html'))||fs.existsSync(target);
}
function markup(slug,entry){
 const cards=entry.steps.map(([title,body],idx)=>
  '<section class="nf145-step"><div class="nf145-step-num">'+String(idx+1).padStart(2,'0')+'</div><div><h3>'+esc(title)+'</h3><p>'+esc(body)+'</p></div></section>'
 ).join('');
 const official=entry.sources.map(([label,url])=>'<a href="'+esc(url)+'" target="_blank" rel="noopener noreferrer"><span>'+esc(label)+'</span><span aria-hidden="true">↗</span></a>').join('');
 const relates=entry.related.map(slug2=>'<a href="'+pageURL(slug2)+'">'+esc(entries[slug2].region)+' 여행 더 보기 <span aria-hidden="true">→</span></a>').join('');
 const type=entry.kind==='cruise-port'?'CRUISE PORT · SAFE RETURN':entry.kind==='island-ferry'?'COASTAL FERRY · ISLAND TRIP':'LOCAL MARITIME JOURNEY';
 return '<section id="nf-v145-maritime" class="nf145-maritime" aria-label="'+esc(entry.region)+' 공식 자료 기반 바다 여행 실전 안내" data-nf145="10-existing-guides">'
  +'<div class="nf145-topline">'+type+'</div>'
  +'<h2>'+esc(entry.region)+' — 출발부터 복귀까지</h2>'
  +'<p class="nf145-summary">'+esc(entry.summary)+'</p>'
  +'<div class="nf145-nav"><a href="#nf145-steps">이동·관광 동선</a><a href="#nf145-official">공식 교통·관광 자료</a><a href="#nf145-related">관련 여행 가이드</a></div>'
  +'<div class="nf145-steps" id="nf145-steps">'+cards+'</div>'
  +'<aside class="nf145-return" aria-label="하선과 귀선 안전"><strong>귀선 시간은 반드시 내 항차 공지로 확인하세요</strong>'
  +'<p>관광 안내에 표시된 페리 시간표는 크루즈 승객의 귀선 마감과 다릅니다. 실제 입항 선석·하선 게이트·셔틀·마지막 복귀 차량·승객 귀선 마감은 선사와 현지 운영기관 원문이 우선합니다. 이 페이지는 특정 날짜·잔여 좌석·입장 가능 여부를 보증하지 않습니다.</p></aside>'
  +'<div class="nf145-official" id="nf145-official"><h3>관광·교통의 공식 원문</h3><p>촬영 사진이나 과거 관광 글로 최신 운항·입장 조건을 단정하지 않습니다. 예약·구매 전 아래 원문을 다시 확인하세요.</p>'
  +'<div class="nf145-official-links">'+official+'</div></div>'
  +'<div class="nf145-related" id="nf145-related"><h3>이어서 계획할 여행</h3><div>'+relates+'</div></div>'
  +'<p class="nf145-photo-note"><strong>이 글 대표사진의 검증 범위:</strong> '+esc(entry.photoNote)+'</p>'
  +'</section>';
}
const staged=[],audit={version:'V145',date:'2026-10-23',scope:'10 previously published maritime articles',expected:10,updated:[],title_meta_canonical_preserved:true,structured_data_preserved:true,images_modified:0,new_posts:0,verified_timetable_realtime:false,limitations:["Original imagery remains unchanged; for entries without confirmed image provenance do not call images documentary photographs.","No live ship berth, last bus, real-time booking inventory, or ticket price asserted."],added_steps:0};
for(const slug of slugs){
 const d=entries[slug],file=path.join(site,'things-to-do',slug,'index.html');
 if(!fs.existsSync(file))throw Error('Missing published article '+slug);
 if(!Array.isArray(d.steps)||d.steps.length!==5)throw Error('Incorrect 5 steps '+slug);
 if(d.related.length<2||d.sources.length<2)throw Error('Source/link sparsity '+slug);
 for(const rel of d.related){
  if(!entries[rel]||!linkExists(pageURL(rel)))throw Error('Broken related link '+slug+' to '+rel);
 }
 for(const [label,url] of d.sources){
  if(!label||!/^https:\/\/(www\.japan\.travel|www\.shikokuferry\.com|www\.my-kagawa\.jp|dogo\.jp)\//.test(url))throw Error('Unexpected official source '+slug+' '+url);
 }
 const html=fs.readFileSync(file,'utf8');
 if(html.includes('data-nf145='))throw Error('V145 already applied '+slug);
 if(!html.includes('<link rel="stylesheet" href="/style.css">'))throw Error('Missing css anchor '+slug);
 let insertion='';
 if(html.includes('<article')){const i=html.lastIndexOf('</article>');if(i<0)throw Error('unclosed article '+slug);insertion=html.slice(0,i)+markup(slug,d)+html.slice(i)}
 else {const i=html.lastIndexOf('</main>');if(i<0)throw Error('unclosed main '+slug);insertion=html.slice(0,i)+markup(slug,d)+html.slice(i)}
 insertion=insertion.replace('<link rel="stylesheet" href="/style.css">','<link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/nf-v145-maritime-deep.css?v=20261023">');
 for(const [name,re] of protect){
  if((html.match(re)||[])[0]!==(insertion.match(re)||[])[0])throw Error('Protected SEO '+name+' on '+slug);
 }
 const oldImageNodes=[...html.matchAll(/<img\b[^>]*>/g)].map(x=>x[0]);
 const newImageNodes=[...insertion.matchAll(/<img\b[^>]*>/g)].map(x=>x[0]);
 if(JSON.stringify(oldImageNodes)!==JSON.stringify(newImageNodes))throw Error('Image source changed '+slug);
 const locallinks=[...insertion.matchAll(/<a href="(\/things-to-do\/[^"]+)"/g)].map(x=>x[1]);
 for(const url of locallinks.filter(x=>d.related.some(t=>url===pageURL(t))))if(!linkExists(url))throw Error('Unavailable link '+url);
 staged.push({file,html:insertion,slug,original:html});
 audit.updated.push({url:pageURL(slug),region:d.region,kind:d.kind,originalSha256:sha(html),newSha256:sha(insertion),steps:5,sources:d.sources,related:d.related.map(pageURL),imageStatus:d.photoNote,seoPreserved:true,originalImagesPreserved:true});
 audit.added_steps+=5;
}
if(staged.length!==10)throw Error('Wrong staged count');
for(const row of staged)fs.writeFileSync(row.file,row.html,'utf8');
const endSet=fs.readdirSync(path.join(site,'things-to-do'),{withFileTypes:true}).filter(x=>x.isDirectory()).length;
if(origSet!==endSet)throw Error('Modified publication count!');
const out=path.join(root,'audit-reports/v145');
fs.mkdirSync(out,{recursive:true});
fs.writeFileSync(path.join(out,'verified-maritime-content-audit.json'),JSON.stringify(audit,null,2)+'\n','utf8');
console.log(JSON.stringify({updated:staged.length,steps:audit.added_steps,old_images_retained:true,official_sources:audit.updated.reduce((n,v)=>n+v.sources.length,0),new_articles:0}));
