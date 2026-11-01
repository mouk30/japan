import assert from "node:assert/strict";
import fs from "node:fs";
import crypto from "node:crypto";
import {execFileSync} from "node:child_process";
const m=JSON.parse(fs.readFileSync("audit-reports/v284/three-photo-first-cruise-ports.json","utf8"));
assert.equal(m.version,"V284");assert.equal(m.changes.length,3);
const css=fs.readFileSync("site/v284-cruise-ports-magazine.css","utf8");
assert.ok(css.includes("object-fit:cover")&&css.includes("max-width:620px"));
function blob(buf){return crypto.createHash("sha1").update(Buffer.from("blob "+buf.length+"\0")).update(buf).digest("hex")}
function htmlHead(h){return h.match(/<head>([\s\S]*?)<\/head>/)?.[1]||""}
for(const c of m.changes){
 const newHtml=fs.readFileSync(c.path,"utf8");
 const origBuf=execFileSync("git",["show",m.baseCommit+":"+c.path],{maxBuffer:12*1024*1024});
 const orig=origBuf.toString("utf8");
 assert.equal(blob(origBuf),c.oldFileBlob,"Baseline source changed "+c.path);
 for(const rx of [/<title>[\s\S]*?<\/title>/,/<meta name="description"[^>]*>/,/<meta name="robots"[^>]*>/,/<link rel="canonical"[^>]*>/,/<meta property="og:title"[^>]*>/,/<meta property="og:url"[^>]*>/,/<script type="application\/ld\+json">[\s\S]*?<\/script>/]){
  assert.equal(htmlHead(newHtml).match(rx)?.[0],htmlHead(orig).match(rx)?.[0],"SEO/schema changed "+c.path+" "+rx);
 }
 assert.equal((newHtml.match(/<h1\b/g)||[]).length,1,"One H1 required "+c.path);
 assert.equal((newHtml.match(/class="nf-v282-card nf-v284-card"/g)||[]).length,3,"3 photo cards");
 assert.equal((newHtml.match(/class="nf-v283-topic nf-v284-topic"/g)||[]).length,3,"3 exact explanations");
 assert.equal((newHtml.match(/class="nf-v282-warning nf-v284-warning"/g)||[]).length,1,"Visible return warning");
 assert.equal((newHtml.match(/class="nf-v282-license nf-v284-license"/g)||[]).length,1,"Photo attribution section");
 assert.ok(newHtml.includes('class="nf-premium-v2 nf-v282 nf-v284"'));
 for(const name of ["/v282-magazine.css","/v283-topic-targets.css","/v284-cruise-ports-magazine.css"])assert.ok(newHtml.includes(name));
 assert.ok(newHtml.includes("승객 최종 귀선")&&newHtml.includes("출항 시간과 귀선 마감 시각은 다를 수 있다"));
 const originalIds=[...orig.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);
 const allIds=[...newHtml.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);
 const ids=new Set(allIds);assert.equal(ids.size,allIds.length,"Duplicate document IDs");
 for(const id of originalIds)assert.ok(ids.has(id),"Original anchor removed "+id);
 const oldLinks=new Set([...orig.matchAll(/\bhref="([^"]+)"/g)].map(x=>x[1]));
 const newLinks=new Set([...newHtml.matchAll(/\bhref="([^"]+)"/g)].map(x=>x[1]));
 for(const link of oldLinks)assert.ok(newLinks.has(link),"Original booking or source URL removed "+link);
 const thumbs=[...newHtml.matchAll(/<a class="nf-v282-card nf-v284-card" href="#([^"]+)"[^>]*>([\s\S]*?)<\/a>/g)];
 assert.equal(thumbs.length,3);
 for(const [i,item] of c.cards.entries()){
  assert.equal(thumbs[i][1],item.id,"Wrong image card destination "+item.id);
  assert.ok(thumbs[i][2].includes(item.title));
  assert.ok(ids.has(item.id));
  assert.ok(newHtml.includes('<h3 id="'+item.id+'-title">'+item.title+'</h3>'));
  const at=newHtml.indexOf('id="'+item.id+'"');
  const content=newHtml.slice(Math.max(0,at-180),at+1500);
  assert.ok(content.includes('class="nf-v283-topic nf-v284-topic"')&&content.includes("<p>"),"Missing relevant place explanation "+item.id);
  const photo=m.photos[item.photo];assert.ok(photo);
  assert.ok(thumbs[i][2].includes(photo.src),"Photographed place does not match title "+item.title);
  assert.ok(newHtml.includes('href="'+photo.origin+'"')&&newHtml.includes('href="'+photo.licenseUrl+'"')&&newHtml.includes(photo.author),"Original photo credit missing "+item.photo);
  assert.equal(blob(fs.readFileSync("site"+photo.src)),photo.sha,"Photo changed without new licensing "+item.photo);
  assert.ok(ids.has(item.support.slice(1)),"Original supporting guide lost "+item.support);
 }
 const hero=m.photos[c.hero];assert.ok(newHtml.includes(hero.src));
 assert.equal(blob(fs.readFileSync("site"+hero.src)),hero.sha);
 for(const ref of [...newHtml.matchAll(/href="#([^"]+)"/g)])assert.ok(ids.has(ref[1]),"Broken hash #"+ref[1]+" in "+c.path);
}
console.log("V284 STATIC PASS: 3 original pages, 9 individually matching place/photo/cards, exact photo blobs, original SEO/schema/booking/safety and ID/link graph preserved.");
