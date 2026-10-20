#!/usr/bin/env python3
"""Inventory image claims, source evidence, and replacement readiness for 85 guides.
This is a metadata audit, NOT visual verification of real-world photo identity.
"""
import csv, json, re
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self):
  super().__init__();self.img=[];self.caption=[];self.cap=False;self.buf=[]
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=="img":self.img.append(d)
  if t=="figcaption":self.cap=True;self.buf=[]
 def handle_data(self,d):
  if self.cap:self.buf.append(d)
 def handle_endtag(self,t):
  if t=="figcaption" and self.cap:self.caption.append("".join(self.buf).strip());self.cap=False
def main():
 paths=json.loads((ROOT/"scripts/postdeploy-editorial-manifest.json").read_text())["pages"]
 assert len(paths)==85
 out=[]
 for path in paths:
  file=ROOT/path;html=file.read_text(encoding="utf-8");p=Page();p.feed(html)
  img=p.img[0] if p.img else {};src=img.get("src","");alt=img.get("alt","")
  captions=" | ".join(p.caption)
  evidence=bool(re.search(r"https?://(?:commons.wikimedia.org|.*?\.go\.jp|.*?\.jp)",captions,re.I))
  declared_ai="AI 생성" in (alt+captions)
  actual_photo_claim=bool(re.search(r"실제\s*(?:현장\s*)?(?:촬영|사진)|실사\s*사진",alt+captions)) and not declared_ai
  asset=(ROOT/"site"/src.lstrip("/")) if src.startswith("/") else None
  image_exists=bool(asset and asset.is_file())
  if declared_ai: classification="AI_REFERENCE_NOT_REAL_SITE_PHOTO"
  elif src.lower().endswith(".svg"): classification="EDITORIAL_GRAPHIC"
  elif actual_photo_claim: classification="PHOTO_CLAIM_UNVERIFIED"
  else:classification="IMAGE_TYPE_UNVERIFIED"
  out.append(dict(page=path,hero_src=src,alt=alt,caption=captions,image_exists=image_exists,declared_ai=declared_ai,source_in_caption=evidence,classification=classification,site_match_verified=False,license_verified=False,action="RETAIN_DISCLOSURE_RESEARCH_SOURCE_BEFORE_REPLACEMENT" if declared_ai else "MANUAL_REVIEW_REQUIRED"))
 folder=ROOT/"audit-reports"/"editorial-85";folder.mkdir(parents=True,exist_ok=True)
 with (folder/"image-provenance-inventory.csv").open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=out[0].keys());w.writeheader();w.writerows(out)
 summary=dict(total=len(out),images_present=sum(x["image_exists"] for x in out),ai_reference=sum(x["declared_ai"] for x in out),missing_images=[x["page"] for x in out if not x["image_exists"]],source_link_in_caption=sum(x["source_in_caption"] for x in out),verified_site_matches=0,verified_licenses=0,disclaimer="File existence and editorial labeling only. Source/rights/location verification requires original evidence and visual comparison.")
 (folder/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps(summary,ensure_ascii=False))
if __name__=="__main__":main()
