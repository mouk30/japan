#!/usr/bin/env node
"use strict";
const fs=require("fs"), path=require("path");
const root=path.resolve("dist");
const results=[],errors=[];
const walk=(dir)=>{for(const name of fs.readdirSync(dir)){
  const full=path.join(dir,name),stat=fs.statSync(full);
  if(stat.isDirectory())walk(full);else if(name.endsWith(".html"))results.push(full);
}};
if(!fs.existsSync(root))throw Error("Run node build.js before this QA");
walk(root);
let folded=0;let siteCount=0;
for(const file of results){
  const html=fs.readFileSync(file,"utf8");
  const count=(html.match(/id="nf-v148-photo-credits"/g)||[]).length;
  if(count===0)continue;
  folded++;siteCount+=count;
  if(count!==1)errors.push(file+": V148 disclosure duplicated");
  if(html.includes('class="nf-photo-credits-panel"'))
    errors.push(file+": V139 nested/duplicate disclosure present");
  if(!html.includes("<summary>사진 출처 보기</summary>"))
    errors.push(file+": photo credit compact summary missing");
  if(!html.includes("commons.wikimedia.org")&&!html.includes("creativecommons.org"))
    errors.push(file+": CC sources missing");
}
const home=fs.readFileSync(path.join(root,"index.html"),"utf8");
if(home.includes('class="nf-photo-credits-panel"'))errors.push("home V139 double-folded");
if(!home.includes('id="nf-v148-photo-credits"'))errors.push("home V148 missing");
const ports=fs.readFileSync(path.join(root,"things-to-do/cruise-ports/index.html"),"utf8");
if(ports.includes('class="nf-photo-credits-panel"'))errors.push("ports V139 double-folded");
const tokyo=fs.readFileSync(path.join(root,"japan/tokyo/photo-review/index.html"),"utf8");
if((tokyo.match(/게시글 보기 ↗/g)||[]).length<20)errors.push("photo review navigation lost");
if(folded<500)errors.push("less than 500 compacted credit pages");
console.log(JSON.stringify({folded,html_total:results.length,errors:errors.slice(0,20)},null,2));
if(errors.length)process.exit(1);
