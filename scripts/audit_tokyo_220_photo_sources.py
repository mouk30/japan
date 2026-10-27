#!/usr/bin/env python3
"""Audit every Tokyo page for exact image availability and source links; fail closed."""
import json,re,html,pathlib,urllib.request,urllib.error,concurrent.futures
root=pathlib.Path("site")
# noindex photo-review workbench is not a public travel article
excluded_workbench={"photo-review"}
pages=sorted(p for p in (root/"japan/tokyo").glob("*/index.html") if p.parent.name not in excluded_workbench)
expected_pages=220
count_mismatch=len(pages)!=expected_pages
if count_mismatch:
 print(f"WARNING: Expected {expected_pages} Tokyo articles, got {len(pages)}")
credits=json.loads((root/"tokyo-photo-credits.json").read_text(encoding="utf-8"))
photos={x["slug"]:x for x in credits}
report=[]
for p in pages:
 s=p.read_text(encoding="utf-8");slug=p.parent.name
 name=re.search(r"<h1[^>]*>(.*?)</h1>",s,re.S)
 title=html.unescape(re.sub(r"<[^>]+>","",name.group(1))) if name else slug
 urls=re.findall(r'<a[^>]+href="(https://[^"]+)"',s)
 official=[u for u in urls if not ("nipponferry.com" in u or "commons.wikimedia.org" in u)]
 photo=photos.get(slug)
 present=bool(photo and (root/photo["src"].lstrip("/")).is_file())
 if present:
  b=(root/photo["src"].lstrip("/")).read_bytes()[:12]
  present=b[:4]==b"RIFF" and b[8:12]==b"WEBP"
 report.append({"slug":slug,"title":title,"page":"/japan/tokyo/"+slug+"/",
 "related_official_or_reference_urls":official[:5],
 "source_reachable":"not checked","photo_file_valid":present,
 "photo_path":photo["src"] if present else None,
 "photo_license":photo["license"] if present else None,
 "photo_source":photo["source"] if present else None,
 "photo_in_live_browser":"not checked",
 "status":"photo_file_checked_only" if present else "missing_unique_verified_photo"})
counts={"pages":len(report),"expected_pages":expected_pages,"page_count_mismatch":count_mismatch,"excluded_non_article_pages":sorted(excluded_workbench),"valid_local_webp":sum(x["photo_file_valid"] for x in report),
"need_verified_photos":sum(not x["photo_file_valid"] for x in report),
"with_external_reference":sum(bool(x["related_official_or_reference_urls"]) for x in report),
"official_conditions_individually_verified":0,
"live_browser_render_checked":0}
out=pathlib.Path("audit-reports/tokyo-220-photo-source-audit.json")
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps({"summary":counts,"note":"Do not equate existing external hyperlinks with officially verified operational conditions. Photo names and licences must be checked against original." ,"items":report},ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(counts,ensure_ascii=False))

priority=sorted((x for x in report if not x["photo_file_valid"]),key=lambda x:(0 if any(k in x["slug"] for k in ("disney","asakusa","shibuya","shinjuku","tokyo-station")) else 1,x["slug"]))
queue=pathlib.Path("audit-reports/tokyo-photo-review-priority.json")
queue.write_text(json.dumps({"note":"Local file validation only; photo identity and rights require manual verification","page_count_mismatch":count_mismatch,"items":[{"page":x["page"],"title":x["title"],"reason":x["status"]} for x in priority]},ensure_ascii=False,indent=2),encoding="utf-8")
if count_mismatch:
 print("WARNING: Page count mismatch remains unresolved; editorial QA is NOT complete.")
