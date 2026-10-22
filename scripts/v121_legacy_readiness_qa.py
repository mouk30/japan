#!/usr/bin/env python3
"""V121 precise scope closure after V117/V118/V120. Only classify validated states."""
from pathlib import Path
from urllib.parse import urlsplit
import json, re, xml.etree.ElementTree as ET
from v117_sitewide_audit import scan,ROOT,SITE
OUT=ROOT/"audit-reports/v121";OUT.mkdir(parents=True,exist_ok=True)
# Recalculate from the actual current checkout, after the exact 56 V122 canonical repairs.
data=scan()
raw=json.loads((ROOT/"audit-reports/v117/detail-inventory.json").read_text("utf8"))
targets=[]
for row in raw["canonical_mismatches"]:
 path=urlsplit(row["canonical"]).path
 dst=SITE/path.lstrip("/")/"index.html"
 origin=SITE/row["page"].lstrip("/")/"index.html"
 src=origin.read_text("utf8") if origin.exists() else ""
 if not dst.exists():
  kind="broken_canonical_target"
 elif re.search(r'<meta\s+http-equiv=["\']refresh',src,re.I):
  kind="intentional_redirect"
 elif path.startswith(("/japan/","/guide/")):
  kind="canonical_consolidation_to_existing_primary"
 else:
  kind="needs_manual_canonical_review"
 targets.append({**row,"type":kind,"destination_exists":dst.exists()})
seo=[]
for kind,urls in raw.get("missing_seo_pages",{}).items():
 for url in urls:
  file=SITE/url.lstrip("/")/"index.html"
  source=file.read_text("utf8") if file.exists() else ""
  noindex=bool(re.search(r'<meta name=["\']robots["\'] content=["\'][^"\']*noindex',source,re.I))
  refresh=bool(re.search(r'<meta http-equiv=["\']refresh',source,re.I))
  seo.append({"page":url,"missing":kind,"excluded_reason":"noindex" if noindex else "legacy_redirect" if refresh else "indexable_page_requires_review"})
sitemap_xml=ET.parse(SITE/"sitemap.xml").getroot()
ns={"sm":"http://www.sitemaps.org/schemas/sitemap/0.9"}
urls=[loc.text for loc in sitemap_xml.findall(".//sm:loc",ns) if loc.text]
aliases={x["page"] for x in targets if x["type"] in ("canonical_consolidation_to_existing_primary","intentional_redirect")}
aliases_in_sitemap=[url for url in urls if urlsplit(url).path in aliases]
report={
 "version":"V121","scope":"Exact current main-branch static-file revision of NIPPONFERRY",
 "checked_html_pages":data["scope"]["pages_scanned"],
 "missing_local_images":data["photo"]["missing_local_images"],
 "missing_image_alts":data["photo"]["missing_alt_tags"],
 "explicit_ai_cover_remaining":data["photo"]["confirmed_ai_cover_candidates"],
 "broken_local_link_targets":data["links"]["missing_internal_targets"],
 "canonical_classification":{
  k:sum(x["type"]==k for x in targets)
  for k in sorted({x["type"] for x in targets})
 },
 "missing_seo_classification":{
  k:sum(x["excluded_reason"]==k for x in seo)
  for k in sorted({x["excluded_reason"] for x in seo})
 },
 "sitemap_urls":len(urls),"sitemap_canonical_alias_urls":aliases_in_sitemap,
 "photo_note":"An explicit AI-label inventory is not a machine proof of every photo's real location or license. 20 Tokyo photo-review cases in separate noindex review page remain manually pending.",
 "external_note":"V119 checked a prioritized 260/1275 external links; it is not a verified current fare or booking availability inventory.",
 "open_items":[
  "Replace the remaining actual AI hero candidates one by one with visually exact photos, source, date and legally permitted reuse",
  "Manually inspect twenty Tokyo source-photo review cases where photo/subject/license identity is not yet signed off",
  "Recheck remaining external URL set and five currently blocked/503 official reservation-or-information paths without inventing booking",
  "Validate current operator schedules/fares, tourist venue opening hours and reservation cancellation conditions before labeling information real-time"
 ],
 "canonical_details":targets,
 "missing_seo_details":seo
}
(OUT/"remaining-work-and-source-evidence.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
print(json.dumps({k:v for k,v in report.items() if k not in ("open_items","canonical_details","missing_seo_details","sitemap_canonical_alias_urls")},ensure_ascii=False,indent=2))
assert report["missing_local_images"]==0 and report["missing_image_alts"]==0 and report["broken_local_link_targets"]==0, "Known local integrity checks must be resolved"
assert report["canonical_classification"].get("broken_canonical_target",0)==0, "Broken canonical destination needs repair"
assert report["missing_seo_classification"].get("indexable_page_requires_review",0)==0, "Missing critical SEO fields on indexable pages"
