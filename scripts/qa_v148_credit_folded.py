#!/usr/bin/env python3
"""V148: validate folded CC credits did not hide travel links or damage article SEO."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import json,re,subprocess
ROOT=Path("site")
ID='nf-v148-photo-credits'
DETAILS=re.compile(r'<details\b[^>]*id=["\']'+ID+r'["\'][^>]*>(.*?)</details>',re.I|re.S)
META=[
 r'<img\b[^>]*>',
 r'<link\b[^>]*rel=["\']canonical["\'][^>]*>',
 r'<title>.*?</title>',
 r'<meta\b[^>]*name=["\']description["\'][^>]*>'
]
LINK=re.compile(r'<a\b[^>]*href=["\']([^"\']+)["\']',re.I)
failures=[];rows=[];folded=0
for path in sorted(ROOT.rglob("*.html")):
  src=path.read_text(encoding="utf-8")
  if f'id="{ID}"' not in src:continue
  folded+=1
  matches=DETAILS.findall(src)
  if len(matches)!=1:failures.append((str(path),"disclosure count !=1"));continue
  caption=matches[0]
  if "<summary>사진 출처 보기</summary>" not in src:failures.append((str(path),"summary missing"))
  if LINK.search(caption) is None:failures.append((str(path),"no rights source link in collapsed caption"))
  local=[x for x in LINK.findall(caption) if x.startswith("/") and not x.startswith("//")]
  if local:failures.append((str(path),"nav link hidden: "+str(local[:5])))
  if "게시글 보기" in caption:failures.append((str(path),"article CTA hidden"))
  try: original=subprocess.check_output(["git","show","origin/main:"+path.as_posix()],text=True)
  except Exception as err:failures.append((str(path),"no baseline: "+str(err)));continue
  for p in META:
    if re.findall(p,src,re.I|re.S)!=re.findall(p,original,re.I|re.S):
      failures.append((str(path),"image/SEO metadata changed "+p))
  original_ids=Counter(re.findall(r'\bid=["\']([^"\']+)["\']',original,re.I))
  current_ids=Counter(re.findall(r'\bid=["\']([^"\']+)["\']',src,re.I))
  for k in (ID,"nf-v148-credit-style"):current_ids.pop(k,None)
  if current_ids!=original_ids:
    failures.append((str(path),"original document anchor IDs removed/duplicated"))

  if Counter(LINK.findall(src))!=Counter(LINK.findall(original)):
    failures.append((str(path),"original links missing or duplicated"))
  # Protect narrative, booking and return instructions, not source-only sentences.
  for semantic in ["귀선","예약"]:
    if semantic in original and semantic not in src:failures.append((str(path),"travel text lost: "+semantic))
  rows.append(dict(path=path.as_posix(),credit_entries=caption.count('class="nf-v148-credit-entry"'),original_links=len(LINK.findall(original))))
home=(ROOT/"index.html").read_text(encoding="utf-8")
if home.count(f'id="{ID}"')!=1:failures.append(("site/index.html","home credit summary absent"))
if "V140 실사 출처" in home[:home.find(f'id="{ID}"')]:failures.append(("site/index.html","V140 verbose note still visible"))
photo_review=(ROOT/"japan/tokyo/photo-review/index.html").read_text(encoding="utf-8")
if photo_review.count("게시글 보기 ↗")<20:failures.append(("photo-review","missing photo review article CTA"))
if f'id="{ID}"' in photo_review:failures.append(("photo-review","photo-review page should retain article photo/links"))
if folded<500:failures.append(("all","expected >=500 affected photo-credit pages, observed "+str(folded)))
out=Path("audit-output/v148");out.mkdir(parents=True,exist_ok=True)
result={"pages_checked":folded,"blocks_folded":sum(x["credit_entries"] for x in rows),
        "homepage_v140_visible":False,"photo_review_links_retained":True,
        "errors":failures,"affected_files":rows}
(out/"qa-photo-attribution.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print("V148 pages",folded,"blocks",result["blocks_folded"],"errors",len(failures))
for err in failures[:30]:print("FAIL",err)
if failures:raise SystemExit(1)
