#!/usr/bin/env python3
"""V134 provenance backlog triage; no automatic claim of copyright or visual truth.

Identify 262 still-unreviewed legacy image placements by page,
show common repeated generic assets and whether the author's license
is displayed near its hero / elsewhere in article.
"""
from pathlib import Path
from collections import Counter,defaultdict
import json,re
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"audit-reports/v132/sitewide-inventory-before-photo-repair.json"
PLAN=ROOT/"audit-reports/v134/photo-plan.json"
OUT=ROOT/"audit-reports/v134"
def scan():
 src=json.loads(BASE.read_text("utf8"))
 originals=src["findings"]["photo_source_visibility"]
 first22={x["page"] for x in originals if x["page"].startswith("/things-to-do/")}
 done={"/guide/"+x["slug"]+"/" for x in json.loads(PLAN.read_text("utf8"))["entries"]}
 if len(originals)!=289 or len(first22)!=22 or len(done)!=5:raise ValueError("Original backlogged data changed; no blind selection")
 remaining=[x for x in originals if x["page"] not in first22 and x["page"] not in done]
 if len(remaining)!=262:raise ValueError("Unexpected remaining photo-candidate count")
 covers=Counter(x["cover"] for x in remaining)
 pages=[]
 for x in remaining:
  p=x["page"];html=(ROOT/"site"/p.lstrip("/")/"index.html").read_text("utf8")
  match=re.search(r'<img\b[^>]*class=["\x27][^"\x27]*(?:cover|article-cover)[^"\x27]*["\x27][^>]*>',html)
  if not match:status="missing_expected_image_tag";near=""
  else:
   near=html[match.end():match.end()+2100]
   has_source="commons.wikimedia.org" in near
   has_author=bool(re.search(r"촬영자|저작자|사진:|사진：|author|photographer",near,re.I))
   has_license=bool(re.search(r"CC0|CC BY|Public domain|creativecommons.org",near,re.I))
   if has_source and has_author and has_license:status="attribution_near_photo_present_source_license_not_independently_verified"
   elif "commons.wikimedia.org" in html:status="possible_photo_origin_elsewhere_need_check"
   else:status="original_provenance_not_identified_from_page"
  pg={
   "page":p,"old_cover":x["cover"],"cover_used_in_remaining_pages":covers[x["cover"]],
   "category":p.split("/")[1],"status":status,"review_priority":("P1-ferry-primary" if p.startswith("/guide/") else "P2-location-exact" if p.startswith("/japan/") or p.startswith("/season/") else "P3-generic-context"),
   "note":"not proof of image/place mismatch or infringement; locate originals, attribution, photographer, license, date, visual match before replacing"
  }
  pages.append(pg)
 count=dict(Counter(x["status"] for x in pages))
 cats=dict(Counter(x["category"] for x in pages))
 repeated=[{"cover":k,"remaining_pages":n,"samples":[x["page"] for x in pages if x["old_cover"]==k][:8]} for k,n in covers.most_common()]
 report={"version":"V134","source_candidates_total":289,"already_reviewed_visible_attribution_in_v133":22,"newly_verified_and_replaced_route_guides":5,"remaining_review_queue":262,"status_counts":count,"categories":cats,"repeated_generic_cover_clusters":repeated,"pages":pages,
 "safety_limits":["repeated image is not necessarily wrong; it may be illustration or thematic image, but must not be represented as a specific cruise terminal","source or license absent from near image does not conclusively establish infringement; check template and archived asset provenance","do not create fake Commons attributions or imply 2026 operations from old facility photos"]}
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/"remaining-262-provenance-queue.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
 print(json.dumps({"remaining":262,"status_counts":count,"categories":cats,"top_photo_clusters":repeated[:8]},ensure_ascii=False))
 return report
if __name__=="__main__":scan()
