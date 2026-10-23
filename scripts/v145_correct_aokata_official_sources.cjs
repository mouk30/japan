/* V145 final factual correction: Aokata is not Fukue.
   Replace general Fukue island references with an MLIT Aokata cruise-berth
   source and Shinkamigoto church visit/advance-contact source. Preserve SEO.
*/
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..');
const file=path.join(root,'site/things-to-do/aokata-cruise-port-day-trip/index.html');
const manifestPath=path.join(__dirname,'v145_maritime_content.json');
const auditPath=path.join(root,'audit-reports/v145/verified-maritime-content-audit.json');
const manifest=JSON.parse(fs.readFileSync(manifestPath,'utf8'));
const audit=JSON.parse(fs.readFileSync(auditPath,'utf8'));
const entry=manifest.entries['aokata-cruise-port-day-trip'];
const oldSources=entry.sources;
const newSources=[
  ["국토교통성 크루즈항 공식 아오카타항·선석 안내","https://www.mlit.go.jp/kankocho/cruise/detail/061/index.html"],
  ["신카미고토 관광협회 가시라가시마 성당 사전 연락·방문조건","https://shinkamigoto.nagasaki-tabinet.com/junrei/10239"]
];
const oldBody="가시라가시마 천주당은 아오카타항 바로 앞 관광지가 아닙니다. 실방문 가능 여부와 성당 출입·보존구역 제한, 접근도로·차량 이동방법을 현지 공식 관광정보로 확인하세요.";
const newBody="가시라가시마 천주당은 아오카타항 바로 앞 관광지가 아닙니다. 실제 내부 방문에는 사전 연락이 필요하다는 신카미고토 관광협회의 안내가 있습니다. 이용일의 접수·방문 가능 여부, 보존구역 제한, 접근도로와 차량 이동방법을 공식 원문에서 확인하세요.";
const html=fs.readFileSync(file,'utf8');
const begin=html.indexOf('<section id="nf-v145-maritime"');
if(begin<0)throw Error('V145 page section not installed');
const part=html.slice(begin);
const actualPath=newSources[0][1],chapter=newSources[1][1];
const sourceChanged=entry.sources[0][1]!==actualPath;
const patch=(a,b,txt)=>{if(!txt.includes(a))throw Error('Missing expected text '+a.slice(0,80));return txt.replace(a,b)};
let next=html;
if(sourceChanged){
 let tail=part;
 for(let i=0;i<2;i++){
  const old=oldSources[i],neu=newSources[i];
  tail=patch('<a href="'+old[1]+'" target="_blank" rel="noopener noreferrer"><span>'+old[0]+'</span>',
    '<a href="'+neu[1]+'" target="_blank" rel="noopener noreferrer"><span>'+neu[0]+'</span>',tail);
 }
 tail=patch(oldBody,newBody,tail);
 next=html.slice(0,begin)+tail;
 entry.sources=newSources;
 entry.steps[1][1]=newBody;
 audit.updated.find(x=>x.url==='/things-to-do/aokata-cruise-port-day-trip/').sources=newSources;
}
const protect=[/<title>[^<]+<\/title>/i,/<meta name="description"[^>]+>/i,/<link rel="canonical"[^>]+>/i,/<meta property="og:image"[^>]+>/i];
for(const re of protect)if((next.match(re)||[])[0] !== (html.match(re)||[])[0])throw Error('SEO drift');
if(!next.includes(newBody)||!next.includes(chapter)||!next.includes(actualPath))throw Error('corrected official evidence missing');
const sha=crypto.createHash('sha256').update(next).digest('hex');
audit.updated.find(x=>x.url==='/things-to-do/aokata-cruise-port-day-trip/').newSha256=sha;
audit.fact_check_note="Aokata port official cruise-berth and Kashiragashima church advance contact verified; Fukue-specific links removed from the Aokata V145 section.";
fs.writeFileSync(file,next,'utf8');
fs.writeFileSync(manifestPath,JSON.stringify(manifest,null,2)+'\n','utf8');
fs.writeFileSync(auditPath,JSON.stringify(audit,null,2)+'\n','utf8');
console.log(JSON.stringify({revised:sourceChanged,slug:'aokata-cruise-port-day-trip',portSource:actualPath,churchSource:chapter,siteContentsValidated:true}));
