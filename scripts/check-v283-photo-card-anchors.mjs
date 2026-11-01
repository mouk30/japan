import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
const report=JSON.parse(fs.readFileSync('audit-reports/v283/photo-card-targets-and-legacy-qa.json','utf8'));
const registry=JSON.parse(fs.readFileSync('audit-reports/v282/photo-first-pilot-registry.json','utf8'));
const oldBase=report.baseHead;
assert.equal(report.version,'V283');
assert.equal(registry.modified.length,3);
const css=fs.readFileSync('site/v283-topic-targets.css','utf8');
assert.ok(css.includes('scroll-margin-top')&&css.includes(':target')&&css.includes('max-width:620px'));
let targets=0;
function links(html){return [...html.matchAll(/<a\b[^>]*\bhref=["']([^"']+)["']/g)].map(m=>m[1])}
function titleHead(html){const s=html.match(/<head>([\s\S]*?)<\/head>/)?.[1];assert.ok(s);return s}
for(const page of report.pages){
 const current=fs.readFileSync(page.path,'utf8');
 const before=execFileSync('git',['show',oldBase+':'+page.path],{encoding:'utf8',maxBuffer:8*1024*1024});
 const prior=registry.modified.find(p=>p.path===page.path);
 assert.ok(prior,'Missing V282 predecessor '+page.path);
 assert.equal((current.match(/class="nf-v282-card"/g)||[]).length,3);
 assert.equal((current.match(/<h1\b/gi)||[]).length,1);
 assert.ok(current.includes('href="/v283-topic-targets.css?v=20261101"'));
 for(const expression of [
 /<title>[\s\S]*?<\/title>/,
 /<meta name=["']description["'][^>]*>/,
 /<link rel=["']canonical["'][^>]*>/,
 /<meta name=["']robots["'][^>]*>/,
 /<meta property=["']og:image["'][^>]*>/
 ]){
  assert.equal(titleHead(current).match(expression)?.[0],titleHead(before).match(expression)?.[0],'SEO metadata regressed '+page.path);
 }
 const schema=/\b<script type=["']application\/ld\+json["']>[\s\S]*?<\/script>/g;
 assert.deepEqual([...current.matchAll(schema)].map(x=>x[0]),[...before.matchAll(schema)].map(x=>x[0]),'Schema changed '+page.path);
 const baselineLinks=links(before);
 const oldCardRefs=prior.cards.map(c=>c.originalV282Href);
 const currentLinks=links(current);
 for(const ref of new Set(baselineLinks)){
  const allowedLoss=oldCardRefs.filter(x=>x===ref).length;
  const beforeCount=baselineLinks.filter(x=>x===ref).length;
  const currentCount=currentLinks.filter(x=>x===ref).length;
  assert.ok(currentCount>=beforeCount-allowedLoss,'Non-card existing link lost '+page.path+' '+ref);
 }
 const oldIDs=new Set([...before.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]));
 const newIDs=[...current.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);
 const idSet=new Set(newIDs);
 assert.equal(newIDs.length,idSet.size,'Duplicate DOM IDs '+page.path);
 for(const id of oldIDs)assert.ok(idSet.has(id),'Existing article target removed '+page.path+' '+id);
 assert.equal(page.targets.length,3);
 const expectedRefs=page.targets.map(t=>'#'+t.id);
 assert.equal(new Set(expectedRefs).size,3,'Photo cards must not share a generic anchor');
 const cardMarkup=[...current.matchAll(/<a class="nf-v282-card" href="([^"]+)">([\s\S]*?)<\/a>/g)];
 assert.equal(cardMarkup.length,3);
 for(const [index,t] of page.targets.entries()){
  const card=cardMarkup[index];
  assert.equal(card[1],'#'+t.id,'Wrong exact photo link for '+t.label);
  assert.ok(card[2].includes(t.label),'Card title/context mismatch '+t.label);
  assert.ok(idSet.has(t.id),'Missing physical destination '+t.id);
  const targetStart=current.indexOf('id="'+t.id+'"');
  assert.ok(targetStart>=0);
  const local=current.slice(targetStart,targetStart+650);
  assert.ok(local.includes(t.mustInclude),'Destination not about the correct place '+t.label);
  if(t.type==='new-scoped-detail'){
   assert.ok(local.includes('class="nf-v283-topic"')||current.slice(Math.max(0,targetStart-90),targetStart).includes('nf-v283-topic'),'Missing dedicated factual description');
   assert.ok(local.includes('<p>')&&local.includes('</p>'),'No actual visible details at destination '+t.id);
  }
  if(t.supportingAnchor)assert.ok(idSet.has(t.supportingAnchor),'Supporting older travel detail missing '+t.supportingAnchor);
  targets++;
 }
 for(const hash of [...current.matchAll(/href="#([^"]+)"/g)])assert.ok(idSet.has(hash[1]),'Broken hash destination '+hash[1]);
 assert.ok(current.includes('최종 승객 귀선')||current.includes('귀선')||current.includes('승선'));
 assert.equal((current.match(/class="nf-v282-warning"/g)||[]).length,1);
 assert.equal((current.match(/class="nf-v282-license"/g)||[]).length,1);
 for(const priorImage of [...before.matchAll(/<img\b[^>]*src="([^"]+)"/g)].map(x=>x[1])){
  assert.ok(current.includes('src="'+priorImage+'"'),'V282 verified source image removed '+priorImage);
 }
}
assert.equal(targets,9);
console.log('V283 STATIC PASS: 9 unique attraction-specific targets; original SEO/schema/IDs/old links and V282 photos preserved on 3 existing pages.');
