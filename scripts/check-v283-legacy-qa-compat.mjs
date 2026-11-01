/**
 * V283: do not modify or disable V158/V160/V164 legacy validators.
 * Run all of them on untouched main and on this photo-first branch.
 * Compare actual rule failures: only the six explicitly bounded historic
 * image-count/link-count assumptions may become newly invalid; no other
 * official source/booking/return/SEO rule is permitted to regress.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {spawnSync} from 'node:child_process';
const reg=JSON.parse(fs.readFileSync('audit-reports/v283/photo-card-targets-and-legacy-qa.json','utf8'));
const main="c17fec39626600b9b83c7890d8a0857ea19d661e";
const audits=[
{version:"v158",script:"scripts/qa_v158_five_port_operator_changes.py",out:"audit-output/v158/five-actual-operating-changes.json",prop:"details"},
{version:"v160",script:"scripts/qa_v160_five_weather_booking_return.py",out:"audit-output/v160/existing-five-cancellations-and-safe-return.json",prop:"results"},
{version:"v164",script:"scripts/qa_v164_seven_official_originals.py",out:"audit-output/v164/seven-original-ports-booking-ship-return.json",prop:"rows"}
];
const allowed=new Set(reg.legacyQA.permittedOnly.map(x=>x.join(":")));
const dir=fs.mkdtempSync(path.join(os.tmpdir(),"nf-v283-main-"));
const add=spawnSync("git",["worktree","add","--detach",dir,main],{encoding:"utf8"});
if(add.status!==0)throw Error("Cannot prepare original main worktree: "+add.stderr);
function runTest(a,cwd){
 const r=spawnSync("python3",[a.script],{cwd,encoding:"utf8",maxBuffer:4*1024*1024});
 const file=path.join(cwd,a.out);
 assert.ok(fs.existsSync(file),"Historic QA did not emit its original evidence: "+file+" stderr:"+r.stderr?.slice(-400));
 const j=JSON.parse(fs.readFileSync(file,"utf8"));
 const records=j[a.prop];
 assert.ok(Array.isArray(records),"Unrecognized historical validator results: "+a.version);
 const failures=[];
 for(const item of records){
  const slug=item.slug,fail=item.failed??Object.entries(item.checks??{}).filter(([,value])=>!value).map(([key])=>key);
  for(const rule of fail)failures.push(a.version+":"+slug+":"+rule);
 }
 const global=j.failures??j.failed??[];
 for(const fault of global)if(!failures.some(x=>x.split(":").slice(1).join(":")===fault))failures.push(a.version+":global:"+fault);
 return {status:r.status,failures:[...new Set(failures)].sort(),records:records.length};
}
let results=[],unexpected=[];
try{
 for(const a of audits){
  const original=runTest(a,dir);
  const current=runTest(a,process.cwd());
  const prior=new Set(original.failures);
  const newFailures=current.failures.filter(x=>!prior.has(x));
  const notAllowed=newFailures.filter(x=>!allowed.has(x));
  unexpected.push(...notAllowed);
  results.push({validator:a.version,originalMain:original,currentBranch:current,newVisualAssumptionFailures:newFailures.filter(x=>allowed.has(x)),unexpectedRegressions:notAllowed});
 }
}finally{
 const rem=spawnSync("git",["worktree","remove","--force",dir],{encoding:"utf8"});
 if(rem.status!==0)console.warn("Worktree removal failure: "+rem.stderr?.slice(0,500));
 try{fs.rmSync(dir,{recursive:true,force:true})}catch{}
}
const report={
stage:"V283",
definition:"Historical tests remain unchanged; compare original main to branch. The v282/V283 strict current photo blob, SEO, links and 9 actual targets are checked separately.",
expectedAllowedLegacyDifferences:[...allowed],
results,unexpected,
status:unexpected.length===0?"PASS_VISUAL_COMPAT_DELTA_WITH_EXISTING_HISTORIC_FAILURES":"FAIL_NEW_NONVISUAL_REGRESSION",
note:"An existing failing legacy validation remains a failure. This comparator does not turn those CI checks green or assert they passed."
};
fs.mkdirSync('audit-reports/v283',{recursive:true});
fs.writeFileSync('audit-reports/v283/historical-compatibility-results.json',JSON.stringify(report,null,2)+"\n");
console.log("V283 HISTORIC COMPAT "+report.status+" "+JSON.stringify(results.map(x=>({version:x.validator,mainErrors:x.originalMain.failures.length,branchErrors:x.currentBranch.failures.length,newVisual:x.newVisualAssumptionFailures,unexpected:x.unexpectedRegressions}))));
assert.equal(unexpected.length,0,"New failures outside V282 photo/card count expectations: "+unexpected.join(", "));
