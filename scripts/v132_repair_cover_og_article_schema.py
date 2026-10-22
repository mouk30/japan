#!/usr/bin/env python3
"""V132 guardrail repair of cover/OG/Article image metadata mismatches on existing pages.

Candidates discovered by an independent full-site source scan.
Preserves existing title, meta description, canonical, H1, all other structured
schema fields, body, alt, photo rights and every URL; only adjusts OG/Twitter
image references and the Article schema image value to match actual cover.
No photographic location or rights claims are inferred.
"""
from pathlib import Path
from collections import defaultdict
import json,re,hashlib,argparse
ROOT=Path(__file__).resolve().parents[1]
INVENTORY=ROOT/"audit-reports/v132/sitewide-inventory.json"
OUT=ROOT/"audit-reports/v132/image-metadata-repair.json"
FIELDS={
 "title":r"<title>(.*?)</title>",
 "description":r'<meta name="description" content="([^"]*)"',
 "canonical":r'<link rel="canonical" href="([^"]*)"',
 "H1":r"<h1[^>]*>([\s\S]*?)</h1>"
}
def only(html,regex):
 m=re.search(regex,html,re.S)
 return m.group(1) if m else None
def prepare():
 data=json.loads(INVENTORY.read_text("utf8"))
 candidates=defaultdict(set)
 for row in data["findings"]["image_meta_mismatch"]:
  candidates[row["page"]].add(row["issue"])
 if len(candidates)!=83:raise ValueError("expected 83 photo-metadata pages, got "+str(len(candidates)))
 staged=[];fails=[];unchanged=[]
 for page,issues in sorted(candidates.items()):
  path=ROOT/"site"/page.lstrip("/")/"index.html"
  try:
   old=path.read_text("utf8")
   cover=re.search(r"""<img[^>]*class=["'][^"']*cover[^"']*["'][^>]*>""",old)
   if not cover:raise ValueError("missing single cover tag")
   img=re.search(r"""src=["']([^"']+)""",cover.group(0))
   if not img:raise ValueError("cover src missing")
   src=img.group(1)
   if not src.startswith("/images/"):raise ValueError("cover not local")
   if not (ROOT/"site"/src.lstrip("/")).is_file():raise ValueError("new OG target local photo missing")
   target="https://www.nipponferry.com"+src
   baseline={k:only(old,regex) for k,regex in FIELDS.items()}
   social=re.search(r'<meta property="og:image" content="([^"]*)"',old)
   if not social:raise ValueError("OG image absent")
   oldog=social.group(1)
   updated=old
   ogchange=False
   if oldog!=target:
    oldogtag='<meta property="og:image" content="'+oldog+'">'
    if old.count(oldogtag)!=1:raise ValueError("OG meta not unique")
    updated=updated.replace(oldogtag,'<meta property="og:image" content="'+target+'">',1)
    for role in ("name","property"):
     prev='<meta '+role+'="twitter:image" content="'+oldog+'">'
     new='<meta '+role+'="twitter:image" content="'+target+'">'
     if prev in updated:updated=updated.replace(prev,new,1)
    ogchange=True
   scripts=list(re.finditer(r"""<script[^>]*type=["']application/ld\+json["'][^>]*>([\s\S]*?)</script>""",updated,re.I))
   schema_actions=[]
   # Apply from the last script toward the first so source span indices stay valid.
   for match in reversed(scripts):
    body=match.group(1)
    try:parsed=json.loads(body)
    except (ValueError,TypeError):continue
    group=parsed if isinstance(parsed,list) else [parsed]
    articles=[p for p in group if isinstance(p,dict) and p.get("@type")=="Article"]
    if not articles:continue
    if len(articles)!=1:raise ValueError("multiple Articles in one LD block")
    current=articles[0].get("image")
    urls=current if isinstance(current,list) else [current]
    if len(urls)!=1 or not isinstance(urls[0],str):raise ValueError("non-single Article image")
    oldarticle=urls[0]
    if oldarticle==target:continue
    # Replace the JSON literal in this script body, not other FAQ or Breadcrumb content.
    oldstr=json.dumps(oldarticle,ensure_ascii=False)
    newstr=json.dumps(target,ensure_ascii=False)
    if body.count(oldstr)!=1:
     oldstr=json.dumps(oldarticle)
     newstr=json.dumps(target)
    if body.count(oldstr)!=1:raise ValueError("old Article photo path not uniquely found")
    newbody=body.replace(oldstr,newstr,1)
    updated=updated[:match.start(1)]+newbody+updated[match.end(1):]
    schema_actions.append((oldarticle,target))
   if not schema_actions and "cover_vs_article_schema" in issues:
    raise ValueError("schema mismatch reported but no single Article image changed")
   for k,regexp in FIELDS.items():
    if only(updated,regexp)!=baseline[k]:raise ValueError("protected SEO drift "+k)
   if only(updated,r'<meta property="og:image" content="([^"]*)"')!=target:
    raise ValueError("OG target failed")
   if src not in updated:raise ValueError("lost original image")
   if updated!=old:staged.append({"path":path,"page":page,"before_sha256":hashlib.sha256(old.encode()).hexdigest(),"after_sha256":hashlib.sha256(updated.encode()).hexdigest(),"new":updated,"cover":src,"og_fixed":ogchange,"schema_fixed":len(schema_actions)})
   else:unchanged.append(page)
  except Exception as e:fails.append({"page":page,"error":str(e)[:200]})
 return staged,unchanged,fails
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--apply",action="store_true")
 a=ap.parse_args()
 staged,unchanged,fail=prepare()
 if fail:raise ValueError("FAILED TO PRESERVE GUARDS: "+json.dumps(fail,ensure_ascii=False))
 if len(staged)+len(unchanged)!=83:raise ValueError("83-page reconciliation mismatch")
 if a.apply:
  for row in staged:row["path"].write_text(row["new"],encoding="utf8")
 report={"version":"V132","mode":"apply" if a.apply else "preview","checked":83,"changed":len(staged),"already_correct":len(unchanged),"og_fixed":sum(row["og_fixed"] for row in staged),"article_schema_fixed":sum(row["schema_fixed"] for row in staged),"protected_seo":"title, description, canonical and H1 preserved exactly; all non-image JSON-LD untouched","issues":fail,"pages":[{k:v for k,v in row.items() if k not in ("path","new")} for row in staged]}
 if a.apply:
  OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
 print(json.dumps({k:v for k,v in report.items() if k!="pages"},ensure_ascii=False))
if __name__=="__main__":main()
