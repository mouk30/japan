#!/usr/bin/env node
/**
 * V280 evidence-gated FINAL RELEASE BLOCKER audit.
 * Checks local main-baseline structure and dated evidence integrity only.
 * PASS does not authorize merge or assert an authenticated Preview render.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const evidence=JSON.parse(fs.readFileSync(new URL('../audit-reports/v280-stay-final-release-gate.json',import.meta.url),'utf8'));
assert.equal(evidence.stage,'V280');
assert.equal(evidence.repository,'mouk30/japan');
assert.equal(evidence.scope.existingGuides,28);
assert.equal(evidence.scope.newArticles,0);
assert.equal(evidence.scope.paths.length,28);
assert.equal(new Set(evidence.scope.paths).size,28);
assert(evidence.scope.paths.every(p=>/^site\/stay\/(?:[a-z-]+\/)?index\.html$/.test(p)));
const existing=['site/stay/index.html',...fs.readdirSync('site/stay',{withFileTypes:true})
 .filter(d=>d.isDirectory()&&fs.existsSync(path.join('site/stay',d.name,'index.html')))
 .map(d=>'site/stay/'+d.name+'/index.html')].sort();
assert.deepEqual(existing,[...evidence.scope.paths].sort(),'28-page scope differs from actual site');
const sitemap=fs.readFileSync('site/sitemap.xml','utf8');
const robots=fs.readFileSync('site/robots.txt','utf8');
assert.match(robots,/Sitemap:\s*https:\/\/www\.nipponferry\.com\/sitemap\.xml/);
const locs=[...sitemap.matchAll(/<loc>(https:\/\/www\.nipponferry\.com\/stay\/[^<]*)<\/loc>/g)].map(m=>m[1]);
assert.equal(locs.length,28,'Expected 28 existing /stay/ sitemap URLs');
let links=0,legacyImageReferences=0;
for(const file of existing){
 const html=fs.readFileSync(file,'utf8');
 const url=file==='site/stay/index.html'?'/stay/':'/stay/'+file.split('/')[2]+'/';
 const title=html.match(/<title>([\s\S]*?)<\/title>/i)?.[1]||'';
 const desc=html.match(/<meta\s+name=['"]description['"]\s+content=['"]([^'"]+)/i)?.[1]||'';
 const canonical=html.match(/<link\s+rel=['"]canonical['"]\s+href=['"]([^'"]+)/i)?.[1];
 assert.ok(title.length>10,'Missing title '+file);
 assert.ok(desc.length>20,'Missing description '+file);
 assert.equal(canonical,'https://www.nipponferry.com'+url,'Canonical mismatch '+file);
 assert.match(html,/<meta\s+name=['"]robots['"]\s+content=['"]index,follow/i,'Robots policy changed '+file);
 assert.match(html,/<h1\b/i,'Missing H1 '+file);
 assert.ok(locs.includes('https://www.nipponferry.com'+url),'Missing sitemap entry '+file);
 assert.match(html,/class=['"]stay-convert['"]/,'Ferry booking section missing '+file);
 assert.match(html,/class=['"]stay-ferry-note['"]/,'Ferry vs lodging disclaimer missing '+file);
 assert.doesNotMatch(html,/kids-stay\.com|kidsstay-v5\.vercel\.app/i,'Unapproved KidsStay link '+file);
 assert.match(html,/href=['"]\/booking\//,'Booking guide link missing '+file);
 links += [...html.matchAll(/<a\b[^>]*\bhref=/gi)].length;
 legacyImageReferences += [...html.matchAll(/(?:src=['"]|url\(['"]?)\/stay\/assets\/[^'"\)]+/gi)].length;
}
assert(legacyImageReferences>0,'Expected existing legacy media risk on main baseline; review report if changed');
assert.equal(evidence.releaseGates.authenticatedVercelPreview.startsWith('BLOCKED:'),true);
assert.equal(evidence.releaseGates.integratedCandidateCI.startsWith('NOT RUN'),true);
assert.equal(evidence.decision.stageComplete,false);
assert.equal(evidence.decision.readyToMerge,false);
assert.equal(evidence.decision.readyForProduction,false);
assert.equal(evidence.decision.merged,false);
assert.equal(evidence.decision.productionDeployed,false);
assert(evidence.headChecksFreshlyVerified.every(x=>x.workflowRuns===5&&x.allCompletedSuccess));
console.log('V280 EVIDENCE/BASELINE INTEGRITY PASS: '+existing.length+' existing stay guides, '+links+' links, '+legacyImageReferences+' legacy media references.');
console.log('V280 RELEASE GATE BLOCKED: photo rights, overlapping PRs, integrated CI and authenticated Vercel Preview are NOT verified. NO MERGE OR PRODUCTION APPROVAL.');
