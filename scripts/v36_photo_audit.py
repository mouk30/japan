#!/usr/bin/env python3
from pathlib import Path
import re, json
site=Path(__file__).resolve().parents[1]/"site"
s=(site/"things-to-do/index.html").read_text("utf-8")
links=re.findall(r'<a\s+class="v28-panel"\s+href="([^"]+)"[^>]*>',s)
def images_for_slug(slug):
 f=site/slug.strip("/")/"index.html"
 if not f.exists():return {"exists":False}
 t=f.read_text("utf-8")
 images=re.findall(r'<img\b[^>]*\bsrc="([^"]+)"',t)
 og=re.findall(r'<meta\b[^>]*property="og:image"[^>]*content="([^"]+)"',t)
 return {"exists":True,"imgs":images[:5],"og":og[:2],"n":len(images)}
out={"cards":len(links),"existing_img_filenames":len(list((site/"images").rglob("*.*"))),"link_images":{}}
for link in links:
 out["link_images"][link]=images_for_slug(link)
d=Path(__file__).resolve().parents[1]/"docs"/"v36-photo-audit.json"
d.parent.mkdir(exist_ok=True)
d.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print("V36 AUDIT",out["cards"],out["existing_img_filenames"])
