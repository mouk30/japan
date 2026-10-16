import fs from 'node:fs';
const slugs=['yokohama','nagasaki','hakata','naha','ishigaki','osaka','kobe','hakodate','aomori','kagoshima','beppu','sasebo','shimonoseki','shimizu','kanazawa','sendai','kochi','niigata','matsuyama','sakaiminato'];
const base='https://www.nipponferry.com/things-to-do/';
const outfile='audit-reports/v69/live-production.json';fs.mkdirSync('audit-reports/v69',{recursive:true});
const history=[];let passed=false;
for(let round=0;round<10&&!passed;round++){
 const checks=await Promise.all(slugs.map(async slug=>{
  const pathname=slug+'-cruise-port-day-trip/';
  let status=0,missing=[],error='',bytes=0,originalURL='';
  try{
    const res=await fetch(base+pathname+'?v69_live='+Date.now(),{headers:{'Cache-Control':'no-cache','User-Agent':'NIPPONFERRY-Production-V69-QA'},signal:AbortSignal.timeout(19000)});
    status=res.status;originalURL=res.url;
    const html=await res.text();bytes=html.length;
    const required=['id="v69-berth-qa"','class="v69-facts"','v69-return','v69-disclaimer',base+pathname,'rel="canonical"'];
    missing=required.filter(x=>!html.includes(x));
    const cards=(html.match(/class="v69-fact"/g)||[]).length;
    if(cards!==3)missing.push('3 original official source cards; got '+cards);
    if(!html.includes('style="width:38px;height:38px;'))missing.push('Production built logo width guard');
    if(html.includes('**해당 항차'))missing.push('Markdown emphasis leaked into HTML');
  }catch(e){error=String(e)}
  return {slug,status,bytes,missing,error,originalURL};
 }));
 passed=checks.every(x=>x.status===200&&!x.error&&!x.missing.length);
 history.push({round:round+1,time:new Date().toISOString(),passed,checks});
 if(!passed&&round<9)await new Promise(r=>setTimeout(r,12000));
}
const report={checkedAt:new Date().toISOString(),articles:slugs.length,passed,rounds:history.length,checks:history.at(-1).checks,history};
fs.writeFileSync(outfile,JSON.stringify(report,null,2));
console.log(JSON.stringify({passed,rounds:history.length,checked:report.checks.length,failures:report.checks.filter(x=>x.status!==200||x.missing.length||x.error)},null,2));
if(!passed)process.exitCode=1;
