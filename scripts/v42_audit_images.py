#!/usr/bin/env python3
"""V42: inspect 52 pre-V37 images as found, without asserting source authenticity."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageStat
import io,base64,hashlib,json,re,math,statistics

ROOT=Path("site"); OUT=Path("docs/v42-image-audit"); OUT.mkdir(parents=True,exist_ok=True)
data=json.loads(Path("docs/v36-hub-cards-audit.json").read_text("utf-8"))
rows=[r for r in data["things"]["mappings"] if r["kind"] in ("exact","topic")]
assert len(rows)==52 and sum(r["kind"]=="exact" for r in rows)==40 and sum(r["kind"]=="topic" for r in rows)==12
directory=(ROOT/"things-to-do/index.html").read_text("utf-8")
reviews=[]
for i,r in enumerate(rows):
    slug=r["slug"]; path=ROOT/r["image"].lstrip("/")
    articlepath=ROOT/"things-to-do"/slug/"index.html"
    article=articlepath.read_text("utf-8") if articlepath.exists() else ""
    index=directory.find(f'href="/things-to-do/{slug}/"')
    card=directory[index:index+1100] if index>=0 else ""
    item=dict(seq=i+1,slug=slug,title=r["title"],category=r["kind"],image=r["image"],image_exists=path.is_file(),
             article_exists=articlepath.exists(),in_card=r["image"] in card,
             in_article=r["image"] in article,
             matches_og=(f'content="https://www.nipponferry.com{r["image"]}"' in article and 'property="og:image"' in article),
             matches_twitter=(f'content="https://www.nipponferry.com{r["image"]}"' in article and 'name="twitter:image"' in article),
             article_has_explicit_commons=("Wikimedia Commons" in article),
             article_has_credit=bool(re.search(r'(CC BY|CC0|사진 출처|이미지 출처|저작권|photographer|촬영자|출처)',article,re.I)),
             source_registered=bool(r.get("photo_source")),
             source_uri=r.get("photo_source"),article_hero_count=len(re.findall(r'<img\b[^>]*>',article)),
             actual_kind_unverified=True)
    if path.exists():
        raw=path.read_bytes()
        item["bytes"]=len(raw);item["sha256"]=hashlib.sha256(raw).hexdigest()
        try:
            with Image.open(io.BytesIO(raw)) as img:
                img.load()
                item["format"]=img.format;item["width"]=img.width;item["height"]=img.height
                item["aspect_ratio"]=round(img.width/img.height,3)
                item["channel_stddev"]=[round(v,1) for v in ImageStat.Stat(img.convert("RGB").resize((60,60))).stddev]
        except Exception as e:item["image_open_error"]=str(e)[:150]
    reviews.append(item)
duplicates={}
for x in reviews:
    if x.get("sha256"):duplicates.setdefault(x["sha256"],[]).append(x["slug"])
repeats=[x for x in duplicates.values() if len(x)>1]
summary=dict(total=len(reviews),exact_count=40,topic_count=12,
             image_files_ok=sum(x.get("image_exists",False) for x in reviews),
             readable_webp=sum(x.get("format")=="WEBP" for x in reviews),
             article_files_ok=sum(x["article_exists"] for x in reviews),
             directory_paths_ok=sum(x["in_card"] for x in reviews),
             article_hero_links_ok=sum(x["in_article"] for x in reviews),
             article_og_links_ok=sum(x["matches_og"] for x in reviews),
             article_twitter_links_ok=sum(x["matches_twitter"] for x in reviews),
             proven_in_artwork_summary=sum(x["source_registered"] for x in reviews),
             visible_author_or_license=sum(x["article_has_credit"] for x in reviews),
             duplicated_pixel_hash_groups=repeats,
             conclusion="Technical file/path verification; still requires visual subject comparison and photo/license provenance verification.")
(OUT/"inventory.json").write_text(json.dumps({"summary":summary,"rows":reviews},ensure_ascii=False,indent=2),encoding="utf-8")

try:font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",16)
except Exception:font=ImageFont.load_default()
thumb_w,thumb_h=245,146; cell_w,cell_h=270,202
def make_sheet(group,portion,idx):
    cols=4
    rows_count=math.ceil(len(portion)/cols)
    canvas=Image.new("RGB",(cols*cell_w,rows_count*cell_h),(246,249,251))
    d=ImageDraw.Draw(canvas)
    for n,item in enumerate(portion):
        x=(n%cols)*cell_w; y=(n//cols)*cell_h
        d.rounded_rectangle((x+4,y+4,x+cell_w-4,y+cell_h-4),radius=9,fill=(255,255,255),outline=(211,218,226))
        p=ROOT/item["image"].lstrip("/")
        if p.is_file():
            try:
                with Image.open(p) as img:
                    im=ImageOps.contain(img.convert("RGB"),(thumb_w,thumb_h),Image.Resampling.LANCZOS)
                px=x+(cell_w-im.width)//2;py=y+9+(thumb_h-im.height)//2
                canvas.paste(im,(px,py))
            except:pass
        else:d.text((x+20,y+48),"MISSING",fill=(150,0,0),font=font)
        d.text((x+12,y+157),f'{item["seq"]:02d}  '+item["slug"][:31],font=font,fill=(30,40,55))
        d.text((x+12,y+182),f'{item["category"].upper()}  {item.get("width",0)}x{item.get("height",0)}',font=font,fill=(100,110,125))
    buf=io.BytesIO();canvas.save(buf,format="JPEG",quality=76,optimize=True)
    (OUT/f"contact-{group}-{idx}.b64").write_text(base64.b64encode(buf.getvalue()).decode(),encoding="ascii")
    print(group,idx,"sheet bytes",len(buf.getvalue()),flush=True)

for group in ("exact","topic"):
    group_rows=[r for r in reviews if r["category"]==group]
    for i in range(0,len(group_rows),12):
        make_sheet(group,group_rows[i:i+12],i//12+1)
print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
