#!/usr/bin/env python3
"""V32: diagnose 27 previously image-undetected pages as CSS-hero,
text-first utility guides, or actual missing media. Do not invent images.
"""
import json,re,subprocess
from pathlib import Path
ROOT=Path('site')
if not Path('audit-reports/v30/sitewide-scan.json').exists():
 subprocess.run(['python3','scripts/audit-v30-sitewide-images.py'],check=True,capture_output=True)
report=json.loads(Path('audit-reports/v30/sitewide-scan.json').read_text())
missing=report['missing_primary']
out=[]
for x in missing:
 p=Path(x['page'])
 s=p.read_text(encoding='utf8')
 # Includes CSS custom properties, inline and embedded background assets.
 css_refs=re.findall(r'url\(\s*["\']?(\/images\/[^"\')\s]+)',s)
 css_refs=list(dict.fromkeys(css_refs))
 broken_css=[y for y in css_refs if not (ROOT/y.lstrip('/')).exists()]
 content_imgs=[y for y in re.findall(r'<img\b[^>]*src="(\/images\/[^"]+)"',s) if 'mascot' not in y and 'kakao' not in y]
 og=re.search(r'<meta property="og:image" content="([^"]+)"',s)
 group='booking utility' if '/booking/' in x['page'] else 'destination plan' if '/plan/' in x['page'] else 'shopping utility' if '/shopping/' in x['page'] else 'category/index guide'
 status='CSS hero (not a missing photo)' if css_refs and not broken_css else 'text-first page without hero' if not content_imgs and not css_refs else 'review required'
 out.append({'path':x['page'],'title':x['title'],'group':group,'status':status,'css_backgrounds':css_refs,'broken_css_backgrounds':broken_css,'content_img_count':len(content_imgs),'og':og.group(1) if og else None})
counts={}
for x in out:counts[x['status']]=counts.get(x['status'],0)+1
payload={'pages_reviewed':len(out),'classification':counts,'pages':out}
Path('audit-reports/v32').mkdir(parents=True,exist_ok=True)
Path('audit-reports/v32/missing-hero-triage.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('V32_HERO_TRIAGE',json.dumps({'pages':len(out),'status':counts,'broken_css':sum(len(x['broken_css_backgrounds']) for x in out)},ensure_ascii=False),flush=True)
if len(out)!=27 or any(x['broken_css_backgrounds'] for x in out):raise SystemExit('Unexpected missing CSS asset or changed page count')
