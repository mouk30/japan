#!/usr/bin/env python3
"""V117 inventory: every HTML page, exact image and internal-link locations, AI hero disclosure and SEO.
No guesses or automatic replacements: emits inspectable grounded evidence.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,unquote
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"
OUT=ROOT/"audit-reports/v117"
OUT.mkdir(parents=True,exist_ok=True)
BASE="https://www.nipponferry.com"
class Tags(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.img=[];self.a=[];self.meta=[];self.links=[];self.h1=[];self.scripts=[];self.head_title=False;self.titles=[];self.ai_terms=[];self.current_h1=False
    def handle_starttag(self,tag,atts):
        d=dict(atts)
        if tag=="img":self.img.append(d)
        elif tag=="a":self.a.append(d)
        elif tag=="meta":self.meta.append(d)
        elif tag=="link":self.links.append(d)
        elif tag=="script":self.scripts.append(d)
        if tag=="title":self.head_title=True
        if tag=="h1":self.current_h1=True
    def handle_endtag(self,tag):
        if tag=="title":self.head_title=False
        if tag=="h1":self.current_h1=False
    def handle_data(self,data):
        if self.head_title:self.titles.append(data)
        if self.current_h1:self.h1.append(data)
def resolve(source, raw):
    raw=(raw or "").strip()
    if not raw or raw[0]=="#" or raw.startswith(("mailto:","tel:","javascript:","data:","blob:")):
        return None
    u=urlsplit(raw)
    if u.scheme and u.scheme not in ("http","https"):return None
    if u.netloc and u.netloc.lower() not in ("www.nipponferry.com","nipponferry.com"):return None
    path=unquote(u.path)
    if not path:return None
    if path.startswith("/"):candidate=SITE/path.lstrip("/")
    else:candidate=(source.parent/path)
    # Stay inside site and resolve conventional static folders.
    try:
        candidate=candidate.resolve()
        candidate.relative_to(SITE.resolve())
    except ValueError:return None
    if candidate.is_dir() or path.endswith("/"):candidate=candidate/"index.html"
    if candidate.exists():return None
    if candidate.suffix=="" and (Path(str(candidate)+".html")).exists():return None
    return "/"+str(candidate.relative_to(SITE.resolve())).replace("\\","/")
def scan():
    files=sorted(SITE.rglob("*.html"))
    image_broken=defaultdict(list);links_broken=defaultdict(list);canonical_issues=[];photos_ai=[];alt_missing=[]
    photos_by_type=Counter();outbound=defaultdict(set)
    metas=Counter();missing_seo=Counter();missing_seo_pages=defaultdict(list);samples=[]
    external=Counter();article_hero_count=0
    for file in files:
        relative="/"+file.relative_to(SITE).as_posix()
        if relative.endswith("/index.html"): url=relative[:-len("index.html")]
        else:url=relative
        try: html=file.read_text("utf8")
        except UnicodeDecodeError:continue
        p=Tags()
        try:p.feed(html)
        except Exception:continue
        metas["HTML pages"]+=1
        title="".join(p.titles).strip()
        meta_desc=next((m.get("content") for m in p.meta if m.get("name")=="description"),None)
        canonical=next((l.get("href") for l in p.links if l.get("rel")=="canonical"),None)
        if not title:missing_seo["title"]+=1;missing_seo_pages["title"].append(url)
        if not meta_desc:missing_seo["description"]+=1;missing_seo_pages["description"].append(url)
        if not canonical:missing_seo["canonical"]+=1;missing_seo_pages["canonical"].append(url)
        if not p.h1:missing_seo["H1"]+=1;missing_seo_pages["H1"].append(url)
        if canonical:
            normalized=urlsplit(canonical).path
            if not normalized.endswith("/") and normalized!= "/":normalized+="/"
            expected=url if url.endswith("/") else url
            if url.endswith("/") and normalized!=expected:
                canonical_issues.append({"page":url,"canonical":canonical,"expected":BASE+url})
        for i in p.img:
            source=i.get("src") or i.get("data-src")
            if source:
                missing=resolve(file,source)
                if missing:image_broken[missing].append(url)
            if not i.get("alt"):alt_missing.append({"page":url,"src":source})
        for a in p.a:
            href=a.get("href")
            if href:
                broken=resolve(file,href)
                if broken:links_broken[broken].append(url)
                if href.startswith("https://") or href.startswith("http://"):
                    host=urlsplit(href).netloc.lower()
                    if "nipponferry.com" not in host:
                        outbound[host].add(href);external[host]+=1
        # First article hero explicitly AI by alt or URL, not generic editorial folders.
        imgs=p.img
        hero=next((i for i in imgs if "cover" in (i.get("class") or "").split()),None)
        if hero:
            article_hero_count+=1
            name=(hero.get("src") or "")
            alt=hero.get("alt") or ""
            if re.search(r'AI|생성|연출|참고 이미지|generated',alt,re.I) or (
                name.startswith("/images/editorial/") and re.search(r'AI 생성|AI 여행|AI 연출',html[html.find(name):html.find(name)+350],re.I)
            ):
                photos_ai.append({"page":url,"hero":name,"alt":alt[:170],"first_heading":"".join(p.h1)[:120]})
            photos_by_type["editorial" if name.startswith("/images/editorial/") else "other"]+=1
    summary={
        "version":"V117","snapshot_method":"GitHub Actions checkout of main branch, static HTML parse",
        "scope":{"html_pages":len(files),"pages_scanned":metas["HTML pages"],"article_cover_images":article_hero_count},
        "photo":{"confirmed_ai_cover_candidates":len(photos_ai),"missing_local_images":len(image_broken),"missing_alt_tags":len(alt_missing),
                 "note":"Confirmed AI cover candidates inferred from explicit generated AI alt/caption, not all AI pixels sitewide"},
        "links":{"missing_internal_targets":len(links_broken),"distinct_external_hosts":len(outbound),
                 "note":"Static local path checks only; network availability of external reservations requires separate checks"},
        "seo":{"missing_fields":dict(missing_seo),"canonical_mismatches":len(canonical_issues)},
        "examples":{"ai_cover":photos_ai[:30],"missing_image":dict(list(image_broken.items())[:45]),
                    "broken_internal_link":dict(list(links_broken.items())[:45]),
                    "canonical":canonical_issues[:20]},
        "status":"Sitewide investigation, NOT a claim all places or usage rights are verified."
    }
    detail={"ai_cover_candidates":photos_ai,"missing_local_images":{k:sorted(set(v)) for k,v in image_broken.items()},
        "broken_internal_links":{k:sorted(set(v)) for k,v in links_broken.items()},
        "missing_img_alt":alt_missing[:600],"canonical_mismatches":canonical_issues,"missing_seo_pages":dict(missing_seo_pages),
        "external_links_by_host":{h:{"count":len(urls),"examples":sorted(urls)[:12]} for h,urls in sorted(outbound.items(),key=lambda p:-len(p[1]))},
        "external_link_unique_count":sum(len(v) for v in outbound.values())}
    (OUT/"sitewide-qa.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n","utf8")
    (OUT/"detail-inventory.json").write_text(json.dumps(detail,ensure_ascii=False,indent=2)+"\n","utf8")
    print(json.dumps({k:v for k,v in summary.items() if k!="examples"},ensure_ascii=False,indent=2))
    return summary
if __name__=="__main__":scan()
