#!/usr/bin/env python3
"""V175 four old cruise guide regression, ticket and return, source audit."""
from pathlib import Path
from html.parser import HTMLParser
import subprocess,json,sys
BASE="0dc1e8ffdf6ee3b34cc6702a00bb1a004dd77fc5"
CASES={
 "miyako":{"phrases":["현장 신청","2,000엔","1,800엔","15:30","16:00"],"urls":["kankou385.jp/spots/aonodoukutsu-sappasen-taiken/","jodo-yuransen.jp/timetable/","jodo-yuransen.jp/access/"],"cta":"사파선 현장 신청·운영조건"},
 "ishinomaki":{"phrases":["2027년 1월 8일","전관 휴관","1,300엔","도보 약 12분"],"urls":["mangattan.jp/manga/open/","mangattan.jp/manga/ticket/","mangattan.jp/manga/access/"],"cta":"이시노모리 만화관 전관 휴관 공지"},
 "toba":{"phrases":["Webket","2,800엔","9월 30일","텐더"],"urls":["aquarium.co.jp/ryoukin/","aquarium.co.jp/ryoukin/coupon.html","tobanoyado.com/event.php"],"cta":"수족관 공식 요금·웹티켓 진입"},
 "hachinohe":{"phrases":["일요일","8:30","4편","11월 6일","4호부두"],"urls":["minatonichiyouasaichikai.com/533/","visithachinohe.com/stories/asaichi-junkan-bus/","pref.aomori.lg.jp/soshiki/kendo/ha-kokan/asuka.html"],"cta":"2026년 시장 실제 개최일·현장정보"}
}
class Reader(HTMLParser):
 def __init__(self):super().__init__();self.title=[];self.intitle=False;self.h1=0;self.meta=[];self.canonical=[];self.images=[];self.links=[];self.ids=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if tag=="title":self.intitle=True
  if tag=="h1":self.h1+=1
  if tag=="meta":self.meta.append((d.get("name",""),d.get("property",""),d.get("content","")))
  if tag=="link" and d.get("rel")=="canonical":self.canonical.append(d.get("href",""))
  if tag=="img":self.images.append(tuple(d.get(k,"") for k in ("src","alt","width","height","onerror")))
  if tag=="a":self.links.append(d.get("href",""))
  if "id" in d:self.ids.append(d["id"])
 def handle_data(self,x):
  if self.intitle:self.title.append(x)
 def handle_endtag(self,tag):
  if tag=="title":self.intitle=False
def read(s):p=Reader();p.feed(s);return p
rows=[]
for slug,d in CASES.items():
 path=Path("site/things-to-do")/(slug+"-cruise-port-day-trip")/"index.html"
 curr=path.read_text("utf-8");orig=subprocess.check_output(["git","show",BASE+":"+str(path)],text=True)
 a,b=read(curr),read(orig);block=curr[curr.index('id="nf-v175-'+slug+'"'):][:6500].replace("&amp;","&")
 tests={
  "specific_operator_claims":all(t in block for t in d["phrases"]),
  "three_matching_official_outbound_links":all(t in block for t in d["urls"]),
  "three_action_buttons":all(block.count('data-nf-v175-action="'+q+'"')==1 for q in ("ticket","conditions","return")),
  "original_misleading_portal_CTA_replaced":d["cta"]+" ↗</a>" in curr and "입장·예약 운영기관 안내 확인 ↗" not in curr,
  "new_panel_once":a.ids.count("nf-v175-"+slug)==1,
  "unchanged_image_src_alt_dimensions_fallback":a.images==b.images,
  "unchanged_title_description_canonical_H1":a.title==b.title and a.meta==b.meta and a.canonical==b.canonical and a.h1==b.h1==1,
  "all_original_href_destinations_preserved":set(b.links).issubset(set(a.links)),
  "existing_ids_not_removed":set(b.ids).issubset(set(a.ids)) and len(a.ids)==len(set(a.ids)),
  "AI_or_real_original_credit_disclosure_preserved":("AI 생성 참고 이미지" in curr)==("AI 생성 참고 이미지" in orig) and all(x in a.links for x in b.links if "commons.wikimedia.org" in x or "creativecommons.org" in x),
  "responsive_button_style":'id="nf-v175-operational-style"' in curr and "min-height:52px" in curr and "@media(max-width:630px)" in curr
 }
 ok=all(tests.values());print("PASS" if ok else "FAIL",slug,tests,flush=True)
 rows.append({"slug":slug,"pass":ok,"checks":tests})
p=Path("site/sitemap.xml");old_sitemap=subprocess.check_output(["git","show",BASE+":site/sitemap.xml"],text=True)
same_sitemap=p.read_text("utf-8")==old_sitemap
rows.append({"slug":"sitemap","pass":same_sitemap})
out=Path("audit-output/v175");out.mkdir(parents=True,exist_ok=True)
res={"version":"V175","pages":4,"new_articles":0,"rows":rows,"pass":all(r["pass"] for r in rows)}
(out/"source.json").write_text(json.dumps(res,ensure_ascii=False,indent=2))
print("SUMMARY",sum(r["pass"] for r in rows),"/",len(rows))
if not res["pass"]:sys.exit(1)
