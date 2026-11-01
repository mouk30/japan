/**
 * V273: compare SEO, internal links and sitemap for 28 existing /stay/ guides
 * against the pinned, unmerged main baseline using actual Git objects.
 * Does not claim live search indexation, hotel booking or Vercel Preview access.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
const BASE='c17fec39626600b9b83c7890d8a0857ea19d661e';
const run=(...args)=>execFileSync('git',args,{encoding:'utf8',maxBuffer:2*1024*1024});
const fromGit=p=>run('show',BASE+':'+p);
const currentFiles=['site/stay/index.html',...fs.readdirSync('site/stay',{withFileTypes:true})
 .filter(d=>d.isDirectory()&&fs.existsSync('site/stay/'+d.name+'/index.html'))
 .map(d=>'site/stay/'+d.name+'/index.html')].sort();
const baselineFiles=run('ls-tree','-r','--name-only',BASE,'site/stay').split('\n')
 .filter(p=>/^site\/stay\/(?:[^/]+\/)?index\.html$/.test(p)).sort();
assert.equal(currentFiles.length,28,'Exactly 28 existing /stay/ guides must remain');
assert.deepEqual(currentFiles,baselineFiles,'Existing stay guide URL set changed');
const meta=(html,key,attr='name')=>html.match(new RegExp('<meta\\s+'+attr+'=["\x27]'+key+'["\x27]\\s+content=["\x27]([^"\x27]*)["\x27]','i'))?.[1]??null;
function fields(html,file){
 const title=html.match(/<title>([\s\S]*?)<\/title>/i)?.[1]?.trim()??null;
 const h1Tags=[...html.matchAll(/<h1\b[^>]*>([\s\S]*?)<\/h1>/gi)];
 const h1=h1Tags[0]?.[1].replace(/<[^>]*>/g,'').replace(/\s+/g,' ').trim()??null;
 const canonical=html.match(/<link\s+rel=["\x27]canonical["\x27]\s+href=["\x27]([^"\x27]*)["\x27]/i)?.[1]??null;
 const anchors=[...html.matchAll(/<a\b[^>]*\bhref=["\x27]([^"\x27]+)["\x27]/gi)].map(x=>x[1]);
 const stayUrl=file==='site/stay/index.html'?'/stay/':'/stay/'+file.split('/')[2]+'/';
 assert.equal(h1Tags.length,1,'Expected one H1 '+file);
 assert.ok(title&&h1&&meta(html,'description')&&canonical,'Missing SEO metadata '+file);
 assert.equal(canonical,'https://www.nipponferry.com'+stayUrl,'Canonical incorrect '+file);
 assert.ok(meta(html,'robots')?.startsWith('index,follow'),'Robots unexpectedly changed '+file);
 assert.ok(anchors.length>=1,'No anchor links '+file);
 assert.doesNotMatch(html,/kids-stay\.com|kidsstay-v5\.vercel\.app/i,'KidsStay live boundary '+file);
 return {page:stayUrl,title,h1,description:meta(html,'description'),
  robots:meta(html,'robots'),canonical,
  ogTitle:meta(html,'og:title','property'),ogDescription:meta(html,'og:description','property'),
  anchors,stayLinks:anchors.filter(x=>x.startsWith('/stay/')),
  bookingLinks:anchors.filter(x=>x.startsWith('/booking/')||x.includes('willer-travel.com/ko/ferry/'))};
}
const pages=[];
for(const file of currentFiles){
 const original=fields(fromGit(file),file),now=fields(fs.readFileSync(file,'utf8'),file);
 assert.deepEqual(now,original,'SEO/H1/links changed from main baseline: '+file);
 pages.push({file,...now,baselineMatches:true});
}
const sitemap=fs.readFileSync('site/sitemap.xml','utf8');
const baselineSitemap=fromGit('site/sitemap.xml');
const stayLocs=xml=>[...xml.matchAll(/<loc>([^<]+)<\/loc>/g)]
 .map(x=>x[1]).filter(x=>x.startsWith('https://www.nipponferry.com/stay/')).sort();
const currentStayLocs=stayLocs(sitemap),oldStayLocs=stayLocs(baselineSitemap);
assert.equal(currentStayLocs.length,28,'Stay sitemap entries must equal 28');
assert.equal(new Set(currentStayLocs).size,28,'Duplicate stay sitemap entries');
assert.deepEqual(currentStayLocs,oldStayLocs,'Sitemap stay URL set changed');
assert.deepEqual(currentStayLocs,pages.map(p=>p.canonical).sort(),'Canonical/sitemap mismatch');
const robots=fs.readFileSync('site/robots.txt','utf8');
assert.equal(robots,fromGit('site/robots.txt'),'Robots.txt changed from baseline');
assert.match(robots,/Sitemap:\s*https:\/\/www\.nipponferry\.com\/sitemap\.xml/i);
const report={stage:'V273',generatedAt:new Date().toISOString(),baselineMain:BASE,
 pagesAudited:28,summary:{pageCount:pages.length,uniqueSitemapStayUrls:currentStayLocs.length,
 anchorOccurrences:pages.reduce((n,p)=>n+p.anchors.length,0),
 stayInternalLinkOccurrences:pages.reduce((n,p)=>n+p.stayLinks.length,0),
 bookingLinkOccurrences:pages.reduce((n,p)=>n+p.bookingLinks.length,0),
 unchangedTitlesH1DescriptionsCanonicalRobotsOgAndAnchors:28,
 sitemapAndRobotsUnchanged:true},pages,sitemapStayUrls:currentStayLocs,
 caveats:['Baseline main is unchanged but V258-V272 changes are in separate unmerged PRs.',
  'This is a local Git object regression, not a Google/Naver indexation check.',
  'Actual booking availability, rights, Vercel Preview and live deployment are not verified.',
  'Do not merge without every mandatory CI and independently authenticated Vercel Preview render.']};
const out='audit-reports/v273-stay-seo-generated.json';
fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');
console.log('V273 SEO BASELINE PASS '+JSON.stringify(report.summary));
console.log('V273 evidence artifact '+out+'; no new articles, no merge or deployment');
