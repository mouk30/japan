import json,pathlib,re,html
slugs=json.loads("[\"disneyland-beauty-beast-ride\",\"disneyland-baymax-happy-ride\",\"disneyland-splash-mountain\",\"disneyland-big-thunder-mountain\",\"disneyland-pooh-hunny-hunt\",\"disneyland-monsters-inc\",\"disneyland-haunted-mansion-season\",\"disneysea-frozen-ever-after\",\"disneysea-peter-pan-adventure\",\"disneysea-rapunzel-lantern\",\"disneysea-soaring-flight\",\"disneysea-toy-story-mania\",\"disneysea-tower-of-terror\",\"disneysea-journey-center-earth\",\"disney-miracosta-hotel\",\"disney-fantasy-springs-hotel\",\"disney-toy-story-hotel\",\"disney-ambassador-hotel\",\"disney-celebration-hotel\",\"disney-vacation-package-vs-regular\"]")
data=json.loads("[[\"미녀와 야수: 마법 이야기\",\"도쿄 디즈니랜드 판타지랜드. 유료 DPA 대상이며 공식 안내 요금은 1회 2,500엔입니다.\",\"정해진 이용시간을 우선 고려하고, 매진 시 일반 대기열 운영 여부를 앱에서 확인하세요.\"],[\"베이맥스 해피 라이드\",\"도쿄 디즈니랜드 투모로우랜드. DPA 대상이며 공식 안내 요금은 1회 1,500엔입니다.\",\"회전·급격한 방향 변화에 민감한 동행자는 탑승 제한 및 안전 안내를 먼저 읽으세요.\"],[\"스플래시 마운틴\",\"도쿄 디즈니랜드 크리터 컨트리. 물 튀김과 낙하 구간이 있는 어트랙션이며 DPA 대상입니다.\",\"젖을 수 있는 옷·소지품을 고려하고 어린이 키 제한·안전 기준을 확인하세요.\"],[\"빅선더 마운틴\",\"도쿄 디즈니랜드 웨스턴랜드의 야외 롤러코스터이며 DPA 대상입니다.\",\"빠른 회전·충격이 있으므로 건강상 제한과 실제 운휴 여부를 확인하세요.\"],[\"푸의 허니헌트\",\"도쿄 디즈니랜드 판타지랜드의 탑승형 어트랙션이며 DPA 대상에 포함됩니다.\",\"어린이와 이용할 때는 혼자 앉는 조건·탑승 자세를 확인하고 대기시간을 비교하세요.\"],[\"몬스터 주식회사 라이드 앤 고 시크\",\"도쿄 디즈니랜드 투모로우랜드. 공식 DPA 대상이며 안내 요금은 1회 1,000엔입니다.\",\"놀이기구와 퍼레이드의 예약·대기 시스템이 다르므로 앱에서 대상 시설을 구분하세요.\"],[\"헌티드 맨션\",\"도쿄 디즈니랜드 판타지랜드. 공식 안내상 DPA 적용 기간은 2026년 9월 15일~2027년 1월 7일입니다.\",\"어두운 실내와 무서운 연출이 있으므로 어린아이 동반 시 체험 적합성을 먼저 판단하세요.\"],[\"프로즌 에버 애프터\",\"도쿄 디즈니씨 판타지 스프링스의 프로즌 테마 보트형 어트랙션입니다.\",\"판타지 스프링스 구역 진입과 개별 어트랙션 대기·DPA 판매는 분리해 확인하세요.\"],[\"피터팬 네버랜드 어드벤처\",\"도쿄 디즈니씨 판타지 스프링스의 3D·움직임 효과가 있는 어트랙션입니다.\",\"멀미·3D 영상에 민감한 동행자는 사전 탑승 주의사항을 확인하세요.\"],[\"라푼젤 랜턴 페스티벌\",\"도쿄 디즈니씨 판타지 스프링스의 라푼젤 테마 어트랙션입니다.\",\"야간 풍경을 보장하는 예약 상품이 아니며, 일몰과 실제 탑승 시간·대기는 달라질 수 있습니다.\"],[\"소어링: 판타스틱 플라이트\",\"도쿄 디즈니씨 메디테러니언 하버의 비행 시뮬레이션 어트랙션입니다.\",\"높이감·영상 움직임에 민감하면 주의사항을 확인하고 DPA 재고를 앱에서 조회하세요.\"],[\"토이 스토리 마니아!\",\"도쿄 디즈니씨 아메리칸 워터프런트의 슈팅 게임형 어트랙션입니다.\",\"가족 동반 시 체험 시간보다 대기 시간이 클 수 있으며, DPA 가능 여부를 앱에서 확인하세요.\"],[\"타워 오브 테러\",\"도쿄 디즈니씨 아메리칸 워터프런트의 급하강 스릴 어트랙션입니다.\",\"높이·건강상 탑승 제한과 어린이 동반 가능 여부를 현장 기준으로 확인하세요.\"],[\"센터 오브 디 어스\",\"도쿄 디즈니씨 미스테리어스 아일랜드의 스릴 어트랙션입니다.\",\"속도·낙하감을 예상하고 키 제한·운휴 여부·DPA 대상 여부를 공식 앱에서 확인하세요.\"],[\"호텔 미라코스타\",\"도쿄 디즈니씨 파크에 인접한 디즈니 호텔로, 디즈니씨 해피엔트리 대상입니다.\",\"디즈니씨 특별입구는 파크 엔트런스 노스이며 호텔 객실 예약과 파크 티켓은 별도 조건입니다.\"],[\"판타지 스프링스 호텔\",\"그랜드 샤토와 판타지 샤토 두 건물로 구분됩니다.\",\"디즈니씨 해피엔트리에서 그랜드 샤토 게이트웨이와 판타지 스프링스 엔트런스가 달라 예약한 건물에 맞는 출입구를 사용해야 합니다.\"],[\"토이 스토리 호텔\",\"디즈니리조트 호텔 중 하나이며 디즈니랜드 해피엔트리 대상입니다.\",\"2026년 공식 호텔별 표 기준 디즈니씨 해피엔트리는 대상이 아니며, 파크 이동에는 리조트라인 등 교통을 확인하세요.\"],[\"디즈니 앰배서더 호텔\",\"디즈니리조트 호텔로 디즈니랜드 해피엔트리 대상입니다.\",\"디즈니씨 해피엔트리 대상은 기간에 따라 달라질 수 있으므로 현재 공식 표를 우선하고, 파크 셔틀·조식은 객실 상품별로 확인하세요.\"],[\"디즈니 셀러브레이션 호텔\",\"파크 주변 호텔들과 위치·이동시간이 다른 숙소로, 디즈니랜드 해피엔트리 대상입니다.\",\"호텔 셔틀의 승차 위치·첫차·막차를 확인하고, 디즈니씨 해피엔트리 대상 여부를 혼동하지 마세요.\"],[\"베케이션 패키지와 개별 예약\",\"베케이션 패키지는 호텔 숙박·파크 티켓·어트랙션 관련 혜택을 묶은 별도 예약 상품입니다.\",\"객실 단독 예약에는 파크 티켓·DPA 등이 자동 포함되는 것이 아니므로 패키지 구성표와 취소 규정을 항목별로 비교하세요.\"]]")
root=pathlib.Path("site/japan/tokyo")
report=[]
for i,(slug,(title,a,b)) in enumerate(zip(slugs,data),101):
 p=root/slug/"index.html"
 assert p.exists(),slug
 text=p.read_text(encoding="utf-8")
 assert "tokyo-editorial-v101" not in text,slug
 url="https://www.tokyodisneyresort.jp/en/hotel/topics/info/happy_entry" if 115<=i<=119 else ("https://www.tokyodisneyresort.jp/en/hotel/dh.html" if i==120 else "https://www.tokyodisneyresort.jp/en/tdr/guide/app_service/disneypremieraccess.html")
 section='<section class="tky-block tokyo-editorial-v101" id="specific-guide"><h2>'+html.escape(title)+' · 실전 이용정보</h2><p>'+html.escape(a)+'</p><p>'+html.escape(b)+'</p><p><a href="'+url+'" target="_blank" rel="noopener noreferrer">도쿄 디즈니리조트 공식 운영·특전 정보 ↗</a></p><p class="tky-dated">2026년 10월 기준 참고사항. 운휴, DPA 판매, 호텔 혜택 적용일, 입구 변경은 공식 앱·홈페이지에서 최종 확인.</p></section>'
 text=text.replace("<article>","<article>"+section,1)
 removed=[]
 for label,pattern in [
 ("intro",r'<section class="tky-block"><div class="tky-dated">.*?<h2>이 주제를 선택하기 전에</h2>.*?</section>'),
 ("route",r'<section class="tky-block" id="plan"><h2>시간 낭비를 줄이는 실제 여행 동선</h2>.*?</section>'),
 ("tickets",r'<section class="tky-block" id="tickets"><h2>가격·영업시간·예약에서 놓치기 쉬운 조건</h2>.*?</section>'),
 ("faq",r'<section class="tky-block"><h2>자주 묻는 질문</h2>.*?</section>'),
 ("generic",r'<section class="tky-block"><h2>방문자가 가장 많이 혼동하는 세 가지</h2>.*?</section>'),
 ("field",r'<section class="tky-block tokyo-field-check-v307"[^>]*>.*?</section>')
 ]:
  text,n=re.subn(pattern,"",text,count=1,flags=re.S)
  if n:removed.append(label)
 text=text.replace('href="#plan"','href="#specific-guide"').replace('href="#tickets"','href="#specific-guide"')
 p.write_text(text,encoding="utf-8")
 report.append({"v":i,"slug":slug,"removed":removed})
audit={"updated":len(report),"removed_boilerplate":sum(len(x["removed"]) for x in report),"photo_manual_review":[110,111,116],"items":report,"caveat":"Specific official DPA and hotel rules referenced; individual attraction safety requirements, photos and live public page remain to be visually verified."}
pathlib.Path("audit-reports/tokyo-v101-v120-editorial-upgrade.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"updated":audit["updated"],"removed":audit["removed_boilerplate"]}))
