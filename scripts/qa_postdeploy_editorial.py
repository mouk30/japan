#!/usr/bin/env python3
"""Verify exact PR #9 homepage + 85 editorial pages, locally or from the PUBLIC domain.

This is a deploy/SEO/assets health check, NOT search traffic, visual content accuracy,
photo licensing, live reservation availability, or conversion tracking.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
from urllib.request import Request, urlopen
import json
import time

ORIGIN="https://www.nipponferry.com"
MANIFEST=Path("scripts/postdeploy-editorial-manifest.json")
ROOT=Path("site")
OUT=Path("audit-output/postdeploy-editorial")
HOME_LINKS=[
    "/things-to-do/naha-cruise-terminal-kokusai-dori/",
    "/things-to-do/hakata-port-hakata-station-access/",
    "/things-to-do/nagasaki-matsugae-glover-garden-cruise-access/",
    "/things-to-do/ishigaki-cruise-kabira-bay-bus-taxi/",
]
LONGTAIL=[
    "/japan-cruise/busan-hakata-ferry-reservation/",
    "/japan-cruise/bukan-ferry-shimonoseki-price/",
    "/japan-cruise/panstar-miracle-osaka-cabin-types/",
]
AGENT="Mozilla/5.0 (compatible; NipponFerry-PostDeployQA/1.0)"

class Parse(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1=0;self.title="";self._title=False
        self.canonical=[];self.description=[];self.robots=[]
        self.images=[];self.links=[];self.jsonld=[];self._ld=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="h1":self.h1+=1
        if tag=="title":self._title=True
        if tag=="link" and "canonical" in a.get("rel",""):self.canonical.append(a.get("href",""))
        if tag=="meta" and a.get("name","").lower()=="description":self.description.append(a.get("content",""))
        if tag=="meta" and a.get("name","").lower()=="robots":self.robots.append(a.get("content","").lower())
        if tag=="a":self.links.append(a.get("href",""))
        if tag=="img":self.images.append(a.get("src",""))
        if tag=="script" and a.get("type")=="application/ld+json":self._ld=[]
    def handle_endtag(self,tag):
        if tag=="title":self._title=False
        if tag=="script" and self._ld is not None:
            try:self.jsonld.append(json.loads("".join(self._ld)))
            except ValueError:self.jsonld.append(None)
            self._ld=None
    def handle_data(self,data):
        if self._title:self.title+=data
        if self._ld is not None:self._ld.append(data)

def fetch(url,head=False):
    request=Request(url,headers={"User-Agent":AGENT},method="HEAD" if head else "GET")
    with urlopen(request,timeout=20) as response:
        return response.status,response.geturl(),response.headers.get("Content-Type",""),(b"" if head else response.read())

def request(url,head=False):
    last=None
    for attempt in range(2):
        try:return fetch(url,head)
        except Exception as exc:
            last=str(exc)
            if attempt==0:time.sleep(1)
    raise RuntimeError(last)

def local_get(path):
    target=ROOT/path.lstrip("/")
    if not target.suffix or path.endswith("/"):target=target/"index.html"
    return target.read_bytes()

def url_for_file(file):
    return "/"+file.removeprefix("site/").removesuffix("index.html")

def image_check(src,mode):
    if not src or not src.startswith("/") or src.startswith("//"):return None
    route=unquote(urlsplit(src).path)
    if mode=="static":
        return (ROOT/route.lstrip("/")).is_file()
    try:
        status,_,ctype,_=request(ORIGIN+route,head=True)
        return status==200 and (ctype.startswith("image/") or ctype.startswith("application/octet-stream"))
    except Exception:
        try:
            status,_,ctype,_=request(ORIGIN+route,head=False)
            return status==200 and ctype.startswith("image/")
        except Exception:return False

def check_page(route,mode):
    item={"route":route,"checks":{},"missing_images":[],"errors":[]}
    try:
        if mode=="static":html=local_get(route).decode("utf-8")
        else:
            status,final,ctype,payload=request(ORIGIN+route)
            item["checks"]["http_200"]=status==200
            item["checks"]["correct_destination"]=final.rstrip("/")== (ORIGIN+route).rstrip("/")
            item["checks"]["html_response"]="html" in ctype.lower()
            html=payload.decode("utf-8","replace")
        p=Parse();p.feed(html)
        item["h1_count"]=p.h1
        item["html_bytes"]=len(html.encode("utf-8"))
        if p.h1 != 1:
            import re
            item["h1_excerpts"]=re.findall(r"<h1\\b[^>]*>[\\s\\S]{0,180}",html,re.I)[:4]
        item["checks"].update({
            "canonical":p.canonical==[ORIGIN+route],
            "title_description":bool(p.title.strip() and any(p.description)),
            "single_h1":p.h1==1,
            "not_noindex":not any("noindex" in value for value in p.robots),
            "jsonld_parses":len(p.jsonld)>0 and all(v is not None for v in p.jsonld),
            "booking_cta":"/booking/japan-cruise/" in p.links,
        })
        images=list(dict.fromkeys(x for x in p.images if x and x.startswith("/") and not x.startswith("//")))
        item["image_count"]=len(p.images)
        if mode=="static":
            item["missing_images"]=[src for src in images if image_check(src,mode) is False]
            item["checks"]["local_images"]=len(item["missing_images"])==0
        else:
            # Remote hero image only; static audit covers every local image.
            item["hero_image"]=images[0] if images else None
            item["checks"]["hero_image_live"]=bool(images) and image_check(images[0],mode) is True
        item["premium_css_marker"]="nf-editorial-premium-v2.css" in html
    except Exception as exc:item["errors"].append(str(exc))
    item["pass"]=not item["errors"] and all(item["checks"].values())
    return item

def check_home(mode):
    item={"checks":{},"errors":[]}
    try:
        if mode=="static":html=local_get("/").decode("utf-8")
        else:
            status,final,ctype,data=request(ORIGIN+"/")
            item["checks"]["http_200"]=status==200
            item["checks"]["html_response"]="html" in ctype.lower()
            html=data.decode("utf-8","replace")
        p=Parse();p.feed(html)
        item["checks"]["new_feature_section"]="nf-refreshed-port-guides-20261019" in html
        item["checks"]["four_feature_links"]=all(link in p.links for link in HOME_LINKS)
        item["checks"]["preserve_premium_home"]="nf-premium-v2.css" in html
        item["checks"]["canonical"]=p.canonical==[ORIGIN+"/"]
        item["checks"]["no_noindex"]=not any("noindex" in s for s in p.robots)
        if mode=="static":
            item["checks"]["features_exist_local"]=all((ROOT/link.lstrip("/")/"index.html").is_file() for link in HOME_LINKS)
    except Exception as exc:item["errors"].append(str(exc))
    item["pass"]=not item["errors"] and all(item["checks"].values())
    return item

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--mode",choices=["static","live"],required=True)
    parser.add_argument("--root",default="site",help="Local files root, use dist to audit Vercel build output")
    args=parser.parse_args();mode=args.mode
    global ROOT
    ROOT=Path(args.root)
    files=json.loads(MANIFEST.read_text())["pages"]
    if len(files)!=85:
        raise SystemExit("PR #9 expected exactly 85 editorial files, found "+str(len(files)))
    home=check_home(mode)
    with ThreadPoolExecutor(max_workers=8 if mode=="live" else 4) as pool:
        futures={pool.submit(check_page,url_for_file(file),mode):file for file in files}
        pages=[future.result() for future in as_completed(futures)]
    pages.sort(key=lambda x:x["route"])
    passing=sum(x["pass"] for x in pages)
    premium=sum(x.get("premium_css_marker",False) for x in pages)
    report={
        "checked_utc":datetime.now(timezone.utc).isoformat(),
        "mode":mode,"source_release_pr":9,
        "pages":len(pages),"page_pass":passing,"page_fail":len(pages)-passing,
        "homepage_pass":home["pass"],"premium_css_count":premium,
        "homepage":home,"failures":[x for x in pages if not x["pass"]],
        "pages_detail":pages,"verified_scope":"Technical HTTP/SEO and local/hero-image availability, not factual or SEO-rank verification",
    }
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/(mode+"-result.json")).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:report[k] for k in ("mode","pages","page_pass","page_fail","homepage_pass","premium_css_count")},ensure_ascii=False))
    if report["failures"]:
        print("SAMPLE FAILURES:",json.dumps(report["failures"][:15],ensure_ascii=False))
    if not home["pass"]:print("HOME FAILURE:",json.dumps(home,ensure_ascii=False))
    if passing!=85 or not home["pass"]:
        raise SystemExit(1)

if __name__=="__main__":main()
