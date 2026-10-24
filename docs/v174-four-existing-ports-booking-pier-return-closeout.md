# NIPPONFERRY V174 — 기존 기항지 예약 버튼·실제 부두·귀선 정보 검증 완료

기준일: 2026-10-24 KST.
**기존 글 4편 보강, 신규 글 0편, 원본 사진 파일 수정 0건, 이미지·출처·URL·SEO·sitemap 변경 0건.**

## 실제 변경된 파일

- `site/things-to-do/yokohama-cruise-port-day-trip/index.html`
- `site/things-to-do/kanazawa-cruise-port-day-trip/index.html`
- `site/things-to-do/akita-cruise-port-day-trip/index.html`
- `site/things-to-do/kushiro-cruise-port-day-trip/index.html`

기존 메인 이미지 바로 아래에 항만/예약과 귀선 3카드씩 총 12개를 추가. 예약·취소/영업조건·안전 귀선 링크 3종, 중노년 이용자를 위한 명확한 52px 이상 CTA, 모바일 1열/태블릿 2열/PC 3열.

## 운영기관 확인·수정 내용

### 요코하마
- [마린루주 운영사 실제 예약 절차](https://yokohama-cruising.jp/rouge/reservation/): 15명 미만 승선만 하는 일반 승객은 사전예약이 아닌 현장매표, 식사·뷔페 상품과 15명 이상 단체는 공식 웹/전화 사전예약 045-662-6125.
- 개인 예약 취소 수수료: 이용 이틀 전~전날 50%, 당일 100%; 세부 상품 결제조건은 운영사 상품별로 재확인.
- [운항상황](https://yokohama-cruising.jp/operation/)은 정비 후 개별 날짜별 확인. 2026-09-29~10-02 운휴 이력은 이후 모든 날짜 결항 확정이 아님.
- [마린루주 관광선 피어 아카렌가](https://yokohama-cruising.jp/rouge/access/)는 외항 크루즈의 오산바시·신코·다이코쿠와 다름. 관광선 수속 15분 전, 별도 귀선 차량 안내.

### 가나자와
- [21세기 미술관 스위밍 풀 지상/지하 2026-10-19~10-30 폐장](https://www.kanazawa21.jp/data_list.php?d=1&g=120).
- 재개 시 지하 관람은 **방문 당일 오전 9시부터 별도 시간대 예약** + 전시 관람권 구매의 2단계. 20분 호출 불응 자동 취소, 전화예약 불가.
- [2026-10-31 개막 예정인 '오늘부터 내일로' 전시 실제 티켓 판매처](https://www.asoview.com/channel/ticket/TEPUUS2F0o/ticket0000057382/) 직접 링크. 오래된 e-tix는 현재 미판매, 신규 전시의 구매 페이지 및 이용일·잔여좌석 표시 재확인. '미술관 무료 교류구역'과 유료 전시권도 구별.
- [호쿠리쿠철도 2026 최신 버스 시간표](https://www.hokutetsu.co.jp/route-bus/timetable/). 가나자와 크루즈터미널(무료지마마치 리-65)은 일반 시설, 별도 오하마 접안이면 동일 정류장·귀선 게이트 아님.

### 아키타
- [셀리온 전망대 실제 무료입장](https://www.selion-akita.com/facility/): 전망대 09:00~21:00, 마지막 입장 20:50. 상점/식당·유료 대관과 분리, 유료 입장권 예약 버튼으로 속이지 않음.
- [아키타중앙교통 2026-10-01 개정](https://www2.akita-chuoukotsu.co.jp/news.php). JR 아키타역 서쪽 4번 승강장–셀리온 방향 일반 유료버스 계통 115, 복귀방향·요일별 마지막 시각 확인, 예전 시간표 고정으로 인한 귀선 실패 방지.
- [신일본해페리 안내](https://faq.snf.jp/%E9%80%A3%E7%B5%A1%E3%83%90%E3%82%B9%EF%BC%88%E7%A7%8B%E7%94%B0%EF%BC%89-6a83a89a6119dc3d97fbf75c): 일반 버스는 정기선 지연을 기다리지 않으며 정기페리터미널·셀리온 정류장은 외항 크루즈 전용 부두/셔틀과 별개.

### 구시로
- [구시로 습원 2026 카누 직접 신청 양식](https://mizu-no-kamuy.com/reservation/form/28) 연결. 2026-05-07~10-31 운영 예정; 11:00 출발, 10:50 집합, 약 2시간, 체험 약 80분.
- [구시로 관광 공식 상품 조건](https://ja.kushiro-lakeakan.com/things_to_do/14182/): 성인 10,000엔/초등학생 6,500엔, 최소 2명·정원 8명, 현금 현장결제. 전일 최종전화 확인, 집결지와 차량·환불은 예약처 공지 따름.
- [구시로시 공식 동항·서항 접안 구분](https://www.city.kushiro.lg.jp/sangyou/umisora/1006541/1006598/1012111.html): 동항 내진·여객선터미널 또는 서항 제4부두. 구시로 MOO/시내 선착장에 도착했다고 대형 크루즈 귀선 완료 아님. 실제 선사 귀선게이트에 택시·셔틀로 복귀.

## 커밋·QA 결과

- 콘텐츠/검사 도입: [28601ff0905d94808c4fb92ff8bc3ea905fa1abe](https://github.com/mouk30/japan/commit/28601ff0905d94808c4fb92ff8bc3ea905fa1abe)
- 검사 스크립트 최종 보정: [f6388d612bdff44e1b7cd718e94aa6e97fd96b2d](https://github.com/mouk30/japan/commit/f6388d612bdff44e1b7cd718e94aa6e97fd96b2d)
- 최종 GitHub Actions: [40103903282](https://github.com/mouk30/japan/actions/runs/40103903282) — source regression·원본 포토/SEO/기존 링크·빌드 성공, **공개 Chromium 4페이지 × 390/768/945/1440 = 16/16 성공**.
- 공개 사이트 16장 스크린샷 및 JSON은 `v174-public-four-port-sixteen-screens` artifact (3,851,912 bytes). QA source result `v174-original-source-4` (430 bytes).
- Vercel deployment: **success**, 커밋 `f6388d612bdff44e1b7cd718e94aa6e97fd96b2d`.
- 1차 source regression에서 가나자와 공식 URL query string HTML `&amp;`와 원문 `&`를 다르게 비교해 3/4 실패. 웹 페이지 링크 오류 아님. 디코딩 비교 수정 후 **4/4 성공**, 최종 16/16 공개 브라우저 성공.

## 별도 확인이 필요한 항목

공식 연결은 직접 확인했고 사진/웹 렌더링도 검사했으나, 실제 신청서 제출·로그인·개인 결제 성공/잔여석, 10월 31일 이후 일정의 현장 사용 가능성, 항차별 크루즈 최종 탑승 마감·마지막 셔틀·택시 확보는 검증한 것이 아님. 여행일의 운영사·항만당국/선사 최신 공지가 최종 기준.

## 후속 V175

신규 콘텐츠 증산 없이 기존 상세페이지의 **'예매' 버튼이 운영기관 정보 포털에만 연결되는 사례, 날짜별 예약 조건, 귀선 목적지/마지막 교통 누락**을 우선 검수하고 실제 사용자 동선까지 단축한다.
