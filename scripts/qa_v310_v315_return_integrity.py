#!/usr/bin/env python3
"""V310-V315: source-backed booking and safe-return fixes on six EXISTING guides.
Freeze canonical, metadata, JSON-LD, original image and credited licenses.
"""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
from hashlib import sha256
import subprocess,re
ROOT=Path("site")
CASES={
 "fukuoka-busan-ferry":{"v":"V310","links":["https://www.camellia-line.co.jp/boarding/","https://www.camellia-line.co.jp/newcamellia/"],"terms":["10:30~11:30","18:00~19:00","국제터미널 1층"]},
 "osaka-busan-ferry":{"v":"V311","links":["https://www.panstarcruise.com/product/osaka/procedure","https://www.panstarcruise.com/support/notice/310"],"terms":["15:00~16:10","15:40~16:20","2,700엔","27,000원"]},
 "shimonoseki-busan-ferry":{"v":"V312","links":["https://www.kampuferry.co.jp/lang_kor/passenger_info/t_access/checkin.html","https://www.kampuferry.co.jp/reserve/"],"terms":["15:00~18:00","현금","19:45"]},
 "tsushima-busan-ferry":{"v":"V313","links":["https://www.panstarcruise.com/product/daemado/procedure","https://www.panstarcruise.com/product/daemado/info","https://www.panstarcruise.com/support/notice/309"],"terms":["1,600엔","2,700엔","15:30","11월 15일","90분","30분"]},
 "busan-hitakatsu-ferry":{"v":"V314","links":["https://www.panstarcruise.com/product/daemado/info","https://www.panstarcruise.com/product/daemado/procedure","https://www.panstarcruise.com/support/notice/309"],"terms":["16,000원","1,600엔","30분"]},
 "busan-izuhara-ferry":{"v":"V315","links":["https://www.panstarcruise.com/product/daemado/info","https://www.panstarcruise.com/product/daemado/procedure","https://www.panstarcruise.com/support/notice/309"],"terms":["27,000원","2,700엔","15:30"]}
}
class H(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.canonical=[];self.desc=[];self.robots=[];self.img=[];self.links=[];self.ids=[];self.jsonld=[];self._ld=False;self._ld_text=""
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=="h1":self.h1+=1
  if t=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href"))
  if t=="meta" and a.get("name")=="description":self.desc.append(a.get("content"))
  if t=="meta" and a.get("name")=="robots":self.robots.append(a.get("content"))
  if t=="img":self.img.append(a)
  if t=="a":self.links.append(a.get("href",""))
  if "id" in a:self.ids.append(a["id"])
  if t=="script" and a.get("type")=="application/ld+json":self._ld=True;self._ld_text=""
 def handle_data(self,s):
  if self._ld:self._ld_text+=s
 def handle_endtag(self,t):
  if t=="script" and self._ld:self.jsonld.append(self._ld_text);self._ld=False
def parse(s):
 h=H();h.feed(s);return h
for slug,c in CASES.items():
 path=ROOT/"guide"/slug/"index.html"
 s=path.read_text(encoding="utf8")
 old=subprocess.check_output(["git","show","origin/main:"+str(path)],text=True)
 h,p=parse(s),parse(old)
 assert h.h1==p.h1==1,(slug,"H1 changed")
 assert h.canonical==p.canonical==["https://www.nipponferry.com/guide/"+slug+"/"],(slug,"canonical")
 assert h.desc==p.desc and h.robots==p.robots and h.jsonld==p.jsonld,(slug,"SEO data changed")
 assert h.img==p.img,(slug,"original real photo or ALT changed")
 assert not (Counter(p.links)-Counter(h.links)-Counter({"https://willer-travel.com/ko/ferry/":2})),(slug,"original link unexpectedly lost")
 assert len(h.ids)==len(set(h.ids)),(slug,"duplicate anchor")
 assert "willer-travel.com/ko/ferry" not in s,(slug,"wrong domestic ferry booking link")
 assert 'id="nf310-verified-return"' in s and 'id="nf310-return-heading"' in s,(slug,"decision section")
 assert s.count('class="nf310-return-card"')==3,(slug,"3 useful checks missing")
 assert 'nf-v310-return-proof.css' in s and "nf310-safe-guide" in s,(slug,"responsive style")
 assert "실시간" in s and "마지막" in s,(slug,"honest non-live warning missing")
 assert c["v"] in s,(slug,"milestone")
 for link in c["links"]:assert link in h.links,(slug,"official source not linked",link)
 for term in c["terms"]:assert term in s,(slug,"official fact not stated",term)
 assert s.count("href=\"https://willer-travel.com/ko/ferry/\"")==0
 assert "귀국를" not in s,(slug,"grammatical template artifact")
 for img in h.img:
  src=img.get("src","")
  if src.startswith("/") and not src.startswith("//"):
   assert (ROOT/src.lstrip("/").split("?")[0]).is_file(),(slug,"image absent",src)
 print("PASS",c["v"],slug,": official operator, return facts and original SEO/images")
assert "25,000원" not in (ROOT/"guide/osaka-busan-ferry/index.html").read_text()
assert "2,500엔" not in (ROOT/"guide/osaka-busan-ferry/index.html").read_text()
assert "15,000원" not in (ROOT/"guide/tsushima-busan-ferry/index.html").read_text()
assert "25,000원" not in (ROOT/"guide/tsushima-busan-ferry/index.html").read_text()
assert (ROOT/"images/panstar-cruise-clean-2048.webp").is_file()
assert sha256((ROOT/"images/panstar-cruise-clean-2048.webp").read_bytes()).hexdigest()=="bbcfa65a0e670060b5ce6fe79b2a9ea3272874b4d96f96799800ec9ccb631bdd"
new=subprocess.check_output(["git","diff","--name-only","--diff-filter=A","origin/main...HEAD"],text=True).splitlines()
assert not any(p.startswith("site/") and p.endswith(".html") for p in new),("new article prohibited",new)
print("V310–V315 PASS: exactly six existing guide pages corrected, no new HTML")
