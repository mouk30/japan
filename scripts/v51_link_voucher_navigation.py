#!/usr/bin/env python3
"""Add the voucher navigation link to each eligible published HTML page.

Edits only header desktop/mobile nav wrappers, never article content or images.
"""
from pathlib import Path
from collections import Counter
import json
import re

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"
REPORT=ROOT/"docs"/"v51-voucher-navigation-audit.json"
DESKTOP=re.compile(r'<nav\b[^>]*class="[^"]*\bdesktop-nav\b[^"]*"[^>]*>[\s\S]*?</nav>')
MOBILE=re.compile(r'<div\b[^>]*class="[^"]*\bmobile-menu\b[^"]*"[^>]*>[\s\S]*?</div>')
LINK='<a href="/voucher/" class="nav-voucher">🎟 쿠폰·바우처</a>'
MLINK='<a href="/voucher/">🎟 쿠폰·바우처</a>'
def add(text,pat,closing,link):
    arr=pat.findall(text)
    if len(arr)!=1:return text,False
    matched=arr[0]
    if re.search(r'href=["\']/voucher/["\']',matched):return text,False
    new=matched.replace(closing,link+closing,1)
    return text.replace(matched,new,1),True

def main():
    count=Counter()
    changed=[]
    for p in sorted(SITE.rglob("*.html")):
        if any(x in p.parts for x in (".git",".vercel","node_modules")):continue
        count["scanned"]+=1
        original=p.read_text("utf-8")
        new,d=add(original,DESKTOP,"</nav>",LINK)
        new,m=add(new,MOBILE,"</div>",MLINK)
        if new!=original:
            p.write_text(new,"utf-8")
            changed.append({"path":str(p.relative_to(ROOT)),"desktop":d,"mobile":m})
            count["updated_pages"]+=1
            count["desktop_links_added"]+=int(d)
            count["mobile_links_added"]+=int(m)
        if DESKTOP.search(new):
            count["pages_with_desktop_header"]+=1
            if not re.search(r'href=["\']/voucher/["\']', DESKTOP.search(new).group()):
                count["unlinked_desktop_headers"]+=1
        if MOBILE.search(new):
            count["pages_with_mobile_header"]+=1
            if not re.search(r'href=["\']/voucher/["\']',MOBILE.search(new).group()):
                count["unlinked_mobile_headers"]+=1
    assert count["desktop_links_added"]>5, "unexpected low desktop link coverage"
    assert count["unlinked_desktop_headers"]==0
    assert count["unlinked_mobile_headers"]==0
    assert (SITE/"voucher"/"index.html").exists()
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({"summary":dict(count),"files":changed},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(dict(count),ensure_ascii=False))

if __name__=="__main__": main()
