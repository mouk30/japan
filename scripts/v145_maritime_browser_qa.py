#!/usr/bin/env python3
"""V145 10 article x 3 responsive widths against actual static build.
Uses Chromium to test readability, matching existing photos, official references,
internal links, horizontal overflow and preservation of SEO.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,os
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'scripts/v145_maritime_content.json').read_text('utf8'))['entries']
base=os.environ.get('NF_V145_BASE','http://127.0.0.1:8789').rstrip('/')
out=root/'audit-output/v145';out.mkdir(parents=True,exist_ok=True)
result={'scope':'V145','domain':base,'tested':0,'expected':len(manifest)*3,'errors':[],'screenshots':[],'pages':[]}
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
 for slug,info in manifest.items():
  for width in [320,390,1440]:
   page=browser.new_page(viewport={'width':width,'height':900},device_scale_factor=1)
   bad=[];url='/things-to-do/'+slug+'/'
   try:
    response=page.goto(base+url,wait_until='domcontentloaded',timeout=40000)
    if not response or response.status!=200: bad.append('page HTTP!=200')
    if page.locator('link[rel="canonical"]').get_attribute('href')!='https://www.nipponferry.com'+url:bad.append('canonical incorrect')
    if page.locator('meta[name="description"]').count()!=1:bad.append('meta description missing')
    if page.locator('h1').count()<1:bad.append('H1 missing')
    if page.locator('.nf301-header').count()!=1:bad.append('shared header missing')
    rootdiv=page.locator('[data-nf145="10-existing-guides"]')
    if rootdiv.count()!=1:bad.append('V145 detail missing')
    else:
     if rootdiv.locator('.nf145-step').count()!=5:bad.append('missing original five practical steps')
     if rootdiv.locator('.nf145-official-links a').count()!=len(info['sources']):bad.append('official link count changed')
     if rootdiv.locator('.nf145-related a').count()!=len(info['related']):bad.append('related links count changed')
     if len(rootdiv.inner_text())<1100:bad.append('too thin for V145 detail')
     if width==390:
      p=rootdiv.locator('.nf145-step p').first
      size=p.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)')
      if size<16:bad.append(f'mobile text too small {size}')
     for a in rootdiv.locator('.nf145-related a').all():
      href=a.get_attribute('href')
      if href not in ['/things-to-do/'+x+'/' for x in info['related']]:bad.append('unexpected related URL')
     if not rootdiv.locator('.nf145-return').is_visible():bad.append('safe-return notice invisible')
    if page.locator('link[href*="nf-v145-maritime-deep.css"]').count()!=1:bad.append('V145 stylesheet missing')
    if page.evaluate('document.documentElement.scrollWidth')>width+3:bad.append('page horizontal overflow')
    if width in (390,1440) and slug in ['shodoshima-ferry-island-access','amami-naze-cruise-port-day-trip','goto-fukue-cruise-port-day-trip','tokushima-komatsushima-cruise-port-day-trip']:
     rootdiv.scroll_into_view_if_needed()
     fn=f'{slug}-{width}.png';rootdiv.screenshot(path=str(out/fn),animations='disabled',timeout=30000);result['screenshots'].append(fn)
   except Exception as e:bad.append('browser: '+str(e)[:220])
   result['pages'].append({'slug':slug,'width':width,'errors':bad})
   result['errors'].extend([slug+' '+str(width)+': '+x for x in bad])
   page.close()
 browser.close()
result['tested']=len(result['pages'])
result['passed']=result['tested']==result['expected'] and not result['errors']
(out/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'passed':result['passed'],'screens':result['screenshots'],'cases':result['tested'],'errors':result['errors'][:14]},ensure_ascii=False))
raise SystemExit(0 if result['passed'] else 1)
