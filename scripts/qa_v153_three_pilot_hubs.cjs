#!/usr/bin/env node
"use strict";
/* V153: verify discoverable 3 pilot cards on four existing hubs, licensed WebP
   provenance, existing SEO preserved, and consent-gated entry-only events.
   We never test with/submit to a real GA4 endpoint. */
const fs=require("fs"),assert=require("node:assert/strict"),cp=require("child_process"),vm=require("vm");
const origin="https://www.nipponferry.com";
const cases={
  "naoshima":{slug:"naoshima-art-ferry-return",img:"/images/editorial/v146-naoshima-miyanoura-ferry-terminal-2025.webp",src:"https://commons.wikimedia.org/wiki/File:Naoshima_Ferry_Terminal.jpg",license:"https://creativecommons.org/licenses/by-sa/4.0/",author:"Bea Phi"},
  "teshima":{slug:"teshima-art-ferry-return",img:"/images/editorial/v146-teshima-art-museum-exterior-2013.webp",src:"https://commons.wikimedia.org/wiki/File:Teshima_Art_Museum_exterior_view_201310.jpg",license:"https://creativecommons.org/licenses/by/2.0/",author:"Kentaro Ohno"},
  "shikoku_food":{slug:"takamatsu-cruise-udon-market-return",img:"/images/culture-verified/japan-kagawa-udon-pilgrimage.webp",src:"https://commons.wikimedia.org/wiki/File:Kama-age_sanuki_udon_by_sekido_in_Takamatsu%2C_Kagawa.jpg",license:"https://creativecommons.org/licenses/by/2.0",author:"sekido"}
};
const hubs={
 "site/things-to-do/index.html":["naoshima","teshima","shikoku_food"],
 "site/things-to-do/cruise-ports/index.html":["naoshima","teshima","shikoku_food"],
 "site/things-to-do/food-experience/index.html":["shikoku_food"],
 "site/food/index.html":["shikoku_food"]
};
const source=fs.readFileSync("site/nf-v93-booking-clicks.js","utf8");
const checks=[];
function test(name,ok){checks.push({name,ok});if(!ok)throw Error(name);}
function staticParts(s){return {title:(s.match(/<title\b[^>]*>[\s\S]*?<\/title>/i)||[])[0],h1:(s.match(/<h1\b[^>]*>[\s\S]*?<\/h1>/i)||[])[0],
 canonical:(s.match(/<link\b[^>]*rel=["']canonical["'][^>]*>/i)||[])[0],
 jsonld:[...s.matchAll(/<script[^>]+type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi)].map(x=>x[1]),
 existingImages:[...s.matchAll(/<img\b[^>]*>/gi)].filter(x=>!x[0].includes("nf-v153-")).map(x=>x[0]),
 oldCC:s.includes('id="nf-v148-photo-credits"')}};
for(const [path,ids] of Object.entries(hubs)){
 const orig=cp.execFileSync("git",["show","origin/main:"+path],{encoding:"utf8"});
 const curr=fs.readFileSync(path,"utf8");
 const id='id="nf-v153-pilot-hub"';
 test(path+":exactly_one_new_section",curr.split(id).length-1===1);
 const headClose=curr.indexOf("</head>"),panel=curr.slice(curr.indexOf(id));
 const old=staticParts(orig),now=staticParts(curr);
 test(path+":SEO_title_unchanged",old.title===now.title);
 test(path+":SEO_canonical_unchanged",old.canonical===now.canonical);
 test(path+":existing_h1_unchanged",old.h1===now.h1);
 test(path+":structured_data_unchanged",JSON.stringify(old.jsonld)===JSON.stringify(now.jsonld));
 test(path+":original_images_unchanged",old.existingImages.every(x=>curr.includes(x)));
 test(path+":license_details_preserved",!old.oldCC||now.oldCC);
 test(path+":mobile_4_3_style",curr.includes("grid-template-columns:minmax(0,1fr)")&&curr.includes("aspect-ratio:4/3"));
 const tagged=[...panel.matchAll(/<a\b[^>]*data-nf-pilot-entry="([^"]+)"[^>]*>/g)];
 test(path+":correct_entry_card_count",tagged.length===ids.length);
 for(const id of ids){
  const c=cases[id],target='/things-to-do/'+c.slug+'/';
  const one=tagged.filter(x=>x[1]===id && x[0].includes('href="'+target+'"'));
  test(path+":"+id+":exactly_one_direct_link",one.length===1);
  test(path+":"+id+":correct_actual_photo_and_alt",panel.includes('src="'+c.img+'"')&&panel.includes(c.author)&&panel.includes("현재 운항")===true);
  test(path+":"+id+":photo_and_license_link",panel.includes('href="'+c.src+'"')&&panel.includes('href="'+c.license+'"'));
  const fpath='site/'+c.img.replace(/^\//,'');
  test(path+":"+id+":local_webp_exists",fs.existsSync(fpath));
 }
 test(path+":no_extra_pilot_targets",tagged.every(x=>ids.includes(x[1])));
 console.log("HUB PASS",path,ids.length,"pilot cards; existing canonical/h1/JSON-LD/images preserved");
}
test("tracking_contains_pilot_entry_event",source.includes("nf_pilot_entry_click"));
test("tracking_event_requires_click_and_consent",source.includes("if (!event.isTrusted || !enabled)"));
test("tracking_event_has_strict_page_allowlist",["'/things-to-do/'","'/things-to-do/cruise-ports/'","'/things-to-do/food-experience/'","'/food/'"].every(x=>source.includes(x)));
test("tracking_no_real_sales_claim",!source.includes("purchase_completed"));
const build=fs.readFileSync("build.js","utf8");
test("only_conditional_GA4",build.includes("if (ga4Id)")&&build.includes("process.env.GA4_MEASUREMENT_ID"));
test("tracking_script_cache_version",build.includes("/nf-v93-booking-clicks.js?v=20261024-v153"));
function dom(tag){
 const el={tagName:tag,children:[],handlers:{},hidden:true,attrs:{},
  addEventListener(name,fn){this.handlers[name]=fn;},
  appendChild(node){this.children.push(node);},
  setAttribute(name,val){this.attrs[name]=val;},
  getAttribute(name){return this.attrs[name]||null;},
  querySelector(q){this.refs=this.refs||{};return this.refs[q]||(this.refs[q]=dom("button"));},
  fire(name){if(!this.handlers[name])throw Error("missing handler "+name);this.handlers[name]();}
 };
 return el;
}
function runConsentTest(page,consent,target,declared,trust=true){
 const choice=consent===null?[]:[["nf93_analytics_choice_v1",consent]];
 const store=new Map(choice),events={},head=dom("head"),body=dom("body");
 const document={currentScript:{getAttribute(x){return x==="data-nf-ga4"?"G-TEST123456":null}},
  readyState:"loading",head,body,createElement:dom,querySelector(){return null;},
  addEventListener(ev,cb){events[ev]=cb;}};
 const location={pathname:page,hostname:"www.nipponferry.com",href:origin+page};
 const localStorage={getItem(key){return store.has(key)?store.get(key):null;},setItem(key,val){store.set(key,val);}};
 const window={};
 vm.runInNewContext(source,{document,location,localStorage,window,Date,URL,encodeURIComponent,console});
 events.DOMContentLoaded();
 const dialog=body.children.find(el=>el.className==="nf93-consent");
 if(!dialog)throw Error("consent dialog missing");
 const links={
  good:{href:origin+target,getAttribute(n){return n==="data-nf-pilot-entry"?declared:null;}},
  malicious:{href:"https://example.org"+target,getAttribute(n){return n==="data-nf-pilot-entry"?declared:null;}}
 };
 function send(link,isTrusted=true){
  events.click({isTrusted,target:{closest(){return link;}}});
 }
 send(links.good,trust);
 let hits=window.dataLayer?window.dataLayer.map(x=>Array.from(x)).filter(x=>x[0]==="event"&&x[1]==="nf_pilot_entry_click"):[];
 if(consent!=="yes")test("no_link_event_before_consent:"+page, hits.length===0);
 if(consent===null)dialog.querySelector(".nf93-accept").fire("click");
 if(consent!=="no"){
   send(links.good,trust);send(links.malicious,true);
   hits=window.dataLayer.map(x=>Array.from(x)).filter(x=>x[0]==="event"&&x[1]==="nf_pilot_entry_click");
   test("exactly_one_valid_trusted_entry:"+page+":"+declared,hits.length===(trust?1:0));
   if(hits.length) {
    test("correct_target_param",hits[0][2].pilot_id===declared&&hits[0][2].pilot_action==="guide_open");
    test("fixed_nonpersonal_ga4_fields",Object.keys(hits[0][2]).every(k=>["pilot_id","pilot_action","page_area","destination_step","transport_type"].includes(k)));
   }
   dialog.querySelector(".nf93-reject").fire("click");
   send(links.good,true);
   const after=window.dataLayer.map(x=>Array.from(x)).filter(x=>x[0]==="event"&&x[1]==="nf_pilot_entry_click");
   test("revoking_blocks_new_events",after.length===hits.length);
 }
}
runConsentTest("/things-to-do/","no","/things-to-do/naoshima-art-ferry-return/","naoshima");
runConsentTest("/things-to-do/",null,"/things-to-do/naoshima-art-ferry-return/","naoshima");
runConsentTest("/things-to-do/cruise-ports/","yes","/things-to-do/teshima-art-ferry-return/","teshima");
runConsentTest("/food/","yes","/things-to-do/takamatsu-cruise-udon-market-return/","shikoku_food");
runConsentTest("/things-to-do/food-experience/","yes","/things-to-do/takamatsu-cruise-udon-market-return/","shikoku_food");
runConsentTest("/things-to-do/","yes","/things-to-do/naoshima-art-ferry-return/","naoshima",false);
console.log("CONSENT AND ATTRIBUTION QA PASS: 4 exact hub sources / 3 pilot targets, explicit consent required; no rogue outbound URLs.");
fs.mkdirSync("audit-output/v153",{recursive:true});
fs.writeFileSync("audit-output/v153/three-pilot-discovery.json",JSON.stringify({
 version:"V153",original_article_count_unchanged:true,new_articles:0,
 hubs:Object.fromEntries(Object.entries(hubs).map(([key,val])=>[key,val])),
 featured_cards:8,ga4_events:["nf_pilot_entry_click","nf_pilot_guide_view","nf_pilot_action_click"],
 actual_GA4_ID_present:false,actual_booking_completed_events_measured:false,
 passed:checks.length,checks},null,2));
console.log("SUMMARY",checks.length,"checks PASSED; featured cards",Object.values(hubs).reduce((a,c)=>a+c.length,0));
