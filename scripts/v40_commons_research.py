#!/usr/bin/env python3
"""V40 investigate Wikimedia Commons candidate images; no edits before editorial review."""
from __future__ import annotations
import html,json,re,time,urllib.parse,urllib.request
from pathlib import Path
DEST=Path("docs/v40-commons-research.json")
TOPICS={
  "onsen-first-time": [
    "Japanese onsen bath rotenburo outdoor Japan",
    "onsen yukata bath ryokan Japan"
  ],
  "traditional-experience-booking": [
    "Japanese tea ceremony kimono participant",
    "Japanese tea ceremony Kyoto experience"
  ],
  "nature-outdoor-checklist": [
    "Japanese hiking trail mountain hikers",
    "mountain hike Kamikochi Japan"
  ],
  "shopping-city-night-guide": [
    "Dotonbori Osaka night shopping street",
    "Tokyo Shinjuku city neon night shopping"
  ],
  "port-to-experience-planner": [
    "Naha cruise terminal port passenger",
    "Yokohama Osanbashi cruise terminal passengers"
  ],
  "japan-four-shopping-experiences": [
    "Japanese shotengai arcade shopping shops",
    "Nishiki Market Kyoto retail shops"
  ],
  "japan-railway-platform-melodies": [
    "Japanese railway station platform trains Tokyo",
    "JR station platform departure melody speaker"
  ],
  "japan-rail-pass-why-changes": [
    "Japan Rail Pass ticket paper",
    "JR Pass Japan rail ticket"
  ],
  "japan-station-bento-vending": [
    "Ekiben station bento box Japan railway",
    "Ekiben vending machine Japan station"
  ],
  "japan-sea-of-japan-coast": [
    "Tojinbo waves winter Fukui Japan sea",
    "Noto peninsula winter waves sea of Japan"
  ],
  "japan-shotengai-neon-signs": [
    "Shinsaibashi shopping arcade sign Osaka night",
    "Tenjinbashisuji shotengai signs Osaka"
  ],
  "japan-sakura-forecast-science": [
    "Sakura cherry blossom blooming Japan close up",
    "Cherry blossom forecast Japan sakura"
  ],
  "kabuki-japanese-theater": [
    "Kabuki theatre actor kumadori stage Tokyo performance",
    "Kabuki makeup performer Japan"
  ],
  "rakugo-japanese-storytelling": [
    "Rakugo artist sitting zabuton on stage",
    "Rakugo storytelling yose performance"
  ],
  "aizome-japanese-indigo-dye": [
    "Aizome indigo dye Japan workshop",
    "Japanese indigo dyed cloth traditional"
  ],
  "kutani-japanese-porcelain": [
    "Kutani ware painted ceramics Japan plate",
    "Kutani-yaki porcelain museum Japan"
  ],
  "tanuki-japanese-shop-statues": [
    "Shigaraki tanuki ceramic pottery Japan",
    "Shigaraki ware tanuki statue street"
  ],
  "miso-japanese-fermented-soy": [
    "Japanese red white miso paste bowl",
    "Japan miso soybean fermented paste"
  ],
  "dashi-japanese-umami-stock": [
    "Japanese katsuobushi kombu dashi ingredients",
    "Bonito flakes kombu stock Japan food"
  ],
  "japanese-train-manners-quiet-car": [
    "Japanese train interior passengers quiet",
    "Tokyo Japanese subway train interior"
  ],
  "japanese-queue-culture": [
    "Japan passengers queue station platform line",
    "Tokyo queue waiting train people"
  ],
  "japan-trash-bin-shortage": [
    "Japanese public waste bin street",
    "Japan trash separation bins public"
  ],
  "japanese-sento-public-bath-manners": [
    "Sento Japanese public bathhouse interior wash area",
    "Japanese traditional sento bathhouse"
  ],
  "kissaten-japanese-retro-coffee": [
    "Tokyo kissaten coffee shop retro interior",
    "Traditional Japanese kissaten coffee cafe"
  ],
  "shichi-go-san-japanese-children": [
    "Shichi Go San kids kimono shrine Japan",
    "Shichigosan Japanese festival children shrine"
  ],
  "obon-japanese-ancestors": [
    "Bon Odori Japanese festival dancing people",
    "Obon lantern festival Japan ancestors"
  ],
  "toji-yuzu-bath-japan": [
    "Yuzuyu yuzu floating bath Japan solstice",
    "Yuzu citrus bath Japanese winter"
  ],
  "yukimi-japanese-snow-viewing-tradition": [
    "Japanese snow covered garden yukimi lantern",
    "Kenrokuen winter yukitsuri garden snow"
  ],
  "kodo-japanese-incense-appreciation": [
    "Japanese incense ceremony kodo incense utensils",
    "Japanese incense burner traditional kodo"
  ],
  "japan-forest-bathing-shinrin-yoku": [
    "Yakushima moss forest Japanese forest path",
    "Aokigahara hiking forest trail Japan"
  ],
  "japan-diving-first-time": [
    "Okinawa scuba diver coral underwater",
    "Ishigaki Japan scuba diving divers"
  ],
  "why-japanese-onsen-special": [
    "Japanese rotenburo open air bath scenic Japan",
    "Beppu traditional onsen outdoor"
  ],
  "japan-konbini-culture": [
    "Japanese convenience store onigiri shelves",
    "Japanese konbini shop exterior Japan"
  ],
  "ryokan-vs-hotel": [
    "Japanese ryokan tatami room futon traditional",
    "Ryokan traditional inn Japanese garden interior"
  ],
  "why-travel-japan-by-sea": [
    "Japan ferry ship deck port",
    "Ferry Shodoshima sea Japan passenger"
  ]
}
USER_AGENT="Nipponferry-editorial-research/1.0 (https://www.nipponferry.com/; Wikimedia licence verification)"
def fetch(q):
    params={"action":"query","generator":"search","gsrsearch":q,"gsrnamespace":6,"gsrlimit":10,
            "prop":"imageinfo","iiprop":"url|mime|size|extmetadata","iiurlwidth":"1200","format":"json","formatversion":2}
    url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(params)
    req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=50) as r:
       j=json.load(r)
    if "error" in j:raise RuntimeError(str(j["error"])[:160])
    candidates=[]
    for page in j.get("query",{}).get("pages",[]):
        if page.get("missing") or not page.get("imageinfo"):continue
        img=page["imageinfo"][0]
        if img.get("mime") not in ("image/jpeg","image/png","image/webp"):continue
        if img.get("width",0)<500 or img.get("height",0)<370:continue
        meta=img.get("extmetadata",{})
        get=lambda k:html.unescape(re.sub("<[^>]*>"," ",meta.get(k,{}).get("value",""))).strip()
        code=get("LicenseShortName")
        if not (code.startswith("CC BY") or code in ("CC0","Public domain","PD","CC0 1.0") or "Public Domain" in code):
            continue
        title=page["title"].replace("File:","")
        candidates.append({
          "filename":title,"author":get("Artist")[:350],"description":get("ImageDescription")[:850],
          "credit":get("Credit")[:200],"licence":code,"licence_url":get("LicenseUrl"),
          "source_page":"https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(title.replace(" ","_")),
          "remote":img.get("thumburl",img.get("url")),"width":img.get("width"),"height":img.get("height")
        })
    return candidates
report={}
for slug,queries in TOPICS.items():
    options=[]
    errors=[]
    for query in queries:
        for attempt in range(2):
            try:
                c=fetch(query)
                for v in c:
                    if v["filename"] not in [o["filename"] for o in options]:
                        v["query"]=query
                        options.append(v)
                break
            except Exception as e:
                errors.append(f"{query}: {e}")
                time.sleep(3*(attempt+1))
        time.sleep(0.4)
    report[slug]={"candidate_count":len(options),"options":options[:14],"errors":errors}
    print(slug,len(options),"errors",len(errors),flush=True)
DEST.parent.mkdir(parents=True,exist_ok=True)
DEST.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("Wrote",DEST,"targets",len(report))
