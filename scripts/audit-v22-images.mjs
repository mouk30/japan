// V22 repository-wide cruise imagery structure audit (read-only).
import fs from 'node:fs';
import path from 'node:path';
const root='site/things-to-do';
const dirs=fs.readdirSync(root,{withFileTypes:true}).filter(d=>d.isDirectory()&&d.name.includes('cruise'));
const rows=dirs.filter(d=>fs.existsSync(path.join(root,d.name,'index.html'))).map(d=>{
 const src=fs.readFileSync(path.join(root,d.name,'index.html'),'utf8');
 const companion=/cruise-(family|couple|parents)-guide$/.test(d.name);
 const usesStyles=src.includes('href="/style.css"') || (companion && src.includes('/companion-card-standard.css'));
 const companionStyles=src.includes('/companion-card-standard.css');
 const portHero=/<header[^>]*>[\s\S]*?<img[^>]+src=["'][^"']*(?:cruise-port|\/v\d+_)[^"']*["'][^>]*>/i.test(src);
 const venueGallery=src.includes('id="ct-topic-dashboard"');
 return {page:d.name,type:companion?'companion':'port',usesStyles,companionStyles,portHero,venueGallery};
});
const companion=rows.filter(x=>x.type==='companion'),ports=rows.filter(x=>x.type==='port');
const errors=rows.flatMap(x=>[
 ...(!x.usesStyles?[x.page+': common CSS missing']:[]),
 ...(x.type==='companion'&&(!x.companionStyles||!x.venueGallery)?[x.page+': venue gallery CSS or section missing']:[]),
 ...(x.type==='port'&&!x.portHero?[x.page+': editorial port hero pattern needs manual review']:[])
]);
const style=fs.readFileSync('site/style.css','utf8');
const cards=fs.readFileSync('site/companion-card-standard.css','utf8');
if(!style.includes('V22 Cruise port articles')||!style.includes('legacy cruise-port templates'))errors.push('image-first common style missing');
if(!cards.includes('V21 · image-first'))errors.push('companion image-first CSS missing');
const result={checked:rows.length,companion:companion.length,port:ports.length,errors:errors.length,sample:errors.slice(0,50)};
fs.mkdirSync('audit-reports/v22',{recursive:true});
fs.writeFileSync('audit-reports/v22/structure.json',JSON.stringify(result,null,2)+'\n');
console.log('V22_IMAGE_STRUCTURE',JSON.stringify(result));
if(errors.length)process.exitCode=1;
