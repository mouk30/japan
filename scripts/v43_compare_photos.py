#!/usr/bin/env python3
import json,io,base64,urllib.request,time,concurrent.futures
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
choices={
  "ryokan-japanese-inn-hospitality": [
    "My traditional accomodation at Toshiharu Ryokan (48885681992).jpg",
    "Evening twilight Ginzan Onsen town seen from the guest room of Kosekiya Bekkan.jpg",
    "Our room at Seikansō Ryokan (6156061472).jpg"
  ],
  "kotatsu-japanese-winter-table": [
    "Kotatsu-tastefulTN.jpg",
    "こたつ (3251928073).jpg",
    "Kotatsu (5104045).jpg",
    "Kotatsu (52871643948).jpg"
  ],
  "wagashi-japanese-seasonal-sweets": [
    "Wagashi closeup 14.jpg",
    "Wagashi closeup 15.jpg",
    "Summer wagashi 10.jpg",
    "Wagashi 001.jpg"
  ],
  "izakaya-japanese-afterwork-culture": [
    "Gion Kappa Restaurant in Kyoto.jpg",
    "Quality izakaya in Ebisu 3.jpg",
    "かねふく やまや あごおとし (10857010905).jpg",
    "Dinner at Yopparai with Sidra (36793821404).jpg"
  ],
  "ramen-japanese-noodle-evolution": [
    "Tonkotsu ramen in Tokyo.jpg",
    "Clear tonkotsu ramen.jpg",
    "Ramen Bowl.jpg",
    "Ramen Bowl 2.jpg"
  ]
}
first=json.loads(Path("docs/v43-commons-candidates.json").read_text("utf-8"))
second=json.loads(Path("docs/v43-commons-supplement.json").read_text("utf-8"))
listings=[]
for slug,names in choices.items():
 for filename in names:
  pool=[*first.get(slug,{}).get("options",[]),*second.get(slug,{}).get("options",[])]
  o=next((v for v in pool if v["filename"]==filename),None)
  if not o:raise RuntimeError(slug+" missing "+filename)
  if not o["licence"].startswith(("CC BY","CC0","Public domain")):raise RuntimeError("bad license "+filename)
  listings.append((slug,o))
def download(item):
 slug,obj=item
 for a in range(3):
  try:
   req=urllib.request.Request(obj["remote"],headers={"User-Agent":"Nipponferry-V43-visual-comparison/1.0 (https://www.nipponferry.com/)"})
   with urllib.request.urlopen(req,timeout=60) as stream:raw=stream.read()
   with Image.open(io.BytesIO(raw)) as im:
    image=ImageOps.contain(im.convert("RGB"),(290,180),Image.Resampling.LANCZOS)
    image.load()
   return image
  except Exception as e:
   if a==2:
    print("unavailable",obj["filename"],str(e)[:100],flush=True)
    return None
   time.sleep(3)
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool: photos=list(pool.map(download,listings))
out=Image.new("RGB",(4*310,5*237),(247,249,252))
d=ImageDraw.Draw(out)
try:font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",13)
except:font=ImageFont.load_default()
for n,((slug,obj),im) in enumerate(zip(listings,photos)):
 x=n%4*310;y=n//4*237
 if im:out.paste(im,(x+(310-im.width)//2,y+(180-im.height)//2+3))
 else:d.text((x+12,y+30),"PHOTO UNAVAILABLE",fill=(160,30,30),font=font)
 d.text((x+9,y+185),f"{n+1}. {slug[:35]}",font=font,fill=(27,46,62))
 d.text((x+9,y+206),obj["filename"][:43],font=font,fill=(62,84,104))
b=io.BytesIO();out.save(b,format="JPEG",quality=81,optimize=True)
Path("docs/v43-alternative-contact.b64").write_text(base64.b64encode(b.getvalue()).decode(),encoding="ascii")
print("Candidate comparison 19 images",len(b.getvalue()),flush=True)
