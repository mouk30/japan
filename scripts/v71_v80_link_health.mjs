import fs from 'node:fs';
const dir='audit-reports/v71-v80',manifest=JSON.parse(fs.readFileSync(dir+'/manifest.json','utf8'));
const refs=new Map(),bad=[];
for(const p of manifest.pages){
 const html=fs.readFileSync('site/things-to-do/'+p.slug+'/index.html','utf8');
 const id='v'+p.version+'-verification',start=html.indexOf('id="'+id+'"');
 if(start<0){bad.push('missing '+p.slug);continue}
 const end=html.indexOf('</section>',start),part=html.slice(start,end);
 for(const m of part.matchAll(/href="(https?:\/\/[^"]+)"/g)){
   const href=m[1].replaceAll('&amp;','&');
   if(!refs.has(href))refs.set(href,[]);
   refs.get(href).push(p.slug);
 }
}
const links=[...refs.entries()].map(([url,pages])=>({url,pages}));
const chunks=(a,n)=>Array.from({length:Math.ceil(a.length/n)},(_,i)=>a.slice(i*n,(i+1)*n));
const results=[];
async function check(x){
 const row={...x,status:0,finalUrl:'',error:'',state:'unknown'};
 try{
  const res=await fetch(x.url,{redirect:'follow',headers:{'user-agent':'Mozilla/5.0 (compatible; NIPPONFERRY link QA; travel-source-verification)'},signal:AbortSignal.timeout(12500)});
  row.status=res.status;row.finalUrl=res.url;
  await res.body?.cancel().catch(()=>{});
  row.state=res.status>=200&&res.status<400?'reachable':res.status===404||res.status===410?'not_found':res.status===401||res.status===403||res.status===429?'restricted':'unconfirmed';
 }catch(e){row.error=String(e).slice(0,220)}
 return row;
}
for(const batch of chunks(links,12))results.push(...await Promise.all(batch.map(check)));
const report={checkedAt:new Date().toISOString(),scope:'External references introduced in V71-V80 travel decision panels',links:results.length,independentSources:results.filter(x=>x.state==='reachable').length,notFound:results.filter(x=>x.state==='not_found').length,restricted:results.filter(x=>x.state==='restricted').length,unconfirmed:results.filter(x=>x.state==='unknown'||x.state==='unconfirmed').length,issues:bad,results};
fs.writeFileSync(dir+'/official-link-health.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({links:report.links,reachable:report.independentSources,notFound:report.notFound,restricted:report.restricted,unconfirmed:report.unconfirmed,hard404:results.filter(x=>x.state==='not_found').slice(0,35)},null,2));
if(report.notFound>0)process.exitCode=1;
