#!/usr/bin/env node
// V355: read-only inventory of ferry/ship photos for human visual and license review.
// Pixel-level rust, vessel identity and rights CANNOT be inferred from filenames.
import fs from 'node:fs';
import path from 'node:path';
const root=process.cwd(), site=path.join(root,'site');
const output=path.join(root,'audit-reports/v355');
const files=[];
function walk(dir){if(!fs.existsSync(dir))return;for(const ent of fs.readdirSync(dir,{withFileTypes:true})){const p=path.join(dir,ent.name);if(ent.isDirectory())walk(p);else if(ent.isFile()&&p.endsWith('.html'))files.push(p);}}
walk(site);
const ship=/ferry|cruise|camellia|panstar|ship|vessel|boat|선박|페리|크루즈|카멜리아|부관훼리|관부훼리|팬스타|뉴카멜리아/i;
const rows=[];
for(const file of files){
 const html=fs.readFileSync(file,'utf8');
 const title=(html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)||[])[1]||'';
 const imgs=html.match(/<img\b[^>]*>/gi)||[];
 for(const tag of imgs){
  const src=(tag.match(/\bsrc\s*=\s*["']([^"']+)["']/i)||[])[1]||'';
  const alt=(tag.match(/\balt\s*=\s*["']([^"']*)["']/i)||[])[1]||'';
  const isHero=/article-cover|hero|featured|lead|cover/i.test(tag);
  if(!ship.test(src+' '+alt+' '+title)&&!isHero)continue;
  const rel=path.relative(root,file).replaceAll('\\','/');
  const local=src.startsWith('/')?path.join(site,src.slice(1)):null;
  const exists=local?fs.existsSync(local):null;
  rows.push({page:rel,title:title.replace(/<[^>]+>/g,'').trim(),src,alt,isHero,localAssetExists:exists,manualReview:['rust/stains and condition','correct vessel/port','capture date','author and commercial-use license','visual quality']});
 }
}
rows.sort((a,b)=>Number(b.isHero)-Number(a.isHero)||a.page.localeCompare(b.page));
fs.mkdirSync(output,{recursive:true});
fs.writeFileSync(path.join(output,'ferry-photo-candidates.json'),JSON.stringify({note:'Candidates only; no automated rust or rights verdict. No photo replaced.',pagesScanned:files.length,imagesFlagged:rows.length,rows},null,2));
fs.writeFileSync(path.join(output,'ferry-photo-candidates.csv'),['page,src,hero,local_asset_exists,alt',...rows.map(r=>[r.page,r.src,r.isHero,r.localAssetExists,r.alt].map(v=>'"'+String(v??'').replaceAll('"','""')+'"').join(','))].join('\n')+'\n');
console.log(JSON.stringify({pagesScanned:files.length,imagesFlagged:rows.length,heroCandidates:rows.filter(r=>r.isHero).length,missingLocalAssets:rows.filter(r=>r.localAssetExists===false).length}));
