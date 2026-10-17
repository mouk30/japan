#!/usr/bin/env python3
"""Generate 212 unique, topic-inspired Tokyo thumbnail illustrations, never pass off as venue photographs."""
import pathlib,hashlib,json,html,re,random,math
root=pathlib.Path("site"); pages=sorted((root/"japan/tokyo").glob("*/index.html"))
if len(pages)!=220:raise RuntimeError(f"Expected 220 articles; got {len(pages)}")
photos={x["slug"]:x for x in json.loads((root/"tokyo-photo-credits.json").read_text(encoding="utf8"))}
out=root/"images"/"tokyo-topics";out.mkdir(parents=True,exist_ok=True)
def topic(slug):
 s=slug.lower()
 for k,v in [("disney","themepark"),("hotel","hotel"),("shopping","shopping"),("department","shopping"),("isetan","shopping"),("daimaru","shopping"),("food","food"),("ramen","food"),("sushi","food"),("coffee","food"),("restaurant","food"),("station","train"),("metro","train"),("subway","train"),("transfer","train"),("line","train"),("train","train"),("museum","museum"),("art","museum"),("temple","temple"),("shrine","temple"),("garden","nature"),("park","nature"),("cruise","sea"),("port","sea"),("bay","sea"),("river","sea"),("odaiba","sea"),("night","night"),("sky","sky"),("tower","sky"),("observation","sky"),("view","sky"),("family","family"),("kids","family"),("airport","airport")]:
  if k in s:return v
 return "city"
palette=[("#112948","#57a4be","#f0bd7e"),("#1a3141","#64a3a2","#ffc98b"),("#251f46","#8f82d4","#f9b88d"),("#123342","#56a9a2","#f3d188"),("#243652","#699dd6","#ffc699"),("#242e46","#82a7bb","#ffd9a1")]
mapping={}
for page in pages:
 slug=page.parent.name
 if slug in photos:
  p=photos[slug]
  mapping[slug]={"src":p["src"],"alt":p["title"]+" 실제 현장 사진","caption":"실제 사진 · "+p["credit"]+" · "+p["license"],"source":p["source"]}
  continue
 seed=int(hashlib.sha256(slug.encode()).hexdigest()[:16],16);rng=random.Random(seed);kind=topic(slug)
 bg,accent,light=palette[seed%len(palette)]
 buildings=[]
 for i in range(17):
  x=i*58-5+rng.randint(-9,9);h=rng.randint(95,270);w=rng.randint(35,65)
  windows="".join(f'<rect x="{x+8+(k%3)*13}" y="{440-h+18+(k//3)*21}" width="5" height="8" rx="1" fill="{light}" opacity="{.25+.12*(k%4):.2f}"/>' for k in range(min(27,max(3,(h-24)//21*3))))
  buildings.append(f'<rect x="{x}" y="{440-h}" width="{w}" height="{h}" rx="4" fill="{accent}" opacity="{.12+.025*(i%6):.2f}"/>{windows}')
 landmarks={
 "train":'<path d="M190 310 Q190 220 280 220 H680 Q770 220 770 310 V390 H190Z" fill="#f5f5ef"/><rect x="235" y="245" width="490" height="88" rx="14" fill="'+bg+'"/><path d="M210 353H750" stroke="'+accent+'" stroke-width="14"/><circle cx="300" cy="389" r="13" fill="'+bg+'"/><circle cx="660" cy="389" r="13" fill="'+bg+'"/>',
 "food":'<ellipse cx="480" cy="350" rx="190" ry="80" fill="#f9ede1"/><ellipse cx="480" cy="330" rx="160" ry="51" fill="'+accent+'"/><path d="M340 322Q480 242 620 323" stroke="'+light+'" fill="none" stroke-width="13" stroke-dasharray="20 13"/><path d="M360 218L560 295M387 198L590 273" stroke="#ead5ad" stroke-width="9"/>',
 "temple":'<path d="M240 255L480 152L720 255L695 281H265Z" fill="'+light+'"/><rect x="306" y="280" width="348" height="145" fill="#e6dfd0"/><path d="M283 309H677" stroke="'+bg+'" stroke-width="20"/><rect x="431" y="319" width="98" height="106" fill="'+bg+'"/>',
 "nature":'<path d="M120 440Q220 255 380 440M340 440Q515 168 715 440" fill="'+accent+'" opacity=".75"/><path d="M545 410V240" stroke="#d9c39b" stroke-width="25"/><circle cx="545" cy="230" r="95" fill="#8ac3a4"/><circle cx="485" cy="260" r="60" fill="#9ed1b0"/>',
 "sea":'<path d="M0 360Q90 330 180 360T360 360T540 360T720 360T960 360V540H0Z" fill="'+accent+'" opacity=".63"/><path d="M260 335H706L650 405H320Z" fill="#eee8dc"/><path d="M472 335V205L584 335Z" fill="'+light+'"/>',
 "night":'<circle cx="735" cy="126" r="52" fill="'+light+'"/><path d="M430 440V198L480 140L530 198V440" fill="'+accent+'"/><path d="M463 141V96" stroke="'+light+'" stroke-width="7"/>',
 "sky":'<path d="M430 440V198L480 140L530 198V440" fill="'+accent+'"/><path d="M463 141V70" stroke="'+light+'" stroke-width="8"/><rect x="400" y="265" width="160" height="18" rx="6" fill="#e5e6df"/>',
 "shopping":'<rect x="330" y="210" width="300" height="230" rx="17" fill="#f2eade"/><path d="M330 267H630" stroke="'+accent+'" stroke-width="19"/><path d="M399 211Q399 132 480 132T561 211" stroke="'+accent+'" stroke-width="20" fill="none"/>',
 "themepark":'<circle cx="480" cy="260" r="133" fill="none" stroke="'+light+'" stroke-width="12"/><path d="M480 115V409M340 260H620M375 155L585 365M585 155L375 365" stroke="'+light+'" stroke-width="8"/><circle cx="480" cy="260" r="20" fill="'+accent+'"/>',
 "museum":'<path d="M260 242L480 138L700 242Z" fill="'+light+'"/><rect x="272" y="250" width="416" height="23" fill="#eadfd2"/>'+''.join(f'<rect x="{320+i*77}" y="280" width="25" height="140" fill="#eadfd2"/>' for i in range(5)),
 "airport":'<path d="M480 135L510 304L695 350V378L510 370L494 427H466L450 370L265 378V350L450 304Z" fill="#e9e9df"/>',
 "hotel":'<rect x="335" y="165" width="290" height="275" rx="11" fill="#ebe4d9"/>'+''.join(f'<rect x="{360+i*56}" y="{195+j*65}" width="34" height="40" rx="3" fill="{accent}"/>' for i in range(5) for j in range(3)),
 "family":'<circle cx="440" cy="216" r="55" fill="#e9d4b5"/><circle cx="555" cy="267" r="38" fill="#f5d9b4"/><path d="M353 440V353Q353 286 440 286Q527 286 527 353V440" fill="'+accent+'"/><path d="M515 440V360Q515 320 555 320Q612 320 612 360V440" fill="'+light+'"/>',
 "city":'<path d="M440 440V180L480 127L520 180V440" fill="'+accent+'"/><rect x="406" y="275" width="148" height="18" fill="'+light+'"/>'
 }
 art=landmarks.get(kind,landmarks["city"])
 stars="".join(f'<circle cx="{rng.randint(20,920)}" cy="{rng.randint(24,230)}" r="{rng.randint(1,4)}" fill="#fff4de" opacity=".45"/>' for _ in range(30))
 svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 540"><title>도쿄 여행 {html.escape(kind)} 주제 참고 일러스트</title><defs><linearGradient id="g" x2="1" y2="1"><stop stop-color="{bg}"/><stop offset="1" stop-color="{accent}"/></linearGradient></defs><rect width="960" height="540" fill="url(#g)"/><circle cx="{120+seed%700}" cy="120" r="98" fill="{light}" opacity=".18"/>{stars}<g>{''.join(buildings)}</g>{art}<path d="M0 439H960V540H0" fill="{bg}" opacity=".38"/><text x="40" y="502" fill="#ffffff" font-family="Arial,sans-serif" font-size="20" letter-spacing="4">TOKYO GUIDE / TOPIC VISUAL</text><text x="918" y="502" text-anchor="end" fill="#ffffff" font-family="Arial,sans-serif" font-size="16" opacity=".85">{hashlib.sha1(slug.encode()).hexdigest()[:8].upper()}</text></svg>'''
 path=out/(slug+".svg");path.write_text(svg,encoding="utf8")
 mapping[slug]={"src":"/images/tokyo-topics/"+slug+".svg","alt":"해당 여행 주제를 표현한 참고 일러스트","caption":"주제 참고 일러스트 · 실제 현장 사진 아님","source":""}
# Directly inject matching visuals on every card on the existing hub.
js='''/* 220 Tokyo cards, 8 photo credits + 212 unique topic illustrations. */\n(()=>{const map=__DATA__;document.querySelectorAll(".tky-card").forEach(card=>{const slug=(card.getAttribute("href")||"").split("/").filter(Boolean).pop(),p=map[slug];if(!p||card.querySelector(".tky-card-photo"))return;const figure=document.createElement("span");figure.className="tky-card-photo";const img=document.createElement("img");img.src=p.src;img.alt=p.alt;img.loading="lazy";img.decoding="async";img.addEventListener("error",()=>figure.remove(),{once:true});figure.append(img);const caption=document.createElement("span");caption.className="tky-photo-label";caption.textContent=p.caption;figure.append(caption);card.insertBefore(figure,card.firstChild)})})();'''.replace("__DATA__",json.dumps(mapping,ensure_ascii=False,separators=(",",":")))
(root/"tokyo-card-photos.js").write_text(js,encoding="utf8")
css=root/"tokyo-guide.css";st=css.read_text(encoding="utf8")
if ".tky-photo-label{" not in st:st+='\n.tky-card-photo{position:relative;display:block;overflow:hidden}.tky-card-photo img{display:block;width:100%;height:190px;object-fit:cover}.tky-photo-label{display:block;padding:5px 8px;font-size:10px;line-height:1.4;color:#50637d;background:#f0f4f7;white-space:normal}\n'
css.write_text(st,encoding="utf8")
report={"pages":len(pages),"real_photo_count":len(photos),"unique_topic_illustrations":len(pages)-len(photos),"unique_image_sources":len(set(x["src"] for x in mapping.values()))}
pathlib.Path("audit-reports/tokyo-220-images-built.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
print(json.dumps(report,ensure_ascii=False))
