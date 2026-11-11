import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
const registry=JSON.parse(fs.readFileSync('audit-reports/v282/photo-first-pilot-registry.json','utf8'));
assert.equal(registry.version,'V282');
assert.equal(registry.modified.length,3);
const css=fs.readFileSync('site/v282-magazine.css','utf8');
assert.ok(css.includes('aspect-ratio:4/3')&&css.includes('max-width:620px')&&css.includes('focus-visible'),'Responsive/accessibility styles missing');
const baseline=registry.baselineMain;
function rawHead(html){
 const head=html.match(/<head>([\s\S]*?)<\/head>/)?.[1]||'';
 assert.ok(head,'Head missing');return head;
}
function refs(html){return [...html.matchAll(/\bhref=["']([^"']+)["']/g)].map(x=>x[1])}
function tagHead(head,regexp,label){const a=head.match(regexp)?.[0];assert.ok(a,'Missing '+label);return a}
let imageChecks=0;
const photoRecords=registry.photos;
for(const r of registry.modified){
 const h=fs.readFileSync(r.path,'utf8');
 const old=execFileSync('git',['show',baseline+':'+r.path],{encoding:'utf8',maxBuffer:8*1024*1024});
 assert.match(h,/<body class="nf-premium-v2 nf-v282">/,'Scoped body class missing '+r.path);
 assert.equal((h.match(/class="nf-v282-card"/g)||[]).length,3,'3 subject cards missing');
 assert.equal((h.match(/class="nf-v282-warning"/g)||[]).length,1,'Visible gate/return warning absent');
 assert.equal((h.match(/class="nf-v282-license"/g)||[]).length,1,'Photo rights disclosure absent');
 assert.equal((h.match(/<h1\b/gi)||[]).length,1,'One H1 required');
 assert.ok(h.includes('href="/v282-magazine.css?v=20261101"'));
 const oldHead=rawHead(old),newHead=rawHead(h);
 for(const [name,rx] of [
  ['title',/<title>[\s\S]*?<\/title>/],
  ['meta description',/<meta name=["']description["'][^>]*>/],
  ['canonical',/<link rel=["']canonical["'][^>]*>/],
  ['robots',/<meta name=["']robots["'][^>]*>/],
  ['og:image',/<meta property=["']og:image["'][^>]*>/],
  ['OG title',/<meta property=["']og:title["'][^>]*>/],
  ['JSON-LD',/<script type=["']application\/ld\+json["']>[\s\S]*?<\/script>/]
 ]){
  const a=oldHead.match(rx)?.[0],b=newHead.match(rx)?.[0];
  if(a||b)assert.equal(b,a,'Original '+name+' changed '+r.path);
 }
 const oldRefs=new Set(refs(old)),newRefs=new Set(refs(h));
 for(const href of oldRefs) assert.ok(newRefs.has(href),'Previously existing link removed '+r.path+' => '+href);
 const oldIDs=new Set([...old.matchAll(/\bid=["']([^"']+)["']/g)].map(x=>x[1]));
 const newIDs=new Set([...h.matchAll(/\bid=["']([^"']+)["']/g)].map(x=>x[1]));
 for(const id of oldIDs)assert.ok(newIDs.has(id),'Original section/anchor lost '+r.path+' '+id);
 for(const item of r.cards)assert.ok(newIDs.has(item.href.slice(1)),'Photo card broken hash '+item.href);
 for(const link of [...h.matchAll(/href="#([^"]+)"/g)])assert.ok(newIDs.has(link[1]),'Broken hash target '+link[1]+' in '+r.path);
 for(const p of [r.hero,...r.cards.map(z=>z.src)]){
  const actual=Object.values(photoRecords).find(x=>x.src===p);
  assert.ok(actual,'Unregistered image '+p);
  const b=fs.readFileSync('site'+p);
  assert.equal(b.toString('ascii',0,4),'RIFF','Not WebP '+p);
  assert.equal(b.toString('ascii',8,12),'WEBP','Not WebP '+p);
  const sha=crypto.createHash('sha1').update(Buffer.from('blob '+b.length+'\0')).update(b).digest('hex');
  assert.equal(sha,actual.sha,'Photo source content changed; re-license check required '+p);
  assert.ok(h.includes(actual.url)&&h.includes(actual.licenseURL)&&h.includes(actual.author),'Photo attribution incomplete '+p);
  imageChecks++;
 }
 if(r.path.includes('/things-to-do/')){
  assert.equal((h.match(/<details class="nf-v282-archive"/g)||[]).length,1,'Archive absent '+r.path);
  assert.ok(h.includes('최종 승객 귀선'),'Required passenger return safety missing '+r.path);
  const marker=h.indexOf('<section class="v69-port"');
  const details=h.indexOf('</details><section class="v69-port"');
  assert.ok(details>=0&&details===marker-10,'Archive not closed before remaining content '+r.path);
 }
 assert.equal((h.match(/class="nf-v282-card-grid"/g)||[]).length,1);
}
const allPagePaths=['site/things-to-do/kobe-cruise-port-day-trip/index.html','site/things-to-do/hakata-cruise-port-day-trip/index.html','site/japan/kobe/index.html'];
assert.deepEqual(registry.modified.map(x=>x.path),allPagePaths);
console.log('V282 STATIC PASS: 3 existing pages; original SEO, all original href/IDs, licensed WebP SHA and photo credits preserved; '+imageChecks+' image references checked.');
