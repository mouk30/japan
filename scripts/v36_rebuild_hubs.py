#!/usr/bin/env python3
"""V36 image-card catalog rebuild: food + things-to-do.

Only uses local repository media. Distinguishes same-subject images from
editorial reference images; creates neutral non-photographic illustrated
thumbnail only when no reasonably matching asset exists.
The existing article URLs, copy, and canonical tags are preserved.
"""
from __future__ import annotations

import html
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
THINGS = SITE / "things-to-do" / "index.html"
FOOD = SITE / "food" / "index.html"
IMAGE_ROOT = SITE / "images"
REPORT = ROOT / "docs" / "v36-hub-cards-audit.json"
ASSETS = {"/" + str(p.relative_to(SITE)).replace("\\", "/"): p for p in IMAGE_ROOT.rglob("*") if p.is_file() and p.suffix.lower() in (".webp",".png",".jpg",".jpeg")}
BANNED = ("mascot", "kakao", "logo", "hero-blue", "favicon", "qrcode", "banner", "icon")
FALLBACK_DIR = IMAGE_ROOT / "hub-thumbnails"
FALLBACK_DIR.mkdir(parents=True, exist_ok=True)

def clean(v: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", v)).strip()

def tokens(v: str) -> set[str]:
    v = re.sub(r"[^a-z0-9]+", "-", v.lower())
    return {x for x in v.split("-") if len(x) >= 3 and x not in {"japan","japanese","culture","hero","guide","the","and","editorial","travel","why","history"}}

def category(v: str) -> str:
    terms = {
        "철도·교통":("train","rail","shinkansen","tram","station","ferry","ship","ropeway","subway","pass","metro","ekiben"),
        "음식·식문화":("sushi","ramen","food","udon","soba","bento","tempura","takoyaki","wagashi","miso","onigiri","izakaya","yatai","dashi"),
        "전통공예":("pottery","kimono","urushi","lacquer","kumiko","glass","craft","woodblock","origami","washi","porcelain","textile","sashiko","fabric","kintsugi"),
        "사계절·자연":("forest","sakura","flower","nature","volcan","onsen","yakushima","geology","bamboo","snow","cherry","mountain","sea","ocean","tree"),
        "건축·역사":("castle","temple","samurai","roof","pagoda","shrine","jizo","engawa","machiya","house","historic","architecture"),
        "일본 생활":("convenience","konbini","shopping","life","street","queue","culture","city","garden","bath","park"),
    }
    for k, words in terms.items():
        if any(w in v for w in words):
            return k
    return "일본 문화·여행"

PALETTES=[("#0b436b","#177fa0"),("#173b59","#337c72"),("#303f74","#7486ab"),("#69503c","#af7459"),("#315755","#509690"),("#324972","#5387ad")]
def svg_cover(slug: str, title: str) -> str:
    # Visibly graphic rather than falsely claiming a particular place or food photo.
    group=category(slug)
    color1,color2=PALETTES[sum(map(ord,slug))%len(PALETTES)]
    safe=html.escape(title[:30],quote=True)
    sub=html.escape(group)
    # Keep text readable, give a simple editorial vector illustration.
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="560" viewBox="0 0 900 560">
<defs><linearGradient id="g" x2="1" y2="1"><stop stop-color="{color1}"/><stop offset="1" stop-color="{color2}"/></linearGradient></defs>
<rect width="900" height="560" fill="url(#g)"/>
<circle cx="770" cy="132" r="185" fill="#fff" fill-opacity=".10"/>
<circle cx="742" cy="420" r="210" fill="#fff" fill-opacity=".06"/>
<path d="M-10 370 C160 295 265 490 440 380 S760 270 910 365" stroke="#fff" stroke-opacity=".18" stroke-width="16" fill="none"/>
<rect x="58" y="64" width="210" height="39" rx="19" fill="#fff" fill-opacity=".21"/>
<text x="76" y="90" fill="#fff" font-size="21" font-family="sans-serif" font-weight="700">NIPPONFERRY</text>
<text x="60" y="266" fill="#fff" font-size="52" font-family="sans-serif" font-weight="900">{safe}</text>
<text x="60" y="332" fill="#dbf4ff" font-size="29" font-family="sans-serif">{sub} · 콘텐츠 가이드</text>
<text x="60" y="495" fill="#fff" font-size="20" font-family="sans-serif" opacity=".82">주제 안내 그래픽 · 실제 촬영 사진 아님</text>
</svg>'''

def topic_graphic(slug: str, title: str) -> str:
    p=FALLBACK_DIR / f"{slug}.svg"
    p.write_text(svg_cover(slug,title),encoding="utf-8")
    return "/images/hub-thumbnails/"+slug+".svg"

def article_image(slug: str, title: str) -> tuple[str,str]:
    article = SITE / "things-to-do" / slug / "index.html"
    expected = (
        f"/images/culture-verified/{slug}.webp",
        f"/images/editorial/{slug}.webp",
        f"/images/editorial/{slug}.jpg",
        f"/images/{slug}.webp",
    )
    for path in expected:
        if path in ASSETS:return path,"exact"
    if article.is_file():
        text=article.read_text("utf-8")
        imgs=re.findall(r'<img\b[^>]*\bsrc="([^"]+)"',text)
        for photo in imgs:
            if photo in ASSETS and slug in photo:return photo,"exact"
        # A related image is only accepted if the filename's subject overlaps the article.
        # Avoid visually false examples such as toilets illustrated with shoji sliding doors.
        for photo in imgs:
            if photo not in ASSETS or any(term in photo for term in BANNED):continue
            similar=len(tokens(slug) & tokens(photo.split("/")[-1]))
            if similar>=1:return photo,"topic"
    # Find another image with a meaningful keyword overlap; block unrelated stock city photos.
    candidates=[]
    for asset in ASSETS:
        if any(t in asset for t in BANNED):continue
        overlap=tokens(slug)&tokens(asset.split("/")[-1])
        if len(overlap)>=2:
            candidates.append((len(overlap),asset))
    if candidates:
        return sorted(candidates,key=lambda x:(-x[0],x[1]))[0][1],"topic"
    return topic_graphic(slug,title),"graphic"

def css():
    return """<style id="v36-companion-image-cards">
/* Companion-guide visual system: topic-matched thumbnails + title + intro */
.v28-panel.v36-photo-card{display:flex!important;flex-direction:column;padding:0!important;background:#fff!important;overflow:hidden;min-width:0;border:1px solid #d8e6ef;border-radius:17px;box-shadow:0 8px 22px rgba(13,54,83,.075);height:100%;transition:transform .18s ease,box-shadow .18s ease}
.v28-panel.v36-photo-card:hover{transform:translateY(-3px);box-shadow:0 13px 28px rgba(13,54,83,.13)}
.v36-photo-card .v36-photo{position:relative;display:block;margin:0;width:100%;aspect-ratio:16/10;overflow:hidden;background:#d8e7ef}
.v36-photo-card .v36-photo img{display:block;width:100%;height:100%;object-fit:cover}
.v36-photo-card .v36-photo em{position:absolute;bottom:8px;right:8px;max-width:94%;background:rgba(4,38,61,.79);border-radius:4px;padding:3px 6px;font-size:10px;line-height:1.35;font-style:normal;color:#fff}
.v36-photo-card .v36-card-copy{padding:16px 17px 19px;display:flex;flex-direction:column;gap:6px;flex:1;min-width:0}
.v36-photo-card .v36-card-copy h3{font-size:18px!important;line-height:1.4!important;margin:0!important;color:#102f4e}
.v36-photo-card .v36-card-copy p{font-size:13px;line-height:1.65;color:#62788b;margin:0;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.v36-photo-card .v36-card-copy small{font-size:10px;font-weight:850;letter-spacing:.04em;color:#08758e}
.v36-photo-card .v36-card-footer{font-size:12px;color:#087ca2;font-weight:850;margin-top:auto;padding-top:9px}
.v28-text-grid{gap:17px}
#japan-new-50 .v36-photo-card,#japan-new-50 [class*="card"]{min-width:0}
@media(max-width:780px){.v28-text-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.v36-photo-card .v36-card-copy{padding:12px}.v36-photo-card .v36-card-copy h3{font-size:15px!important}.v36-photo-card .v36-photo em{font-size:9px}}
@media(max-width:430px){.v28-text-grid{gap:9px}.v36-photo-card .v36-card-copy{padding:10px}.v36-photo-card .v36-card-copy h3{font-size:14px!important}.v36-photo-card .v36-card-copy p{font-size:12px}.v36-photo-card .v36-card-copy small{font-size:9px}}
@media(prefers-reduced-motion:reduce){.v36-photo-card{transition:none}}
</style>"""

things=THINGS.read_text("utf-8")
if "v36-companion-image-cards" in things: raise RuntimeError("Already updated V36")
cards=[]
pat=re.compile(r'<a class="v28-panel" href="(/things-to-do/([^"/]+)/)"([^>]*)>([\s\S]*?)</a>')
def replace_panel(m):
    url,slug,other,body=m.groups()
    h=re.search(r'<h3[^>]*>([\s\S]*?)</h3>',body)
    if not h:return m.group(0)
    title=clean(h.group(1)).removesuffix("→").strip()
    p=re.search(r'<p[^>]*>([\s\S]*?)</p>',body)
    description=clean(p.group(1)) if p else f"{title}의 배경과 여행 중 확인할 내용을 정리했습니다."
    badge=re.search(r'<small[^>]*>([\s\S]*?)</small>',body)
    label=clean(badge.group(1)) if badge else category(slug)
    # Some unfinished index entries used English slug fragments instead of Korean.
    if title.replace("·","").strip().lower() ==slug.replace("-"," ") or (
       len(re.findall("[가-힣]",title))<2):
        article=(SITE/"things-to-do"/slug/"index.html")
        if article.is_file():
            source=article.read_text("utf-8")
            title=clean((re.search(r'<h1[^>]*>([\s\S]*?)</h1>',source) or re.search(r'<title>([\s\S]*?)</title>',source) or [None,title])[1]).split("|")[0].strip()
    src,kind=article_image(slug,title)
    tag = {"exact":"게시글 대표 이미지","topic":"주제 참고 이미지","graphic":"주제 안내 그래픽"}[kind]
    cards.append({"slug":slug,"image":src,"kind":kind,"title":title})
    return (f'<a class="v28-panel v36-photo-card" href="{url}"{other}>'
            f'<figure class="v36-photo"><img src="{html.escape(src,quote=True)}" alt="{html.escape(title,quote=True)} 관련 {tag}" loading="lazy" decoding="async">'
            f'<em>{tag}</em></figure><div class="v36-card-copy"><small>{html.escape(label)}</small>'
            f'<h3>{html.escape(title)}</h3><p>{html.escape(description)}</p><span class="v36-card-footer">자세히 보기 →</span></div></a>')
things,n=pat.subn(replace_panel,things)
if len(cards)!=152:raise RuntimeError(f"Unexpected indexed cards: {len(cards)} regex matches {n}")
things=things.replace("</head>",css()+"</head>",1)
THINGS.write_text(things,encoding="utf-8")

# Create a differentiated food gallery, never a city skyline photo.
FOOD_RULES = {
 "food": ("ramen","takoyaki","okonomiyaki","seafood","fugu","soba","sushi","yakitori","food","udon","izakaya","ekiben"),
 "market": ("market","yatai","shopping-street","fish","sushi","seafood","food-stall","izakaya"),
 "dessert": ("wagashi","matcha","sweets","dessert","tea","parfait","mochi"),
 "local-food": ("regional-food","yakitori","soba","udon","ramen","izakaya","ekiben","food"),
}
CITY_BANNED=("fukuoka.jpg","osaka.jpg","tsushima.jpg","shimonoseki.jpg","city.jpg")
FOOD_KEYWORDS=("food","ramen","soba","udon","takoyaki","wagashi","matcha","sweets","dessert","market","fish","seafood","sushi","yatai","izakaya","dashi","ekiben","yakitori","tea","tempura","mochi","okonomiyaki","bento","rice","cafe")
food_assets=[p for p in ASSETS if any(s in p.lower() for s in FOOD_KEYWORDS) and not any(t in p for t in BANNED) and not any(t in p for t in CITY_BANNED)]
if "/images/ramen-close.jpg" in ASSETS and "/images/ramen-close.jpg" not in food_assets:food_assets.append("/images/ramen-close.jpg")
if "/images/food.jpg" in ASSETS and "/images/food.jpg" not in food_assets:food_assets.append("/images/food.jpg")
used=Counter()
foods=[]
city_guide={"fukuoka":"후쿠오카","osaka":"오사카","tsushima":"대마도","shimonoseki":"시모노세키"}
def select_food(city: str,kind: str) -> tuple[str,str]:
    keywords=FOOD_RULES[kind]
    scored=[]
    for asset in food_assets:
        name=asset.lower().rsplit("/",1)[-1]
        ranking=0
        for index,term in enumerate(keywords):
            if term in name:ranking=max(ranking,100-index*7)
        if city in name:ranking+=42
        if "verified" in asset:ranking+=5
        if asset.endswith(".webp"):ranking+=3
        if ranking:
            scored.append((ranking - used[asset]*35,ranking,asset))
    if not scored:
        return topic_graphic(f"food-{city}-{kind}",city_guide[city]+" 식도락"),"graphic"
    _,raw,path=sorted(scored,key=lambda x:(-x[0],-x[1],x[2]))[0]
    used[path]+=1
    return path,"subject-illustration"

food=FOOD.read_text("utf-8")
if "v36-food-cards" in food:raise RuntimeError("Food already updated")
p=re.compile(r'(<a class="dircard" href="/japan/((?:fukuoka|osaka|tsushima|shimonoseki))-(food|market|dessert|local-food)/"><img )([^>]+)(>)')
def replace_food(m):
    city,kind=m.group(2),m.group(3)
    photo,typ=select_food(city,kind)
    foods.append({"city":city,"type":kind,"link":f"/japan/{city}-{kind}/","image":photo,"kind":typ})
    title=city_guide[city]+" "+{"food":"대표 음식","market":"시장·먹거리","dessert":"디저트·카페","local-food":"지역 식문화"}[kind]
    attrs=m.group(4)
    attrs=re.sub(r'src="[^"]+"',f'src="{photo}"',attrs)
    attrs=re.sub(r'alt="[^"]+"',f'alt="{title}를 소개하는 음식·시장 주제 참고 이미지"',attrs)
    attrs=attrs.replace('loading="lazy"','loading="lazy" decoding="async"')
    return m.group(1)+attrs+m.group(5)
food,n=p.subn(replace_food,food)
if len(foods)!=16:raise RuntimeError(f"Expected 16 food cards, found {len(foods)} in {n}")
food_css="""<style id="v36-food-cards">
.dirgrid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:17px}
.dircard{display:flex!important;flex-direction:column;min-width:0;background:#fff;border-radius:17px;overflow:hidden;border:1px solid #dae6ee;box-shadow:0 9px 25px rgba(8,53,83,.085);transition:transform .17s,box-shadow .17s}
.dircard:hover{transform:translateY(-3px);box-shadow:0 14px 30px rgba(8,53,83,.14)}
.dircard>img{display:block;width:100%;aspect-ratio:16/10;height:auto;object-fit:cover}
.dircard .dirin{padding:17px;flex:1}
.dircard .dirin h2{font-size:19px;line-height:1.4}
.dircard .dirin p{font-size:13px;line-height:1.7}
@media(max-width:990px){.dirgrid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:700px){.dirgrid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.dircard .dirin{padding:12px}.dircard .dirin h2{font-size:16px}.dircard .dirin p{font-size:12px}}
@media(max-width:340px){.dirgrid{grid-template-columns:1fr}}
@media(prefers-reduced-motion:reduce){.dircard{transition:none}}
</style>"""
food=food.replace("</head>",food_css+"</head>",1)
FOOD.write_text(food,encoding="utf-8")

# For the 16 existing food articles, replace only their generic (city skyline) lead cover;
# other illustration images in the body are left alone and tracked for the next editorial pass.
updated_articles=[]
for item in foods:
    f=SITE/"japan"/f'{item["city"]}-{item["type"]}'/"index.html"
    if not f.is_file():continue
    s=f.read_text("utf-8")
    original=s
    photo=item["image"]
    if photo.endswith(".svg"):
        continue
    # Do not rewrite nested body illustrations; only large article main cover.
    s=re.sub(r'(<img\b[^>]*\bclass="(?:article-cover|d-img|s17-img)"[^>]*\bsrc=")[^"]+(")',
             lambda m:m.group(1)+photo+m.group(2),s,count=1)
    if 'property="og:image"' in s:
        s=re.sub(r'<meta property="og:image" content="[^"]+">',
                 f'<meta property="og:image" content="https://www.nipponferry.com{photo}">',s,count=1)
    if s!=original:
        f.write_text(s,encoding="utf-8")
        updated_articles.append(str(f.relative_to(SITE)))

REPORT.parent.mkdir(exist_ok=True)
REPORT.write_text(json.dumps({
 "v36":"food-and-things-to-do-companion-style",
 "things": {"cards":len(cards),"kinds":dict(Counter(x["kind"] for x in cards)),"mappings":cards},
 "food":{"cards":len(foods),"mappings":foods},
 "food_article_covers_updated":updated_articles,
 "caveat":"Topic/reference images are not automatically verified actual photos of a particular site. SVG covers explicitly say they are graphics. All matched file paths exist in repository."
},ensure_ascii=False,indent=2),encoding="utf-8")

# hard stop on broken local image references
for entry in cards:
    assert entry["image"].startswith("/images/")
    assert (SITE/entry["image"].lstrip("/")).exists(),entry["image"]
for entry in foods:
    assert (SITE/entry["image"].lstrip("/")).exists(),entry["image"]
assert n==16
print(f"V36 updated: {len(cards)} illustrated topic cards, {len(foods)} food cards, {len(updated_articles)} food article hero covers")
print("Things:",Counter(x["kind"] for x in cards))
print("Food images:",Counter(x["image"] for x in foods))
