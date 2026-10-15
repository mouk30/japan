#!/usr/bin/env python3
"""V37 investigate Wikimedia Commons candidate images; no edits before editorial review."""
from __future__ import annotations
import html,json,re,time,urllib.parse,urllib.request
from pathlib import Path
DEST=Path("docs/v37-commons-research.json")
TOPICS={
"local-food-market-guide":["Nishiki market food Kyoto","Japanese market food stalls"],
"japan-castle-stone-walls":["Himeji Castle stone walls","Japan castle stone masonry"],
"japan-castle-tenshu-towers":["Himeji Castle keep","Japanese castle tenshu"],
"japan-temple-bells":["RyoanJi-Kane.jpg","Bonsho temple bell Japan"],
"japan-night-train-travel":["Sunrise Izumo sleeper train","Sunrise Seto train Japan"],
"japan-volcanic-onsen-geology":["Beppu geothermal steam","Beppu Jigoku hot spring"],
"japan-izakaya-yokocho-alleys":["Omoide Yokocho Tokyo","Shinjuku yokocho alley"],
"japan-public-parks-hanami":["Hanami Ueno Park Tokyo","Hanami cherry blossom park Japan"],
"japan-kanazawa-gold-leaf":["Kanazawa Gold Factory.jpg","Kanazawa gold leaf craft"],
"japan-niigata-rice-snow":["Niigata rice paddy","Niigata rice fields"],
"japan-nagasaki-lantern-festival":["Lanterns in Nagasaki.jpg","Nagasaki Lantern Festival"],
"washi-japanese-handmade-paper":["Washi papermaking Japan","Echizen washi making"],
"sushi-edo-japanese-food-history":["Nigiri sushi","Edomae sushi"],
"tempura-japanese-fried-food":["Japanese tempura","Tempura shrimp Japan"],
"regional-soba-japanese-buckwheat":["Zaru soba","Japanese soba noodles"],
"okonomiyaki-osaka-hiroshima":["Okonomiyaki osaka.jpg","Osaka okonomiyaki food"],
"takoyaki-osaka-street-food":["Takoyaki in Osaka.jpg","Osaka takoyaki food"],
"depachika-japanese-department-food":["Depachika Japan food hall","Japanese department store basement food"],
"hanabi-japanese-fireworks-summer":["Sumida River fireworks","Japanese hanabi festival fireworks"],
"hatsumode-japanese-first-shrine-visit":["Hatsumode Meiji shrine","Hatsumode Japanese shrine"],
"tsushima-kasumaki":["かすまき","kasumaki Tsushima sweets"],
"tsushima-taiyaki":["Sakanotaiyaki.jpg"],
"tsushima-market":["Izuhara Tsushima shopping street","Tsushima Nagasaki fish market"],
"tsushima-rokubee":["rokubee Tsushima","対馬 ろくべえ"]
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
