# 도쿄 V121~V300 — 아침 검수·수정 인계서
기준일: 2026-10-17 (KST) · GitHub: `mouk30/japan` · 배포: https://www.nipponferry.com/japan/tokyo/

## 실제 완료 범위
- V81~V120 기존 도쿄 40편 유지, V121~V300 **신규 도쿄 상세 글 180편**, **도쿄 총 220편**.
- 신규 9개 분야 × 20편: 역별 출구, 노선/패스, 디즈니 입장권/예약, 디즈니 어트랙션/호텔, 백화점 층별, 돈키호테/쇼핑, 도쿄 동네, 식도락/문화, 가족/크루즈 일정.
- 도쿄 허브에 접기/펴기 카테고리 9개, 총 전문 카드 220개 연결. 기존 인기 여행지 도쿄 카드·실사 사진·SEO 주소 유지.
- 신규 상세 URL 180개 sitemap.xml에 추가. 기존 40개 글을 덮어쓰지 않음.
- 732개 반응형 브라우저 화면 테스트 (180×4 + 홈·지역·도쿄허브 3×4) 통과.
- 공개 도메인 223개 문서 (180 신규+40 기존+3 허브/홈) 모두 200 응답·새 콘텐츠 표시 확인.
- 공식 자료 URLs 53개 검사: HTTP 정상 51, 404 0, **자동검사 접근제한 2** (돈키호테 지점 검색 `https://www.donki.com/en/store/`, 핸즈 `https://hands.net/`). 실제 접속 환경에서 다시 확인 필요.

## 확인할 수 있는 대표 도쿄 글
- 디즈니 DPA 구입·환불: https://www.nipponferry.com/japan/tokyo/disney-dpa-app-purchase/
- 디즈니 해피엔트리 적용 호텔: https://www.nipponferry.com/japan/tokyo/disney-happy-entry-hotel-list/
- 이세탄 B1 식품관: https://www.nipponferry.com/japan/tokyo/isetan-shinjuku-b1-food/
- 다이마루 12층 면세·식당: https://www.nipponferry.com/japan/tokyo/daimaru-tokyo-12f-taxfree/
- 도부 이케부쿠로 식당가: https://www.nipponferry.com/japan/tokyo/tobu-ikebukuro-restaurants/
- 시부야 돈키호테: https://www.nipponferry.com/japan/tokyo/shibuya-mega-donki-by-floor/
- 국제크루즈터미널 3시간 코스: https://www.nipponferry.com/japan/tokyo/tokyo-cruise-odaiba-3hours/

## 반드시 해야 할 2차 현장 수준 품질 검사 (우선순위)
1. **사진 정확성**: 180편의 개별 장소 전용 실물 사진을 모두 확보하지는 못함. 기존 도쿄 허브의 실제 야경 사진만 검증됨. 웹에서 장소별 사진의 실제 시설·저작권 출처를 확보하고 WebP로 전환하는 단계 필요. 범용 도쿄 야경을 개별 장소 사진인 것처럼 쓰지 않음.
2. **시설 직접 출처**: 73편은 일반 관광포털·관광지도·도시철도 공식 노선도·일반 식도락 포털처럼 범위가 넓은 공식 출처를 안내. 특히 V241~V260 도쿄 동네(18/20), V261~V280 미식·문화(15/20), V281~V300 동행 코스(14/20)는 **개별 장소/업체의 정확한 공식 페이지**로 단계적 교체 권장. 도쿄메트로 노선도 링크는 노선정보에 실질적 도움을 주므로 일괄 삭제할 필요 없음.
3. **디즈니 티켓 판매조건**: 1일권, DPA, 무료 우선입장, 호텔 특전, 기간 한정 호퍼 여권의 현재 판매 여부·적용 파크·예약 가능 날짜·취소 가능성 매일 변경 가능. 글에서 상시 적용이라고 단정한 부분이 없는지 점검.
4. **백화점 층별 지도**: 실제 공식 지도에서 확인한 B1·1F·B2·식당층 등은 넣었음. 그러나 전체 20편의 브랜드별 개별 점포명·현행 입점 층별 도면은 지속 변동하므로 방문일 기준 정밀 대조, 면세 카운터 마감 확인.
5. **지하철 역별 출구**: 기존에는 출입구 권역 중심. 실제 출구 번호·엘리베이터 우회 동선·운영사 변경 공지는 시설별 공식 역 안내와 대조할 것.
6. **크루즈 안전**: 항차별 하선 시간, 무료 셔틀 제공, 귀선 마감, 실시간 정박부두는 **직접 확인되지 않았으므로 페이지에서 확정 값으로 쓰지 않음**.

## 감사(검수) 보고서
- 전체 신규 글/카테고리: `audit-reports/v121-v300/editorial-manifest.json`
- 9개 버전 각 20편: `audit-reports/v121-v300/batch-v121-v140.json` 등
- 모바일/PC 732 화면: `audit-reports/v121-v300/browser-qa.json`
- 223개 공개 URL: `audit-reports/v121-v300/live-production.json`
- 공식 링크(53개) 상태: `audit-reports/v121-v300/official-sources-qa.json`

참고: 페이지 수·HTTP 200·반응형 검사 통과는 검색 순위 상승, 예약 가능, 개별 매장 재고 또는 매년 동일한 가격을 보증하지 않습니다. 정보의 진위·지속성·사진의 정확도는 사용자의 실제 여행 날짜에 맞춰 추가 검수해야 합니다.
