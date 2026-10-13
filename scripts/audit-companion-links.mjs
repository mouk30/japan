#!/usr/bin/env node
/* V10 external link audit. Run: node scripts/audit-companion-links.mjs
 * Requires Node >=20; evaluates HTTP accessibility, NOT real-time ticket inventory.
 */
import { readdir, readFile, mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
const root=path.resolve('site/things-to-do');
const ports=await readdir(root,{withFileTypes:true});
const pages=ports.filter(x=>x.isDirectory()&&/-cruise-(family|couple)-guide$/.test(x.name)).map(x=>x.name+'/index.html');
const matches=[];
for(const page of pages){let html;try{html=await readFile(path.join(root,page),'utf8')}catch{continue}
 const re=/<a\b[^>]*\bhref=["'](https?:\/\/[^"'\s<>]+)["'][^>]*>([\s\S]*?)<\/a>/gi;
 for(const m of html.matchAll(re)){let url=m[1].replace(/&amp;/g,'&');let label=m[2].replace(/<[^>]*>/g,'').replace(/\s+/g,' ').trim();matches.push({page,url,label})}
}
const uniq=[...new Set(matches.map(x=>x.url))];
let next=0;const results=[];
async function check(url){const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),12000);
try{
let resp=await fetch(url,{method:'HEAD',redirect:'follow',signal:controller.signal,headers:{'User-Agent':'NipponFerry-LinkAudit/1.0 (content QA)'}});
if([403,405,429,500,501,502,503].includes(resp.status))resp=await fetch(url,{method:'GET',redirect:'follow',signal:controller.signal,headers:{'User-Agent':'Mozilla/5.0 (compatible; NipponFerryAudit/1.0)'}});
const status=resp.status;try{await resp.body?.cancel()}catch{}
return {url,status,final_url:resp.url,check:status>=200&&status<400?'reachable':(status===403||status===429)?'manual_review':'error'}
}catch(e){return {url,status:null,check:'manual_review',error:String(e.message).slice(0,150)}}finally{clearTimeout(timer)}}
await Promise.all(Array.from({length:Math.min(6,uniq.length)},async()=>{while(next<uniq.length){const i=next++;results[i]=await check(uniq[i])}}));
const mapping=new Map(results.map(x=>[x.url,x]));
const rows=matches.map(x=>({...x,...mapping.get(x.url)}));
const summary={date:new Date().toISOString(),scope:'30 family/couple companion guides',pages:pages.length,total_link_occurrences:rows.length,unique_urls:uniq.length,reachable:results.filter(x=>x.check==='reachable').length,manual_review:results.filter(x=>x.check==='manual_review').length,errors:results.filter(x=>x.check==='error').length,note:'HTTP reachable does not mean reservable. Login, bot-blocks, dates, price, tickets, refund, port shuttle require manual review.'};
await mkdir('audit-reports',{recursive:true});
await writeFile('audit-reports/companion-links.json',JSON.stringify({summary,results,occurrences:rows},null,2)+'\n');
const csv=(v)=>'"'+String(v??'').replaceAll('"','""')+'"';
await writeFile('audit-reports/companion-links.csv',[['page','label','url','status','check','final_url'].join(','),...rows.map(x=>[x.page,x.label,x.url,x.status,x.check,x.final_url].map(csv).join(','))].join('\n')+'\n');
console.log(JSON.stringify(summary,null,2));
if(summary.errors)process.exitCode=1;
