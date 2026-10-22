#!/usr/bin/env python3
"""V120: restore missing alt descriptions on 13 known decorative/informational existing assets.
No hero swaps, no metadata/canonical/title/H1 edits, no new posts.
"""
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1];SITE=ROOT/"site"
CAPTIONS={
 "/images/cash.jpg":"일본 여행 경비와 결제 정보를 설명하는 사진",
 "/images/cabin.jpg":"일본 페리 객실 선택을 설명하는 이미지",
 "/images/transport.jpg":"일본 여행 교통과 이동 방법 안내 이미지",
 "/images/esim.jpg":"일본 여행 유심과 이심 준비 안내 이미지",
 "/images/season.jpg":"일본 계절별 여행 안내 이미지",
 "/images/ferry.jpg":"일본 페리 및 크루즈 여행 참고 이미지",
 "/images/tsushima.jpg":"일본 대마도 여행지 사진",
 "/images/osaka.jpg":"일본 오사카 여행지 사진",
 "/images/fukuoka.jpg":"일본 후쿠오카 여행지 사진",
 "/images/hokkaido.jpg":"일본 홋카이도 여행지 사진",
 "/images/kobe.jpg":"일본 고베 여행지 사진",
 "/images/car.jpg":"일본 렌터카 이동 안내 이미지",
 "/images/shimonoseki.jpg":"일본 시모노세키 여행지 사진",
}
PAT=re.compile(r"<img\b[^>]*>",re.I|re.S)
META=[r"<title>[\s\S]*?</title>",r'<meta name="description"[^>]*>',r'<link rel="canonical"[^>]*>',r"<h1\b[^>]*>[\s\S]*?</h1>",r'<script type="application/ld\+json">[\s\S]*?</script>']
def protect(html):
 return [[m.group() for m in re.finditer(rx,html,re.I)] for rx in META]
changed=[];unmatched=[];total=0
for file in sorted(SITE.rglob("*.html")):
 before=file.read_text("utf8")
 found=0
 def replace(m):
  global total
  nonlocal_alt=m.group()
  if re.search(r"\balt\s*=",nonlocal_alt,re.I):return nonlocal_alt
  a=re.search(r'\bsrc="([^"]+)"',nonlocal_alt)
  if not a:return nonlocal_alt
  path=a.group(1)
  if path not in CAPTIONS:
   unmatched.append({"file":str(file.relative_to(ROOT)),"src":path})
   return nonlocal_alt
  total+=1
  return nonlocal_alt.replace("<img",'<img alt="'+CAPTIONS[path]+'"',1)
 after=PAT.sub(replace,before)
 if before!=after:
  if protect(before)!=protect(after):raise ValueError("Protected SEO changed: "+str(file))
  changed.append(str(file.relative_to(ROOT)))
  file.write_text(after,"utf8")
if total!=224 or len(changed)!=56:raise ValueError(f"Expected exactly 224 photo alt corrections on 56 articles; observed {total} / {len(changed)}")
if unmatched:raise ValueError(f"Unknown nondecorative images without alt: {unmatched[:5]}")
report={"version":"V120","scope":"Existing content image accessibility, no SEO metadata changes or photo substitutions","updated_pages":len(changed),"alt_descriptions_added":total,"protected_seo":True,"source_files":changed}
out=ROOT/"audit-reports/v120";out.mkdir(parents=True,exist_ok=True)
(out/"alt-audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps({k:report[k] for k in ("updated_pages","alt_descriptions_added","protected_seo")},ensure_ascii=False))
