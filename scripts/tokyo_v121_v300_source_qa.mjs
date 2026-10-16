import fs from 'node:fs';
const manifest=JSON.parse(fs.readFileSync('audit-reports/v121-v300/editorial-manifest.json','utf8'));
const sources=new Map();
for(const t of manifest.topics){
 if(!sources.has(t.source))sources.set(t.source,[]);
 sources.get(t.source).push({v:t.version,slug:t.slug});
}
const arr=[...sources.entries()];
const report={checkedAt:new Date().toISOString(),sourceCount:arr.length,reachable:0,notFound:0,restricted:0,unconfirmed:0,links:[],passed:false};
for(let i=0;i<arr.length;i+=12){
 const results=await Promise.all(arr.slice(i,i+12).map(async ([url,articles])=>{
  let status=0,state='unknown',finalUrl='',error='';
  try{
   const r=await fetch(url,{redirect:'follow',signal:AbortSignal.timeout(17000),headers:{'User-Agent':'Mozilla/5.0 (compatible; NIPPONFERRY Tokyo guide editorial reference QA)'}});
   status=r.status;finalUrl=r.url;
   await r.body?.cancel().catch(()=>{});
   state=status>=200&&status<400?'reachable':[404,410].includes(status)?'not_found':[401,403,429].includes(status)?'restricted':'unconfirmed';
  }catch(e){error=String(e).slice(0,240)}
  return {url,status,state,finalUrl,error,articles};
 }));
 report.links.push(...results);
}
for(const r of report.links){
 if(r.state==='reachable')report.reachable++;
 else if(r.state==='not_found')report.notFound++;
 else if(r.state==='restricted')report.restricted++;
 else report.unconfirmed++;
}
report.passed=report.notFound===0;
fs.writeFileSync('audit-reports/v121-v300/official-sources-qa.json',JSON.stringify(report,null,2));
console.log(JSON.stringify({passed:report.passed,sources:report.sourceCount,reachable:report.reachable,missing:report.notFound,restricted:report.restricted,unconfirmed:report.unconfirmed,problematic:report.links.filter(x=>x.state!=='reachable').map(x=>({url:x.url,status:x.status,state:x.state,error:x.error,articles:x.articles.slice(0,5)}))},null,2));
if(!report.passed)process.exitCode=1;
