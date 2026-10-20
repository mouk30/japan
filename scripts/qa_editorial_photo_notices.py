#!/usr/bin/env python3
"""Guard 19 corrected misleading photo notices across 85 deployed editorial guides.

An existing AI reference image must never be accompanied by copy saying
no image has been published. This does NOT establish image location accuracy.
"""
import argparse, concurrent.futures, json, re, sys, time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL="https://www.nipponferry.com"
MANIFEST=Path("scripts/postdeploy-editorial-manifest.json")
OLD="이미지가 실제 생성·검수되어 등록되기 전까지는 사진을 게시하지 않습니다."
NEW="현재 대표 이미지는 실제 현장 촬영 사진이 아닌 AI 생성 여행 참고 이미지입니다."
FIXED=set((
"aizu-wakamatsu-tsurugajo","akita-kakunodate-bukeyashiki",
"gifu-shirakawago-gassho-roof","hakodate-goryokaku-fort",
"himeji-castle-defense-route","iwami-ginzan-silver-mine",
"kanazawa-nagamachi-samurai","kobe-kitano-ijinkan-houses",
"kumamoto-castle-restoration","kyoto-kiyomizu-stage-structure",
"matsumoto-castle-black-walls","nagasaki-dejima-island-trade",
"nagasaki-glover-garden","nara-heijokyo-palace",
"osaka-central-public-hall","tokyo-station-marunouchi-facade",
"tomonoura-setouchi-port","toyama-gokayama-ainokura",
"uji-byodoin-phoenix-hall",
))
class Scan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1=0;self.canonicals=[];self.photos=[];self.captions=[];self._cap=False;self._words=[]
    def handle_starttag(self, tag,attrs):
        a=dict(attrs)
        if tag=="h1":self.h1+=1
        if tag=="link" and "canonical" in a.get("rel",""):self.canonicals.append(a.get("href",""))
        if tag=="img":self.photos.append({"src":a.get("src",""),"alt":a.get("alt","")})
        if tag=="figcaption":self._cap=True;self._words=[]
    def handle_data(self,text):
        if self._cap:self._words.append(text)
    def handle_endtag(self,tag):
        if tag=="figcaption" and self._cap:
            self.captions.append("".join(self._words));self._cap=False

def read_page(filename, mode,root):
    path="/"+filename.removeprefix("site/").removesuffix("index.html")
    if mode=="static":return (root/filename.removeprefix("site/")).read_text(encoding="utf-8")
    url=BASE_URL+path
    req=Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; NipponFerry-PhotoNoticeQA/1.0)"})
    last=None
    for attempt in range(2):
        try:
            with urlopen(req,timeout=15) as resp:
                if resp.status != 200 or "html" not in resp.headers.get("Content-Type","").lower():
                    raise ValueError("Bad public response "+str(resp.status))
                if resp.geturl().rstrip("/")!=url.rstrip("/"):
                    raise ValueError("Unexpected redirect")
                return resp.read().decode("utf-8","replace")
        except (HTTPError,URLError,TimeoutError,ValueError) as error:
            last=error
            if attempt==0:time.sleep(.5)
    raise RuntimeError(str(last))

def audit(filename,mode,root):
    slug=filename.split("/")[2]
    result={"slug":slug,"corrected":slug in FIXED,"checks":{},"errors":[]}
    try:
        html=read_page(filename,mode,root)
        p=Scan();p.feed(html)
        url=BASE_URL+"/things-to-do/"+slug+"/"
        ck=result["checks"]
        ck["one_h1"]=p.h1==1
        ck["canonical_exact"]=p.canonicals==[url]
        ck["has_article_image"]=bool(p.photos) and any(photo["src"].startswith("/") for photo in p.photos)
        ck["no_published_image_contradiction"]=OLD not in html
        if slug in FIXED:
            ck["accurate_AI_reference_note"]=NEW in html
            ck["image_alt_AI_reference"]=any("AI 생성" in p["alt"] for p in p.photos)
            ck["image_caption_AI_disclosure"]=any("AI 생성" in cap for cap in p.captions)
    except Exception as e:result["errors"].append(str(e))
    result["pass"]=bool(result["checks"]) and all(result["checks"].values()) and not result["errors"]
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=["static","live"],required=True)
    parser.add_argument("--root",default="dist")
    args=parser.parse_args()
    paths=json.loads(MANIFEST.read_text(encoding="utf-8"))["pages"]
    if len(paths)!=85 or len(FIXED)!=19:raise SystemExit("Manifest/target list invariant failed")
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results=list(pool.map(lambda f:audit(f,args.mode,Path(args.root)),paths))
    failures=[r for r in results if not r["pass"]]
    report={
      "checked_at_utc":datetime.now(timezone.utc).isoformat(),
      "mode":args.mode,"total":len(results),"passed":len(results)-len(failures),
      "corrected_count":sum(x["corrected"] for x in results),"failures":failures,
      "scope":"Visible image and statement consistency, not photo rights or authenticity",
    }
    out=Path("audit-output/editorial-photo-notices");out.mkdir(parents=True,exist_ok=True)
    (out/(args.mode+"-result.json")).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("SUMMARY",json.dumps({k:report[k] for k in ("mode","total","passed","corrected_count")}))
    for x in failures[:12]:
        print("FAIL",x["slug"],[k for k,v in x["checks"].items() if not v],x["errors"])
    if failures:raise SystemExit(1)

if __name__=="__main__":main()
