#!/usr/bin/env python3
"""V133 photo provenance audit: review previously flagged 289 pages for visible attribution.

A caption mentioning Commons or a license is DOCUMENTATION only, not independent
verification of source image rights. Three originals were independently crosschecked
against their Wikimedia Commons file descriptions on 2026-10-23.
"""
from pathlib import Path
from collections import Counter
import json,re,html
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"
V132=ROOT/"audit-reports/v132/sitewide-inventory-before-photo-repair.json"
OUT=ROOT/"audit-reports/v133"
VERIFIED=[
 {"page":"/things-to-do/okinawa-shuri-castle/","source":"https://commons.wikimedia.org/wiki/File:Shuri_Castle_Reconstruction.jpg","author":"おにく","taken":"2025-02-11","license":"CC0 1.0","scene":"Shuri Castle main hall reconstruction, NOT a completed 2026 hall","verification":"source file's original date, author, subject, and CC0 licensing"},
 {"page":"/things-to-do/nanao-cruise-port-day-trip/","source":"https://commons.wikimedia.org/wiki/File:Nanao_port.JPG","author":"nanaoshimin","taken":"2007-12-25","license":"Public domain (author release)","scene":"2007 port view, NOT post-2024-earthquake or live current berth","verification":"source file's original date, author, subject, and public-domain dedication"},
 {"page":"/things-to-do/nagasaki-cruise-port-day-trip/","source":"https://commons.wikimedia.org/wiki/File:Nagasaki-Glover-Garden-5384.jpg","author":"Fg2","taken":"2007","license":"Public domain (author release)","scene":"Historic Ringer House in Nagasaki Glover Garden, NOT cruise terminal","verification":"source file's original date, author, subject, and public-domain dedication"}
]
def load_page(page):
 f=SITE/page.lstrip("/")/"index.html"
 return f.read_text("utf8")
def base_url_simplify(url):
 return html.unescape(url).replace("%20","_").replace("https://commons.wikimedia.org/wiki/File:","").replace("_"," ").lower()
def check_verified(item):
 page=load_page(item["page"])
 # Source string and local attribution may use encoded spaces, preserve exact names.
 file=item["source"].split("File:")[1].lower()
 refs=[html.unescape(u) for u in re.findall(r'href=["\x27](https?://[^"\x27]+)',page)]
 linked=any(item["source"]==u or base_url_simplify(item["source"])==base_url_simplify(u) for u in refs)
 creator=item["author"] in page
 license_tag=(("CC0" in page or "creativecommons.org/publicdomain/zero" in page) if "CC0" in item["license"] else "Public domain" in page)
 scene_dates=("2025" in page if item["taken"]=="2025-02-11" else ("2007" in page if item["taken"].startswith("2007") else True))
 return {"page":item["page"],"source":item["source"],"author":item["author"],"date":item["taken"],"license":item["license"],"scene":item["scene"],"source_link_visible":linked,"creator_visible":creator,"licence_displayed":license_tag,"historical_date_displayed":scene_dates,"passed":linked and creator and license_tag and scene_dates}

def run():
 baseline=json.loads(V132.read_text("utf8"))
 listed=baseline["findings"]["photo_source_visibility"]
 results=[]
 for c in listed:
  page=c["page"];s=load_page(page)
  start=s.find('class="cover"')
  if start<0:
   results.append({"page":page,"reason":"cover not found","confidence":"review_required"});continue
  end=s.find(">",start)
  near=s[end+1:end+2200]
  full=s[:]
  commons="commons.wikimedia.org" in near
  author=bool(re.search(r"촬영자|저작자|사진[:：]|Photo[:：]|Author",near,re.I))
  license_tag=bool(re.search(r"CC BY|CC0|Public domain|creativecommons.org",near,re.I))
  origin_only="commons.wikimedia.org" in full
  classify="visible_source_creator_license" if commons and author and license_tag else "some_photo_attribution" if commons or author or license_tag else "no_nearby_origin"
  results.append({"page":page,"cover":c["cover"],"kind":classify,"commons_near_cover":commons,"author_near_cover":author,"license_near_cover":license_tag,"somewhere_commons_link":origin_only,"note":"local caption evidence only; neither photographer rights nor correct city guaranteed"})
 verified=[check_verified(x) for x in VERIFIED]
 if any(not x["passed"] for x in verified):
  raise RuntimeError("V133 manually-checked original source no longer attributed correctly: "+str([x for x in verified if not x["passed"]]))
 counts=dict(Counter(x.get("kind","unclassified") for x in results))
 summary={"version":"V133","checked_previous_photo_credit_candidates":len(results),"classifications":counts,"independently_original_source_compared":len(verified),"verified_originals":verified,"limitations":["HTML attribution is not proof of actual visual match or legal permission","Many older page templates credit photos elsewhere; not automatically an error","Missing attribution candidate requires inspecting original image and author license before editing","Photo depiction of facilities and operating state can change after image was taken"],"pages":results}
 OUT.mkdir(exist_ok=True,parents=True)
 (OUT/"photo-provenance-review.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n","utf8")
 print(json.dumps({"previous_candidates":len(results),"classification":counts,"source_originals_verified":len(verified),"passed":True},ensure_ascii=False))
 return summary
if __name__=="__main__":run()
