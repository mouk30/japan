import fs from 'node:fs';
const m=JSON.parse(fs.readFileSync('audit-reports/v81-v120/manifest.json','utf8'));
const urls=[...new Set(m.articlesMeta.flatMap(x=>x.sources))].sort();
const refs=new Map(urls.map(u=>[u,m.articlesMeta.filter(x=>x.sources.includes(u)).map(x=>x.path)]));
const results=[];
for(let i=0;i<urls.length;i+=9){
 const group=urls.slice(i,i+9);
 results.push(...await Promise.all(group.map(async url=>{
  let status=0,state='unknown',error='',finalUrl='';
  try{
   const r=await fetch(url,{redirect:'follow',headers:{'user-agent':'Mozilla/5.0 (compatible; NIPPONFERRY-Site-Official-Link-QA/1.0)'},signal:AbortSignal.timeout(13000)});
   status=r.status;finalUrl=r.url;
   await r.body?.cancel().catch(()=>{});
   state=status>=200&&status<400?'reachable':[404,410].includes(status)?'not_found':[401,403,429].includes(status)?'restricted':'unconfirmed';
  }catch(e){error=String(e).slice(0,180)}
  return {url,status,state,error,finalUrl,articles:refs.get(url)};
 })));
}
const report={time:new Date().toISOString(),urls:urls.length,reachable:results.filter(x=>x.state==='reachable').length,missing:results.filter(x=>x.state==='not_found').length,restricted:results.filter(x=>x.state==='restricted').length,unconfirmed:results.filter(x=>['unknown','unconfirmed'].includes(x.state)).length,results};
fs.writeFileSync('audit-reports/v81-v120/official-link-health.json',JSON.stringify(report,null,2));
console.log(JSON.stringify({links:report.urls,reachable:report.reachable,missing:report.missing,restricted:report.restricted,unconfirmed:report.unconfirmed,issues:results.filter(x=>x.state!=='reachable').slice(0,25)},null,2));
if(report.missing>0)process.exitCode=1;
