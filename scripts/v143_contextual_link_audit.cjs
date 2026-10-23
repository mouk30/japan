/* V143 build QA: every new related link must be an existing page and SEO immutable. */
const fs=require('fs'),path=require('path');
const source='site',built='dist';
function walk(root,out=[]){for(const entry of fs.readdirSync(root,{withFileTypes:true})){const p=path.join(root,entry.name);if(entry.isDirectory())walk(p,out);else if(entry.name.endsWith('.html'))out.push(p)}return out}
const result={version:'V143',pagesScanned:0,originalGeneric:0,updatedContextual:0,remainingGeneric:0,updatedPages:[],errors:[]};
const seoTags=[/<title>[\s\S]*?<\/title>/i,/<meta name="description"[^>]*>/i,/<link rel="canonical"[^>]*>/i];
for(const p of walk(built)){
 result.pagesScanned++;
 const h=fs.readFileSync(p,'utf8');
 const rel=path.relative(built,p),orig=path.join(source,rel);
 const sourceText=fs.existsSync(orig)?fs.readFileSync(orig,'utf8'):'';
 const href='/'+rel.replaceAll('\\','/').replace(/index\.html$/,'');
 if(sourceText.includes('<div class="curiosity">'))result.originalGeneric++;
 if(h.includes('<div class="curiosity">'))result.remainingGeneric++;
 if(!h.includes('data-v143-context="true"'))continue;
 result.updatedContextual++;result.updatedPages.push(href);
 if(h.includes('NEXT QUESTION'))result.errors.push(href+' generic English text remained');
 if(h.match(/data-v143-context="true"/g).length!==1)result.errors.push(href+' duplicate transformed navigation');
 if(!h.includes('/nf-v143-topic-guides.css'))result.errors.push(href+' stylesheet missing');
 const nav=/<nav class="v143-context-journey"[^>]*>([\s\S]*?)<\/nav>/.exec(h);
 if(!nav){result.errors.push(href+' navigation malformed');continue}
 const links=[...nav[1].matchAll(/<a href="([^"]+)"/g)].map(m=>m[1]);
 if(links.length<2||links.length>3)result.errors.push(href+' needs 2-3 links');
 for(const dest of links){
  if(!sourceText.includes('href="'+dest+'"'))result.errors.push(href+' link not present in original related section: '+dest);
  const target=path.join(built,dest.replace(/^\//,''));
  if(!fs.existsSync(target)&&!fs.existsSync(path.join(target,'index.html')))
   result.errors.push(href+' broken topic path '+dest);
 }
 for(const regex of seoTags){
  const a=sourceText.match(regex)?.[0]||null;
  const b=h.match(regex)?.[0]||null;
  if(a!==b)result.errors.push(href+' unexpected SEO metadata change');
 }
}
result.pass=!result.errors.length&&result.updatedContextual>0;
fs.mkdirSync('audit-reports/v143',{recursive:true});
fs.writeFileSync('audit-reports/v143/contextual-links-build-qa.json',JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({pass:result.pass,pages:result.pagesScanned,originalGeneric:result.originalGeneric,updatedContextual:result.updatedContextual,remainingGeneric:result.remainingGeneric,errors:result.errors.slice(0,12)},null,2));
if(!result.pass)process.exit(1);
