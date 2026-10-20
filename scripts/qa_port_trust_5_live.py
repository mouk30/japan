#!/usr/bin/env python3
"""Check content that users ACTUALLY receive from 5 public priority port URLs.

Independent of the source tree: verifies release fixes on the live domain. This
does not prove live berth assignments, business hours, photo rights or bookings.
"""
import argparse
import json
import re
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ORIGIN="https://www.nipponferry.com"
PORTS={
    "naha-cruise-terminal-kokusai-dori": {
        "official": "https://nahaport.jp/english/introduction/cruise_promotion/",
        "required": ["관리조합 사무소", "실제 접안 선석"],
        "forbidden": ["나하 크루즈터미널의 주소를 나하시 돈도초 2-1로 안내합니다"],
        "image_kind": "ai",
    },
    "ishigaki-cruise-kabira-bay-bus-taxi": {
        "official": "https://www.city.ishigaki.okinawa.jp/soshiki/kowan/kuruzusenn/370.html",
        "required": ["무료 셔틀은 확정 교통편이 아닙니다", "도보 약 40~50분"],
        "forbidden": [],
        "image_kind": "real",
    },
    "hakata-port-hakata-station-access": {
        "official": "https://hakataport.com/center/",
        "required": ["국제여객터미널", "추가 도보 약 500m"],
        "forbidden": [],
        "image_kind": "ai",
    },
    "nagasaki-matsugae-glover-garden-cruise-access": {
        "official": "https://www.discover-nagasaki.com/en/transit/100790",
        "required": ["실제 접안 부두부터 확인", "미나미야마테"],
        "forbidden": [],
        "image_kind": "real",
    },
    "yokohama-red-brick-warehouse": {
        "official": "https://www.city.yokohama.lg.jp/lang/overseas/port/cruise/terminal_info.html",
        "required": ["오산바시·신코·다이코쿠", "현재 게시된 이미지는 AI 생성"],
        "forbidden": ["이미지가 실제 생성·검수되어 등록되기 전까지는 사진을 게시하지 않습니다"],
        "image_kind": "ai",
    },
}
USER_AGENT="Mozilla/5.0 (compatible; NipponFerry-PortTrustLiveQA/1.0)"

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headings=0;self.canonicals=[];self.links=[];self.img=[]
        self.figcaptions=[];self._cap=False;self._current=[]
        self.robots=[];self.jsonld=0;self._injson=False;self._json=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="h1":self.headings+=1
        if tag=="link" and "canonical" in a.get("rel",""):self.canonicals.append(a.get("href"))
        if tag=="a":self.links.append(a.get("href",""))
        if tag=="img":self.img.append(a)
        if tag=="meta" and a.get("name","").lower()=="robots":self.robots.append(a.get("content","").lower())
        if tag=="figcaption":self._cap=True;self._current=[]
        if tag=="script" and a.get("type")=="application/ld+json":self._injson=True;self._json=[]
    def handle_data(self,s):
        if self._cap:self._current.append(s)
        if self._injson:self._json.append(s)
    def handle_endtag(self,tag):
        if tag=="figcaption" and self._cap:
            self.figcaptions.append("".join(self._current))
            self._cap=False
        if tag=="script" and self._injson:
            try:json.loads("".join(self._json));self.jsonld+=1
            except ValueError:pass
            self._injson=False

def fetch(url):
    last=None
    for attempt in range(2):
        try:
            with urlopen(Request(url,headers={"User-Agent":USER_AGENT}),timeout=20) as r:
                return r.status,r.geturl(),r.headers.get("content-type",""),r.read()
        except (HTTPError,URLError,TimeoutError,ValueError) as exc:
            last=exc
            if attempt==0:time.sleep(.6)
    raise RuntimeError(str(last))

def audit(slug,expected,mode,root):
    url=ORIGIN+"/things-to-do/"+slug+"/"
    checks={};data={"slug":slug,"url":url,"checks":checks,"errors":[]}
    try:
        if mode=="live":
            status,final,ctype,bytes_=fetch(url)
            checks["http_200"]=status==200
            checks["url_correct"]=final.rstrip("/")==url.rstrip("/")
            checks["html_content_type"]="html" in ctype
        else:
            bytes_=(root/"things-to-do"/slug/"index.html").read_bytes()
        text=bytes_.decode("utf-8","replace")
        p=Page();p.feed(text)
        checks["single_H1"]=p.headings==1
        checks["canonical_exact"]=p.canonicals==[url]
        checks["indexable_meta"]=all("noindex" not in x for x in p.robots)
        checks["valid_json_ld"]=p.jsonld>=1
        checks["official_source_href"]=expected["official"] in p.links
        checks["booking_guide_href"]="/booking/japan-cruise/" in p.links
        checks["verified_section_once"]=text.count('id="nf-official-facts-20261020"')==1
        checks["corrections_present"]=all(x in text for x in expected["required"])
        checks["old_errors_removed"]=all(x not in text for x in expected["forbidden"])
        hero=next((x for x in p.img if x.get("src","").startswith("/") and
                    not x.get("src","").endswith(("/mascot.png","/kakao-talk.jpg"))),None)
        checks["editorial_image_present"]=bool(hero)
        if hero:
            path=hero["src"].split("?")[0]
            if mode=="live":
                try:
                    status2,final2,ctype2,blob=fetch(ORIGIN+path)
                    checks["editorial_image_live"]=status2==200 and ctype2.startswith("image/") and len(blob)>1000
                    data["image_bytes"]=len(blob)
                except Exception as error:
                    checks["editorial_image_live"]=False
                    data["errors"].append("Image: "+str(error))
            else:
                checks["editorial_image_in_build"]=(root/path.lstrip("/")).is_file()
            data["image"]=path
        if expected["image_kind"]=="real":
            # In the main article's real-photo figure, the original stale caption
            # claimed that the image is an AI-generated depiction.
            checks["real_photo_no_false_AI_caption"]=not any(
                "AI 생성 여행 참고 이미지" in s for s in p.figcaptions)
        else:
            checks["AI_reference_disclosure"]="AI 생성" in text
        data["html_bytes"]=len(bytes_)
    except Exception as error:
        data["errors"].append(str(error))
        checks["page_opened"]=False
    data["pass"]=all(checks.values()) and not data["errors"]
    return data

def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--mode",choices=["live","static"],required=True)
    arg.add_argument("--root",default="dist")
    a=arg.parse_args()
    root=Path(a.root)
    results=[audit(slug,val,a.mode,root) for slug,val in PORTS.items()]
    summary={"checked_utc":datetime.now(timezone.utc).isoformat(),
             "mode":a.mode,"pass":sum(row["pass"] for row in results),
             "total":len(results),"pages":results,
             "scope":"Public-page source/asset verification only; operating conditions not confirmed"}
    out=Path("audit-output/port-trust-live")
    out.mkdir(parents=True,exist_ok=True)
    (out/(a.mode+"-report.json")).write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")
    for row in results:
        failed=[name for name,passed in row["checks"].items() if not passed]
        print(("PASS" if row["pass"] else "FAIL"),row["slug"],"failed",failed,"errors",row["errors"])
    print("SUMMARY",json.dumps({"mode":a.mode,"pass":summary["pass"],"total":summary["total"]},ensure_ascii=False))
    if summary["pass"]!=summary["total"]:
        raise SystemExit(1)

if __name__=="__main__":main()
