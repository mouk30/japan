#!/usr/bin/env python3
"""V148: remove long editorial photo-provenance prose from the *visible reading flow*.

Only high-confidence picture provenance (Wikimedia/CC photo-credit elements) is moved
into one collapsed, keyboard-accessible photo-attribution disclosure per existing page.
Retain every original author, photographer, link, license, modification notice and year
inside the disclosure to honor Creative Commons source conditions.
Do not change URLs, images, image alt, title, article text, canonicals, sitemap or SEO.

Run: python scripts/v148_compact_photo_credits.py
     python scripts/v148_compact_photo_credits.py --audit-only
"""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess
from pathlib import Path

ROOT=Path("site")
OUT=Path("audit-output/v148")
MARKER="nf-v148-photo-credits"
TAG=re.compile(r"<(p|figcaption|small)\b([^>]*)>(.*?)</\1\s*>",re.I|re.S)
ASIDE=re.compile(r"<aside\b([^>]*)>(.*?)</aside\s*>",re.I|re.S)
CREDIT_CLASS=re.compile(r"(?:credit|attribution|photo-source|photo-caption)",re.I)
PHOTO_WORDS=("사진","촬영","라이선스","저작","원본","webp","cc by","cc0","flickr","credit","photograph","attribution","source")
ASSET_SOURCES=("commons.wikimedia.org/wiki/file:","creativecommons.org/licenses/","creativecommons.org/publicdomain/")
CSS='''<style id="nf-v148-credit-style">
#nf-v148-photo-credits{box-sizing:border-box;max-width:1120px;width:calc(100% - 36px);
margin:22px auto 34px;border:1px solid #d8e5ec;border-radius:11px;background:#f9fbfc;
color:#486477;font-family:inherit;font-size:13px;line-height:1.7}
#nf-v148-photo-credits summary{cursor:pointer;list-style:revert;padding:10px 15px;
font-size:13px;font-weight:700;color:#46697b;outline-offset:3px}
#nf-v148-photo-credits summary:hover{color:#155979}
#nf-v148-photo-credits summary:focus-visible{outline:3px solid #087cac}
#nf-v148-photo-credits .nf-v148-credit-inner{padding:7px 17px 16px;border-top:1px solid #e5edf2;
max-height:min(65vh,650px);overflow-y:auto}
#nf-v148-photo-credits .nf-v148-credit-inner a{color:#146282;text-decoration:underline;text-underline-offset:2px;overflow-wrap:anywhere}
#nf-v148-photo-credits .nf-v148-credit-entry{margin:8px 0;padding:8px 0;border-bottom:1px solid #e7edf1;overflow-wrap:anywhere}
#nf-v148-photo-credits .nf-v148-credit-entry:last-child{border-bottom:0}
@media(max-width:600px){#nf-v148-photo-credits{font-size:12px;margin:17px auto 26px}
#nf-v148-photo-credits summary{font-size:12px;padding:11px 13px}
#nf-v148-photo-credits .nf-v148-credit-inner{padding:8px 12px 14px}}
</style>'''
def is_photo_credit(attrs: str, body: str)->bool:
    txt=(attrs+" "+body).lower()
    # Never hide navigational links/buttons to actual travel guides inside credit disclosures.
    if re.search(r'href=["\\\']/[^"\\\']+["\\\']',body,re.I) or "게시글 보기" in body:
        return False
    if re.search(r'class=["\\\'][^"\\\']*actions[^"\\\']*["\\\']',attrs,re.I):
        return False
    if "http" not in txt: return False
    if not any(domain in txt for domain in ASSET_SOURCES):return False
    if not any(term in txt for term in PHOTO_WORDS):return False
    # Transparency about AI imagery must remain visible, not be hidden as CC credit.
    if "ai 생성" in body.lower() or "생성 참고 이미지" in body:return False
    return True

def move_credits(src: str):
    found=[]
    def move_aside(m):
        attrs,body=m.group(1),m.group(2)
        if CREDIT_CLASS.search(attrs) and is_photo_credit(attrs,body):
            found.append(("aside",body))
            return ""
        return m.group(0)
    src=ASIDE.sub(move_aside,src)
    def move_item(m):
        tag,attrs,body=m.group(1),m.group(2),m.group(3)
        if is_photo_credit(attrs,body):
            found.append((tag.lower(),body))
            return ""
        return m.group(0)
    src=TAG.sub(move_item,src)
    return src,found

def process(path:Path, audit_only:bool, source_override=None):
    old=path.read_text(encoding="utf-8") if source_override is None else source_override
    if f'id="{MARKER}"' in old:
        return None
    new,found=move_credits(old)
    if not found:
        if source_override is not None and not audit_only:
            path.write_text(old,encoding="utf-8")
        return None
    # These full prose blocks were source acknowledgments, not the picture itself.
    entries="".join('<div class="nf-v148-credit-entry">'+body+'</div>' for _,body in found)
    panel='<details id="'+MARKER+'" class="nf-v148-credit-details">'+\
        '<summary>사진 출처 보기</summary><div class="nf-v148-credit-inner">'+entries+'</div></details>'
    if "</head>" in new:
        new=new.replace("</head>",CSS+"</head>",1)
    else:
        panel=CSS+panel
    # Attribution remains accessible at the end of the existing page.
    if "</main>" in new:
        new=new.replace("</main>",panel+"</main>",1)
    elif "<footer" in new:
        new=new.replace("<footer",panel+"<footer",1)
    elif "</body>" in new:
        new=new.replace("</body>",panel+"</body>",1)
    else:
        raise ValueError(f"Cannot find safe document insertion point: {path}")
    if len(re.findall(r'id="'+MARKER+'"',new))!=1:
        raise ValueError(f"Duplicate photo disclosure: {path}")
    if not all(link in new for link in re.findall(r'href=["\'](https?://[^"\']+)["\']',old) if "commons.wikimedia.org" in link or "creativecommons.org" in link):
        raise ValueError(f"Photo author/license hyperlinks were lost: {path}")
    # Ensure other SEO, images, booking/canonical anchors were untouched
    def capture(pattern,text):
        return re.findall(pattern,text,re.I|re.S)
    for pattern in (r'<img\b[^>]*>',r'<link\b[^>]*rel=["\']canonical["\'][^>]*>',
                    r'<title>.*?</title>',r'<meta\b[^>]*name=["\']description["\'][^>]*>'):
        if capture(pattern,old)!=capture(pattern,new):
            raise ValueError(f"SEO/image metadata unexpectedly changed: {path}")
    if not audit_only:path.write_text(new,encoding="utf-8")
    return dict(path=path.as_posix(),moved=len(found),tags={tag:sum(k==tag for k,_ in found) for tag,_ in found},
                old_bytes=len(old.encode()),new_bytes=len(new.encode()),
                old_sha256=hashlib.sha256(old.encode()).hexdigest(),
                license_links_preserved=True,
                no_image_or_seo_change=True,
                includes_v140=any("V140 실사 출처" in body for _,body in found))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--audit-only",action="store_true")
    ap.add_argument("--rewrite-from-main",action="store_true",help="Rebuild only existing folded pages from their unchanged main-branch originals")
    args=ap.parse_args()
    rows=[]; total=0; errors=[]
    for p in sorted(ROOT.rglob("*.html")):
        try:
            raw=None
            if args.rewrite_from_main:
                if f'id="{MARKER}"' not in p.read_text(encoding="utf-8"):
                    continue
                raw=subprocess.check_output(["git","show","origin/main:"+p.as_posix()],text=True)
            item=process(p,args.audit_only,source_override=raw)
            if item: rows.append(item);total+=item["moved"]
        except Exception as err:
            errors.append(f"{p}: {err}")
    summary=dict(affected_pages=len(rows),photo_provenance_blocks_collapsed=total,
       homepage_v140_removed_from_visible_flow=any(r["includes_v140"] and r["path"]=="site/index.html" for r in rows),
       no_new_article_pages=True,retains_cc_credit_links=True,
       collapsed_disclosure_label="사진 출처 보기",errors=errors,files=rows)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"photo-credits-summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k!="files"},ensure_ascii=False))
    print("top affected:",[(r["path"],r["moved"]) for r in sorted(rows,key=lambda x:-x["moved"])[:20]])
    if errors or not summary["homepage_v140_removed_from_visible_flow"] or total<5:
        raise SystemExit("V148 audit failed: unsafe transformation or expected credits not found")
if __name__=="__main__":main()
