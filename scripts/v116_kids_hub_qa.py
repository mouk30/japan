#!/usr/bin/env python3
"""V116: validate independent kids theme routes, linked existing guides and SEO safety."""
from pathlib import Path
from html.parser import HTMLParser
import json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"
class Scan(HTMLParser):
 def __init__(self):
  super().__init__();self.hrefs=[];self.images=[];self.nav=[];self.scripts=[];self.h1=0
 def handle_starttag(self,tag,atts):
  a=dict(atts)
  if tag=="a" and a.get("href"):self.hrefs.append(a["href"])
  if tag=="img" and a.get("src"):self.images.append(a["src"])
  if tag=="h1":self.h1+=1
  if tag=="script" and a.get("src"):self.scripts.append(a["src"])
  if tag=="nav":self.nav.append(a.get("class",""))
def run():
 error=[]
 def ensure(v,msg):
  if not v:error.append(msg)
 hp=(SITE/"kids/index.html").read_text("utf8")
 h=Scan();h.feed(hp)
 ensure(h.h1==1,"Kids collection must have 1 H1")
 ensure(len(re.findall(r'<article class="kid-card"',hp))==12,"Kids hub needs 12 existing-guide cards")
 ensure("https://www.nipponferry.com/kids/" in hp,"canonical missing")
 ensure('<meta name="robots" content="index,follow' in hp,"index metadata absent")
 ensure('href="/kids/" aria-current="page"' in hp,"kids hub nav lacks current aria state")
 ensure("/nf-v116-kids.css?v=20261022" in hp,"styles absent")
 ensure("/nf-v116-kids.js" in h.scripts,"functional filter js absent")
 ensure("id=\"kids-area\"" in hp and "id=\"kids-age\"" in hp and "id=\"kids-type\"" in hp,"filter controls missing")
 ensure("CRUISE · COASTAL FERRY" in hp,"parent brand lost")
 ensure("크루즈·페리 탑승은 필수가 아닙니다" in hp,"independent identity missing")
 for a in h.hrefs:
  if not a.startswith("/") or a.startswith("//"):continue
  target=SITE/a.split("?",1)[0].lstrip("/")
  if a.endswith("/"):target=target/"index.html"
  ensure(target.exists(),"broken kids link: "+a)
 for im in h.images:
  ensure((SITE/im.lstrip("/")).is_file(),"missing image file: "+im)
 for path in ["/nf-v116-kids.css","/nf-v116-kids.js"]:
  ensure((SITE/path.lstrip("/")).is_file(),"missing new resource "+path)
 for name in ("site/index.html","site/things-to-do/travel-companions/index.html",
              "site/stay/family/index.html","site/things-to-do/family-with-kids/index.html"):
  c=(ROOT/name).read_text("utf8")
  ensure(c.count('href="/kids/"')>=2,"no desktop + mobile kids anchor in "+name)
 home=(SITE/"index.html").read_text("utf8")
 ensure("<title>일본크루즈 여행 | 가격·일정·기항지 | 일본페리</title>" in home,"brand home title changed")
 ensure('<link rel="canonical" href="https://www.nipponferry.com/">' in home,"home canonical changed")
 ensure("nf-v116-kids-home" in home,"home entrance card missing")
 navjs=(SITE/"nf-premium-v2.js").read_text("utf8")
 ensure('a[href="/kids/"]' in navjs,"sitewide progressive nav injection missing")
 ensure("if(!nav.querySelector" in navjs,"idempotent nav injection missing")
 stylesheet=(SITE/"nf-premium-v2.css").read_text("utf8")
 ensure(".nf-kids-menu" in stylesheet,"kids link highlight missing")
 sitemap=(SITE/"sitemap.xml").read_text("utf8")
 ET.fromstring(sitemap)
 ensure(sitemap.count("<loc>https://www.nipponferry.com/kids/</loc>")==1,"sitemap kids URL duplicate/missing")
 jsonlds=re.findall(r'<script type="application/ld\+json">([\s\S]*?)</script>',hp)
 ensure(len(jsonlds)==1,"structured data block missing/duplicate")
 if jsonlds:
  ld=json.loads(jsonlds[0])
  ensure(any(x.get("@type")=="CollectionPage" for x in ld),"CollectionPage structured data absent")
  ensure(any(x.get("@type")=="BreadcrumbList" for x in ld),"BreadcrumbList structured data absent")
 report={"passed":not error,"pages":1,"existing_guides":12,"images":len(h.images),"navigation_pages":4,"sitemap":True,"error_count":len(error),"errors":error}
 print(json.dumps(report,ensure_ascii=False,indent=2))
 raise SystemExit(0 if not error else 1)
if __name__=="__main__":run()
