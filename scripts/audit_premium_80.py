#!/usr/bin/env python3
"""Build premium editorial manifest and conservative content audit from the repository.
Only pages with the premium stylesheet are counted. Never promote unverified facts.
"""
import csv, json, re, argparse
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.images=[]; self.headings=[]; self.scripts=[]; self.current_script=False
        self.canonical=[]; self.description=[]
    def handle_starttag(self,tag,a):
        a=dict(a)
        if tag=="a": self.links.append(a.get("href",""))
        if tag=="img": self.images.append(a.get("src",""))
        if tag=="link" and "canonical" in a.get("rel",""): self.canonical.append(a.get("href",""))
        if tag=="meta" and a.get("name","").lower()=="description": self.description.append(a.get("content",""))
        if tag=="script" and a.get("type")=="application/ld+json": self.current_script=True
        if tag=="h1": self.headings.append("h1")
    def handle_endtag(self,tag):
        if tag=="script" and self.current_script: self.current_script=False
    def handle_data(self,data):
        if self.current_script: self.scripts.append(data)

def local(url,page,root):
    if not url or url.startswith(("data:","//","#")) or urlsplit(url).scheme: return None
    part=unquote(urlsplit(url).path)
    if not part or "{" in part: return None
    if part.startswith("/"): relative=part.lstrip("/")
    else: relative=(page.parent/part).relative_to(root).as_posix()
    p=root/relative
    if p.is_dir(): p=p/"index.html"
    if not p.exists() and not p.suffix: p=p/"index.html"
    return p.exists()

def main():
    ar=argparse.ArgumentParser(); ar.add_argument("--root",default="site"); ar.add_argument("--out",default="audit-output/premium-80"); args=ar.parse_args()
    root=Path(args.root).resolve(); out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for p in sorted((root/"things-to-do").rglob("index.html")):
        try: src=p.read_text(encoding="utf-8")
        except UnicodeError: continue
        if 'nf-editorial-premium-v2.css' not in src: continue
        parser=Page();parser.feed(src)
        url="/"+p.relative_to(root).parent.as_posix()+"/"
        imgs=[local(x,p,root) for x in parser.images]
        links=[local(x,p,root) for x in parser.links if x.startswith("/")]
        external_urls=[x for x in parser.links if x.startswith(("https://","http://"))]
        official_candidates=[x for x in external_urls if any(domain in urlsplit(x).netloc.lower() for domain in
            ("go.jp","lg.jp","okinawastory.jp","churaumi.okinawa","oki-park.jp","discover-nagasaki.com","japan.travel","yokohama-akarenga.jp","osanbashi.jp","nahaport.jp","hakataport.com"))]
        ai_notice=bool(re.search(r"AI 생성 참고 이미지|실제 현장 사진 여부 미검증",src,re.I))
        external_booking_candidates=[x for x in external_urls if any(token in x.lower() for token in
            ("reserve","reservation","booking","ticket","willer-travel.com"))]
        canonical_expected="https://www.nipponferry.com"+url
        rows.append(dict(path=p.relative_to(root).as_posix(),url=url,canonical_ok=len(parser.canonical)==1 and parser.canonical[0]==canonical_expected,
           h1_count=len(parser.headings),meta_description=bool(parser.description and parser.description[0]),
           json_ld_count=len(parser.scripts),internal_link_missing=sum(v is False for v in links),
           image_missing=sum(v is False for v in imgs),external_image_unverified=sum(v is None for v in imgs),
           booking_guide_link='/booking/japan-cruise/' in parser.links,
           official_source_link_candidates=len(official_candidates),ai_reference_disclosure=ai_notice,
           external_booking_link_candidates=len(external_booking_candidates),
           photo_source_verified=False,official_operations_verified=False,live_booking_verified=False))
    with (out/"pages.json").open("w") as f: json.dump(rows,f,ensure_ascii=False,indent=2)
    with (out/"pages.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ["path"]);w.writeheader();w.writerows(rows)
    summary={"page_count":len(rows),"expected":83,"canonical_fail":sum(not x["canonical_ok"] for x in rows),"missing_local_image_pages":sum(x["image_missing"]>0 for x in rows),"missing_internal_link_pages":sum(x["internal_link_missing"]>0 for x in rows),"no_json_ld":sum(x["json_ld_count"]==0 for x in rows),"missing_booking_guide":sum(not x["booking_guide_link"] for x in rows),"official_fact_verification":"pending manual per location","photo_rights_verification":"pending manual per photo","live_booking":"not checked"}
    summary.update({"official_source_candidate_pages":sum(x["official_source_link_candidates"]>0 for x in rows),
                    "ai_disclosure_pages":sum(x["ai_reference_disclosure"] for x in rows),
                    "external_booking_candidate_pages":sum(x["external_booking_link_candidates"]>0 for x in rows),
                    "caveat":"Candidate links and disclosures are not verification of source accuracy, rights, or live bookability."})
    (out/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    pilot_paths = {"things-to-do/naoshima-art-ferry-return/index.html", "things-to-do/teshima-art-ferry-return/index.html"}
    observed_paths = {x["path"] for x in rows}
    if not pilot_paths.issubset(observed_paths):
        raise SystemExit("V146 pilot art-island articles are missing from premium audit")
    if len(rows)!=83: raise SystemExit("Expected 81 existing + 2 V146 premium articles, got "+str(len(rows)))
if __name__=="__main__": main()
