const fs=require('fs'),path=require('path');const root='site';const exact={
season:'계절 이벤트는 날짜와 날씨 변수의 영향을 크게 받습니다.',
practical:'서비스·교통·시설은 노선, 기기, 날짜와 지역에 따라 조건이 달라질 수 있습니다.'
};const out={date:'2026-10-23',source:'V143 left-behind generic-body exact phrase scan',counts:{},targets:{}};
for(const [family,needle] of Object.entries(exact)){
const dir=path.join(root,family);const arr=[];
for(const slug of fs.readdirSync(dir)){const f=path.join(dir,slug,'index.html');if(!fs.existsSync(f))continue;
const h=fs.readFileSync(f,'utf8');if(!h.includes(needle))continue;
const title=(h.match(/<h1[^>]*>(.*?)<\/h1>/)||[])[1]||'';
const og=(h.match(/<meta name="description" content="([^"]+)"/)||[])[1]||'';
const img=(h.match(/<img class="article-cover" src="([^"]+)"/)||[])[1]||'';
const main=(h.match(/<section class="article-card">([\s\S]*?)<\/section>/)||[])[1]||'';
const related=(h.match(/<section class="article-card related">([\s\S]*?)<\/section>/)||[])[1]||'';
arr.push({slug,title,description:og,image:img,
currentHeadings:[...main.matchAll(/<h[23]>([^<]+)<\/h[23]>/g)].map(x=>x[1]),
existingRelated:[...related.matchAll(/<a href="([^"]+)"[^>]*>([^<]+)<\/a>/g)].slice(0,7).map(x=>({href:x[1],text:x[2]})),
genericText:true});
}
out.counts[family]=arr.length;out.targets[family]=arr;}
fs.mkdirSync('audit-reports/v144',{recursive:true});
fs.writeFileSync('audit-reports/v144/repetition-inventory.json',JSON.stringify(out,null,2)+'\n','utf8');
console.log(JSON.stringify({counts:out.counts,slugs:Object.fromEntries(Object.entries(out.targets).map(([k,v])=>[k,v.map(x=>x.slug)]))},null,2));
