import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
const site='site',root='https://www.nipponferry.com',targets=[
 {file:'stay/index.html',url:'/stay/'},
 {file:'stay/family/index.html',url:'/stay/family/'},
 {file:'kids/index.html',url:'/kids/'}
];
const sitemap=fs.readFileSync(path.join(site,'sitemap.xml'),'utf8');
const robots=fs.readFileSync(path.join(site,'robots.txt'),'utf8');
assert.match(robots,/Sitemap:\s*https:\/\/www\.nipponferry\.com\/sitemap\.xml/);
assert.match(robots,/Allow:\s*\//);
let checkedReferences=0;
for(const t of targets){
 const source=fs.readFileSync(path.join(site,t.file),'utf8');
 const title=source.match(/<title>(.*?)<\/title>/i)?.[1]||'';
 const meta=source.match(/<meta\s+name=['"]description['"]\s+content=['"]([^'"]+)/i)?.[1]||'';
 const canonical=source.match(/<link\s+rel=['"]canonical['"]\s+href=['"]([^'"]+)/i)?.[1];
 assert.ok(title.length>15,'missing title: '+t.url);
 assert.ok(meta.length>30,'missing description: '+t.url);
 assert.equal(canonical,root+t.url,'canonical mismatch '+t.url);
 assert.match(source,/<meta\s+name=['"]robots['"]\s+content=['"]index,follow/i,'indexing policy changed '+t.url);
 assert.match(source,/<h1\b/i,'missing H1 '+t.url);
 assert.ok(sitemap.includes('<loc>'+root+t.url+'</loc>'),'sitemap omits '+t.url);
 assert.doesNotMatch(source,/kidsstay-v5\.vercel\.app|kids-stay\.com|kid[s-]?stay\.com/i,
  'public NIPPONFERRY guide must not link an unverified KidsStay booking service '+t.url);
 // Assert only references in static HTML. Running this script does not prove public-site HTTP status.
 const links=[...source.matchAll(/\b(?:href|src)=["'](\/[^"'#]+)["']/g)].map(m=>m[1]);
 for(const url of links){
  if(url.startsWith('//'))continue;
  const localPath=url.split('?')[0].split('#')[0];
  const rel='site'+localPath;
  const destination=path.resolve(rel);
  assert.ok(destination.startsWith(path.resolve(site)+path.sep),'invalid local destination');
  const exact=fs.existsSync(destination)&&fs.statSync(destination).isFile();
  const folderIndex=fs.existsSync(path.join(destination,'index.html'));
  assert.ok(exact||folderIndex,'missing local link or asset '+t.url+' => '+url);
  checkedReferences++;
 }
 console.log('PASS '+t.url+' | local refs '+links.length+' | canonical/SEO/sitemap retained | no unverified KidsStay link');
}
assert.ok(checkedReferences>=150);
console.log('V251 PASS: 3 existing NIPPONFERRY pages, '+checkedReferences+' local links/assets checked; no new pages, no live booking claims.');
