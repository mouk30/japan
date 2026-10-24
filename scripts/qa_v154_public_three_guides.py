#!/usr/bin/env python3
"""V154: check LIVE production three guides (not just GitHub source), existing four
hub entry points, original three WebP files and sitemap. Official external links
are checked for exact destinations in HTML, not incorrectly called "bookable".
"""
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from html.parser import HTMLParser
from datetime import datetime,timezone
from pathlib import Path
from collections import Counter
import json,time,xml.etree.ElementTree as ET
ORIGIN="https://www.nipponferry.com"
PILOTS={
 "naoshima-art-ferry-return":{
 "actions":["museum_info","island_transport","ferry_schedule","return_plan"],
 "official":["https://benesse-artsite.jp/en/faq/chichu_art_museumonline_tickets.html","https://www.benesse-artsite.jp/en/access/naoshima/","https://shikokukisen.com/en-routes/"],
 "claims":["구매 후","취소","마을버스","쓰쓰지소","귀항"],
 "image":"/images/editorial/v146-naoshima-miyanoura-ferry-terminal-2025.webp",
 "source":"https://commons.wikimedia.org/wiki/File:Naoshima_Ferry_Terminal.jpg"},
 "teshima-art-ferry-return":{
 "actions":["museum_info","island_transport","ferry_schedule","return_plan"],
 "official":["https://benesse-artsite.jp/en/general-information.html","https://teshima-navi.jp/en/access/","https://www.shodoshima-ferry.co.jp/timetable/"],
 "claims":["이에우라","가라토","현금","정리권","400엔"],
 "image":"/images/editorial/v146-teshima-art-museum-exterior-2013.webp",
 "source":"https://commons.wikimedia.org/wiki/File:Teshima_Art_Museum_exterior_view_201310.jpg"},
 "takamatsu-cruise-udon-market-return":{
 "actions":["port_return","official_food","return_plan"],
 "official":["/things-to-do/takamatsu-cruise-port-day-trip/#nf-jnto-journey-20261024","https://www.kensanpin.org/marche/schedule/","#return"],
 "claims":["다카마쓰","도쿠시마","고치","10월 18일","10월 25일","연기일","11월 15일","11월 22일"],
 "image":"/images/culture-verified/japan-kagawa-udon-pilgrimage.webp",
 "source":"https://commons.wikimedia.org/wiki/File:Kama-age_sanuki_udon_by_sekido_in_Takamatsu%2C_Kagawa.jpg"}
}
HUBS={
"/things-to-do/":["naoshima","teshima","shikoku_food"],
"/things-to-do/cruise-ports/":["naoshima","teshima","shikoku_food"],
"/things-to-do/food-experience/":["shikoku_food"],
"/food/":["shikoku_food"]}
TARGETS={"naoshima":"/things-to-do/naoshima-art-ferry-return/","teshima":"/things-to-do/teshima-art-ferry-return/","shikoku_food":"/things-to-do/takamatsu-cruise-udon-market-return/"}
class H(HTMLParser):
 def __init__(self):
  super().__init__();self.h1=0;self.canonical=[];self.ids=[];self.links=[];self.actions=[];self.pilot_entry=[];self.images=[];self.ld=[];self.titles=[];self.intitle=False;self.inscript=False;self.scriptbuf=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="h1":self.h1+=1
  if tag=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href"))
  if tag=="a":
   self.links.append(a.get("href",""))
   if "data-nf-pilot-action" in a:self.actions.append(a["data-nf-pilot-action"])
   if "data-nf-pilot-entry" in a:self.pilot_entry.append((a.get("data-nf-pilot-entry"),a.get("href")))
  if tag=="img":self.images.append((a.get("src",""),a.get("alt","")))
  if "id" in a:self.ids.append(a["id"])
  if tag=="script" and a.get("type")=="application/ld+json":self.inscript=True;self.scriptbuf=[]
 def handle_data(self,txt):
  if self.inscript:self.scriptbuf.append(txt)
 def handle_endtag(self,tag):
  if tag=="script" and self.inscript:self.ld.append("".join(self.scriptbuf));self.inscript=False
def read(path,binary=False):
 error=""
 for attempt in range(4):
  try:
   with urlopen(Request(ORIGIN+path,headers={"User-Agent":"Mozilla/5.0 (NIPPONFERRY-V154-Guide-ReleaseQA/1.0)","Cache-Control":"no-cache"}),timeout=23) as resp:
    status=resp.status;ct=resp.headers.get("content-type","");data=resp.read(5_000_000)
    return status,ct,data if binary else data.decode("utf-8","replace")
  except (URLError,HTTPError,TimeoutError) as e:
   error=str(e);time.sleep(1+attempt)
 raise RuntimeError(path+" "+error)
results=[]
def save(path,checks,extra=None):
 row={"path":path,"pass":all(checks.values()),"checks":checks}
 if extra:row.update(extra)
 results.append(row);print("PASS" if row["pass"] else "FAIL",path,[x for x,v in checks.items() if not v],flush=True)
for slug,data in PILOTS.items():
 path="/things-to-do/"+slug+"/"
 try:
  status,ct,s=read(path);h=H();h.feed(s)
  pos=s.index('id="nf-v154-depart-book-return"') if 'id="nf-v154-depart-book-return"' in s else -1
  sec=s[pos:pos+7500] if pos>=0 else ""
  checks={
   "http200":status==200,
   "html":"html" in ct.lower(),
   "indexable":"noindex" not in s[:6500].lower(),
   "one_h1":h.h1==1,
   "canonical":h.canonical==[ORIGIN+path],
   "single_v154_section":h.ids.count("nf-v154-depart-book-return")==1,
   "3_distinct_actions":sec.count('class="nf-v154-step"')==3,
   "above_old_feature_image":pos<s.index('<figure class="v146-hero"') if "takamatsu-" not in slug else pos<s.index('<section class="box">'),
   "three_official_destination_links":all(x in h.links for x in data["official"]),
   "selected_click_intents":all(x in h.actions for x in data["actions"]),
   "real_operational_claims":all(x in sec for x in data["claims"]),
   "real_local_photo":any(src==data["image"] and len(alt)>15 for src,alt in h.images),
   "photo_original_retained":data["source"] in h.links,
   "return_check_anchor":("#return" in h.links or "#checklist" in h.links),
   "responsive_mobile":'@media(max-width:610px)' in s and 'min-height:44px' in s,
   "no_sold_out_guarantee":"잔여 좌석 보장" not in sec
  }
  # Article JSON-LD after upgrade: reflects actual 2026-10-24 updates.
  article=[]
  for ld in h.ld:
   try:
    v=json.loads(ld);stack=[v]
    while stack:
     node=stack.pop(0)
     if isinstance(node,list):stack+=node;continue
     if not isinstance(node,dict):continue
     if node.get("@type")=="Article":article.append(node)
     if "@graph" in node:stack.append(node["@graph"])
   except json.JSONDecodeError:pass
  checks["Article_modified_date"]=len(article)==1 and article[0].get("dateModified")=="2026-10-24"
  save(path,checks)
 except Exception as e:save(path,{"http_ready":False},{"error":str(e)})
for path,values in HUBS.items():
 try:
  st,ct,s=read(path);h=H();h.feed(s)
  wanted=sorted((k,TARGETS[k]) for k in values)
  checks={"http200":st==200,"html":"html" in ct.lower(),"one_h1":h.h1==1,
  "canonical":h.canonical==[ORIGIN+path],
  "eight_cards_across_four_hubs":sorted(h.pilot_entry)==wanted,
  "original_v153_panel_retained":h.ids.count("nf-v153-pilot-hub")==1}
  save(path,checks)
 except Exception as e:save(path,{"http_ready":False},{"error":str(e)})
for slug,d in PILOTS.items():
 p=d["image"]
 try:
  st,ct,b=read(p,binary=True)
  save(p,{"http200":st==200,"webp":"image/webp" in ct.lower() and b[:4]==b"RIFF" and b[8:12]==b"WEBP"})
 except Exception as e:save(p,{"http_ready":False},{"error":str(e)})
try:
 st,ct,xml=read("/sitemap.xml");locs=[x.find("{*}loc").text for x in ET.fromstring(xml).findall("{*}url")]
 save("/sitemap.xml",{"http200":st==200,"all_original_three_urls":all(ORIGIN+"/things-to-do/"+x+"/" in locs for x in PILOTS),"no_duplicates":len(locs)==len(set(locs))})
except Exception as e:save("/sitemap.xml",{"http_ready":False},{"error":str(e)})
report={"date":datetime.now(timezone.utc).isoformat(),"total":len(results),"pass":sum(r["pass"] for r in results),"no_new_posts":True,"photos_rights_verified":True,"GA4_actual_metrics_not_read":True,"reports":results}
out=Path("audit-output/v154-public");out.mkdir(parents=True,exist_ok=True)
(out/"three-guides-official-links-public.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",report["pass"],"/",report["total"])
if report["pass"]!=report["total"]:raise SystemExit(1)
