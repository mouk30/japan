#!/usr/bin/env python3
"""Tokyo 220 factual link / public-photo HTTP audit. No false certification.
All network results retain unknown when blocked or unverifiable."""
import concurrent.futures,datetime,json,pathlib,re,urllib.request,urllib.error,urllib.parse,ssl,time
ROOT=pathlib.Path('site')
inventory=pathlib.Path('audit-reports/tokyo-220-photo-source-audit.json')
data=json.loads(inventory.read_text(encoding='utf8'))
items=data['items']
UA='NIPPONFERRY accuracy-review/1.0 (https://www.nipponferry.com)'
def probe(url):
 try:
  req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'text/html,image/webp,*/*'},method='GET')
  with urllib.request.urlopen(req,timeout=14) as r:
   typ=r.headers.get('Content-Type','').lower()
   head=r.read(64)
   return {'http_status':r.status,'final_url':r.geturl(),'content_type':typ,
           'valid_webp_header':head[:4]==b'RIFF' and head[8:12]==b'WEBP' if 'webp' in url else None,
           'reachability':'ok' if r.status==200 else 'unexpected_status'}
 except urllib.error.HTTPError as e:
  return {'http_status':e.code,'reachability':'access_denied_or_not_found' if e.code in (401,403,404,429) else 'http_error'}
 except Exception as e:
  return {'http_status':None,'reachability':'unknown_network_error','error':str(e)[:100]}
official_urls=sorted({u for x in items for u in x['related_official_or_reference_urls'] if u.startswith('https://')})
photo_urls=sorted({'https://www.nipponferry.com'+x['photo_path'] for x in items if x['photo_file_valid'] and x['photo_path']})
hub='https://www.nipponferry.com/japan/tokyo/'
targets=official_urls+photo_urls+[hub]
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 result=dict(zip(targets,pool.map(probe,targets)))
for x in items:
 urls=x['related_official_or_reference_urls']
 x['external_sources_http']={u:result.get(u) for u in dict.fromkeys(urls)}
 x['external_source_all_http_200']=bool(urls) and all(result[u]['reachability']=='ok' for u in urls)
 if x['photo_file_valid']:
  x['live_photo_http']=result.get('https://www.nipponferry.com'+x['photo_path'])
 else:x['live_photo_http']=None
 # All conditions and visual QA remain unverified by simple HTTP checks.
 x['official_conditions_individually_verified']=False
 x['live_browser_render_checked']=False
summary={'pages':len(items),'official_url_count':len(official_urls),
'external_urls_http_200':sum(result[u]['reachability']=='ok' for u in official_urls),
'urls_unknown_or_blocked':sum(result[u]['reachability']!='ok' for u in official_urls),
'local_photos':len(photo_urls),
'live_webp_http_ok':sum(result[u]['reachability']=='ok' and result[u]['valid_webp_header'] for u in photo_urls),
'hub_http':result[hub],
'operational_facts_individually_verified':0,'browser_render_confirmed':0}
out=pathlib.Path('audit-reports/tokyo-220-live-verification.json')
out.write_text(json.dumps({'run_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'summary':summary,
 'limitations':'HTTP status is not booking accuracy, image semantic identity, license clearance, or real browser rendering. 403 and timeouts remain unknown, not broken.', 'items':items},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(summary,ensure_ascii=False))
