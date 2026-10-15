from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import base64,io,json,urllib.request,time,math
report=json.loads(Path("docs/v42-commons-candidates.json").read_text("utf-8"))
topics=[
 ("japanese-ekiben-railway-bento-culture",["Bento Meals (2908879539).jpg","Asagiri-Morning-Set-Japan-style.jpg","Train station box lunches in Japan called eki ben.jpg","お弁当 お飲物 (20745331392).jpg"]),
 ("japanese-kintsugi-gold-repair-culture",["Hand Pinted Kintsugi Pottery Bowl.jpg","Tea bowl, Korea, Joseon dynasty, 16th century AD, Mishima-hakeme type, buncheong ware, stoneware with white engobe and translucent, greenish-gray glaze, gold lacquer - Ethnological Museum, Berlin - DSC02061.JPG","Kintsugi art.jpg","Kintsugi Failed.jpg"])
]
sources=[]
for topic,files in topics:
   for name in files:
      obj=next((x for x in report[topic]["options"] if x["filename"]==name),None)
      if obj is not None:sources.append((topic,obj))
out=Image.new("RGB",(4*320,2*270),(248,250,252))
d=ImageDraw.Draw(out)
try:font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",14)
except:font=ImageFont.load_default()
for j,(topic,obj) in enumerate(sources):
 x=(j%4)*320; y=(j//4)*270
 for attempt in range(3):
   try:
     req=urllib.request.Request(obj["remote"],headers={"User-Agent":"Nipponferry-V42-editorial-QA/1.0 (https://www.nipponferry.com/)"})
     with urllib.request.urlopen(req,timeout=50) as resp: raw=resp.read()
     im=Image.open(io.BytesIO(raw)).convert("RGB")
     im=ImageOps.contain(im,(298,197),Image.Resampling.LANCZOS)
     out.paste(im,(x+(320-im.width)//2,y+4+(197-im.height)//2))
     break
   except Exception as e:
     print(j,attempt,str(e)[:90],flush=True);time.sleep(2)
 label=str(j+1)+" "+obj["filename"]
 d.text((x+8,y+208),label[:37],font=font,fill=(20,40,64))
 d.text((x+8,y+231),label[37:75],font=font,fill=(50,65,85))
buffer=io.BytesIO();out.save(buffer,"JPEG",quality=77,optimize=True)
Path("docs/v42-image-audit/alternative-contact.b64").write_text(base64.b64encode(buffer.getvalue()).decode("ascii"),encoding="ascii")
print("Alternative file photo previews:",len(sources),len(buffer.getvalue()),flush=True)
