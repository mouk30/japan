/* V143 — replace generic NEXT QUESTION cards with genuinely related in-site links.
   Only links already present in each page's related section; no new URLs. */
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;')}
function plain(s){return s.replace(/<[^>]*>/g,'').replace(/\s+/g,' ').replace(/[→↗]+$/g,'').trim()}
function transformJourney(html,pathname){
 if(!html.includes('<div class="curiosity">')||html.includes('data-v143-context='))return {html,changed:false};
 const related=/<section class="article-card related">([\s\S]*?)<\/section>/.exec(html);
 if(!related)return {html,changed:false};
 const options=[...related[1].matchAll(/<a\s+href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/g)]
  .map(m=>({href:m[1],name:plain(m[2])}))
  .filter(x=>/^\/[a-z]/i.test(x.href)&&x.href!==pathname&&x.name.length>=5);
 const unique=new Map();
 for(const x of options){if(!unique.has(x.href))unique.set(x.href,x)}
 const links=[...unique.values()].slice(0,3);
 if(links.length<2)return {html,changed:false};
 const label=pathname.startsWith('/season/')?'행사장·이동·옷차림을 정리하는 다음 순서':
  pathname.startsWith('/practical/')?'기기·교통·현지 준비를 이어서 확인':
  pathname.startsWith('/guide/')?'항로·예약·출입국 절차를 이어서 확인':
  pathname.startsWith('/couple/')?'동행 장소와 실제 이동 계획을 이어서 확인':
  pathname.startsWith('/life/')?'현지 생활과 이용 조건을 추가 확인':
  pathname.startsWith('/theme/')?'다음 여행 준비에 연결할 안내':
  '주제와 이어지는 상세 안내';
 const linkHtml=links.map((x,i)=>'<a href="'+esc(x.href)+'"><span class="v143-step-label">다음 '+(i+1)+'</span><span>'+esc(x.name)+'</span><span aria-hidden="true">→</span></a>').join('');
 const replacement='<nav class="v143-context-journey" data-v143-context="true" aria-label="현재 글과 연결되는 후속 안내"><h2>이어서 확인할 정보</h2><p>'+label+'</p><div>'+linkHtml+'</div></nav>';
 const updated=html.replace(/<div class="curiosity">[\s\S]*?<\/div>/,replacement);
 if(updated===html)return {html,changed:false};
 html=updated;
 if(!html.includes('/nf-v143-topic-guides.css'))
  html=html.replace('</head>','<link rel="stylesheet" href="/nf-v143-topic-guides.css?v=20261023"></head>');
 return {html,changed:true,selected:links};
}
module.exports={transformJourney};
