#!/usr/bin/env python3
"""Preview four independently-licensed Wikimedia Commons Kouri Bridge scenes before final homepage image selection."""
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen,Request
from PIL import Image,ImageOps,ImageDraw
import json,io
D=Path("audit-output/v140-okinawa-candidates");D.mkdir(parents=True,exist_ok=True)
names=["Kouri Bridge 202006.jpg","Kouri Bridge (15130568259).jpg","Kouri Bridge and the beach 20191109a.jpg","Kouri Bridge 20150212.jpg"]
out=Image.new("RGB",(1140,810),"#f0f4f8")
draw=ImageDraw.Draw(out)
details=[]
for i,name in enumerate(names):
 u="https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(name,safe="")+"?width=1400"
 with urlopen(Request(u,headers={"User-Agent":"NipponFerryCommonsQA/1.0 (https://www.nipponferry.com/)"}),timeout=75) as res:
  raw=res.read(16_000_001)
 im=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
 if im.width<900 or im.height<600:raise RuntimeError("Image too small "+name)
 r=im.width/im.height;target=1.6
 if r<target:
  crop_h=int(im.width/target)
  y=(im.height-crop_h)//2
  im=im.crop((0,y,im.width,y+crop_h))
 else:
  crop_w=int(im.height*target)
  x=(im.width-crop_w)//2
  im=im.crop((x,0,x+crop_w,im.height))
 im=im.resize((550,344),Image.Resampling.LANCZOS)
 x=(i%2)*570+10;y=(i//2)*405+40
 out.paste(im,(x,y));draw.text((x,y-23),str(i+1)+" · "+name,fill="#1c3851")
 im.save(D/f"candidate-{i+1}.png")
 details.append({"n":i+1,"file":name,"source":"https://commons.wikimedia.org/wiki/File:"+quote(name.replace(" ","_"),safe=":(),"),"original_size":len(raw)})
out.save(D/"comparison.png")
(D/"candidates.json").write_text(json.dumps(details,indent=2)+"\n")
print(json.dumps(details))
