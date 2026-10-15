#!/usr/bin/env python3
"""V42 surgical fixes after source-image visual QA: two photos + three broken fallback attributes."""
from pathlib import Path
from PIL import Image,ImageOps
import json,re,html,io,time,urllib.request

site=Path("site")
report=json.loads(Path("docs/v42-commons-candidates.json").read_text("utf-8"))
selected={
 "japanese-ekiben-railway-bento-culture":(
    "Train station box lunches in Japan called eki ben.jpg",
    "오사카 철도역에서 판매되는 여러 종류의 에키벤 도시락 진열 실제 사진",
    "철도역에서 도시락 종류를 살펴보는 예시이며 현재 판매 상품이나 가격은 달라질 수 있습니다."),
 "japanese-kintsugi-gold-repair-culture":(
    "Tea bowl, Korea, Joseon dynasty, 16th century AD, Mishima-hakeme type, buncheong ware, stoneware with white engobe and translucent, greenish-gray glaze, gold lacquer - Ethnological Museum, Berlin - DSC02061.JPG",
    "베를린 박물관에 전시된 한국 조선시대 분청사기 도자기의 금칠 수선선 실제 사진",
    "도자기 원산지는 한국입니다. 금칠 수선기법을 보여주는 역사 유물이지 일본산 도자기 또는 현장 수리 작업 사진은 아닙니다.")
}
errors=[]
credits=json.loads(Path("docs/v42-deployed-photo-credits.json").read_text("utf-8"))
finalized=json.loads(Path("docs/v42-image-audit/finalized-52.json").read_text("utf-8"))
baseline=json.loads(Path("docs/v36-hub-cards-audit.json").read_text("utf-8"))
hubfile=site/"things-to-do/index.html"
hub=hubfile.read_text("utf-8")
redone=[]
imgs={}
for slug,(filename,subject,note) in selected.items():
    c=next((v for v in report[slug]["options"] if v["filename"]==filename),None)
    if not c:raise RuntimeError("Commons photo not independently sourced: "+slug)
    if not (c["licence"].startswith("CC BY") or c["licence"] in ("CC0","Public domain")):
        raise RuntimeError("Unusable photo license: "+slug)
    raw=None
    for attempt in range(4):
      try:
        url=c["remote"]
        req=urllib.request.Request(url,headers={"User-Agent":"Nipponferry-v42-photoaccuracy/1.0 (https://www.nipponferry.com/)"})
        with urllib.request.urlopen(req,timeout=65) as stream:raw=stream.read()
        with Image.open(io.BytesIO(raw)) as im:
          im.load(); im=ImageOps.exif_transpose(im).convert("RGB")
          im.thumbnail((1440,1440),Image.Resampling.LANCZOS)
          b=io.BytesIO();im.save(b,"WEBP",quality=83,method=5)
        data=b.getvalue()
        assert data[:4]==b"RIFF" and data[8:12]==b"WEBP"
        imgs[slug]=data
        break
      except Exception as e:
        if attempt==3:raise
        time.sleep(3*(attempt+1))
    redone.append((slug,c,subject,note))
# Work on text in memory, then persist atomically after validity tests.
pages={}
repaired=[]
for article in sorted((site/"things-to-do").glob("*/index.html")):
    h=article.read_text("utf-8")
    if 'class="v42-image-credit"' not in h:continue
    changed=False
    for m in list(re.finditer(r'<p class="v42-image-credit"',h))[::-1]:
        i=m.start()
        imgstart=h.rfind("<img",0,i)
        if imgstart<0:continue
        text=h[imgstart:i]
        if not ("this.insertAdjacentHTML" in text and "onerror=" in text and len(text)<1500):continue
        term="</div>')\">"
        end=h.find(term,i)
        if end<0:raise RuntimeError("Fallback handler closing boundary not found in "+str(article))
        end+=len(term)
        on=h.find('onerror="',imgstart)
        if on<0 or on>i:raise RuntimeError("No expected onerror attr in "+str(article))
        before=h[imgstart:on].rstrip()
        src=re.search(r'\bsrc="([^"]+)"',before)
        if not src:raise RuntimeError("No expected src in "+str(article))
        credit_end=h.find("</p>",i)
        if credit_end<0 or credit_end>end:raise RuntimeError("Credit closing tag missing in "+str(article))
        credit=h[i:credit_end+4]
        h=h[:imgstart]+before+">\n"+credit+h[end:]
        changed=True
        repaired.append(article.parent.name)
    if changed:pages[article]=h
assert set(repaired)=={"japanese-ekiben-railway-bento-culture","japanese-kintsugi-gold-repair-culture","japanese-omiyage-souvenir-gift-culture"},repaired

for slug,c,subject,note in redone:
    path=site/"things-to-do"/slug/"index.html"
    h=pages.get(path,path.read_text("utf-8"))
    image=f"/images/culture-verified/{slug}.webp"
    patt=re.compile(r'<img\b[^>]*\bsrc="'+re.escape(image)+r'"[^>]*>')
    match=patt.search(h)
    if not match:raise RuntimeError("Cleaned image tag missing: "+slug)
    imgTag=match.group()
    assert "onerror=" not in imgTag
    newalt=html.escape(subject,quote=True)
    cleaned=re.sub(r'\balt="[^"]*"',lambda _:f'alt="{newalt}"',imgTag)
    h=h[:match.start()]+cleaned+h[match.end():]
    # Replace first existing photo provenance caption, preserving on-site visible
    # original source/license and accurately describing location and subject.
    author=html.escape(c.get("author") or "Wikimedia Commons 사용자")
    source=html.escape(c["source_page"],quote=True)
    license=html.escape(c["licence"])
    licence_url=html.escape(c.get("licence_url") or c["source_page"],quote=True)
    caption=(
      f'<p class="v42-image-credit" style="font-size:12px;line-height:1.7;padding:9px 15px;background:#f0f7fc;color:#345b71">'
      f'사진: <a href="{source}" target="_blank" rel="noopener noreferrer">{author} / Wikimedia Commons</a>'
      f' · <a href="{licence_url}" target="_blank" rel="noopener noreferrer">{license}</a>'
      f' · {html.escape(note)} · 원본 사진을 크기 조정해 WebP로 변환했습니다.</p>'
    )
    h,count=re.subn(r'<p class="v42-image-credit"[^>]*>[\s\S]*?</p>',lambda _:caption,h,count=1)
    if count!=1:raise RuntimeError("Photo credit not replaced: "+slug)
    assert c["source_page"] in h and c["licence"] in h,slug
    assert 'onerror="this.onerror=null' not in h[h.find(image):h.find(image)+400],slug
    pages[path]=h
    # Hero card title displayed above image; correct the image alt to exact subject.
    key=f'href="/things-to-do/{slug}/"';j=hub.find(key)
    assert j>=0,slug
    end=hub.find("</a>",j);piece=hub[j:end]
    pat=re.compile(r'<img[^>]*\bsrc="'+re.escape(image)+r'"[^>]*>')
    mm=pat.search(piece);assert mm,slug
    newtag=re.sub(r'\balt="[^"]*"',lambda _:f'alt="{newalt}"',mm.group())
    piece=piece[:mm.start()]+newtag+piece[mm.end():]
    hub=hub[:j]+piece+hub[end:]
    credit_row=next(x for x in credits if x["slug"]==slug)
    credit_row.update({"source_file":c["filename"],"photographer":c["author"],"licence":c["licence"],
      "license_url":c["licence_url"],"source_page":c["source_page"],"subject":subject,"note":note,
      "webp_bytes":len(imgs[slug])})
    final_row=next(x for x in finalized["rows"] if x["slug"]==slug)
    final_row.update({"photo_source":c["source_page"],"licence":c["licence"]})
    audit_row=next(x for x in baseline["things"]["mappings"] if x["slug"]==slug)
    audit_row.update({"photo_source":c["source_page"],"licence":c["licence"]})

for slug,data in imgs.items():
    p=site/f"images/culture-verified/{slug}.webp"
    with Image.open(io.BytesIO(data)) as im:assert im.format=="WEBP" and min(im.size)>=350
for path,h in pages.items():
    for match in re.finditer(r'<p class="v\d+-image-credit"',h):
        i=match.start(); j=h.rfind("<img",0,i)
        assert not ("this.insertAdjacentHTML" in h[j:i] and len(h[j:i])<1500),(str(path),i)
for path,content in pages.items():path.write_text(content,encoding="utf-8")
for slug,data in imgs.items():
    (site/f"images/culture-verified/{slug}.webp").write_bytes(data)
hubfile.write_text(hub,encoding="utf-8")
Path("docs/v42-deployed-photo-credits.json").write_text(json.dumps(credits,ensure_ascii=False,indent=2),encoding="utf-8")
Path("docs/v42-image-audit/finalized-52.json").write_text(json.dumps(finalized,ensure_ascii=False,indent=2),encoding="utf-8")
Path("docs/v36-hub-cards-audit.json").write_text(json.dumps(baseline,ensure_ascii=False,indent=2),encoding="utf-8")
summary={"rewritten_original_photos":[x[0] for x in redone],"html_credit_attribute_repaired":sorted(repaired),
         "actual_new_images_webp":{slug:len(data) for slug,data in imgs.items()}}
Path("docs/v42-image-audit/final-visual-corrections.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
