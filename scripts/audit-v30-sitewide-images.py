#!/usr/bin/env python3
"""Read-only 1047+ HTML page sitewide audit for broken image references and strong topical conflicts.
No image swaps based on loose keyword guesses. Produces JSON evidence for human review.
"""
from pathlib import Path
from collections import Counter,defaultdict
from html import unescape
from urllib.parse import unquote,urlsplit
import re,json

root=Path("site");pages=sorted(root.rglob("index.html"))
regional={
"아키타":"akita","아오모리":"aomori","오타루":"otaru","삿포로":"sapporo",
"홋카이도":"hokkaido","후쿠오카":"fukuoka","하카타":"hakata",
"오사카":"osaka","나고야":"nagoya","고베":"kobe","나가사키":"nagasaki",
"시미즈":"shimizu","요코하마":"yokohama","도쿄":"tokyo",
"교토":"kyoto","오키나와":"okinawa","나하":"naha","이시가키":"ishigaki",
"벳푸":"beppu","가고시마":"kagoshima","구마모토":"kumamoto",
"사세보":"sasebo","히로시마":"hiroshima","구레":"kure",
"이와쿠니":"iwakuni","모지코":"mojiko","다카마쓰":"takamatsu",
"아부라쓰":"aburatsu","마이즈루":"maizuru","미야코지마":"miyakojima",
"시모노세키":"shimonoseki","대마도":"tsushima"}
# Explicit aliases permitted when a photo covers a larger travel region.
alias=[set(("fukuoka","hakata")),set(("hokkaido","sapporo","otaru")),set(("okinawa","naha")),set(("tokyo","yokohama"))]
def htmltext(s):
 return re.sub(r"<[^>]+>","",unescape(s)).strip()
def src_exists(raw):
 val=unquote(raw.split('?',1)[0]).lstrip('/')
 if not val.startswith("images/"):return True
 return (root/val).exists()
def hero_candidate(s):
 # Prioritize OG image, otherwise first image after the article heading, not mascot/logo.
 og=re.search(r'<meta\s+(?:property|name)="(?:og:image|twitter:image)"\s+content="([^"]+)"',s)
 if og:
  m=re.search(r"/images/[^\s?#\"']+",og[1])
  if m:return m[0]
 start=s.find('<h1')
 if start<0:return ''
 end=s.find('</h1>',start)
 imgs=re.findall(r'<img\b[^>]*\bsrc="(/images/[^"]+)"',s[end+5:])
 for i in imgs:
  if not any(x in i for x in ["mascot.","kakao-talk.","favicon"]):return i
 return ''
allbroken=[];unmatched=[];missinghero=[];pageCounts=[];strong=[];repeats=defaultdict(list)
for page in pages:
 txt=page.read_text(encoding="utf8",errors="replace")
 title=htmltext(re.search(r'<h1[^>]*>([\s\S]*?)</h1>',txt).group(1)) if re.search(r'<h1[^>]*>([\s\S]*?)</h1>',txt) else ""
 imgs=[x for x in re.findall(r'<img\b[^>]*?\bsrc="(/images/[^"]+)"',txt) if "mascot." not in x and "kakao-talk." not in x]
 broken=[x for x in imgs if not src_exists(x)]
 if broken: allbroken.append({"page":str(page),"title":title,"broken":sorted(set(broken))})
 main_img=hero_candidate(txt)
 if not main_img and "<article" in txt:missinghero.append({"page":str(page),"title":title})
 if main_img and not src_exists(main_img):unmatched.append({"page":str(page),"title":title,"og_or_hero":main_img})
 pageCounts.append({"page":str(page),"total_images":len(imgs),"main":main_img})
 if main_img:
  repeats[main_img].append(str(page))
  low=main_img.lower().split('/')[-1]
  regions=[(ko,en) for ko,en in regional.items() if ko in title]
  mentions=[en for en in set(regional.values()) if en+"-" in low or low.startswith(en+".")]
  if regions and mentions:
   regionnames=set(en for _,en in regions)
   def matches(en):
    if en in regionnames:return True
    return any(en in group and regionnames.intersection(group) for group in alias)
   if not any(matches(en) for en in mentions):
    # Only single-destination articles; comparisons mention multiple valid regions.
    if len(regionnames)==1 and not any(x in title for x in [" vs "," 비교 ","·","에서","까지"]):
     strong.append({"page":str(page),"title":title,"main_photo":main_img,"photo_region":mentions})
# Text categories: reliable false match, not broad semantics, card-only.
for hub in ["shopping","practical","couple","seasons"]:
 page=root/hub/"index.html"
 if not page.is_file():continue
 s=page.read_text()
 for url,image,title in re.findall(r'<a class="dircard" href="([^"]+)"><img[^>]*src="([^"]+)"[^>]*>(?:<span class="season-photo-note">[^<]*</span>)?<div class="dirin"><small>[^<]*</small><h2>([^<]+)</h2>',s):
  im=image.lower()
  bad=False
  if "eSIM" in title and any(x in im for x in ["garden","shrine","rail","train","cash","kobe","osaka"]):bad=True
  if "버스" in title and " vs " not in title and any(x in im for x in ["shinkansen","tunnel","yurikamome","goshuin","ekiben","railway","station-marunouchi"]):bad=True
  if "드럭스토어" in title and any(x in im for x in ["ramen","izakaya","kimono","ekiben","ryokan","bento"]):bad=True
  if "코인락커" in title and "cabin" in im:bad=True
  if "교통카드" in title and "goshuin" in im:bad=True
  if bad: strong.append({"page":str(page),"url":url,"title":title,"main_photo":image,"reason":"category image contradiction"})
report={"html_pages_scanned":len(pages),"img_references":sum(x["total_images"] for x in pageCounts),
 "missing_images":allbroken,"missing_primary":missinghero,"broken_primary":unmatched,
 "strong_location_or_category_mismatches":strong,
 "top_reused_primary":[{"src":img,"pages":len(entries)} for img,entries in sorted(repeats.items(),key=lambda x:-len(x[1]))[:25]],
 "summary":{"broken_img_pages":len(allbroken),"broken_primary":len(unmatched),"missing_primary_candidates":len(missinghero),"flagged_mismatches":len(strong)}}
out=Path("audit-reports/v30/sitewide-scan.json");out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print("V30_SITEWIDE_AUDIT",json.dumps({"html_pages_scanned":report["html_pages_scanned"],"img_references":report["img_references"],**report["summary"]},ensure_ascii=False),flush=True)
if strong:print("V30_FLAGGED_EXAMPLES",json.dumps(strong[:35],ensure_ascii=False),flush=True)
print("V32_MISSING_HERO_CANDIDATES",json.dumps(missinghero,ensure_ascii=False),flush=True)
if allbroken:print("V30_BROKEN_EXAMPLES",json.dumps(allbroken[:20],ensure_ascii=False),flush=True)
# Broken assets are definite regression risks. Semantic flags require review, not automatic removal.
print("V30_ALL_BROKEN",json.dumps(allbroken,ensure_ascii=False),flush=True)
# Scan reports findings rather than failing: repairs are a separate verified workflow.
