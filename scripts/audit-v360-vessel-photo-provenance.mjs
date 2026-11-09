#!/usr/bin/env node
// V360: inspect vessel-photo claims in existing ferry guide pages.
// Source, photographer, license and condition must be checked manually.
import fs from 'node:fs';
import path from 'node:path';
const root='site',files=[],rows=[];
function walk(d){for(const e of fs.readdirSync(d,{withFileTypes:true})){const p=path.join(d,e.name);if(e.isDirectory())walk(p);else if(e.isFile()&&p.endsWith('.html'))files.push(p)}}
walk(root);
for(const file of files){
 if(!/ferry|cruise|booking|guide/.test(file))continue;
 const html=fs.readFileSync(file,'utf8');
 for(const m of html.matchAll(/<img\b[^>]*>/gi)){
  const tag=m[0],src=(tag.match(/\bsrc=["']([^"']+)["']/i)||[])[1]||'',alt=(tag.match(/\balt=["']([^"']*)["']/i)||[])[1]||'';
  if(!/camellia|panstar|ferry|ship|cruise|카멜리아|팬스타|선박|여객선|페리|크루즈/i.test(src+' '+alt))continue;
  const nearby=html.slice(Math.max(0,m.index-400),Math.min(html.length,m.index+1000));
  const credits=/촬영자|저작자|photo credit|출처|라이선스|license/i.test(nearby);
  const date=/20\d{2}[년.\-/]|촬영일/i.test(nearby);
  const label=/AI\s*연출|참고\s*이미지|실제\s*사진|실사/i.test(nearby);
  rows.push({page:'/'+path.relative(root,file).replaceAll('\\','/').replace(/index\.html$/,''),src,alt,nearbyCreditMention:credits,nearbyDateMention:date,contextLabel:label,priority:/camellia|카멜리아/i.test(src+' '+alt)?'new-camellia-first':'normal',review:'Visually inspect rust/condition; verify exact vessel, capture date, source and commercial license. Text proximity is not proof of rights.'});
 }
}
rows.sort((a,b)=>Number(b.priority==='new-camellia-first')-Number(a.priority==='new-camellia-first'));
fs.mkdirSync('audit-reports/v360',{recursive:true});
fs.writeFileSync('audit-reports/v360/vessel-photo-provenance.json',JSON.stringify({pagesScanned:files.length,candidates:rows.length,rows},null,2)+'\n');
console.log(JSON.stringify({pagesScanned:files.length,vesselPhotoCandidates:rows.length,newCamelliaPriority:rows.filter(x=>x.priority==='new-camellia-first').length}));
