#!/usr/bin/env python3
"""V41 investigate Wikimedia Commons candidate images; no edits before editorial review."""
from __future__ import annotations
import html,json,re,time,urllib.parse,urllib.request
from pathlib import Path
DEST=Path("docs/v41-commons-research.json")
TOPICS={
  "traditional-experience-booking": [
    "Japanese tea ceremony Kyoto participant",
    "Japanese tea ceremony matcha whisk photograph",
    "茶道 体験 京都"
  ],
  "japan-railway-platform-melodies": [
    "Japanese railway platform speaker departure melody",
    "Hassha melody station Japan",
    "発車メロディー 駅 スピーカー"
  ],
  "japan-sea-of-japan-coast": [
    "Tojinbo cliffs rough sea waves Japan",
    "Japan Sea rough winter waves Kanazawa",
    "日本海 冬 荒波 東尋坊"
  ],
  "kabuki-japanese-theater": [
    "Kabuki actor kumadori makeup",
    "Kabuki actor Shibaraku photo",
    "歌舞伎 隈取 役者"
  ],
  "rakugo-japanese-storytelling": [
    "Rakugo storyteller performance zabuton",
    "Japanese rakugo performer sitting stage",
    "落語家 高座 座布団"
  ],
  "aizome-japanese-indigo-dye": [
    "aizome Japanese indigo dyed textile",
    "Japanese indigo dyeing crafts blue fabric",
    "藍染め 藍染 布"
  ],
  "kutani-japanese-porcelain": [
    "Kutani ware pottery colorful plate Japan",
    "Kutani yaki porcelain museum decorated",
    "九谷焼 色絵 皿"
  ],
  "dashi-japanese-umami-stock": [
    "Japanese dashi katsuobushi kombu dried ingredients",
    "Japanese soup stock kombu bonito flakes",
    "昆布 鰹節 だし"
  ],
  "japan-trash-bin-shortage": [
    "Tokyo trash bin station sorting Japan",
    "Japanese recycling bins vending machines",
    "日本 ゴミ箱 分別 駅"
  ],
  "japanese-sento-public-bath-manners": [
    "Japanese sento indoor public bath washing stools",
    "sento public bath washing area Japan",
    "銭湯 洗い場 脱衣場"
  ],
  "kissaten-japanese-retro-coffee": [
    "Kissaten Japan retro coffee shop interior",
    "Japanese kissaten classic coffee cup",
    "喫茶店 レトロ 店内 珈琲"
  ],
  "toji-yuzu-bath-japan": [
    "yuzu citrus bath winter Japan",
    "Japanese yuzuyu bath yuzu floating",
    "柚子湯 浴槽 柚子"
  ],
  "japan-forest-bathing-shinrin-yoku": [
    "Shiratani Unsuikyo Yakushima moss forest trail",
    "Yakushima moss forest walking",
    "白谷雲水峡 苔 森"
  ],
  "japan-diving-first-time": [
    "Okinawa scuba diving Japan diver coral",
    "Ishigaki scuba diving underwater coral",
    "沖縄 ダイビング 海中"
  ],
  "why-japanese-onsen-special": [
    "Rotenburo Takanoyu Onsen Japan",
    "Beppu open air hot spring baths Japan",
    "露天風呂 温泉 景色"
  ],
  "family-with-kids": [
    "Tokyo Disneyland park attractions family Japan",
    "Japan aquarium families children",
    "日本 水族館 子供 家族"
  ],
  "solo-cultural-day": [
    "Kyoto Japanese tea ceremony visitor",
    "Japanese museum exhibit traditional culture",
    "京都 伝統 体験 文化"
  ],
  "japan-free-low-budget": [
    "Tokyo Ueno park Japan free cherry blossoms",
    "Japanese public parks Kyoto gardens free",
    "東京 上野公園 散歩"
  ],
  "accessible-slow-travel": [
    "Japan accessible travel wheelchair garden path",
    "Japanese elderly tourists garden walkway",
    "日本 バリアフリー 観光"
  ],
  "experience-booking-checklist": [
    "Japanese traditional pottery workshop experience",
    "Japanese tea ceremony hands bowl tea",
    "日本 体験予約 茶道"
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
