#!/usr/bin/env python3
"""V132: reproducible source-only inventory of the complete current NIPPONFERRY site.

This audit searches for *candidates*. It does NOT certify:
- whether an image truthfully depicts a site (human/provenance verification needed);
- whether an external ticket link actually completes a booking;
- actual ship-specific berths, shuttles, cutoff times or current fee schedules.
Only exact local assets and unambiguous source contradictions are marked errors.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime,timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote,urlsplit
import json,re,os
SITE=Path(__file__).resolve().parents[1]/"site"
OUT=Path(__file__).resolve().parents[1]/"audit-reports/v132"
REPO="https://www.nipponferry.com"
BOOKWORDS=("예약","예매","발권","book now","buy ticket","티켓 구매","입장권 구매")
RETURNWORDS=("귀선","재승선","승선 마감","복귀","출항","선내 복귀","승선시각","탑승 마감")
PORTWORDS=("크루즈","기항지","하선","cruise","항만","선석")
PHOTO_WORDS=("촬영","촬영자","라이선스","저작자","출처","실사","원본")
ESCAPE_EXT=(".png",".jpg",".jpeg",".webp",".svg",".gif",".avif",".ico",".pdf",".mp4",".woff",".woff2")
SKIP_ROOT=("/api/","/_next/","/cdn-cgi/")
class Tags(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True);self.images=[];self.anchors=[];self.canonicals=[];self.og=[];self.desc=[];self.robots=[];self.headings=[];self.scripts=[];self._h=None;self._atxt=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="img":self.images.append(a)
  if tag=="a":
   self.anchors.append({"href":a.get("href",""),"text":""});self._atxt=len(self.anchors)-1
  if tag=="link" and a.get("rel")=="canonical":self.canonicals.append(a.get("href",""))
  if tag=="meta":
   if a.get("property")=="og:image":self.og.append(a.get("content",""))
   if a.get("name")=="description":self.desc.append(a.get("content",""))
   if a.get("name")=="robots":self.robots.append(a.get("content",""))
  if tag=="h1":self.headings.append("");self._h="h1"
 def handle_data(self,text):
  if self._atxt is not None:self.anchors[self._atxt]["text"]+=text
  if self.headings and self._h=="h1":self.headings[-1]+=text
 def handle_endtag(self,tag):
  if tag=="a":self._atxt=None
  if tag=="h1":self._h=None
 def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs)

def canonical_path(file):
 p="/"+file.relative_to(SITE).as_posix()
 return p[:-len("index.html")] if p.endswith("/index.html") else p

def resolve_local(url,owner):
 if not url:return None
 if url.startswith(("mailto:","tel:","javascript:","data:","blob:","#")):return None
 u=urlsplit(unescape(url))
 if u.scheme in ("http","https"):
  if u.hostname not in ("www.nipponferry.com","nipponferry.com"):return None
 elif u.scheme:return None
 path=unquote(u.path)
 if not path:return None
 if path.startswith(SKIP_ROOT):return None
 if not path.startswith("/"):
  path=(owner if owner.endswith("/") else owner.rsplit("/",1)[0]+"/")+path
 from posixpath import normpath
 path=normpath(path)
 if not path.startswith("/"):path="/"+path
 return path

def exists(path):
 if not path:return True
 file=SITE/path.lstrip("/")
 if file.is_file():return True
 if file.is_dir() and (file/"index.html").is_file():return True
 if not path.endswith("/") and (SITE/(path.lstrip("/")+"/index.html")).is_file():return True
 if not path.endswith(".html") and (SITE/(path.lstrip("/")+".html")).is_file():return True
 return False

def text_content(source):
 s=re.sub(r"<script\b[^>]*>[\s\S]*?</script>"," ",source,flags=re.I)
 s=re.sub(r"<style\b[^>]*>[\s\S]*?</style>"," ",s,flags=re.I)
 return unescape(re.sub(r"<[^>]*>"," ",s))

def main():
 files=sorted(SITE.rglob("*.html"))
 assets=[];bad_links=[];mismatches=[];no_return=[];booking=[];time_candidates=[];ai_candidates=[];seo=[];credit=[];meta=[];pages=[]
 photos=Counter();groups=Counter();link_domains=Counter()
 for file in files:
  url=canonical_path(file); s=file.read_text("utf8",errors="replace")
  parse=Tags();parse.feed(s)
  text=text_content(s);is_cruise=url.startswith("/things-to-do/") and bool(re.search(r"(cruise|port|harbor|terminal)",url))
  group=url.split("/")[1] if len(url.split("/"))>1 else "/";groups[group]+=1
  pages.append(url)
  # Audit-only/photo-review pages and intentional legacy meta-refresh aliases are
  # deliberately noindex/redirected; missing SEO text is not a public indexing defect.
  aux="noindex" in ",".join(parse.robots).lower() or bool(re.search(r'<meta[^>]+http-equiv=["\\\']refresh["\\\']',s,re.I))
  if url not in ("/404.html",) and not aux:
   if not parse.desc:seo.append({"page":url,"issue":"no_description"})
   if not parse.canonicals:seo.append({"page":url,"issue":"no_canonical"})
   if not parse.headings:seo.append({"page":url,"issue":"no_h1"})
   if parse.canonicals and parse.canonicals[0]!=REPO+url:
    if "noindex" not in ",".join(parse.robots).lower():
     seo.append({"page":url,"issue":"canonical_target_different","value":parse.canonicals[0]})
  for im in parse.images:
   src=im.get("src","");local=resolve_local(src,url)
   if local and not exists(local):assets.append({"page":url,"image":src,"local_path":local})
   if not im.get("alt","").strip():credit.append({"page":url,"issue":"missing_image_alt","src":src})
  for a in parse.anchors:
   link=a["href"];local=resolve_local(link,url)
   if local:
    if not exists(local):
     bad_links.append({"page":url,"href":link,"local_path":local,"label":a["text"].strip()[:90]})
   else:
    domain=urlsplit(link).hostname
    if domain:link_domains[domain]+=1
   label=re.sub(r"\s+"," ",a["text"]).strip()
   if any(x in label.lower() for x in BOOKWORDS):
    if local and (local=="/" or local.startswith("/things-to-do/")):
     booking.append({"page":url,"label":label[:100],"href":link,"why":"booking-label-links-to-nonbooking-content"})
    elif link.startswith(("http://","https://")):
     host=urlsplit(link).hostname or ""
     if host in ("www.nipponferry.com","nipponferry.com"):continue
     if urlsplit(link).path in ("","/","/index.html"):
      booking.append({"page":url,"label":label[:100],"href":link,"why":"booking-label-links-to-external-homepage-not-checkout"})
  m=re.search(r"""<img[^>]*class=["'][^"']*cover[^"']*["'][^>]*>""",s)
  cover=None
  if m:
   cover=(re.search(r"""src=["']([^"']+)""",m.group(0)) or [None,None])[1]
  if cover:
   photos["pages_with_cover"]+=1
   full=REPO+cover if cover.startswith("/") else cover
   oldog=parse.og[0] if parse.og else ""
   if oldog and oldog!=full:
    mismatches.append({"page":url,"issue":"cover_vs_og","cover":cover,"og":oldog})
   ld=re.findall(r"""<script[^>]*type=["']application/ld\+json["'][^>]*>([\s\S]*?)</script>""",s,re.I)
   for raw in ld:
    try: parsed=json.loads(raw)
    except (ValueError,TypeError):continue
    schema=parsed if isinstance(parsed,list) else [parsed]
    for obj in schema:
     if not isinstance(obj,dict) or obj.get("@type")!="Article":continue
     v=obj.get("image");urls=v if isinstance(v,list) else [v]
     if urls!=[full]:
      mismatches.append({"page":url,"issue":"cover_vs_article_schema","cover":cover,"article_images":urls[:3]})
   if "AI 생성" in m.group(0) and "/images/venues/" in cover:
    ai_candidates.append({"page":url,"issue":"AI_alt_on_replaced_real_cover","cover":cover})
   if "/images/venues/" in cover and any(x in text for x in ("대표 이미지는 AI 생성","대표 사진은 AI 생성","사진은 AI 생성")):
    ai_candidates.append({"page":url,"issue":"stale_AI_disclosure_on_real_cover","cover":cover})
   around=s[m.end():m.end()+1400]
   if "figcaption" not in around and "촬영자" not in around:
    credit.append({"page":url,"issue":"hero_missing_nearby_photo_source","cover":cover})
  if is_cruise:
   photos["cruise_pages"]+=1
   if not any(k in text for k in RETURNWORDS):
    no_return.append({"page":url,"reason":"no_visible_return_or_boarding_language"})
   if any(k in s for k in ("최종 셔틀","귀선 마감","마지막 버스","귀선 시간","막차")):
    photos["has_return_terms"]+=1
  matches=re.findall(r".{0,35}(?:202[0-5]년|202[0-5][.-](?:0?[1-9]|1[0-2])(?:[.-]\d{1,2})?|202[0-5]/\d{1,2}).{0,90}(?:요금|운임|영업|운영|입장료|예약|시간표|할증료).{0,80}",text)
  for snippet in matches[:2]:
   context=" ".join(snippet.split())
   # Photo credit dates in a paragraph about historical images are not out-of-date
   # current ticket/operational promises. Keep only actual customer-facing claims.
   if any(p in context for p in ("촬영 당시","사진 원본","WebP","실사 원본","촬영자","촬영일","저작자","촬영 장소")):continue
   time_candidates.append({"page":url,"snippet":context[:200],"classification":"historical_date_near_operational_claim_manual_review"})
 output={
 "version":"V132","generated_utc":datetime.now(timezone.utc).isoformat(),
 "scope":{"site_html_pages":len(files),"site_local_images":sum(1 for x in SITE.rglob("*") if x.is_file() and x.suffix.lower() in (".webp",".png",".jpg",".jpeg",".svg",".gif",".avif")),"regions":dict(groups.most_common())},
 "counts":{"missing_image_local_references":len(assets),"unresolved_internal_links":len(bad_links),"seo_fields_or_nonself_canonical":len(seo),"cover_social_or_article_image_conflicts":len(mismatches),"likely_stale_ai_label":len(ai_candidates),"hero_photo_source_visibility_review":sum(1 for x in credit if x["issue"]=="hero_missing_nearby_photo_source"),"cruise_port_pages":photos["cruise_pages"],"cruise_return_language_missing":len(no_return),"booking_cta_destination_review":len(booking),"old_operational_date_context_review":len(time_candidates),"missing_alt":sum(1 for x in credit if x["issue"]=="missing_image_alt")},
 "limits":["Photo-place truth and reuse rights require original image/site-specific human validation","External HTTP reachable is not a booking-confirmation test","Ship-specific final boarding, berths and shuttles are unavailable without vessel/date/official operator notice","Year-near-operating-information is a review candidate, not proof of expired price","No automatic replacement of unclear official sources"],
 "findings":{
   "missing_local_images":assets,"unresolved_internal_links":bad_links,
   "seo":seo,"image_meta_mismatch":mismatches,"stale_ai_labels":ai_candidates,
   "photo_source_visibility":credit,"cruise_return_language_missing":no_return,
   "booking_cta_destination_review":booking,"historical_operational_info":time_candidates,
  },
 "external_link_hosts_by_anchor_count":dict(link_domains.most_common(110))
 }
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/"sitewide-inventory.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n","utf8")
 rows=[
 "# V132 — NIPPONFERRY 전체 페이지 1차 정적 품질 전수 조사",
 "",
 "**"+str(len(files))+"개 HTML 페이지 소스 조사 · 신규 게시글 0개 · 운항·예약 실시간 확약 없음**",
 "",
 "| 분류 | 건수 | 자동 판정 범위 |",
 "|---|---:|---|",
 ]
 descriptions={
 "missing_image_local_references":"HTML img src와 로컬 파일 존재",
 "unresolved_internal_links":"HTML a href와 내부 경로 존재",
 "seo_fields_or_nonself_canonical":"meta description/canonical/H1 기초 구조",
 "cover_social_or_article_image_conflicts":"상세사진과 OG·Article 이미지 문자열 비교",
 "likely_stale_ai_label":"실사 교체 후 AI 문구 잔존 추정",
 "hero_photo_source_visibility_review":"대표사진 뒤 표기 여부만 판별(진위 검증 아님)",
 "cruise_return_language_missing":"기항지 페이지 귀선·재승선 문구 단어 검색",
 "booking_cta_destination_review":"예약 CTA가 일반 홈·콘텐츠로 이동",
 "old_operational_date_context_review":"과거 날짜 인접 운영정보 수동검토 후보",
 "missing_alt":"HTML 이미지 대체텍스트 누락",
 }
 for k,v in output["counts"].items():rows.append("| "+k+" | "+str(v)+" | "+descriptions.get(k,"")+" |")
 rows+=["","## 반드시 구별할 한계","- 스크립트가 식별한 후보는 **오류가 확정되었다는 뜻이 아닙니다**. 본문 표·FAQ·상품이 유효한지는 공식 원자료 별도 대조 필요.","- 로컬 이미지의 존재는 실제 일본 지역을 올바르게 촬영했는지, 저작권 표시가 합법적인지를 증명하지 않습니다.","- 업체 홈페이지를 향한 예약 버튼이 실제 결제까지 연결되는지의 여부는 페이지 탐색과 날짜/인원 입력 단계로 별도 확인해야 합니다.","- **귀선 시각은 선박명·날짜·접안 선석·재승선 마감이 확인된 항차에 대해서만** 쓸 수 있습니다.","","## 원본 상세 목록","[JSON에서 페이지별·링크별 문제 후보 확인](./sitewide-inventory.json)",""]
 (OUT/"README.md").write_text("\n".join(rows),"utf8")
 print(json.dumps({"version":"V132","scope":output["scope"],"counts":output["counts"],"report":"audit-reports/v132/README.md"},ensure_ascii=False))
 return output
if __name__=="__main__":main()
