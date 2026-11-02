#!/usr/bin/env python3
"""V296: verify international booking buttons point to each route's official operator, not domestic ferry marketplace."""
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path("site")
CASES={
 "fukuoka":("https://www.koreaferry.kr/","고려훼리 공식 예약 안내"),
 "osaka":("https://www.panstarcruise.com/","팬스타 공식 날짜·항로 검색"),
 "shimonoseki":("https://www.kampuferry.co.jp/reserve/","관부훼리 공식 예약방법 확인"),
 "tsushima":("https://www.panstarcruise.com/","팬스타 대마도 공식 날짜 검색"),
}
class A(HTMLParser):
 def __init__(self):super().__init__();self.a=[];self.canonical=[];self.h1=0
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if t=="a":self.a.append(d.get("href",""))
  if t=="link" and d.get("rel")=="canonical":self.canonical.append(d.get("href"))
  if t=="h1":self.h1+=1
for slug,(official,label) in CASES.items():
 p=ROOT/"booking"/slug/"index.html"
 s=p.read_text(encoding="utf-8");a=A();a.feed(s)
 assert "href='https://willer-travel.com/ko/ferry/'" not in s,(slug,"domestic marketplace used for international ticket")
 assert a.a.count(official)>=3,(slug,"official link missing from 3 primary, checklist and footer CTAs")
 assert s.count(">"+label+"</a>")>=2,(slug,"unclear CTA label")
 assert a.canonical==["https://www.nipponferry.com/booking/"+slug+"/"],(slug,"canonical")
 assert a.h1==1,(slug,"H1")
 assert "/stay/" in a.a,(slug,"internal guide link")
 assert "예약 확정되었습니다" not in s,(slug,"unverified reservation claim")
 print("PASS",slug,official)
print("V296 PASS: 4 existing booking pages / 12 official operator links, SEO/internal CTAs preserved")
