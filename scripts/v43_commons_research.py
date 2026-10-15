#!/usr/bin/env python3
"""V41 investigate Wikimedia Commons candidate images; no edits before editorial review."""
from __future__ import annotations
import html,json,re,time,urllib.parse,urllib.request
from pathlib import Path
DEST=Path("docs/v43-commons-candidates.json")
TOPICS={
  "omamori-japanese-amulet-culture": [
    "Omamori Shinto amulet Japan",
    "Omamori Japanese shrine charms",
    "Omamori charm Japanese temple"
  ],
  "ema-japanese-wish-wooden-plaques": [
    "Ema Japanese shrine prayer wooden plaques",
    "Ema wish plaques Japan shrine",
    "Ema Shinto wooden tablets"
  ],
  "goshuin-temple-shrine-stamps": [
    "Goshuin Japanese stamp book",
    "Goshuin cho Japan temple stamp",
    "Goshuin Japanese calligraphy shrine"
  ],
  "ryokan-japanese-inn-hospitality": [
    "Traditional Japanese ryokan tatami room",
    "Kyoto ryokan Japanese-style room",
    "Ryokan guest room Japan"
  ],
  "tatami-floor-japanese-living": [
    "Tatami mats Japanese room",
    "Japanese tatami floor woven straw",
    "Tatami mats traditional Japanese room"
  ],
  "futon-japanese-bedding-culture": [
    "Japanese futon bedding tatami room",
    "Japanese futon bedding on tatami",
    "Shikibuton futon Japan room"
  ],
  "shoji-fusuma-japanese-doors": [
    "Shoji sliding doors Japan house",
    "Japanese fusuma sliding door traditional house",
    "Shoji paper doors Japan interior"
  ],
  "kotatsu-japanese-winter-table": [
    "Japanese kotatsu heated table room",
    "Kotatsu Japanese winter table",
    "Kotatsu futon Japanese heated table"
  ],
  "furoshiki-japanese-wrapping-cloth": [
    "Furoshiki cloth wrapping Japanese",
    "Furoshiki wrapped gift Japanese cloth",
    "Japanese furoshiki wrapping cloth"
  ],
  "bento-japanese-lunchbox-everyday": [
    "Japanese bento lunch box Japan",
    "Bento Japanese lunchbox rice vegetables",
    "Japanese bento box homemade"
  ],
  "wagashi-japanese-seasonal-sweets": [
    "Wagashi traditional Japanese sweets seasonal",
    "Wagashi Japanese sweets nerikiri",
    "Traditional wagashi Japanese pastry"
  ],
  "matcha-sencha-japanese-green-tea": [
    "Matcha tea bowl powder whisk Japan",
    "Sencha green tea Japanese teapot",
    "Japanese matcha sencha tea"
  ],
  "toshikoshi-soba-newyear-tradition": [
    "Toshikoshi soba new year Japan",
    "Japanese soba noodles bowl year end",
    "Soba noodles Japan meal"
  ],
  "ramen-japanese-noodle-evolution": [
    "Japanese ramen noodles bowl Japan",
    "Tonkotsu ramen Japan",
    "Japanese ramen noodle shop bowl"
  ],
  "izakaya-japanese-afterwork-culture": [
    "Izakaya Japanese restaurant interior",
    "Japanese izakaya food dishes",
    "Izakaya drinking dining Japan"
  ],
  "osechi-ryori-japanese-new-year-food": [
    "Osechi ryori Japanese new year bento boxes",
    "Osechi jubako Japan food",
    "Japanese osechi food New Year"
  ],
  "hanami-japanese-cherry-blossom-picnic": [
    "Hanami picnic Japan cherry blossoms people",
    "Ueno Park hanami picnic Japan",
    "Hanami Japanese cherry blossom picnic"
  ],
  "momijigari-japanese-autumn-leaves-culture": [
    "Kyoto autumn momiji temple Japan",
    "Momijigari Japanese autumn leaves viewing",
    "Japan Kyoto fall maple leaves"
  ],
  "koinobori-childrens-day-japan": [
    "Koinobori carp streamers Japan children's day",
    "Japanese Koinobori carp windsocks river",
    "Koinobori carp flags Japan"
  ],
  "tanabata-japanese-star-festival": [
    "Tanabata festival Japan bamboo wishes",
    "Sendai Tanabata festival streamers",
    "Tanabata Japanese star festival decorations"
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

from concurrent.futures import ThreadPoolExecutor,as_completed
report={slug:{"candidate_count":0,"options":[],"errors":[]} for slug in TOPICS}
def task(slug,query):
    for i in range(3):
        try: return slug,query,fetch(query),None
        except Exception as exc:
            error=str(exc)[:170]
            time.sleep(1+2*i)
    return slug,query,[],error
tasks=[(slug,q) for slug,queries in TOPICS.items() for q in queries]
with ThreadPoolExecutor(max_workers=6) as ex:
    futs=[ex.submit(task,slug,q) for slug,q in tasks]
    for fut in as_completed(futs):
        slug,q,pics,error=fut.result()
        row=report[slug]
        if error:row["errors"].append(q+" :: "+error)
        else:
            seen={x["filename"] for x in row["options"]}
            for p in pics:
                if p["filename"] not in seen:
                    p["query"]=q
                    row["options"].append(p)
                    seen.add(p["filename"])
        print(slug,q,len(pics),flush=True)
for slug,row in report.items():
    row["candidate_count"]=len(row["options"])
    row["options"]=row["options"][:24]
DEST.parent.mkdir(parents=True,exist_ok=True)
DEST.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("V43 candidate report",len(report),sum(bool(r["options"]) for r in report.values()),flush=True)
