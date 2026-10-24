#!/usr/bin/env python3
"""V167 follow-up: original Tokyo venue photos must have subject-matched alt.
Compare each entire original HTML against the exact pre-correction Git SHA,
allow ONLY the img alt string change; metadata, licences, structure and URLs
are immutable. Never claim source photo copyright or identity re-verified.
"""
from pathlib import Path
from html.parser import HTMLParser
import subprocess,json
BASE="fcfdc26b22b1183acf914731bfade5dc7fab23f4"
CHANGES={
 "tokyo-autumn-gardens":("Meiji Jingu Gaien Ginkgo Festival (53440769967).jpg 관련 역 사진","도쿄 메이지진구 가이엔 은행나무 축제 현장을 촬영한 사진"),
 "tokyo-firsttime-east-west":("People at the Asakusa Sensoji Kaminarimon entrance.jpg 관련 역 사진","도쿄 아사쿠사 센소지 가미나리몬 입구에서 이동하는 사람들"),
 "tokyo-electronics-bic-yodobashi":("Bic Camera Shinjuku Station East.jpg 관련 역 사진","신주쿠역 동쪽 출구 인근 빅카메라 전자제품 매장 실제 사진"),
 "tokyo-tsukemen-howto":("Tsukemen.jpg 관련 역 사진","면을 진한 국물에 찍어 먹는 일본 츠케멘 음식 사진"),
 "disneyland-beauty-beast-ride":("Tokyo Disneyland Enchanted Tale of Beauty and the Beast (53440869377).jpg 관련 역 사진","도쿄디즈니랜드 미녀와 야수 어트랙션 실제 현장 사진"),
 "shibuya-parco-floor-guide":("Shibuya Parco 2020.jpg 관련 역 사진","2020년 실제 촬영된 도쿄 시부야 PARCO 복합 쇼핑몰"),
 "daikanyama-bookshops":("Daikanyama T-Site (52501035177).jpg 관련 역 사진","도쿄 다이칸야마 T-SITE 서점과 복합 문화시설 실제 사진"),
 "shinjuku-kabukicho-donki":("Don Quijote Shinjuku.JPG 관련 역 사진","신주쿠 가부키초 주변 돈키호테 매장 실제 사진"),
 "donki-roppongi-night-check":("Don Quijote Roppongi Store-2012.jpg 관련 역 사진","2012년 촬영된 도쿄 롯폰기 돈키호테 매장 외관"),
 "tokyo-summer-heat-indoor":("On the way to Sunshine City サンシャインシティ in Ikebukuro, Tokyo, Japan (26295481219).jpg 관련 역 사진","도쿄 이케부쿠로 선샤인시티로 이동하는 거리의 실제 풍경"),
 "asakusa-operators":("Asakusa Station Toei subway entrance A1.jpg 관련 역 사진","도에이 지하철 아사쿠사역 A1 출입구 실제 현장 사진")
}
class Img(HTMLParser):
 def __init__(self):
  super().__init__();self.img=[];self.links=[]
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if t=="img":self.img.append(d)
  if t=="a":self.links.append(d.get("href",""))
def parse(s):
 x=Img();x.feed(s);return x
fail=[];rows=[]
for slug,(old_alt,new_alt) in CHANGES.items():
 path=f"site/japan/tokyo/{slug}/index.html"
 before=subprocess.check_output(["git","show",f"{BASE}:{path}"],text=True)
 after=Path(path).read_text("utf-8")
 oldtag='alt="'+old_alt+'"'
 newtag='alt="'+new_alt+'"'
 now=parse(after);orig=parse(before)
 checks={
  "original_exact_other_than_image_alt": before.replace(oldtag,newtag)==after and before.count(oldtag)==1,
  "wrong_station_alt_gone":oldtag not in after,
  "single_correct_subject_alt":after.count(newtag)==1,
  "all_original_photo_sources_and_links": [z.get("src") for z in now.img]==[z.get("src") for z in orig.img] and now.links==orig.links,
  "Wikimedia_photo_source_kept": any("commons.wikimedia.org/wiki/File:" in (z or "") for z in now.links),
  "no_changed_filename_assets_or_pages":len(now.img)==len(orig.img)==1
 }
 rows.append({"slug":slug,"checks":checks})
 if not all(checks.values()):fail.append({"slug":slug,"bad":[k for k,v in checks.items() if not v]})
 print("PASS" if all(checks.values()) else "FAIL",slug,flush=True)
out=Path("audit-output/v167-alt");out.mkdir(parents=True,exist_ok=True)
report={"version":"V167-subject-match","updated_existing_pages":len(CHANGES),"new_articles":0,"image_file_replacements":0,"all_other_original_file_text_exact":not fail,"failures":fail,"pages":rows}
(out/"tokyo-eleven-originals-exact-alt-match.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SUMMARY",len(rows)-len(fail),"/",len(rows),flush=True)
if fail:raise SystemExit(1)
