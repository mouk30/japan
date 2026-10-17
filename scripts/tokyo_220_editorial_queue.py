#!/usr/bin/env python3
"""Publish an honest 220-article editorial queue, never mark auto-checks as certification."""
import json,pathlib,datetime,csv
root=pathlib.Path("audit-reports")
inventory=json.loads((root/"tokyo-220-photo-source-audit.json").read_text(encoding="utf8"))
candidates=json.loads((root/"tokyo-220-photo-candidates.json").read_text(encoding="utf8"))
live=json.loads((root/"tokyo-220-live-verification.json").read_text(encoding="utf8"))
by_slug={x["slug"]:x for x in candidates["items"]}
live_by={x["slug"]:x for x in live["items"]}
rows=[]
for p in inventory["items"]:
 slug=p["slug"];c=by_slug.get(slug,{});v=live_by.get(slug,{})
 image_file=bool(p["photo_file_valid"])
 http=v.get("live_photo_http") or {}
 refs=v.get("external_sources_http") or {}
 rows.append({
 "slug":slug,"title":p["title"],"article_url":"https://www.nipponferry.com"+p["page"],
 "verified_local_webp":"yes" if image_file else "no",
 "published_webp_http_ok":"yes" if http.get("reachability")=="ok" and http.get("valid_webp_header") else "unconfirmed",
 "commons_candidate_count":len(c.get("candidates",[])),
 "commons_search_error":c.get("search_error",""),
 "official_or_reference_urls":len(refs),
 "official_urls_http_ok":sum(x.get("reachability")=="ok" for x in refs.values()),
 "image_subject_human_verified":"not verified",
 "license_individually_verified":"review required",
 "official_terms_individually_verified":"not verified",
 "browser_visual_check":"not verified",
 "next_action":"Review candidate subject and Commons credits" if c.get("candidates") and not image_file else ("Find exact venue photo and license" if not image_file else "Check operational facts and browser display")
 })
assert len(rows)==220 and len({r["slug"] for r in rows})==220
with (root/"tokyo-220-editorial-queue.csv").open("w",newline="",encoding="utf-8-sig") as f:
 writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
out={"generated_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
"total":220,"files_with_local_verified_webp":sum(r["verified_local_webp"]=="yes" for r in rows),
"image_candidates_not_approved":sum(r["commons_candidate_count"]>0 for r in rows),
"operational_terms_fully_verified":0,"browser_visually_verified":0,
"critical":"This is a task queue, NOT a certification. HTTP 200 and Commons search are insufficient to claim photo identity or booking validity."}
(root/"tokyo-220-editorial-summary.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(out,ensure_ascii=False))
