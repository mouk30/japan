import { readdir, readFile, mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
const root='site';
async function walk(dir) {let out=[];for(const ent of await readdir(dir,{withFileTypes:true})){const full=path.join(dir,ent.name);if(ent.isDirectory())out.push(...await walk(full));else if(ent.name==='index.html')out.push(full)}return out}
const files=await walk(root),cards=[];
for(const file of files){
 const html=await readFile(file,'utf8');
 // Card-level scan: anchor with image and visible heading; avoid linking unrelated page images.
 for(const m of html.matchAll(/<a\b([^>]*)>([\s\S]*?)<\/a>/gi)){
  const href=m[1].match(/\bhref=["']([^"']+)/i)?.[1],img=m[2].match(/<img\b[^>]*>/i)?.[0];
  if(!href||!img)continue;
  const src=img.match(/\bsrc=["']([^"']+)/i)?.[1],alt=img.match(/\balt=["']([^"']*)/i)?.[1]||'';
  const heading=m[2].match(/<h[2-4]\b[^>]*>([\s\S]*?)<\/h[2-4]>/i)?.[1];
  if(!src||!heading)continue;
  const title=heading.replace(/<[^>]+>/g,'').replace(/&[^;]+;/g,' ').trim();
  if(!title)continue;
  cards.push({page:'/'+path.relative(root,file).replaceAll('\\','/').replace(/index\.html$/,''),href,src,alt,title});
 }
}
const by=new Map();for(const c of cards){if(!by.has(c.src))by.set(c.src,[]);by.get(c.src).push(c)}
const repeated=[...by.entries()].filter(([src,arr])=>arr.length>1).map(([src,arr])=>({src,count:arr.length,distinctTitles:new Set(arr.map(c=>c.title)).size,examples:arr.slice(0,20)})).sort((a,b)=>b.count-a.count);
const suspect=cards.filter(c=>/\/images\/(rail|car|hokkaido)\.jpg$/.test(c.src)).map(c=>({...c,reason:'generic image requiring exact location, transport and rights review'}));
const report={filesScanned:files.length,cardsScanned:cards.length,uniqueImages:by.size,repeatedImageGroups:repeated.length,repeated,suspect,notes:['Duplicate images are review candidates, not automatically confirmed errors.','Do not replace without verifying location, season, subject, creator, source and commercial reuse license.','This static scan does not validate image pixels or CSS background imagery.']};
await mkdir('audit-reports/v353',{recursive:true});
await writeFile('audit-reports/v353/sitewide-card-inventory.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({filesScanned:files.length,cardsScanned:cards.length,repeatedImageGroups:repeated.length,suspectCount:suspect.length,topRepeated:repeated.slice(0,8).map(x=>({src:x.src,count:x.count,distinctTitles:x.distinctTitles}))},null,2));
