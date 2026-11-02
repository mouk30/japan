#!/usr/bin/env python3
"""V302: ferry operator image/booking-source and no-regression check."""
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path("site")
s=(ROOT/"ferry/index.html").read_text(encoding="utf-8")
class P(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.canonical=[];self.links=[];self.images=[]
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if t=="h1":self.h1+=1
  if t=="link" and d.get("rel")=="canonical":self.canonical.append(d.get("href"))
  if t=="a":self.links.append(d.get("href",""))
  if t=="img":self.images.append(d)
p=P();p.feed(s)
assert p.h1==1 and p.canonical==["https://www.nipponferry.com/ferry/"]
assert s.count('class="nf302-direct-figure"')==4
assert "id=\"nf-v302-official-thumb-style\"" in s
assert "grid-template-columns:minmax(0,1fr)" in s
for file in ["nf-v85-osaka-dotonbori-licensed.webp","fukuoka-ohori-park.webp","v62-karato-market-real.webp","v62-izuhara-port-real.webp"]:
 assert (ROOT/"images/venues"/file).is_file(),file
 assert sum(img.get("src","").endswith(file) for img in p.images)>=2,file
assert "히타카츠와 다른 항구" in s
assert "국제여객터미널 사진 아님" in s
assert "선박 또는 승선 터미널이 아님" in s
assert "https://www.kampuferry.co.jp/reserve/" in p.links
assert "https://www.kampuferry.co.jp/news/20261027systemmaintenance.html" in p.links
for source in ["https://www.panstarcruise.com/","https://www.koreaferry.co.kr/rs/idv/reservation/calendar_index/1/2?country=2"]:
 assert source in p.links,source
for x in ["/guide/busan-osaka-ferry/","/guide/busan-fukuoka-ferry/","/guide/busan-shimonoseki-ferry/","/guide/busan-tsushima-ferry/"]:
 assert x in p.links,x
assert 'id="recommended-ferry-routes"' in s
assert "실시간 예약·운항현황 화면이 아닙니다" in s
assert "예약 확정되었습니다" not in s
print("V302 PASS: 4 photo-first official operators, correct reservation method, SEO and original notices")
