from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import base64,json,io,math
data=json.loads(Path("docs/v43-deployed-photo-credits.json").read_text("utf-8"))
assert len(data)==20
out=Image.new("RGB",(4*290,5*232),(247,249,251))
d=ImageDraw.Draw(out)
try:font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",14)
except:font=ImageFont.load_default()
for n,x in enumerate(data):
    lx=(n%4)*290;ly=(n//4)*232
    im=Image.open(Path("site")/x["asset"].lstrip("/")).convert("RGB")
    im=ImageOps.contain(im,(266,168))
    out.paste(im,(lx+(290-im.width)//2,ly+6+(168-im.height)//2))
    d.text((lx+10,ly+179),str(n+1)+". "+x["slug"][:30],fill=(33,45,60),font=font)
    d.text((lx+10,ly+200),x["licence"],fill=(82,100,116),font=font)
buf=io.BytesIO()
out.save(buf,format="JPEG",quality=74,optimize=True)
path=Path("docs/v43-photo-contact.b64")
path.write_text(base64.b64encode(buf.getvalue()).decode(),encoding="ascii")
print("new V43 source-verified photos: 20, contact image bytes:",len(buf.getvalue()))
