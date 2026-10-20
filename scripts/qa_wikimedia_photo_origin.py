#!/usr/bin/env python3
"""Reproduce original Wikimedia reference photos and compare the uploaded WebP visually.

This verifies likely same PHOTOGRAPH after common resize/crop/compression.
It cannot establish every copyright, trademark or editing condition by itself.
The expected source, author and rights text are checked against the HTML.
"""
import hashlib, io, json, sys, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageOps

BASE=Path(sys.argv[1] if len(sys.argv)>1 else "dist")
CASES=[
  {"slug":"ishigaki-cruise-kabira-bay-bus-taxi",
   "local":"images/venues/ishigaki-kabira-bay.webp",
   "original":"Kabira_Bay_Ishigaki_Island23n4500.jpg",
   "credit":["663highland","CC BY-SA 3.0","라이선스","WebP"],
   "source":"https://commons.wikimedia.org/wiki/File:Kabira%20Bay%20Ishigaki%20Island23n4500.jpg"},
  {"slug":"nagasaki-matsugae-glover-garden-cruise-access",
   "local":"images/venues/nagasaki-glover-garden.webp",
   "original":"Nagasaki-Glover-Garden-5384.jpg",
   "credit":["Fg2","퍼블릭 도메인","구 링거 주택","WebP"],
   "source":"https://commons.wikimedia.org/wiki/File:Nagasaki-Glover-Garden-5384.jpg"},
]
def source_url(filename):
    hashed=hashlib.md5(filename.encode("utf-8")).hexdigest()
    return "https://upload.wikimedia.org/wikipedia/commons/"+hashed[:1]+"/"+hashed[:2]+"/"+urllib.parse.quote(filename)

def download(file):
    req=urllib.request.Request(source_url(file),headers={
        "User-Agent":"NIPPONFERRY/1.0 (editorial image origin verification; https://www.nipponferry.com/)"})
    with urllib.request.urlopen(req,timeout=30) as reply:
        if reply.status!=200:raise ValueError("original image HTTP "+str(reply.status))
        data=reply.read(12_000_000)
        if len(data)<1000 or len(data)>=12_000_000:raise ValueError("original image response size invalid")
    img=ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
    return img

def dhash(im):
    im=im.convert("L").resize((9,8),Image.Resampling.LANCZOS)
    pix=list(im.getdata())
    return sum((1 << (row*8+col)) for row in range(8) for col in range(8)
               if pix[row*9+col]>pix[row*9+col+1])

def ahash(im):
    im=im.convert("L").resize((8,8),Image.Resampling.LANCZOS)
    pix=list(im.getdata());mean=sum(pix)/64
    return sum((1 << i) for i,val in enumerate(pix) if val>mean)

def crops(img,ratio):
    width,height=img.size
    yield "original",img
    curr=width/height
    if abs(curr-ratio)<.015:return
    if curr < ratio:
        new_h=min(height,max(1,int(width/ratio)))
        for pos in (0,.25,.5,.75,1):
            top=int((height-new_h)*pos)
            yield f"y-crop-{pos}",img.crop((0,top,width,top+new_h))
    else:
        new_w=min(width,max(1,int(height*ratio)))
        for pos in (0,.25,.5,.75,1):
            left=int((width-new_w)*pos)
            yield f"x-crop-{pos}",img.crop((left,0,left+new_w,height))

def check(item):
    page=BASE/"things-to-do"/item["slug"]/"index.html"
    if not page.is_file():raise FileNotFoundError(page)
    text=page.read_text(encoding="utf-8")
    for marker in item["credit"]+[item["source"]]:
        if marker not in text:raise ValueError("Missing provenance on public page: "+marker)
    local=BASE/item["local"]
    if not local.is_file():raise FileNotFoundError(local)
    webp=ImageOps.exif_transpose(Image.open(local)).convert("RGB")
    original=download(item["original"])
    d0,a0=dhash(webp),ahash(webp)
    dists=[]
    for kind,candidate in crops(original,webp.width/webp.height):
        d=(dhash(candidate)^d0).bit_count()
        a=(ahash(candidate)^a0).bit_count()
        dists.append((d,a,kind))
    best=min(dists,key=lambda v:v[0]+v[1]*.25)
    print(json.dumps({"page":item["slug"],"photo":item["original"],
                      "local_size":list(webp.size),"source_size":list(original.size),
                      "best_crop":best[2],"dhash_distance":best[0],
                      "ahash_distance":best[1]},ensure_ascii=False))
    # For 64bit dHash a distance <=18 remains tolerant to resizing / moderate crops.
    # A larger difference needs human verification before labelling the page as a match.
    if best[0]>18:
        raise ValueError(f"Derivative image does not resemble credited original sufficiently (dhash={best[0]})")
    return best

errors=[]
for item in CASES:
    try:check(item)
    except Exception as e:
        print("FAIL",item["slug"],repr(e));errors.append(item["slug"]+": "+str(e))
if errors:
    print("PHOTO VALIDATION FAILED",*errors,sep="\n")
    sys.exit(1)
print("PASS: 2 source-linked, perceptually consistent Wikimedia photos")
