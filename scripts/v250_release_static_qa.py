#!/usr/bin/env python3
"""V250 release gate: source-to-production SEO invariants, internal targets, sitemap,
assets, image alt, route/booking trust, and pre-V246 home SEO baseline.

Read-only. No pages, SEO tags, or sitemap are automatically modified.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import html as htmlmod
import json
import posixpath
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
DIST=ROOT/'dist'
OUT=ROOT/'audit-reports'/'v250'
OUT.mkdir(parents=True,exist_ok=True)
BASE='524b9c4809f50d9e7f567d3a43b63d682fb86b41' # parent of V246 home commit
HOSTS={'www.nipponferry.com','nipponferry.com'}
CANONICAL='https://www.nipponferry.com'
FAIL=[]
WARN=[]
counts=Counter()
samples=defaultdict(list)

class Page(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True)
  self.title='';self.descriptions=[];self.canonicals=[];self.robots=[]
  self.h1=[];self.current='';self.in_title=False;self.h1level=0
  self.links=[];self.images=[];self.styles=[];self.scripts=[];self.anchors=set()
  self.jsonld=[];self._ld=False;self._ldbuf=[]
 def handle_starttag(self,tag,attrs):
  attr=dict(attrs);rel=(attr.get('rel') or '').lower()
  if tag=='title':self.in_title=True
  if tag=='h1':self.h1level+=1;self.current=''
  if attr.get('id'):self.anchors.add(attr['id'])
  if tag=='a' and attr.get('name'):self.anchors.add(attr['name'])
  if tag=='a' and attr.get('href'):self.links.append((attr['href'],attr))
  if tag=='img':self.images.append(attr)
  if tag=='link':
   if 'canonical' in rel:self.canonicals.append(attr.get('href',''))
   if 'stylesheet' in rel and attr.get('href'):self.styles.append(attr['href'])
   if ('icon' in rel or 'preload' in rel) and attr.get('href'):self.styles.append(attr['href'])
  if tag=='meta':
   if (attr.get('name') or '').lower()=='description':self.descriptions.append(attr.get('content',''))
   if (attr.get('name') or '').lower()=='robots':self.robots.append(attr.get('content',''))
  if tag=='script':
   if (attr.get('type') or '').lower()=='application/ld+json':self._ld=True;self._ldbuf=[]
   if attr.get('src'):self.scripts.append(attr['src'])
 def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs)
 def handle_data(self,data):
  if self.in_title:self.title+=data
  if self.h1level:self.current+=data
  if self._ld:self._ldbuf.append(data)
 def handle_endtag(self,tag):
  if tag=='title':self.in_title=False
  if tag=='h1' and self.h1level:
   self.h1.append(self.current.strip());self.current='';self.h1level-=1
  if tag=='script' and self._ld:
   self.jsonld.append(''.join(self._ldbuf).strip());self._ld=False;self._ldbuf=[]

def parse(data):
 p=Page()
 p.feed(data)
 return p

def record(bucket,detail,hard=False):
 (FAIL if hard else WARN).append(bucket+': '+str(detail))
 if len(samples[bucket])<35:samples[bucket].append(str(detail))

def route_for(file):
 rel=file.relative_to(DIST).as_posix()
 return '/'+rel[:-len('index.html')] if rel.endswith('index.html') else '/'+rel

def normalize_href(page,href):
 href=htmlmod.unescape((href or '').strip())
 if not href or href.startswith(('mailto:','tel:','javascript:','data:','blob:','sms:')):return None
 if href.startswith('//'):href='https:'+href
 parts=urlsplit(href)
 if parts.scheme and parts.scheme.lower() not in ('https','http'):return None
 if parts.netloc and parts.hostname and parts.hostname.lower() not in HOSTS:return None
 urlpath=unquote(parts.path)
 if not urlpath and not parts.netloc:
  if href.startswith('#'):return page,parts.fragment,True
  return None
 if not urlpath:urlpath='/'
 if not urlpath.startswith('/'):
  urlpath=posixpath.join(posixpath.dirname(page),urlpath)
 cleaned=posixpath.normpath(urlpath)
 if urlpath.endswith('/') and not cleaned.endswith('/'):cleaned+='/'
 if not cleaned.startswith('/'):cleaned='/'+cleaned
 return cleaned,parts.fragment,False

def target_exists(path):
 if path in ('/contents','/contents/'):return True,'vercel_redirect'
 test=DIST/path.lstrip('/')
 if test.is_file():return True,'file'
 if test.is_dir() and (test/'index.html').is_file():return True,'directory'
 if (DIST/(path.lstrip('/')+'/index.html')).is_file():return True,'directory'
 if not Path(path).suffix and (DIST/(path.lstrip('/')+'.html')).is_file():return True,'clean_url'
 return False,'missing'

built_files=sorted(DIST.rglob('*.html'))
source_files=sorted(SITE.rglob('*.html'))
all_dest={}
source_paths={p.relative_to(SITE).as_posix() for p in source_files}
dist_paths={p.relative_to(DIST).as_posix() for p in built_files}
counts['source_html']=len(source_paths)
counts['built_html']=len(dist_paths)
for x in sorted(source_paths-dist_paths):
 if x not in ('contents/index.html',):record('missing_built_html',x,True)
for x in sorted(dist_paths-source_paths):record('unexpected_new_html',x,True)

for file in built_files:
 rel=file.relative_to(DIST)
 source=SITE/rel
 if not source.exists():continue
 page=route_for(file)
 try:
  src_html=source.read_text('utf-8');built_html=file.read_text('utf-8')
  src=parse(src_html);out=parse(built_html)
 except Exception as exc:
  record('parse_failure',page+' '+str(exc),True);continue
 all_dest[page]=out
 counts['pages_parsed']+=1
 # Canonical, index state, organic snippet content and structured data must survive build.
 if src.title.strip()!=out.title.strip():record('title_changed',page,True)
 if src.descriptions!=out.descriptions:record('description_changed',page,True)
 if src.canonicals!=out.canonicals:record('canonical_changed',page,True)
 if src.robots!=out.robots:record('robots_changed',page,True)
 if src.jsonld!=out.jsonld:record('jsonld_changed',page,True)
 if len(src.h1)!=len(out.h1):record('h1_count_changed',page+' '+str((len(src.h1),len(out.h1))),True)
 if not src.title.strip():counts['missing_title']+=1
 if not out.descriptions or not out.descriptions[0].strip():counts['missing_description']+=1
 if not out.canonicals or not out.canonicals[0].strip():counts['missing_canonical']+=1
 if not out.h1:counts['missing_h1']+=1
 noindex=any('noindex' in x.lower() for x in out.robots)
 if noindex:counts['noindex_pages']+=1
 else:counts['indexable_pages']+=1
 if out.canonicals:
  canonical=out.canonicals[0]
  if not canonical.startswith(CANONICAL+'/'):record('nonpreferred_canonical',page+' → '+canonical)
  parsed=urlsplit(canonical)
  if parsed.hostname in HOSTS:
   exists,_=target_exists(parsed.path or '/')
   if not exists:record('canonical_missing_target',page+' → '+canonical,True)
  if len(out.canonicals)>1:record('multiple_canonicals',page,True)
 if len(out.descriptions)>1:record('multiple_descriptions',page,True)
 if src.h1 and out.h1 and not out.h1[0].strip():record('blank_h1',page,True)
 if '<meta' in src_html and '<head' in src_html and '<head' not in built_html:
  record('lost_head',page,True)

 # Local links, including injected V301 navigation, are checked on the actual build.
 for href,attrs in out.links:
  counts['anchor_links_checked']+=1
  resolved=normalize_href(page,href)
  if resolved is None:
   if href.startswith(('http:','https:','//')):
    counts['outbound_anchor_links']+=1
   continue
  dest,fragment,is_only_fragment=resolved
  if is_only_fragment:
   # Preexisting deep article anchors are reviewed separately, not false 404s.
   continue
  exists,kind=target_exists(dest)
  if exists:counts['internal_links_resolved']+=1
  else:
   counts['internal_links_broken']+=1
   record('broken_internal_link',page+' → '+href,True)
 for tag,arr in [('style',out.styles),('script',out.scripts)]:
  for url in arr:
   resolved=normalize_href(page,url)
   if resolved is None:continue
   dest=resolved[0]
   ok,_=target_exists(dest)
   if not ok:record('missing_'+tag+'_resource',page+' → '+url,True)
   else:counts[tag+'_resources_checked']+=1
 for image in out.images:
  counts['images_checked']+=1
  if 'alt' not in image:counts['images_missing_alt_attribute']+=1;record('image_without_alt_attribute',page+' → '+str(image.get('src','')))
  elif image.get('alt')=='':counts['decorative_images_empty_alt']+=1
  url=image.get('src') or image.get('data-src')
  if not url:continue
  resolved=normalize_href(page,url)
  if resolved is None:continue
  ok,_=target_exists(resolved[0])
  if not ok:
   counts['images_missing']+=1
   record('missing_image',page+' → '+url,True)

# Inventory superseded booking notices across the whole existing site, not just new cards.
stale_operator_pages=[]
for file in built_files:
 text=file.read_text('utf-8')
 if '20261023systemmaintenance.html' in text:
  stale_operator_pages.append(route_for(file))
counts['pages_linking_old_kampu_notice']=len(stale_operator_pages)
print('V250_STALE_OPERATOR_NOTICE_PAGES',json.dumps(stale_operator_pages,ensure_ascii=False))
if stale_operator_pages:
 record('old_kampu_notice_legacy_pages',
        ', '.join(stale_operator_pages[:35]))

# Homepage SEO compared to the exact pre-V246 Git commit (not a model memory).
try:
 old=subprocess.run(['git','show',BASE+':site/index.html'],capture_output=True,text=True,check=True).stdout
 original=parse(old);current=parse((DIST/'index.html').read_text('utf-8'))
 checks={'title':original.title==current.title,
  'meta_description':original.descriptions==current.descriptions,
  'canonical':original.canonicals==current.canonicals,
  'robots':original.robots==current.robots,
  'jsonld':original.jsonld==current.jsonld}
 counts['home_pre_v246_seo_fields_compared']=len(checks)
 for key,match in checks.items():
  if not match:record('pre_v246_home_regression',key,True)
except Exception as e:
 checks={}
 record('pre_v246_baseline_unavailable',str(e),True)

# Original source HTML files must not increase due to this QA-only phase.
try:
 oldfiles=subprocess.run(['git','ls-tree','-r','--name-only',BASE,'site'],capture_output=True,text=True,check=True).stdout.splitlines()
 oldhtml={x.removeprefix('site/') for x in oldfiles if x.endswith('.html')}
 created=sorted(source_paths-oldhtml)
 counts['html_new_since_pre_v246']=len(created)
 if created:record('html_added_since_pre_v246',created[:15],True)
except Exception as e:record('pre_v246_tree_unavailable',str(e),True)

# Sitemap: only intended indexable pages; no invented lastmod updates.
sitemap=SITE/'sitemap.xml'
try:
 urls=[x.text.strip() for x in ET.parse(sitemap).getroot().iter() if x.tag.endswith('}loc') and x.text]
except Exception as e:
 urls=[];record('sitemap_parse',str(e),True)
counts['sitemap_urls']=len(urls)
if len(urls)!=len(set(urls)):record('sitemap_duplicates',len(urls)-len(set(urls)),True)
for url in urls:
 p=urlsplit(url)
 if p.hostname not in HOSTS:record('sitemap_foreign_host',url,True);continue
 if p.fragment or p.query:record('sitemap_unclean_url',url,True)
 exists,kind=target_exists(p.path or '/')
 if not exists:record('sitemap_missing_target',url,True)
 doc=all_dest.get(p.path or '/')
 if doc and any('noindex' in r.lower() for r in doc.robots):record('sitemap_noindex',url,True)
 if doc and doc.canonicals and doc.canonicals[0]!=url:
  record('sitemap_noncanonical',url+' → '+doc.canonicals[0])
counts['sitemap_missing_for_indexable']=sum(
 p not in {urlsplit(x).path for x in urls}
 for p,doc in all_dest.items()
 if p.endswith('/') and not any('noindex' in r.lower() for r in doc.robots)
 and 'refresh' not in (DIST/p.lstrip('/')/'index.html').read_text('utf-8').lower()[:350]
)
if counts['sitemap_missing_for_indexable']:record('indexable_not_in_sitemap',counts['sitemap_missing_for_indexable'])
robots=(DIST/'robots.txt').read_text('utf-8')
if 'Sitemap: https://www.nipponferry.com/sitemap.xml' not in robots:record('robots_missing_sitemap',robots[:100],True)
if re.search(r'(?im)^Disallow:\s*/\s*$',robots):record('robots_blocks_site','Disallow: /',True)

# Homepage critical handoffs must exist as links, not merely text.
home=(DIST/'index.html').read_text('utf-8')
for fragment in ('id="find-sea-route"','data-nf247-finder','href="#find-sea-route"',
  'class="nf-premium-hero nf246-hero"','class="v65-grid"','class="v63-grid"',
  'nf-v249-mobile-consistency.css','nf-v249-mobile-consistency.js',
  'href="/booking/japan-cruise/"','href="/things-to-do/cruise-ports/"'):
 if fragment not in home:record('home_missing_handoff',fragment,True)
if home.count('<article class="nf247-card"')!=18:record('route_card_count','Expected 18',True)
if home.count('<article class="v65-card')!=8:record('destination_card_count','Expected 8',True)
if home.count('<article class="v63-card')!=6:record('theme_card_count','Expected 6',True)
if '20261023systemmaintenance.html' in home:record('stale_kampu_home_notice','10/23 suspension link',True)
if home.count('https://www.kampuferry.co.jp/news/20261027systemmaintenance.html')!=2:
 record('kampu_official_resumption_missing','Expected two 2026-10-27 restart links',True)
if re.search(r'실시간\s*(?:예약|좌석|요금)\s*(?:검색|조회)\s*(?:완료|확정)',home):
 record('unsupported_realtime_claim','Homepage contains unverified realtime/confirmed promise',True)

# The route finder has no synthetic dates/seats/checkout and links all guides.
finder=home.split('<section class="nf247-finder"',1)[1].split('</section>',1)[0] if '<section class="nf247-finder"' in home else ''
if re.search(r'<input\b',finder):record('booking_search_imitation','Unexpected route finder input',True)
if not all(x in finder for x in ('운항','공식','예약')):record('booking_disclosure_missing','Finder safety text',True)
for x in ['/guide/busan-osaka-ferry/','/guide/busan-fukuoka-ferry/','/guide/busan-shimonoseki-ferry/','/guide/busan-tsushima-ferry/']:
 if x not in finder:record('missing_core_ferry_route',x,True)
for x in ('/japan/tokyo/','/ferry/','/booking/japan-cruise/','/things-to-do/cruise-ports/'):
 if x not in home:record('missing_primary_navigation_link',x,True)

# Label historical external issues as independent debt, not this release's false success.
legacy=ROOT/'audit-reports'/'v121'/'remaining-work-and-source-evidence.json'
try:
 baseline=json.loads(legacy.read_text('utf-8'))
 oldstats={key:baseline[key] for key in ['missing_local_images','broken_local_link_targets','explicit_ai_cover_remaining'] if key in baseline}
except Exception:oldstats={}
report={
 'version':'V250','checked_at_utc':datetime.now(timezone.utc).isoformat(),
 'mode':'read-only comprehensive production-build audit; not an external booking availability claim',
 'source_commit':subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True).stdout.strip(),
 'pre_v246_commit':BASE,'home_seo_baseline':checks,
 'counts':dict(counts),'legacy_reference':oldstats,
 'release_blockers':FAIL[:220],'warnings':WARN[:220],
 'error_categories':dict(Counter(x.split(':',1)[0] for x in FAIL)),
 'warning_categories':dict(Counter(x.split(':',1)[0] for x in WARN)),
 'examples':{k:v for k,v in list(samples.items())[:40]},
 'passed':len(FAIL)==0
}
(OUT/'static-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
summary=['# V250 · NIPPONFERRY release audit',
 '','자동 검사: 실제 `dist` 배포 빌드 전체 HTML을 검사했습니다.',
 '',f"- HTML 페이지: {counts['pages_parsed']}",
 f"- 사이트맵 URL: {counts['sitemap_urls']}",
 f"- 내부 링크: {counts['internal_links_resolved']}건 확인, {counts['internal_links_broken']}건 파일 누락",
 f"- 이미지: {counts['images_checked']}건 확인, 파일 누락 {counts['images_missing']}건",
 f"- SEO 변경 위험: {len(FAIL)}건 차단 항목",
 f"- 주의/기존 개선 항목: {len(WARN)}건",
 '', '## 범위 제한',
 '- 외부 선사의 실시간 운항·예약·잔여좌석은 확인하거나 보증하지 않습니다.',
 '- 기존 촬영 이미지의 모든 초상권·원본 사용 권리를 새로 검증한 것은 아닙니다.',
 '- 검색엔진의 실제 색인 여부·검색순위 변화는 Search Console 데이터를 필요로 합니다.',
 '- 배포된 HTML/메타데이터와 링크·모바일 렌더링의 기술적 무결성 검사입니다.',
 '']
if FAIL:summary+=['## 차단 항목']+['- '+x for x in FAIL[:30]]
if WARN:summary+=['','## 검토 항목']+['- '+x for x in WARN[:30]]
(OUT/'audit-summary.md').write_text('\n'.join(summary)+'\n','utf-8')
print(json.dumps({k:report[k] for k in ['passed','source_commit','pre_v246_commit','home_seo_baseline','counts','error_categories','warning_categories']},ensure_ascii=False,indent=2))
if FAIL:
 print('BLOCKING',json.dumps(FAIL[:35],ensure_ascii=False,indent=2))
 raise SystemExit(1)
