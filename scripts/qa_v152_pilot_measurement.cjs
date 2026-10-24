#!/usr/bin/env node
"use strict";
// V152: no GA4 ID/consent -> no analytics, plus 3-pilot event labels and source QA.
const fs=require("fs"),vm=require("vm"),assert=require("node:assert/strict"),cp=require("child_process"),path=require("path");
const slugs={"naoshima-art-ferry-return":"naoshima","teshima-art-ferry-return":"teshima","takamatsu-cruise-udon-market-return":"shikoku_food"};
const allowed=new Set(["museum_ticket","museum_info","ferry_schedule","island_transport","return_plan","port_return","booking_guide","official_food"]);
const hrefList=h=>[...h.matchAll(/<a\b[^>]*\bhref=(["'])(.*?)\1[^>]*>([\s\S]*?)<\/a>/gi)].map(m=>m[2]+" | "+m[3].replace(/<[^>]+>/g," ").replace(/\s+/g," ").trim());
const match=(re,s)=>[...s.matchAll(re)].map(x=>x[1]);
const errors=[];
for(const [slug,id] of Object.entries(slugs)){
 const p="site/things-to-do/"+slug+"/index.html";
 const html=fs.readFileSync(p,"utf8");
 const orig=cp.execFileSync("git",["show","origin/main:"+p],{encoding:"utf8"});
 const imgMatch=/<img\b[^>]*>/gi;
 const a=html.match(imgMatch)||[], b=orig.match(imgMatch)||[];
 const attrsRe=/\b(src|alt|width|height|loading)=["'][^"']*["']/gi;
 const im=x=>x.map(z=>(z.match(attrsRe)||[]).join("|"));
 assert.deepEqual(im(a),im(b),"original image/ALT preserved "+slug);
 assert.deepEqual(hrefList(html),hrefList(orig),"no destination or anchor label changes "+slug);
 assert.equal(match(/<link\b[^>]*rel="canonical"[^>]*href="([^"]+)"/gi,html)[0],
               match(/<link\b[^>]*rel="canonical"[^>]*href="([^"]+)"/gi,orig)[0],slug+" canonical");
 assert.equal((html.match(/<h1\b/g)||[]).length,(orig.match(/<h1\b/g)||[]).length,slug+" H1");
 assert.ok(html.includes('data-nf-pilot="'+id+'"'),slug+" unique pilot id");
 const actions=match(/\bdata-nf-pilot-action="([^"]+)"/g,html);
 assert.ok(actions.length>=6,slug+" events expected");
 assert.ok(actions.every(x=>allowed.has(x)),slug+" whitelisted action");
 assert.ok(actions.includes("return_plan")&&actions.includes("booking_guide"),slug+" booking and return separately counted");
 if(slug.startsWith("takamatsu-"))assert.ok(actions.includes("official_food")&&actions.includes("port_return"));
 else assert.ok(actions.includes("museum_ticket")&&actions.includes("ferry_schedule"));
 assert.ok(html.includes('id="nf-v148-photo-credits"'),slug+" photo license still exists");
 assert.ok(!html.slice(html.indexOf('id="nf-v148-photo-credits"')).includes('data-nf-pilot-action='),slug+" photo rights not counted as booking");
 console.log("SOURCE PASS",id,actions.length,actions.reduce((o,k)=>(o[k]=(o[k]||0)+1,o),{}));
}
// Verify only build-time GA4 ID injection, and no hardcoded data collection in pilot templates.
const build=fs.readFileSync("build.js","utf8");
assert.ok(build.includes("process.env.GA4_MEASUREMENT_ID"),"env GA4 source");
assert.ok(build.includes("if (ga4Id)"),"ID gated");
assert.ok(build.includes("/nf-v93-booking-clicks.js?v=20261024-v152"),"cachebuster");
const analytics=fs.readFileSync("site/nf-v93-booking-clicks.js","utf8");
assert.ok(!/function\s+eval\s*\(/.test(analytics));
assert.ok(analytics.includes("nf_pilot_guide_view")&&analytics.includes("nf_pilot_action_click"));
assert.ok(analytics.includes("!event.isTrusted || !enabled"),"no synthetic clicks and no collection when disabled");
function testVM(id,consent){
 const store=new Map(consent?[["nf93_analytics_choice_v1",consent]]:[]);
 const events={},addedScripts=[],addedBody=[];
 const element=(tag)=>({
   tagName:tag,events:{},hidden:true,attrs:{},
   addEventListener(k,cb){this.events[k]=cb;},
   appendChild(child){this.children=(this.children||[]).concat([child]);},
   setAttribute(k,v){this.attrs[k]=v;},
   getAttribute(k){return this.attrs[k]||null;},
   querySelector(sel){this.refs=this.refs||{};return this.refs[sel]||(this.refs[sel]=element("button"));},
   dispatch(type){assert.ok(this.events[type],this.tagName+"/"+type+" registered");return this.events[type]();}
 });
 const body=element("body");body.appendChild=x=>addedBody.push(x);
 const head=element("head");head.appendChild=x=>addedScripts.push(x);
 const document={currentScript:{getAttribute(k){return k==="data-nf-ga4"?id:null}},
   readyState:"loading",body,head,
   addEventListener(k,cb){events[k]=cb;},
   createElement:element,querySelector(){return null;}};
 const win={};
 const location={pathname:"/things-to-do/naoshima-art-ferry-return/",hostname:"www.nipponferry.com"};
 const storage={getItem(k){return store.has(k)?store.get(k):null;},
   setItem(k,v){store.set(k,v)}};
 vm.runInNewContext(analytics,{document,location,window:win,localStorage:storage,URL,Date,encodeURIComponent,console},{filename:"site/nf-v93-booking-clicks.js"});
 if(!id)return {events,addedScripts,addedBody,win,store};
 assert.ok(events.click&&events.DOMContentLoaded,"consent listener installed");
 events.DOMContentLoaded();
 assert.equal(addedScripts.length,consent==="yes"?1:0,"analytics library gated by explicit user consent");
 const dialog=addedBody.find(x=>x.className==="nf93-consent");
 assert.ok(dialog,"explicit consent dialog");
 const link={href:"https://benesse-artsite.eventos.tokyo/web/portal/797/",
   getAttribute(k){return k==="data-nf-pilot-action"?"museum_ticket":null;}};
 const click={isTrusted:true,target:{closest(){return link;}}};
 events.click(click);
 if(consent!=="yes"){assert.ok(!win.dataLayer,"no GA4 event before consent");assert.equal(addedScripts.length,0);}
 if(consent==="no")return {events,addedScripts,addedBody,win,store};
 if(consent!== "yes"){
   dialog.querySelector(".nf93-accept").dispatch("click");
   assert.equal(addedScripts.length,1,"only one official GA4 loader injected on opt-in");
 }
 assert.ok(win.dataLayer,"GA4 commands after acceptance");
 events.click(click);
 const calls=win.dataLayer.map(x=>Array.from(x));
 const views=calls.filter(x=>x[0]==="event"&&x[1]==="nf_pilot_guide_view");
 const actions=calls.filter(x=>x[0]==="event"&&x[1]==="nf_pilot_action_click");
 assert.equal(views.length,1,"single consented pilot view event");
 assert.equal(actions.length,1,"one ticket intent click, not a confirmed booking");
 assert.equal(actions[0][2].pilot_id,"naoshima");
 assert.equal(actions[0][2].pilot_action,"museum_ticket");
 for(const call of [...views,...actions]){
   assert.ok(Object.keys(call[2]).every(x=>["pilot_id","pilot_action","page_area","destination_step","transport_type"].includes(x)),"only allowlisted nonpersonal parameters");
   assert.ok(!JSON.stringify(call).includes("https:")&&!JSON.stringify(call).includes("?"),"no URL or query strings");
 }
 dialog.querySelector(".nf93-reject").dispatch("click");
 const before=win.dataLayer.filter(x=>Array.from(x)[1]==="nf_pilot_action_click").length;
 events.click(click);
 assert.equal(win.dataLayer.filter(x=>Array.from(x)[1]==="nf_pilot_action_click").length,before,"revoked consent blocks future clicks");
 return {events,addedScripts,addedBody,win,store};
}
const before=testVM("G-TEST123456",null);
const denied=testVM("G-TEST123456","no");
const none=testVM("",null);
assert.equal(Object.keys(none.events).length,0,"no configured GA4 => no tracking listeners");
console.log("CONSENT PASS: no ID/no opt-in/deny/revoke all block analytics; explicit opt-in produces one pilot view and one ticket-intent event.");
// Preserve audit artifact without sending visits/events to real GA4.
fs.mkdirSync("audit-output/v152",{recursive:true});
fs.writeFileSync("audit-output/v152/pilot-measurement-source.json",
 JSON.stringify({pilot_count:3,tagged_links:[9,12,6],source_links_and_images_preserved:true,
  events:["nf_pilot_guide_view","nf_pilot_action_click"],
  test_ga4_id:"G-TEST123456",real_events_sent:0,
  no_identifier_analytics:false,requires_real_Vercel_GA4_ID:true,
  requires_GA4_owner_property_and_Search_Console_access:true},null,2));
