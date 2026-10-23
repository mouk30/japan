/* V144: remaining repeated stock-photo candidates after 51 source updates.
   A duplicated file is NOT proof of copyright or location mismatch. */
const fs=require('fs'),path=require('path');
const ROOT='site';
const pattern=/^\/images\/[a-z0-9-]+\.jpg$/i;
const files=[];
function walk(dir){for(const entry of fs.readdirSync(dir,{withFileTypes:true})){
const fp=path.join(dir,entry.name);
if(entry.isDirectory())walk(fp);else if(entry.name==='index.html')files.push(fp);
}}
walk(ROOT);
const groups=new Map();
for(const filepath of files){
 const h=fs.readFileSync(filepath,'utf8');const cover=/<img class="article-cover" src="([^"]+)"[^>]*>/.exec(h);
 if(!cover||!pattern.test(cover[1]))continue;
 const title=h.match(/<h1[^>]*>([^<]+)<\/h1>/)?.[1]||'';
 const alt=cover[0].match(/alt="([^"]+)"/)?.[1]||'';
 const href='/'+path.relative(ROOT,filepath).replaceAll('\\','/').replace(/index\.html$/,'');
 if(!groups.has(cover[1]))groups.set(cover[1],[]);
 const isNamedPlace=/museum|festival|park|station|port|garden|gion|asahikawa|izuhara|hitakatsu|hakata|ferry-boat|shrine|temple/i.test(href);
 groups.get(cover[1]).push({url:href,title,alt,
  priority:isNamedPlace?'site-specific place or service named':'general editorial topic'});
}
const all=[...groups.entries()].sort((a,b)=>b[1].length-a[1].length);
const report={date:'2026-10-23',after:'V144 replace 51 ambiguous cover instances with accurate information visuals; 3 additional Commons documentary photos',source_html_scanned:files.length,
 reason:'Unresolved image-original/licensing/provenance follow-up; photo repetition itself is NOT evidence of error',
 groups:all.map(([cover,pages])=>({cover,count:pages.length,pages})),
 headline:all.slice(0,8).map(([cover,pages])=>({cover,count:pages.length,first_8:pages.slice(0,8)})),
 priority:'Confirm exact photograph, date, venue, photographer, license, and credit before any replacement; never infer current 2026 operations from historical photograph.',
 confirmed_image_errors:0,possible_mismatches_are_unverified:true};
fs.mkdirSync('audit-reports/v144',{recursive:true});
fs.writeFileSync('audit-reports/v144/remaining-photo-provenance-queue.json',JSON.stringify(report,null,2)+'\n','utf8');
console.log(JSON.stringify({pages:files.length,top:report.headline.map(x=>({name:x.cover,count:x.count})),total_groups:all.length},null,2));
