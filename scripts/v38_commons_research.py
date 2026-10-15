#!/usr/bin/env python3
"""V38 investigate Wikimedia Commons candidate images; no edits before editorial review."""
from __future__ import annotations
import html,json,re,time,urllib.parse,urllib.request
from pathlib import Path
DEST=Path("docs/v38-commons-research.json")
TOPICS={
  "japan-castle-moats": [
    "Matsumoto Castle moat water Japan",
    "Himeji castle moat water"
  ],
  "japanese-pagoda-five-stories": [
    "Toji five story pagoda Kyoto",
    "Five-story pagoda Sensoji Asakusa"
  ],
  "japan-samurai-armor": [
    "Japanese samurai armor museum display",
    "Samurai armor Japan historical kabuto"
  ],
  "japanese-katana-curvature": [
    "Japanese katana sword blade curved museum",
    "Katana curved sword full length"
  ],
  "japanese-sword-guards-tsuba": [
    "Japanese sword tsuba handguard museum",
    "Tsuba Japanese sword guard"
  ],
  "japan-traditional-roof-tiles": [
    "Onigawara Japanese roof tile",
    "Onigawara demon roof tile temple"
  ],
  "japanese-engawa-veranda": [
    "Engawa Japanese veranda traditional house",
    "Japanese engawa porch garden"
  ],
  "japanese-local-train-one-man": [
    "One man operation Japanese train",
    "Japanese local one man train"
  ],
  "japanese-ferries-islands-life": [
    "Shodoshima ferry Japan",
    "Japanese island ferry Setouchi"
  ],
  "japanese-ropeways-mountain-access": [
    "Hakone Ropeway gondola mount fuji",
    "Mt Rokko ropeway Japan"
  ],
  "japan-tram-streetcars-history": [
    "Hiroshima streetcar tram Japan",
    "Nagasaki electric tram"
  ],
  "japan-railway-station-stamps": [
    "Ekistamp Japan station stamp",
    "Japanese railway station stamp collection"
  ],
  "japan-geothermal-steam-hells": [
    "Beppu Umi Jigoku hot spring",
    "Beppu Kamado Jigoku steam"
  ],
  "japan-terraced-rice-fields": [
    "Shiroyone Senmaida terraces Noto Japan",
    "Oyama Senmaida rice terrace Japan"
  ],
  "japan-yakushima-ancient-cedars": [
    "Jomon Sugi 01.jpg",
    "Jomon Sugi Yakushima ancient cedar"
  ],
  "japan-snow-country-architecture": [
    "Shirakawa go Gassho zukuri winter steep roof",
    "Gokayama snow gassho houses"
  ],
  "japan-ajisai-hydrangea-season": [
    "Meigetsuin hydrangea Kamakura Japan",
    "Japanese ajisai hydrangea season"
  ],
  "japan-stone-lanterns": [
    "Japanese garden stone lantern Kyoto",
    "Ishidoro stone lantern garden"
  ],
  "japanese-wind-chimes-furin": [
    "Wind chimes, Tokyo.jpg",
    "Fuurin.jpg"
  ],
  "japan-kagawa-udon-pilgrimage": [
    "Sanuki udon Kagawa Japan bowl",
    "Kagawa udon restaurant noodles"
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
