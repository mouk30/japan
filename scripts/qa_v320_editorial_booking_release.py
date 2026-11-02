#!/usr/bin/env python3
"""V320 release gate: factual and structural review of V316-V319 on existing pages.
Full-site booking-link audit is reported, not silently declared 'all corrected'.
"""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
from hashlib import sha256
import subprocess,json,re
ROOT=Path("site")
M={
 "guide/busan-osaka-timetable":{"v":"V316","operator":"https://www.panstarcruise.com/product/osaka/procedure","tokens":["27,000원","2,700엔","2026년 11월"],"photo":True},
 "guide/busan-tsushima-timetable":{"v":"V316","operator":"https://www.panstarcruise.com/product/daemado/info","tokens":["16,000원","27,000원","15:30"],"photo":True},
 "guide/busan-fukuoka-timetable":{"v":"V317","operator":"https://www.camellia-line.co.jp/boarding/","tokens":["10:30~11:30","18:00~19:00"],"photo":True},
 "guide/japan-ferry-booking-passport":{"v":"V319","operator":"https://www.panstarcruise.com/product/osaka/procedure","tokens":["선사별 공식 안내","출처가 검증되지 않은"],"photo":False},
 "guide/japan-ferry-seasickness":{"v":"V319","operator":"https://www.panstarcruise.com/product/osaka/procedure","tokens":["선사별 공식 안내","출처가 검증되지 않은"],"photo":False},
 "booking/trip-cost-calculator":{"v":"V318","operator":"https://www.camellia-line.co.jp/boarding/","tokens":["원화로 환산","환율 실시간 조회","v26-cost"],"photo":True},
 "guide/busan-osaka-ferry-price":{"v":"V320","operator":"https://www.panstarcruise.com/product/osaka/procedure","tokens":["27,000원","2,700엔","2026년 11월"],"photo":True},
 "guide/busan-tsushima-ferry-price":{"v":"V320","operator":"https://www.panstarcruise.com/product/daemado/info","tokens":["16,000원","27,000원","15:30"],"photo":True},
 "guide/busan-fukuoka-ferry-price":{"v":"V320","operator":"https://www.camellia-line.co.jp/boarding/","tokens":["14,000원","10:30~11:30"],"photo":True},
 "guide/japan-ferry-fuel-surcharge":{"v":"V320","operator":"https://www.panstarcruise.com/support/notice/310","tokens":["27,000원","16,000원","출처·촬영 장소가 검증되지 않은"],"photo":False},
 "guide/japan-ferry-checkin-time":{"v":"V320","operator":"https://www.camellia-line.co.jp/boarding/","tokens":["15:00~16:10","10:30~11:30","출처·촬영 장소가 검증되지 않은"],"photo":False},
}
class H(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.canonical=[];self.meta=[];self.jsonld=[];self.links=[];self.images=[];self._ld=False;self._ldcontent=""
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=="h1":self.h1+=1
  if t=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href"))
  if t=="meta" and a.get("name") in ("description","robots"):self.meta.append((a.get("name"),a.get("content")))
  if t=="img":self.images.append(a)
  if t=="a":self.links.append(a.get("href",""))
  if t=="script" and a.get("type")=="application/ld+json":self._ld=True;self._ldcontent=""
 def handle_data(self,v):
  if self._ld:self._ldcontent+=v
 def handle_endtag(self,t):
  if t=="script" and self._ld:self.jsonld.append(self._ldcontent);self._ld=False
def parse(s):
 h=H();h.feed(s);return h
for slug,conf in M.items():
 p=ROOT/slug/"index.html";s=p.read_text(encoding="utf8")
 old=subprocess.check_output(["git","show","origin/main:"+str(p)],text=True)
 a,b=parse(s),parse(old)
 assert a.h1==b.h1==1,(slug,"H1 modified")
 assert a.canonical==b.canonical==["https://www.nipponferry.com/"+slug+"/"],(slug,"canonical changed")
 assert a.meta==b.meta and a.jsonld==b.jsonld,(slug,"SEO metadata/JSON-LD changed")
 assert conf["operator"] in a.links,(slug,"operator CTA absent")
 assert "willer-travel.com/ko/ferry/" not in s,(slug,"wrong Japanese domestic ferry booking")
 for token in conf["tokens"]:assert token in s,(slug,"missing actionable detail",token)
 assert s.count("</body>")==1 and s.count("</html>")==1,(slug,"broken document closure")
 if conf["photo"]:assert a.images==b.images,(slug,"existing photos/credits changed")
 else:
  removed=Counter(x.get("src") for x in b.images)-Counter(x.get("src") for x in a.images)
  added=Counter(x.get("src") for x in a.images)-Counter(x.get("src") for x in b.images)
  # Post-V320 main already contains the approved removal; a later PR must preserve it.\n  assert (not removed and not added) or (removed==Counter({"/images/ferry.jpg":1}) and not added),(slug,"unlicensed photo removal or preservation only")
  assert "nf319-visual-truth" in s and "nf319-official-booking" in s,(slug,"source transparency panel lost")
  assert "nf-v319-source-first-guides.css" in s,(slug,"visual style link lost")
 assert not (Counter(b.links)-Counter(a.links)-Counter({"https://willer-travel.com/ko/ferry/":2})),(slug,"unrelated old navigation lost")
 for img in a.images:
  src=img.get("src","")
  if src.startswith("/") and not src.startswith("//"):
   assert (ROOT/src.split("?")[0].lstrip("/")).exists(),(slug,"broken local image",src)
 print("PASS",conf["v"],slug)
calc=(ROOT/"booking/trip-cost-calculator/index.html").read_text(encoding="utf8")
assert 'const form=document.getElementById("v26-cost")' in calc
assert calc.index('const form=document.getElementById("v26-cost")')<calc.index("</body>")
assert calc.count("</body></html>")==1
approved=ROOT/"images/panstar-cruise-clean-2048.webp"
assert approved.is_file() and sha256(approved.read_bytes()).hexdigest()=="bbcfa65a0e670060b5ce6fe79b2a9ea3272874b4d96f96799800ec9ccb631bdd"
added=subprocess.check_output(["git","diff","--name-only","--diff-filter=A","origin/main...HEAD"],text=True).splitlines()
assert not any(x.startswith("site/") and x.endswith(".html") for x in added),("new articles prohibited",added)
# Report whole-repo remaining wrong-operator links for future updates.
candidates=[]
for p in ROOT.rglob("*.html"):
 s=p.read_text(encoding="utf8",errors="replace")
 n=s.count("willer-travel.com/ko/ferry/")
 if n:candidates.append({"page":str(p.relative_to(ROOT)),"wrongLinkCount":n})
out=Path("audit-output/v320");out.mkdir(parents=True,exist_ok=True)
(out/"remaining-willer-operator-link-candidates.json").write_text(json.dumps({"inspectedExistingHtml":len(list(ROOT.rglob("*.html"))),"remainingCandidates":len(candidates),"remainingWrongLinkCount":sum(x["wrongLinkCount"] for x in candidates),"pages":candidates},ensure_ascii=False,indent=2),encoding="utf8")
print("V320 PASS 11 changed pages; inventory left for follow-on audit:",len(candidates),"pages",sum(x["wrongLinkCount"] for x in candidates),"links")
