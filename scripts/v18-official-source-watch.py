#!/usr/bin/env python3
"""V18: detect changes in official source documents; never parse guesses into public schedules.
Stdlib-only. Comparison with prior successful artifact is orchestrated by Actions.
"""
import argparse, hashlib, json, os, pathlib, urllib.request, urllib.error, datetime
p=argparse.ArgumentParser()
p.add_argument('--previous',default='audit-reports/v18/previous/snapshot.json')
p.add_argument('--output',default='audit-reports/v18/current')
a=p.parse_args()
sources=json.loads(pathlib.Path('scripts/v17-official-sailings.json').read_text(encoding='utf-8'))
old_path=pathlib.Path(a.previous)
old=json.loads(old_path.read_text(encoding='utf-8')) if old_path.exists() else None
dest=pathlib.Path(a.output);dest.mkdir(parents=True,exist_ok=True)
results={}
for slug,port in sources['ports'].items():
    url=port['scheduleSource']
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'NIPPONFERRY-Official-Schedule-Watch/1.0 (information quality audit)','Accept':'text/html,application/pdf,*/*'})
        with urllib.request.urlopen(req,timeout=28) as r:
            content=r.read(12*1024*1024+1)
            if len(content)>12*1024*1024: raise ValueError('SOURCE_TOO_LARGE')
            result={'source':url,'status':'ok','sha256':hashlib.sha256(content).hexdigest(),'bytes':len(content),'http_status':r.status}
    except Exception as e:
        result={'source':url,'status':'fetch_error','error':type(e).__name__+': '+str(e)[:180]}
    results[slug]=result
changes=[]
errors=[]
if old is not None:
    for slug,current in results.items():
        before=old.get('sources',{}).get(slug)
        if current['status']!='ok':
            errors.append(slug+': source temporarily inaccessible; manual inspection required')
        elif before and before.get('status')=='ok' and before.get('sha256')!=current['sha256']:
            changes.append(slug)
        elif not before or before.get('source')!=current['source']:
            changes.append(slug)
else:
    errors=[slug+': source inaccessible during baseline' for slug,item in results.items() if item['status']!='ok']
# Do not treat a failed fetch as a new baseline. Keep previous usable hashes.
if old is not None:
    for slug,current in results.items():
        if current['status']!='ok' and old.get('sources',{}).get(slug,{}).get('status')=='ok':
            results[slug]=old['sources'][slug]
snapshot={'version':'V18','sources':results}
report={'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ports':len(results),'baseline_created':old is None,'changed_sources':changes,'fetch_warnings':errors,'action':'MANUAL_EVIDENCE_REVIEW_REQUIRED' if changes or errors else 'NO_CHANGE_DETECTED','note':'Document bytes changed, NOT proof of changed ship/berth or final boarding time. Never autopublish.'}
(dest/'snapshot.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(dest/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
with open(os.environ.get('GITHUB_OUTPUT','/dev/null'),'a',encoding='utf-8') as f:
    f.write('attention='+str(bool(changes or errors)).lower()+'\n')
    f.write('changed='+','.join(changes)+'\n')
# Always exit 0: actionable alerts are filed separately.
