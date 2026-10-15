#!/usr/bin/env python3
"""V31: repair 105 hidden/broken story hero images. Topic-adjacent photos are explicitly
marked illustrative, never 'original photography' or photos of the named event.
Keeps article URLs, copy, canonical and JSON-LD fields except broken image references.
"""
from pathlib import Path
from html import escape
import json,re
ROOT=Path("site")
img=lambda short:"/images/editorial/"+short+".webp"
# Hand-reviewed categories; no cross-region cover masquerading as exact destination.
M={
"aizome-japanese-indigo-dye":"fukuoka-hakata-ori-textiles",
"bonsai-japanese-miniature-trees":"japanese-garden-stones-moss",
"bunraku-japanese-puppet-theater":"matsuri-hero",
"dashi-japanese-umami-stock":"ramen-japanese-noodle-evolution",
"depachika-japanese-department-food":"kyoto-nishiki-market-food-culture",
"edo-kiriko-cut-glass":"kintsugi-hero",
"hanabi-japanese-fireworks-summer":"yukata-summer-festival",
"hatsumode-japanese-first-shrine-visit":"shrine-temple-hero",
"hinamatsuri-japanese-dolls":"wagashi-japanese-seasonal-sweets",
"ikebana-japanese-flower-arrangement":"japanese-garden-hero",
"japan-ainu-embroidery":"furoshiki-japanese-wrapping-cloth",
"japan-ajisai-hydrangea-season":"japanese-garden-water",
"japan-amami-oshima-tsumugi":"fukuoka-hakata-ori-textiles",
"japan-aomori-nebuta-floats":"aomori-port-nebuta-day-trip",
"japan-bamboo-grove-ecology":"japanese-garden-stones-moss",
"japan-castle-moats":"hakodate-goryokaku-fort",
"japan-castle-stone-walls":"himeji-castle-defense-route",
"japan-castle-tenshu-towers":"himeji-castle-defense-route",
"japan-coral-okinawa-islands":"okinawa-sea-turtle-snorkeling",
"japan-geothermal-steam-hells":"beppu-port-onsen-day-trip",
"japan-izakaya-yokocho-alleys":"izakaya-japanese-afterwork-culture",
"japan-jizo-roadside-statues":"shrine-temple-hero",
"japan-kagawa-udon-pilgrimage":"toshikoshi-soba-newyear-tradition",
"japan-kanazawa-gold-leaf":"kanazawa-nagamachi-samurai",
"japan-kyoto-gion-festival-floats":"matsuri-hero",
"japan-nagasaki-lantern-festival":"tanabata-japanese-star-festival",
"japan-night-train-travel":"ekiben-train-hero",
"japan-niigata-rice-snow":"niigata-port-day-trip",
"japan-okinawan-bingata-textiles":"kimono-yukata-hero",
"japan-okinawan-eisa-dance":"okinawa-eisa-dance-festival",
"japan-public-parks-hanami":"hanami-japanese-cherry-blossom-picnic",
"japan-rail-pass-why-changes":"aomori-hakodate-seikan-tunnel",
"japan-railway-platform-melodies":"tokyo-yurikamome-automated-train",
"japan-railway-station-stamps":"ekiben-train-hero",
"japan-sakura-forecast-science":"hanami-japanese-cherry-blossom-picnic",
"japan-samurai-armor":"himeji-castle-defense-route",
"japan-sea-of-japan-coast":"akita-port-day-trip",
"japan-shotengai-neon-signs":"okinawa-shopping-street",
"japan-snow-country-architecture":"toyama-gokayama-ainokura",
"japan-snow-monkeys-hot-springs":"akita-nyuto-onsen-beech-forest",
"japan-station-bento-vending":"ekiben-train-hero",
"japan-stone-lanterns":"japanese-garden-stones-moss",
"japan-sudare-bamboo-blinds":"shoji-fusuma-japanese-doors",
"japan-temple-bells":"shrine-temple-hero",
"japan-terraced-rice-fields":"toyama-gokayama-ainokura",
"japan-traditional-roof-tiles":"kanazawa-nagamachi-samurai",
"japan-tram-streetcars-history":"tokyo-yurikamome-automated-train",
"japan-trash-bin-shortage":"noren-hero",
"japan-volcanic-onsen-geology":"beppu-port-onsen-day-trip",
"japan-volcano-mount-aso":"oita-kuju-highland-grassland",
"japan-yakushima-ancient-cedars":"nagano-kamikochi-azusa-river",
"japanese-engawa-veranda":"ryokan-japanese-inn-hospitality",
"japanese-ferries-islands-life":"shodoshima-ferry-island-access",
"japanese-hightech-public-toilets":"shoji-fusuma-japanese-doors",
"japanese-katana-curvature":"osaka-sakai-knife-workshops",
"japanese-local-train-one-man":"sagano-scenic-railway",
"japanese-machiya-townhouses":"kyoto-kiyomizu-stage-structure",
"japanese-pagoda-five-stories":"uji-byodoin-phoenix-hall",
"japanese-pottery-kilns":"kintsugi-hero",
"japanese-queue-culture":"tokyo-station-marunouchi-facade",
"japanese-ropeways-mountain-access":"hakone-tozan-switchback-train",
"japanese-sento-public-bath-manners":"beppu-port-onsen-day-trip",
"japanese-sword-guards-tsuba":"osaka-sakai-knife-workshops",
"japanese-train-manners-quiet-car":"sagano-scenic-railway",
"japanese-urushi-lacquerware":"kintsugi-hero",
"japanese-vending-machine-culture":"noren-hero",
"japanese-wind-chimes-furin":"noren-hero",
"japanese-woodblock-printmaking":"kintsugi-hero",
"kabuki-japanese-theater":"kimono-formal-detail",
"kissaten-japanese-retro-coffee":"izakaya-japanese-afterwork-culture",
"kodo-japanese-incense-appreciation":"tea-ceremony-hero",
"kokeshi-japanese-wooden-dolls":"maneki-neko-hero",
"konbini-japanese-convenience-store-life":"noren-hero",
"kumiko-japanese-wood-joinery":"shoji-fusuma-japanese-doors",
"kutani-japanese-porcelain":"kintsugi-hero",
"miso-japanese-fermented-soy":"ramen-japanese-noodle-evolution",
"noh-japanese-mask-theater":"kimono-formal-detail",
"obon-japanese-ancestors":"tanabata-japanese-star-festival",
"okonomiyaki-osaka-hiroshima":"osaka-central-public-hall",
"omikuji-japanese-fortune":"ema-japanese-wish-wooden-plaques",
"onigiri-japanese-rice-ball":"bento-japanese-lunchbox-everyday",
"origami-japanese-paper-folding-culture":"furoshiki-japanese-wrapping-cloth",
"rakugo-japanese-storytelling":"izakaya-japanese-afterwork-culture",
"regional-soba-japanese-buckwheat":"toshikoshi-soba-newyear-tradition",
"sashiko-japanese-repair-stitching":"furoshiki-japanese-wrapping-cloth",
"setsubun-japanese-beans":"osechi-ryori-japanese-new-year-food",
"shamisen-japanese-three-string-instrument":"matsuri-hero",
"shichi-go-san-japanese-children":"kimono-yukata-hero",
"shinkansen-bullet-train-history":"aomori-hakodate-seikan-tunnel",
"shotengai-japanese-shopping-arcades":"okinawa-shopping-street",
"sushi-edo-japanese-food-history":"kyoto-nishiki-market-food-culture",
"taiko-japanese-drumming":"okinawa-eisa-dance-festival",
"takoyaki-osaka-street-food":"osaka-central-public-hall",
"tanuki-japanese-shop-statues":"maneki-neko-hero",
"temari-japanese-thread-balls":"furoshiki-japanese-wrapping-cloth",
"tempura-japanese-fried-food":"kyoto-nishiki-market-food-culture",
"toji-yuzu-bath-japan":"beppu-port-onsen-day-trip",
"tsukimi-japanese-moon-viewing":"wagashi-japanese-seasonal-sweets",
"udon-japanese-regional-noodles":"toshikoshi-soba-newyear-tradition",
"ukiyoe-japanese-woodblock-art":"japanese-garden-hero",
"ume-japanese-plum-blossoms":"hanami-japanese-cherry-blossom-picnic",
"washi-japanese-handmade-paper":"fukui-echizen-washi-village",
"yakitori-japanese-skewer-culture":"izakaya-japanese-afterwork-culture",
"yatai-japanese-food-stalls":"izakaya-japanese-afterwork-culture",
"yukimi-japanese-snow-viewing-tradition":"akita-nyuto-onsen-beech-forest"
}
# Do not silently treat related images as original location or same species of plant/food.
for slug,subject in M.items():
 assert (ROOT/"things-to-do"/slug/"index.html").exists(),slug
 assert (ROOT/img(subject).lstrip("/")).exists(),subject
broken=[]
for f in sorted((ROOT/"things-to-do").glob("*/index.html")):
 s=f.read_text(encoding="utf8")
 im=re.findall(r'<img[^>]*src="(/images/editorial/[^"]+)"',s)
 for a in im:
  if not (ROOT/a.lstrip("/")).exists():broken.append((f.parent.name,a))
expected=set(k for k,_ in broken)
if expected!=set(M):
 raise RuntimeError("Missing or unexpected mappings: not mapped "+str(sorted(expected-set(M)))+
                    "; stale mappings "+str(sorted(set(M)-expected)))
manifest=[]
for slug,missing in broken:
 f=ROOT/"things-to-do"/slug/"index.html"
 s=f.read_text(encoding="utf8")
 replacement=img(M[slug])
 # Update hero, OG/twitter and schema references of same source.
 if s.count(missing)<1:raise RuntimeError("broken image no longer found: "+slug)
 old=s
 s=s.replace(missing,replacement)
 s=s.replace("https://www.nipponferry.com"+missing,"https://www.nipponferry.com"+replacement)
 # Avoid calling unrelated topical fallback an 'original' photograph of the named subject.
 def clean_alt(m):
  tag=m.group()
  return re.sub(r'alt="[^"]*"', 'alt="일본 문화·여행 주제를 설명하는 참고 이미지 (글에서 소개한 대상의 실제 촬영 사진은 아님)"',tag)
 s=re.sub(r'<img[^>]*\bsrc="'+re.escape(replacement)+r'"[^>]*>',clean_alt,s,count=1)
 if '<meta name="nf-topic-photo-note"' not in s:
  s=s.replace('</head>','<meta name="nf-topic-photo-note" content="대표 이미지는 주제 참고 자료로서 대상 시설·물품·공연의 실제 사진이 아닐 수 있습니다."></head>',1)
 f.write_text(s,encoding="utf8")
 manifest.append({"slug":slug,"before":missing,"after":replacement,"asset_kind":"existing related editorial reference, not exact subject photo"})
print("V31_FIXED_BROKEN",len(manifest))
Path("audit-reports/v31").mkdir(parents=True,exist_ok=True)
Path("audit-reports/v31/recovered-hero-images.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
