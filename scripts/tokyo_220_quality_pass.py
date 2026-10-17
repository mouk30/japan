#!/usr/bin/env python3
"""Tokyo 220 editorial quality pass: unique article checklists, no unverified images.
Does NOT certify live operation, official-link validity or photo licences."""
from pathlib import Path
import re,html,json,datetime
root=Path("site/japan/tokyo")
files=sorted(root.glob("*/index.html"))
assert len(files)==220, f"Expected 220 Tokyo articles; got {len(files)}"
def category(slug):
    if re.search(r"disney|maihama|fantasy.springs|happy.entry|dpa",slug):return ("파크 입장권과 별도 유료·추첨·우선 입장 서비스를 구분","방문일 공식 앱·호텔 안내에서 대상 시설·시간·이용 가능 인원 확인")
    if re.search(r"station|metro|line|rail|train|subway|airport|transfer|bus|keiyo|yurikamome|chiyoda|shinkansen",slug):return ("공식 노선도에서 출발역·도착역·개찰구와 실제 출구 위치 확인","환승 시간·운임·막차·엘리베이터 운영을 방문일 기준 확인")
    if re.search(r"daimaru|isetan|mitsukoshi|department|taxfree|donki|shopping|loft|muji|floor|ginza|takashimaya|hands",slug):return ("공식 층별 안내에서 실제 지점·매장·층을 각각 확인","면세·할인·식품관 영업시간은 해당 지점의 최신 공지로 확인")
    if re.search(r"food|sushi|ramen|coffee|market|restaurant|cafe|meal|soba|yakitori|izakaya|bento|tsukiji|dessert",slug):return ("실제 점포·시장 위치와 영업일·메뉴 및 줄서기 방식을 확인","식품 알레르겐·예약 필요 여부와 매장별 계산 방식을 확인")
    if re.search(r"cruise|pier|terminal|port|harumi",slug):return ("항차 문서에 적힌 실제 접안 부두·하선 위치를 확인","귀선 마감 시각과 여유시간을 반영해 이동 동선을 역산")
    if re.search(r"tower|sky|observ|view|ticket|museum|teamlab|attraction",slug):return ("운영처 공식 페이지에서 실제 시설명·입장권 적용 구역 확인","일자·시간별 가격 및 입장 제한·취소 조건을 결제 직전에 확인")
    return ("운영기관의 시설명·출입구·지도상 위치를 먼저 확인","방문일 운영시간·이동 동선·예약 조건을 공식 안내에서 재확인")
changed=0
report=[]
for path in files:
    content=path.read_text(encoding="utf-8")
    slug=path.parent.name
    title=re.search(r"<h1[^>]*>(.*?)</h1>",content,re.S)
    title=html.unescape(re.sub("<[^>]*>","",title.group(1))) if title else slug
    description=re.search(r'<meta name="description" content="([^"]*)"',content)
    desc=html.unescape(description.group(1)) if description else title
    links=re.findall(r'<a[^>]+href="(https://[^"]+)"',content)
    source=next((u for u in links if "nipponferry.com" not in u),"")
    a,b=category(slug)
    desc=desc[:225].rstrip()
    block='<section class="tky-block tokyo-field-check-v307" aria-label="여행 전 실전 확인"><h2>이 글의 현장 확인표 · '+html.escape(title)+'</h2><p><strong>확인할 핵심:</strong> '+html.escape(desc)+'</p><ol><li>'+a+'</li><li>'+b+'</li><li>이동·예약·결제 전에 방문일의 공식 원문과 세부 규정을 최종 대조합니다.</li></ol><p><strong>사진 검수 상태:</strong> 실제 시설·장소가 식별되고 원본 출처와 사용권이 확인되기 전에는 유사 사진을 대체 썸네일로 게시하지 않습니다.</p>'
    if source:block+='<p><a href="'+html.escape(source,quote=True)+'" target="_blank" rel="noopener noreferrer">게시글에 연결된 운영처·관련 원문 확인 ↗</a></p>'
    else:block+='<p>운영기관 직접 확인 링크가 없으므로 현장 이용조건 미검증으로 분류합니다.</p>'
    block+='<p class="tky-dated">문서 검토 기준: 2026-10-17 · 실시간 운영조건·링크 정상작동·전용사진은 별도 검증 항목</p></section>'
    changed_here=False
    if "tokyo-field-check-v307" not in content and "</article>" in content:
        content=content.replace("</article>",block+"</article>",1)
        changed_here=True
    if "도쿄 전체 40편" in content:
        content=content.replace("도쿄 전체 40편","도쿄 전체 220편")
        changed_here=True
    if changed_here:path.write_text(content,encoding="utf-8");changed+=1
    report.append({"slug":slug,"title":title,"official_link_in_existing_html":source,"editorial_checklist_present":"tokyo-field-check-v307" in content,"photo_verified":False,"real_time_conditions_verified":False})
assert len(report)==220
out=Path("audit-reports/tokyo-220-editorial-pass.json")
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps({"pages":220,"updated_this_run":changed,"meaning":"editorial checklist, not factual or image certification","items":report},ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"total":len(report),"changed":changed,"with_source":sum(bool(x["official_link_in_existing_html"]) for x in report),"no_source":sum(not x["official_link_in_existing_html"] for x in report)},ensure_ascii=False))
