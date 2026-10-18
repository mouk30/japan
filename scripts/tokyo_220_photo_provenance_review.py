import pathlib,json,re,collections,html,urllib.parse
base=pathlib.Path("site")
hub=(base/"japan/tokyo/index.html").read_text()
slugs=re.findall(r'<a\s+class="tky-card"[^>]*href="/japan/tokyo/([^/]+)/"',hub)
js=(base/"tokyo-card-photos.js").read_text();mapping=json.loads(js.split("const map=",1)[1].split(";document.querySelectorAll",1)[0])
records=[]
for v,slug in enumerate(slugs,1):
 page=(base/"japan/tokyo"/slug/"index.html").read_text()
 title=html.unescape(re.search(r'<h1[^>]*>(.*?)</h1>',page,re.S).group(1)) if re.search(r'<h1[^>]*>(.*?)</h1>',page,re.S) else slug
 meta=mapping.get(slug,{})
 src=meta.get("src","")
 source=meta.get("source_file","")
 kind="editorial_graphic" if src.endswith(".svg") else "photograph"
 base_name=source.removeprefix("File:").lower()
 tokens=[x for x in re.findall(r'[a-z]{4,}',slug.lower()) if x not in ("tokyo","guide","with","from","floor","station","line","tickets","ticket")]
 matched=[t for t in tokens if t in base_name]
 flags=[]
 if not src or not (base/src.lstrip("/")).exists():flags.append("asset_missing")
 if not meta.get("alt"):flags.append("alt_missing")
 if kind=="photograph" and not meta.get("source"):flags.append("origin_not_stated")
 if kind=="photograph" and not meta.get("license"):flags.append("license_not_stated")
 if kind=="photograph" and not matched:flags.append("manual_visual_comparison_priority")
 if kind=="editorial_graphic" and "사진 아님" not in (meta.get("caption","")+meta.get("alt","")):flags.append("graphic_unlabeled")
 if any(x in base_name for x in ("kobe","kyoto","nara","shanghai","gdansk","lithuania","romanian","cfr ticket","2010")):flags.append("location_or_historical_filename_warning")
 records.append({"v":v,"slug":slug,"title":title,"type":kind,"image":src,"source_file":source,"source_url":meta.get("source"),"license":meta.get("license"),"matched_slug_tokens":matched,"flags":flags,"human_visual_confirmation":"not_performed"})
report={"total":len(records),"photos":sum(x["type"]=="photograph" for x in records),"editorial_graphics":sum(x["type"]=="editorial_graphic" for x in records),"flag_counts":dict(collections.Counter(flag for r in records for flag in r["flags"])),"priority_visual_review":[r for r in records if "manual_visual_comparison_priority" in r["flags"] or "location_or_historical_filename_warning" in r["flags"]],"rows":records,"limitation":"This is a complete source provenance inventory, not human vision verification of each photograph. Filename token matches are weak evidence and must not be presented as photo-ground truth."}
pathlib.Path("audit-reports/tokyo-220-photo-provenance-review.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({"total":report["total"],"photos":report["photos"],"graphics":report["editorial_graphics"],"flags":report["flag_counts"]}))
