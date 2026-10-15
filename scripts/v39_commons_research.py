#!/usr/bin/env python3
"""V39 investigate Wikimedia Commons candidate images; no edits before editorial review."""
from __future__ import annotations
import html,json,re,time,urllib.parse,urllib.request
from pathlib import Path
DEST=Path("docs/v39-commons-research.json")
TOPICS={
  "japan-sea-of-japan-coast": [
    "Tojinbo winter sea waves Japan Fukui",
    "Sea of Japan winter waves Niigata"
  ],
  "japanese-machiya-townhouses": [
    "Kyoto machiya townhouse facade",
    "Kyoto traditional machiya townhouses"
  ],
  "japan-shotengai-neon-signs": [
    "Osaka shotengai neon sign shopping street",
    "Japan shotengai shopping arcade signage"
  ],
  "japan-ainu-embroidery": [
    "Ainu embroidered robe Japan",
    "Ainu embroidery traditional textile"
  ],
  "japan-amami-oshima-tsumugi": [
    "Oshima tsumugi kimono silk weaving",
    "Amami Oshima tsumugi textile"
  ],
  "kabuki-japanese-theater": [
    "Kabuki actor kumadori makeup",
    "Kabuki theatre performance Japan"
  ],
  "noh-japanese-mask-theater": [
    "Noh theatre mask performer Japan",
    "Noh masks museum"
  ],
  "bunraku-japanese-puppet-theater": [
    "Bunraku puppet Japanese theatre",
    "Bunraku Osaka Japanese puppetry"
  ],
  "rakugo-japanese-storytelling": [
    "Rakugo storyteller performance",
    "Rakugo yose Japanese storytelling"
  ],
  "shamisen-japanese-three-string-instrument": [
    "Shamisen Japanese musical instrument",
    "Shamisen Japanese traditional player"
  ],
  "ukiyoe-japanese-woodblock-art": [
    "Ukiyo e Japanese woodblock printing art",
    "Ukiyoe woodblock print exhibit museum"
  ],
  "aizome-japanese-indigo-dye": [
    "Aizome Japanese indigo dyeing fabric",
    "Japan aizome indigo vat textile"
  ],
  "kutani-japanese-porcelain": [
    "Kutani ware porcelain colorful plate",
    "Kutaniyaki ceramic Japanese museum"
  ],
  "temari-japanese-thread-balls": [
    "Japanese temari thread ball craft",
    "Temari traditional Japanese thread balls"
  ],
  "sashiko-japanese-repair-stitching": [
    "Japanese sashiko stitching textile",
    "Sashiko embroidery Japanese stitches"
  ],
  "tanuki-japanese-shop-statues": [
    "Shigaraki tanuki pottery statue",
    "Japanese tanuki statue ceramic shop"
  ],
  "udon-japanese-regional-noodles": [
    "Udon noodles bowl Japanese",
    "Sanuki udon Kagawa bowl"
  ],
  "yakitori-japanese-skewer-culture": [
    "Yakitori grilled skewers Japan food",
    "Yakitori charcoal restaurant skewers"
  ],
  "miso-japanese-fermented-soy": [
    "Japanese miso paste red white",
    "Miso fermentation Japanese barrels"
  ],
  "dashi-japanese-umami-stock": [
    "Dashi kombu bonito flakes Japan",
    "Dashi broth dried bonito kombu"
  ],
  "onigiri-japanese-rice-ball": [
    "Japanese onigiri rice ball triangular",
    "Onigiri nori Japan rice"
  ],
  "konbini-japanese-convenience-store-life": [
    "Japanese konbini convenience store interior",
    "Japan convenience store food shelves"
  ],
  "japanese-sento-public-bath-manners": [
    "Japanese sento public bath inside",
    "Sento bathhouse wash area Japan"
  ],
  "japanese-hightech-public-toilets": [
    "Japanese washlet bidet toilet control panel",
    "Japan high tech public toilet bidet"
  ],
  "kissaten-japanese-retro-coffee": [
    "Japanese kissaten retro coffee shop",
    "Kissaten cafe Tokyo interior"
  ],
  "yatai-japanese-food-stalls": [
    "Fukuoka yatai food stalls nighttime",
    "Japanese yatai street food stalls"
  ],
  "omikuji-japanese-fortune": [
    "Omikuji paper fortunes Japanese shrine",
    "Omikuji paper fortune tied Japan"
  ],
  "japan-diving-first-time": [
    "Okinawa scuba diving underwater Japan",
    "Ishigaki scuba diving"
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
