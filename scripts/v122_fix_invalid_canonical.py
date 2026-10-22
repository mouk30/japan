#!/usr/bin/env python3
"""V122 fix precisely 56 source-backed invalid canonical URLs without changing other SEO assets.
These URLs were pointing to non-existent paths not emitted by build.js/vercel.json.
"""
from pathlib import Path
from urllib.parse import urlsplit
import json,re
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/"site"
EVIDENCE=ROOT/"audit-reports/v121/remaining-work-and-source-evidence.json"
OUT=ROOT/"audit-reports/v122";OUT.mkdir(parents=True,exist_ok=True)
source=json.loads(EVIDENCE.read_text("utf8"))
cases=[x for x in source["canonical_details"] if x["type"]=="broken_canonical_target"]
if len(cases)!=56:raise ValueError(f"expected 56 source-confirmed broken canonicals, found {len(cases)}")
FIELDS=(r"<title>[\s\S]*?</title>",r"<meta name=['\"]description['\"][^>]*>",r"<h1\b[^>]*>[\s\S]*?</h1>",r"<script type=['\"]application/ld\+json['\"]>[\s\S]*?</script>")
def snapshot(s):
 return [[x.group(0) for x in re.finditer(p,s,re.I)] for p in FIELDS]
changes=[]
for x in cases:
  route=x["page"];f=SITE/route.lstrip("/")/"index.html"
  if not f.is_file():raise ValueError("Missing page "+route)
  old=x["canonical"];src=f.read_text("utf8")
  dst=SITE/urlsplit(old).path.lstrip("/")/"index.html"
  if dst.exists():raise ValueError("Original target now exists, do not replace "+old)
  match=re.search(r'<link\b[^>]*\brel\s*=\s*["\']canonical["\'][^>]*>',src,re.I)
  if not match or old not in match.group(0):raise ValueError("Original canonical not found "+route)
  new="https://www.nipponferry.com"+route
  before=match.group(0)
  after=before.replace(old,new)
  if after==before:raise ValueError("No canonical changed")
  revised=src[:match.start()]+after+src[match.end():]
  if snapshot(src)!=snapshot(revised):raise ValueError("Title description H1 or JSON-LD was altered "+route)
  if len(re.findall(r'<link\b[^>]*\brel\s*=\s*["\']canonical["\']',revised,re.I))!=1:
    raise ValueError("Must have exactly one canonical "+route)
  f.write_text(revised,"utf8")
  changes.append({"page":route,"previous_invalid":old,"corrected_self":new,"other_content_and_seo_unchanged":True})
assert len(changes)==56
report={"version":"V122","corrected_canonicals":len(changes),"existing_pages_changed":len(changes),"new_articles_created":0,"preserved":"all existing title, description, H1, JSON-LD, article body and current URLs","exceptions":"Two purpose-built /route/ and /routes/ redirects canonicalize /ferry/ intentionally and were not touched","pages":changes}
(OUT/"canonical-repair.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps({k:v for k,v in report.items() if k!="pages"},ensure_ascii=False,indent=2))
