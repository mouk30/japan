#!/usr/bin/env python3
"""Repair Tokyo SVG thumbnails and cross-batch duplicate Wikimedia Commons originals.
Never replace with an unrelated image just to fill a card. Emit truthful remaining work.
"""
import pathlib,re,json,html,io,time,urllib.parse,urllib.request,urllib.error,collections,random
from PIL import Image,ImageOps
root=pathlib.Path("site");hub=(root/"japan/tokyo/index.html").read_text(encoding="utf8")
slugs=[x.strip("/").split("/")[-1] for x in re.findall(r'<a\s+class="tky-card"[^>]*href="([^"]+)"',hub)]
assert len(slugs)==220
p=root/"tokyo-card-photos.js";js=p.read_text(encoding="utf8")
m=re.search(r"const map=(\{.*?\});document\.querySelectorAll",js,re.S);assert m
registry=json.loads(m.group(1))
# search phrase followed by identifying tokens that must occur in Commons file title
spec={
"tokyo-ramen-best-areas":("Shoyu ramen bowl",["ramen"]),
"tokyo-sushi-breakfast-guide":("Sushi nigiri platter Japan",["sushi"]),
"tokyo-tsukishima-monjayaki":("Monjayaki griddle Tsukishima",["monjayaki"]),
"tokyo-yakitori-izakaya-guide":("Yakitori skewers Japan",["yakitori"]),
"tokyo-depachika-food-halls":("Depachika food department store Japan",["depachika"]),
"tokyo-night-view-observation-comparison":("Tokyo night skyline",["tokyo"]),
"tokyo-subway-route-map-korean":("Tokyo metro station sign",["metro"]),
"tokyo-subway-ticket-24-48-72":("Tokyo Subway Ticket pass",["ticket"]),
"tokyo-yamanote-line-transfer-guide":("Yamanote Line train",["yamanote"]),
"tokyo-haneda-airport-train-guide":("Keikyu Haneda Airport train",["haneda"]),
"tokyo-narita-airport-train-guide":("Narita Express train",["narita"]),
"tokyo-ginza-department-store-route":("Ginza shopping street Tokyo",["ginza"]),
"tokyo-shinjuku-isetan-shopping":("Isetan Shinjuku store",["isetan"]),
"tokyo-ginza-mitsukoshi-depachika":("Ginza Mitsukoshi department store",["mitsukoshi"]),
"tokyo-station-character-street":("Tokyo Character Street",["character"]),
"tokyo-mega-donki-shibuya":("MEGA Don Quijote Shibuya",["don","quijote"]),
"nippori-skyliner-jr":("Nippori station Keisei Skyliner",["nippori"]),
"toei-one-day-pass":("Toei Subway train Tokyo",["toei"]),
"pasmo-vs-suica-card":("Suica PASMO card",["suica"]),
"metro-elevator-stroller":("Tokyo Metro station elevator",["elevator"]),
"disney-dpa-app-purchase":("Tokyo Disneyland attraction",["disneyland"]),
"disney-priority-pass-free":("Tokyo Disneyland attractions",["disneyland"]),
"disney-standby-pass-store":("Tokyo DisneySea souvenir shop",["disneysea"]),
"disney-priority-seating-restaurants":("Tokyo Disneyland restaurant",["disneyland"]),
"disney-character-dining-booking":("Tokyo Disneyland character dining",["disneyland"]),
"disney-disability-passport":("Tokyo Disneyland accessible entrance",["disneyland"]),
"disney-children-ticket-age":("Tokyo Disneyland entrance",["disneyland"]),
"disney-ticket-date-change":("Tokyo Disneyland entrance",["disneyland"]),
"disneysea-rapunzel-lantern":("Rapunzel Lantern Festival DisneySea",["rapunzel"]),
"disneysea-soaring-flight":("Soaring Fantastic Flight DisneySea",["soaring"]),
"disney-fantasy-springs-hotel":("Fantasy Springs Hotel Tokyo",["fantasy","hotel"]),
"isetan-shinjuku-1f-cosmetics":("Isetan Shinjuku cosmetics store",["isetan"]),
"daimaru-tokyo-b1-food":("Daimaru Tokyo Station building",["daimaru"]),
"daimaru-tokyo-12f-taxfree":("Daimaru Tokyo department store",["daimaru"]),
"daimaru-tokyo-10f-hands":("Daimaru Tokyo storefront",["daimaru"]),
"shinjuku-takashimaya-b1":("Shinjuku Takashimaya",["takashimaya"]),
"shinjuku-takashimaya-9f-kids":("Shinjuku Takashimaya",["takashimaya"]),
"ginza-six-b2-food":("Ginza Six Tokyo",["ginza","six"]),
"ginza-six-b1-beauty":("Ginza Six cosmetics",["ginza","six"]),
"ginza-six-rooftop":("Ginza Six rooftop garden",["ginza","six"]),
"nihombashi-mitsukoshi-floors":("Mitsukoshi Nihombashi",["mitsukoshi"]),
"nihombashi-takashimaya-floor":("Takashimaya Nihombashi",["takashimaya"]),
"odaiba-kirakira-donki":("DiverCity Tokyo Plaza Odaiba",["divercity"]),
"donki-taxfree-passport":("Don Quijote Japan shop",["quijote"]),
"tokyo-drugstore-cosmetics":("Matsumoto Kiyoshi drugstore",["matsumoto"]),
"tokyo-drugstore-sun-care":("Japanese sunscreen products",["sunscreen"]),
"tokyo-kbeauty-vs-jcosmetic":("Japanese cosmetics shop",["cosmetics"]),
"muji-ginza-4f-taxfree":("Muji Ginza Tokyo",["muji","ginza"]),
"muji-ginza-6f-atelier":("Muji Ginza Hotel",["muji","ginza"]),
"muji-ginza-food-b1":("Muji Diner Ginza",["muji"]),
"shibuya-loft-stationery":("Shibuya Loft",["loft"]),
"ikebukuro-loft-floors":("Ikebukuro Loft",["loft"]),
"loft-stationery-gifts":("Japanese stationery stationery shop",["stationery"]),
"tokyo-hands-diy-gifts":("Tokyu Hands Shibuya store",["hands"]),
"kuramae-design-coffee":("Kuramae Tokyo cafe",["kuramae"]),
"kiyosumi-shirakawa-coffee":("Kiyosumi Shirakawa cafe",["kiyosumi"]),
"monzen-nakacho-shrine":("Tomioka Hachimangu Shrine Tokyo",["tomioka"]),
"jiyugaoka-dessert-cafes":("Jiyugaoka Tokyo street",["jiyugaoka"]),
"sugamo-jizo-shopping":("Sugamo Jizo-dori",["sugamo"]),
"oji-asukayama-tram":("Asukayama Toden Arakawa tram",["arakawa"]),
"tokyo-unagi-kabayaki":("Unagi kabayaki unaju Japan",["unagi"]),
"tokyo-izakaya-otoshi":("Japanese izakaya interior",["izakaya"]),
"tokyo-department-bento":("Japanese bento department store",["bento"]),
"tokyo-kissaten-retro-cafe":("Japanese kissaten cafe",["kissaten"]),
"tokyo-matcha-wagashi":("Wagashi matcha",["wagashi"]),
"tokyo-melonpan-bakery":("Melonpan Japan bakery",["melon"]),
"tokyo-food-allergy-japanese":("Japanese food allergy label",["allergy"]),
"tokyo-teamlab-borderless-vs-planets":("teamLab Borderless Tokyo",["teamlab"]),
"tokyo-winter-illumination-evening":("Tokyo winter illumination",["illumination"]),
"tokyo-cruise-to-skytree":("Tokyo Skytree river Sumida",["skytree"])
}
expected=[s for s in slugs if registry[s]["src"].endswith(".svg")]
assert set(expected)==set(spec),(len(expected),len(spec),set(expected)^set(spec))
# Replace second usage in each duplicate pair, preserve original.
used={};dupes=[]
for slug in slugs:
 f=registry[slug].get("source_file")
 if f:
  if f in used:dupes.append(slug)
  else:used[f]=slug
for slug in dupes:
 if slug=="disney-ticket-sold-out":spec[slug]=("Tokyo Disneyland ticket entrance",["disneyland"])
 if slug=="disney-miracosta-hotel":spec[slug]=("Tokyo DisneySea Hotel Miracosta",["miracosta"])
 if slug=="tokyo-lastday-taxfree-baggage":spec[slug]=("Tokyo Station coin locker",["locker"])
 if slug=="tokyo-budget-under-10000yen":spec[slug]=("Tokyo street food Ameyoko Ueno",["ameyoko"])
assert len(dupes)==4
headers={"User-Agent":"NipponferryTokyoPhotoRepair/1.0 (https://www.nipponferry.com)","Accept":"application/json,image/*"}
def get(url):
 for attempt in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=40) as r:return r.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or attempt==3:raise
   time.sleep(5*(attempt+1))
  except Exception:
   if attempt==3:raise
   time.sleep(5*(attempt+1))
def clean(x):return html.unescape(re.sub("<[^>]*>","",x)).strip()
dest=root/"images"/"tokyo-verified";dest.mkdir(exist_ok=True)
changed={};errors={};usedFiles=set(used)
for slug in expected+dupes:
 query,tokens=spec[slug]
 try:
  options=[]
  # Prior results routinely fail because all tokens must appear in titles.
  # Search again by narrower one/two word subject terms while keeping one exact identifying token.
  for phrase in [query," ".join(tokens)]:
   params=urllib.parse.urlencode({"action":"query","format":"json","generator":"search","gsrsearch":phrase+" filetype:bitmap","gsrnamespace":6,"gsrlimit":50,"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":1280})
   response=json.loads(get("https://commons.wikimedia.org/w/api.php?"+params))
   for page in response.get("query",{}).get("pages",{}).values():
    title=page.get("title","");low=title.lower()
    if not any(t.lower() in low for t in tokens):continue
    if any(x in low for x in ("svg","map of","map.","logo","poster","diagram","model","screenshot","ticket price")):continue
    if title in usedFiles or title in [x[0] for x in options]:continue
    info=(page.get("imageinfo") or [{}])[0]
    metadata=info.get("extmetadata") or {}
    lic=clean(metadata.get("LicenseShortName",{}).get("value",""))
    if not (lic.startswith("CC BY") or lic=="CC0"):continue
    options.append((title,info,metadata,lic))
   if len(options)>=3:break
  if not options:raise ValueError("No new licensed topic-matched Commons file")
  found=False
  for title,info,metadata,lic in sorted(options,key=lambda x:len(x[0]))[:8]:
   try:
    img=Image.open(io.BytesIO(get(info.get("thumburl") or info["url"])))
    img.load()
    if min(img.size)<450:continue
    img=ImageOps.exif_transpose(img).convert("RGB")
    img=ImageOps.fit(img,(1280,720),centering=(.5,.5),method=Image.Resampling.LANCZOS)
    img.save(dest/(slug+".webp"),"WEBP",quality=87,method=6)
    author=clean(metadata.get("Artist",{}).get("value",""))[:160] or "Wikimedia Commons"
    registry[slug]={"src":"/images/tokyo-verified/"+slug+".webp","alt":clean(title.removeprefix("File:"))+" 실사진","caption":"사진: "+author+" · "+lic+" · Wikimedia Commons","source":info.get("descriptionurl"),"license":lic,"author":author,"source_file":title}
    changed[slug]=title;usedFiles.add(title);found=True;break
   except Exception:continue
  if not found:raise ValueError("Matching images failed download/size check")
 except Exception as exc:errors[slug]=str(exc)[:170]
 time.sleep(.7)
js=js[:m.start(1)]+json.dumps(registry,ensure_ascii=False,separators=(",",":"))+js[m.end(1):]
p.write_text(js,encoding="utf8")
remain=[{"v":i+1,"slug":slug} for i,slug in enumerate(slugs) if registry[slug]["src"].endswith(".svg")]
sources=collections.defaultdict(list)
for i,slug in enumerate(slugs):
 if registry[slug].get("source_file"):sources[registry[slug]["source_file"]].append({"v":i+1,"slug":slug})
repeats={k:v for k,v in sources.items() if len(v)>1}
report={"total_cards":220,"before_svg":len(expected),"now_svg":len(remain),"before_duplicate_pairs":len(dupes),"now_duplicate_sources":len(repeats),"replacements":changed,"unreplaced":errors,"remaining_svg":remain,"remaining_duplicates":repeats,"limitations":["File title indicates subject but human visual review and live mobile testing still required.","Attribution shown in card caption. Verify original work licenses and required notices before commercial use."]}
path=pathlib.Path("audit-reports/tokyo-220-image-repair-report.json")
path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
print(json.dumps({"replaced":len(changed),"svg_remaining":len(remain),"duplicate_sources_remaining":len(repeats)},ensure_ascii=False))
