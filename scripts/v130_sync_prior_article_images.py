#!/usr/bin/env python3
"""V130: sync 20 prior real-photo Article structured image URLs, preserving other SEO.
Only V126/V127 known-photo heroes with exact verified original JSON-LD are touched.
"""
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FIELD_PATTERNS={
 "title":r"<title>([^<]*)</title>",
 "description":r'<meta name="description" content="([^"]*)"',
 "canonical":r'<link rel="canonical" href="([^"]*)"',
 "h1":r"<h1[^>]*>([\s\S]*?)</h1>",
 "jsonld":r'<script type="application/ld\+json">([\s\S]*?)</script>',
}
def only(h,pat): 
 m=re.search(pat,h,re.S)
 if not m:raise ValueError("not found "+pat[:45])
 return m.group(1)
def run(apply):
 changed=[];fail=[];allrows=[]
 for v in ("126","127"):
  specs=json.loads((ROOT/f"audit-reports/v{v}/photo-plan.json").read_text("utf8"))["selected"]
  originals={p["slug"]:p for p in json.loads((ROOT/f"audit-reports/v{v}/seo-and-ai-candidate-baselines.json").read_text("utf8"))["pages"]}
  for x in specs:
   slug=x["slug"];p=originals[slug]
   filename=ROOT/"site"/p["page"].lstrip("/")/"index.html"
   html=filename.read_text("utf8")
   expected_url="https://www.nipponferry.com"+x["output"]
   if only(html,r'<meta property="og:image" content="([^"]*)"')!=expected_url:
    fail.append(slug+": OG mismatch");continue
   if 'class="cover" src="'+x["output"]+'"' not in html:
    fail.append(slug+": cover mismatch");continue
   for key in ("title","description","canonical","h1"):
    if only(html,FIELD_PATTERNS[key])!=p[key]:fail.append(slug+": "+key+" SEO drift")
   old=p["jsonld"]
   if old.count(p["og_image"])!=1:fail.append(slug+": old JSON-LD expected single image");continue
   new=old.replace(p["og_image"],expected_url)
   actual=only(html,FIELD_PATTERNS["jsonld"])
   if actual not in (old,new):fail.append(slug+": modified unknown JSON-LD");continue
   parsed=json.loads(new)
   article=[obj for obj in (parsed if isinstance(parsed,list) else [parsed]) if obj.get("@type")=="Article"]
   if len(article)!=1 or article[0].get("image")!=[expected_url]:
    fail.append(slug+": invalid new Article image");continue
   if actual==old:
    if apply:
     before='<script type="application/ld+json">'+old+'</script>'
     if html.count(before)!=1:fail.append(slug+": JSON-LD block count");continue
     html=html.replace(before,'<script type="application/ld+json">'+new+'</script>',1)
     filename.write_text(html,"utf8")
    changed.append(slug)
   allrows.append({"slug":slug,"v":v,"image_url":expected_url,"post_state":"synced" if apply or actual==new else "needs_update"})
 if len(allrows)!=20:fail.append("expected twenty protected photos, got "+str(len(allrows)))
 report={"version":"V130","checked":len(allrows),"updated_now":len(changed),"verified":len(allrows)==20 and not fail,"issues":fail,"pages":allrows}
 out=ROOT/"audit-reports/v130"
 out.mkdir(parents=True,exist_ok=True)
 if apply:(out/"jsonld-photo-sync-result.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
 print(json.dumps({k:report[k] for k in ("checked","updated_now","verified","issues")},ensure_ascii=False))
 return not fail
if __name__=="__main__":
 arg=sys.argv[1:] 
 if arg not in ([],["--apply"],["--check"]):raise SystemExit("use --apply or --check")
 raise SystemExit(0 if run("--apply" in arg) else 1)
