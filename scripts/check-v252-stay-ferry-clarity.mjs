import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
const root='site/stay';
const regions=fs.readdirSync(root,{withFileTypes:true}).filter(x=>x.isDirectory()&&fs.existsSync(path.join(root,x.name,'index.html'))).map(x=>x.name).sort();
const files=['site/stay/index.html',...regions.map(x=>'site/stay/'+x+'/index.html')];
assert.equal(files.length,28,'Unexpected stay guide page count: review scope before expanding V252');
const target="https://willer-travel.com/ko/ferry/";
const sitemap=fs.readFileSync('site/sitemap.xml','utf8');
let checked=0,linkCount=0;
for(const file of files){
 const html=fs.readFileSync(file,'utf8');
 const url='/'+path.dirname(file).replace(/^site\//,'')+'/';
 const expectedCanonical='https://www.nipponferry.com'+url;
 assert.ok(html.includes('<title>'),'SEO title missing: '+file);
 const meta=html.match(/<meta name=['"]description['"] content=['"]([^'"]+)/i)?.[1];
 assert.ok(meta&&meta.length>25,'SEO description missing: '+file);
 assert.ok(html.includes("rel='canonical' href='"+expectedCanonical+"'"),'Canonical changed: '+file);
 assert.match(html,/<meta name=['"]robots['"] content=['"]index,follow/i,'Index policy modified '+file);
 assert.ok(sitemap.includes('<loc>'+expectedCanonical+'</loc>'),'Sitemap missing '+file);
 assert.match(html,/<h1\b/i,'H1 missing '+file);
 assert.equal(html.split("class='stay-ferry-note'").length-1,1,'Visible contextual note missing or duplicated '+file);
 assert.ok(html.includes('숙소·객실 예약이 아닌 일본 국내 페리 항로 조회'),'Lodging/ferry distinction missing '+file);
 assert.equal(html.split("href='"+target+"'").length-1,1,'Source external ferry URL changed '+file);
 assert.ok(html.includes("rel='noopener noreferrer' aria-label='WILLER TRAVEL에서 일본 국내 페리 항로와 요금 조회 (새 창)'"),'External accessible-label missing '+file);
 assert.ok(!html.includes('>예약 가능한 항로 확인</a>'),'Old ambiguous CTA remains '+file);
 assert.equal(html.split("id='nf-v252-ferry-stay-clarity'").length-1,1,'Responsive style missing '+file);
 assert.ok(html.includes('min-height:44px')&&html.includes('max-width:640px'),'Touch layout missing '+file);
 assert.ok(!/kidsstay-v5\.vercel\.app|kids-stay\.com/i.test(html),'Unverified KidsStay cross-link '+file);
 for(const m of html.matchAll(/\b(?:href|src)=["'](\/[^"']+)["']/g)){
  const url=m[1].split('?')[0].split('#')[0];
  if(!url.startsWith('/')||url.startsWith('//'))continue;
  const disk='site'+url;
  assert.ok(fs.existsSync(disk)||(fs.existsSync(path.join(disk,'index.html'))),'Local target missing '+file+' -> '+url);
  linkCount++;
 }
 checked++;
}
console.log('NIPPONFERRY V252 PASS '+checked+' stay pages, '+linkCount+' local references, 28 clear ferry-vs-lodging disclosures, no KidsStay links or SEO changes');
