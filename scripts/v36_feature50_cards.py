#!/usr/bin/env python3
"""V36.3: Give the pre-existing 50 editorial photo links companion-guide description cards.

This does not add pages or replace their established editorial images.
Card excerpts come from the linked article's existing meta description, not invented copy.
"""
from __future__ import annotations
import html
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"
PAGE=SITE/"things-to-do"/"index.html"
original=PAGE.read_text("utf-8")
if 'id="v36-feature-50-styles"' in original:
    raise RuntimeError("Already applied")
marker='id="japan-new-50"'
pos=original.find(marker)
if pos<0:raise RuntimeError("Missing editorial 50 section")
start=original[:pos]
tail=original[pos:]
section_end=tail.find("</section>")
if section_end<0:raise RuntimeError("No closing section for 50")
section=tail[:section_end]
replaced=[]
# Existing fully authored article cards have a photo and one title span.
pat=re.compile(r'<a href="(/things-to-do/([^"/]+)/)" style="[^"]+"><img([^>]+)><span style="[^"]+">([\s\S]*?)</span></a>')
def rewrite(match):
    url,slug,imgattrs,title=match.groups()
    source=SITE/"things-to-do"/slug/"index.html"
    if not source.is_file():raise RuntimeError(f"Missing linked article: {url}")
    content=source.read_text("utf-8")
    d=re.search(r'<meta name="description" content="([^"]+)"',content)
    excerpt=html.unescape(d.group(1)) if d else ""
    excerpt=re.sub(r'\s+', ' ', re.sub('<[^>]+>','',excerpt)).strip()
    if not excerpt:excerpt=f"{re.sub('<[^>]+>','',title).strip()}의 현장 경험과 이동 동선을 알아보세요."
    if len(excerpt)>95:excerpt=excerpt[:92].rstrip()+"…"
    real=isinstance(re.search(r'alt="[^"]*(?:실사|실제 촬영|실제 사진)[^"]*"',imgattrs),re.Match)
    note="현장 실사" if real else "여행 주제 참고 이미지"
    replaced.append(slug)
    return (f'<a class="v36-feature-card" href="{url}"><figure><img{imgattrs}>'
            f'<span>{note}</span></figure><div class="v36-feature-copy">'
            f'<h4>{title}</h4><p>{html.escape(excerpt)}</p>'
            '<small>게시글 자세히 보기 →</small></div></a>')
section,n=pat.subn(rewrite,section)
if len(replaced)!=50 or n!=50:raise RuntimeError(f"Expected exactly 50 cards, got {len(replaced)} / {n}")
new=start+section+tail[section_end:]
css="""<style id="v36-feature-50-styles">
#japan-new-50 .v36-feature-card{display:flex;flex-direction:column;min-width:0;overflow:hidden;background:#fff;border:1px solid #d6e5ea;border-radius:16px;color:#163e52;text-decoration:none;box-shadow:0 8px 22px rgba(12,57,76,.07);transition:transform .17s,box-shadow .17s;font-weight:400}
#japan-new-50 .v36-feature-card:hover{transform:translateY(-3px);box-shadow:0 14px 30px rgba(12,57,76,.15)}
#japan-new-50 .v36-feature-card figure{margin:0;position:relative;aspect-ratio:16/10;overflow:hidden;background:#d9e6e7}
#japan-new-50 .v36-feature-card figure img{width:100%;height:100%;display:block;object-fit:cover;aspect-ratio:auto}
#japan-new-50 .v36-feature-card figure span{position:absolute;bottom:7px;right:7px;background:#143e56dd;color:#fff;padding:3px 7px;border-radius:5px;font-size:10px;font-weight:700}
#japan-new-50 .v36-feature-copy{padding:13px 15px 17px;display:flex;flex:1;flex-direction:column;gap:8px}
#japan-new-50 .v36-feature-copy h4{font-size:17px;line-height:1.4;font-weight:900;margin:0;color:#16475d}
#japan-new-50 .v36-feature-copy p{font-size:12px;font-weight:400;color:#5e7782;line-height:1.7;margin:0;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
#japan-new-50 .v36-feature-copy small{margin-top:auto;padding-top:8px;font-size:11px;font-weight:800;color:#097e91}
@media(max-width:620px){#japan-new-50 .v36-feature-copy{padding:11px}#japan-new-50 .v36-feature-copy h4{font-size:15px}#japan-new-50 .v36-feature-copy p{font-size:11px}}
@media(prefers-reduced-motion:reduce){#japan-new-50 .v36-feature-card{transition:none}}
</style>"""
new=new.replace("</head>",css+"</head>",1)
PAGE.write_text(new,encoding="utf-8")
print("V36.3: 50/50 pre-existing image-first editorial cards gained article-derived intros.")
