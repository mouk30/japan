#!/usr/bin/env python3
"""Five high-impact port-page trust checks on the actual Vercel build output.
These are source/copy consistency checks, not third-party operational verification.
"""
import sys, re, json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(sys.argv[1] if len(sys.argv)>1 else "dist")
EXPECT = {
 "naha-cruise-terminal-kokusai-dori": "nahaport.jp",
 "ishigaki-cruise-kabira-bay-bus-taxi": "city.ishigaki.okinawa.jp",
 "hakata-port-hakata-station-access": "hakataport.com",
 "nagasaki-matsugae-glover-garden-cruise-access": "discover-nagasaki.com",
 "yokohama-red-brick-warehouse": "city.yokohama.lg.jp",
}
REAL_PHOTOS={"ishigaki-cruise-kabira-bay-bus-taxi","nagasaki-matsugae-glover-garden-cruise-access"}

class HTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1=0; self.anchors=[]; self.canonical=[]; self.img=[]; self.caption=[]; self._caption=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="h1": self.h1+=1
        if tag=="a":self.anchors.append(a.get("href",""))
        if tag=="img":self.img.append(a)
        if tag=="link" and "canonical" in a.get("rel",""):self.canonical.append(a.get("href",""))
        if tag=="figcaption":self._caption=True
    def handle_endtag(self,tag):
        if tag=="figcaption":self._caption=False
    def handle_data(self,data):
        if self._caption:self.caption.append(data)

fails=[]
for slug,domain in EXPECT.items():
    p=ROOT/"things-to-do"/slug/"index.html"
    if not p.exists():
        fails.append(f"{slug}: built file missing")
        continue
    s=p.read_text(encoding="utf-8")
    h=HTML();h.feed(s)
    expected=f"https://www.nipponferry.com/things-to-do/{slug}/"
    checks={
        "one H1":h.h1==1,
        "canonical unchanged":h.canonical==[expected],
        "one verified facts section":s.count('id="nf-official-facts-20261020"')==1,
        "official exact URL":any(urlsplit(a).hostname==domain or (urlsplit(a).hostname or "").endswith("."+domain) for a in h.anchors),
        "booking path exists":"/booking/japan-cruise/" in h.anchors,
        "article image":bool(h.img),
        "no office address confusion":slug!="naha-cruise-terminal-kokusai-dori" or "나하 크루즈터미널의 주소를 나하시 돈도초 2-1" not in s,
        "no stale photo placeholder":slug!="yokohama-red-brick-warehouse" or "이미지가 실제 생성·검수되어 등록되기 전까지" not in s,
        "no false AI image caption":slug not in REAL_PHOTOS or not any("AI 생성 여행 참고 이미지" in t for t in h.caption),
    }
    broken=[name for name,good in checks.items() if not good]
    print(json.dumps({"slug":slug,"pass":not broken,"checks":checks},ensure_ascii=False))
    if broken:fails.append(f"{slug}: {broken}")
if fails:
    print("FAIL:",*fails,sep="\n")
    raise SystemExit(1)
print("PASS: 5/5 verified port-page source/label checks")
