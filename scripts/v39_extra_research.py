#!/usr/bin/env python3
"""V39 investigate Wikimedia Commons candidate images; no edits before editorial review."""
from __future__ import annotations
import html,json,re,time,urllib.parse,urllib.request
from pathlib import Path
DEST=Path("docs/v39-extra-research.json")
TOPICS={
  "japan-small-streets": [
    "Pontocho alley Kyoto street Japan",
    "Kyoto alley Gion narrow lane"
  ],
  "ume-japanese-plum-blossoms": [
    "Ume blossoms Kairakuen Mito Japan",
    "Japanese plum blossoms white ume Kyoto"
  ],
  "japan-forest-bathing-shinrin-yoku": [
    "Shiratani Unsuikyo moss forest path Yakushima",
    "Japan forest walking trail green"
  ],
  "setsubun-japanese-beans": [
    "Setsubun bean throwing Japan shrine",
    "Setsubun beans roasted soy mask oni"
  ],
  "why-japanese-onsen-special": [
    "Japanese rotenburo open air onsen Japan",
    "Japanese onsen bath hotel outdoors"
  ],
  "japan-konbini-culture": [
    "Japanese convenience store konbini shelves",
    "Lawson convenience store Japan outside"
  ],
  "ryokan-vs-hotel": [
    "Traditional Japanese ryokan tatami futon room",
    "Japanese ryokan inn interior"
  ],
  "tsukimi-japanese-moon-viewing": [
    "Tsukimi dango moon viewing Japan",
    "Japanese tsukimi festival dumplings"
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
