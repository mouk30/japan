#!/usr/bin/env python3
"""V171: protect original three guide URLs/photos/SEO, verify official update on source and public HTML."""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
import json,sys,subprocess,time
from urllib.request import urlopen,Request
from urllib.error import URLError,HTTPError
BASE="e8538221142dcaf83f0dd87beff869129671b17f"
ROOT=Path("site/things-to-do")
DATA={
 "naoshima-art-ferry-return":("naoshima-2027-closure",["2027년 1월 12일~3월 19일","예약시각 30분 전까지","www.benesse-artsite.jp/news/20260525-3518.html","benesse-artsite.eventos.tokyo"]),
 "teshima-art-ferry-return":("teshima-winter-days",["12월 1일~2월 말","화~목요일","www.benesse-artsite.jp/news/20260630-3558.html","benesse-artsite.jp/en/calendar/"]),
 "takamatsu-cruise-udon-market-return":("marche-date-vs-postponement",["11월 15일","11월 22일","1월 17일","1월 24일","www.kensanpin.org/ko/marche/schedule/"])
}
class Parse(HTMLParser):
 def __init__(self): super().__init__();self.titles=[];self.intitle=False;self.meta=[];self.links=[];self.images=[];self.ids=[];self.h1=0;self.canon=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if tag=="title":self.intitle=True
  if tag=="h1":self.h1+=1
  if "id" in d:self.ids.append(d["id"])
  if tag=="img":self.images.append(tuple(d.get(k,"") for k in ("src","alt","width","height")))
  if tag=="a":self.links.append(d.get("href",""))
  if tag=="link" and d.get("rel")=="canonical":self.canon.append(d.get("href",""))
  if tag=="meta":self.meta.append(tuple(d.get(k,"") for k in ("name","property","content")))
 def handle_data(self,data):
  if self.intitle:self.titles.append(data)
 def handle_endtag(self,tag):
  if tag=="title":self.intitle=False
def verify(slug,s,orig=None):
 note,claims=DATA[slug];p=Parse();p.feed(s);checks={}
 checks["one_current_notice"]=s.count('data-nf-v171-note="'+note+'"')==1
 checks["all_verified_claims"]=all(x in s for x in claims)
 checks["single_h1_and_canonical"]=p.h1==1 and p.canon==["https://www.nipponferry.com/things-to-do/"+slug+"/"]
 checks["three_original_v154_steps"]=s.count('class="nf-v154-step"')==3
 checks["current_not_historical_cancellation"]=("구매 후 방문객 사유의 시간 변경·취소는 허용되지 않습니다." not in s)
 checks["image_credits_and_source"]=("commons.wikimedia.org" in s and "creativecommons.org" in s)
 checks["notice_before_original_steps"]=s.index('data-nf-v171-note=')<s.index('class="nf-v154-steps"')
 if orig is not None:
  o=Parse();o.feed(orig)
  checks["SEO_metadata_preserved"]=p.titles==o.titles and p.meta==o.meta and p.canon==o.canon
  checks["all_photo_src_alt_size_preserved"]=p.images==o.images
  checks["original_outgoing_links_retained"]=Counter(p.links)>=Counter(o.links)
  checks["existing_DOM_ids_not_changed"]=p.ids==o.ids
 return checks
def main():
 mode=sys.argv[1] if len(sys.argv)>1 else "source"
 output=Path("audit-output/v171");output.mkdir(parents=True,exist_ok=True)
 results=[]
 for slug in DATA:
  path=ROOT/slug/"index.html"
  if mode=="source":
   s=path.read_text("utf-8");base=subprocess.check_output(["git","show",BASE+":"+str(path)],text=True)
   checks=verify(slug,s,base)
  else:
   url="https://www.nipponferry.com/things-to-do/"+slug+"/"
   latest="";error=""
   for attempt in range(9):
    try:
     with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0 (NIPPONFERRY-V171-Official-QA)","Cache-Control":"no-cache"}),timeout=18) as r:latest=r.read(300000).decode("utf-8","replace")
     if 'data-nf-v171-note="'+DATA[slug][0]+'"' in latest:break
    except (URLError,HTTPError,TimeoutError) as e:error=str(e)
    time.sleep(15)
   if not latest:checks={"http_success":False,"error":False};print("HTTP error",url,error,flush=True)
   else:checks=verify(slug,latest)
  success=all(checks.values());results.append({"slug":slug,"ok":success,"checks":checks})
  print("PASS" if success else "FAIL",slug,checks,flush=True)
 if mode=="source":
  previous=subprocess.check_output(["git","show",BASE+":site/sitemap.xml"],text=True)
  sitemap_ok=previous==Path("site/sitemap.xml").read_text("utf-8")
  results.append({"slug":"sitemap","ok":sitemap_ok,"checks":{"unchanged":sitemap_ok}})
 report={"version":"V171","mode":mode,"existing_guides":3,"new_posts":0,"checks":results,"all_pass":all(x["ok"] for x in results),"limits":"No purchase/seat confirmation; live mode checks HTML not viewport screenshots"}
 (output/(mode+".json")).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
 print("SUMMARY",sum(x["ok"] for x in results),"/",len(results),flush=True)
 if not report["all_pass"]:raise SystemExit(1)
if __name__=="__main__":main()
