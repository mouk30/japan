#!/usr/bin/env python3
"""V41 investigate Wikimedia Commons candidate images; no edits before editorial review."""
from __future__ import annotations
import html,json,re,time,urllib.parse,urllib.request
from pathlib import Path
DEST=Path("docs/v41-broad-commons-research.json")
TOPICS={
  "traditional-experience-booking": [
    "tea ceremony",
    "kimono dressing",
    "pottery workshop Japan"
  ],
  "japan-railway-platform-melodies": [
    "Japanese railway station platform",
    "Japan station speaker",
    "departure melody"
  ],
  "japan-sea-of-japan-coast": [
    "Tojinbo",
    "Japan Sea waves",
    "Tojinbo cliff"
  ],
  "kabuki-japanese-theater": [
    "kabuki makeup",
    "Kabuki",
    "Kabuki performance"
  ],
  "rakugo-japanese-storytelling": [
    "Rakugo",
    "Rakugo performer",
    "Rakugo yose"
  ],
  "aizome-japanese-indigo-dye": [
    "Aizome",
    "indigo dye Japan",
    "indigo textile Japan"
  ],
  "kutani-japanese-porcelain": [
    "Kutani ware",
    "Kutani pottery",
    "Kutani"
  ],
  "dashi-japanese-umami-stock": [
    "kombu",
    "katsuobushi",
    "dashi"
  ],
  "japan-trash-bin-shortage": [
    "trash cans Japan",
    "Japanese recycle bin",
    "Tokyo garbage bin"
  ],
  "japanese-sento-public-bath-manners": [
    "sento",
    "Japanese public bath",
    "sentō"
  ],
  "kissaten-japanese-retro-coffee": [
    "kissaten",
    "Japanese coffee shop",
    "Japanese cafe interior"
  ],
  "toji-yuzu-bath-japan": [
    "yuzu bath",
    "yuzuyu",
    "柚子湯"
  ],
  "japan-forest-bathing-shinrin-yoku": [
    "Yakushima forest",
    "Kumano Kodo forest",
    "Shiratani Unsuikyo"
  ],
  "japan-diving-first-time": [
    "diving Okinawa",
    "scuba diver Japan",
    "Ishigaki scuba"
  ],
  "why-japanese-onsen-special": [
    "onsen rotenburo",
    "Beppu onsen",
    "Kusatsu onsen"
  ],
  "family-with-kids": [
    "Japan aquarium children",
    "Tokyo Disneyland",
    "Japanese zoo family"
  ],
  "solo-cultural-day": [
    "Japanese tea ceremony",
    "Kyoto temple garden",
    "Japanese Museum Kyoto"
  ],
  "japan-free-low-budget": [
    "Ueno Park Tokyo",
    "Sumida park Tokyo",
    "Yoyogi park Japan"
  ],
  "accessible-slow-travel": [
    "Japanese accessible ramp",
    "wheelchair friendly Japan station",
    "Japanese park accessible pathway"
  ],
  "experience-booking-checklist": [
    "tea ceremony Japan",
    "pottery making Japan",
    "Japanese cultural workshop"
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
print("V41 candidate report",len(report),sum(bool(r["options"]) for r in report.values()),flush=True)
