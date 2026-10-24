# NIPPONFERRY V173 — 기존 기항지 4편 실제 예약·발권과 마지막 귀선 품질 개선

검수일: 2026-10-24 (KST). 기존 4편 수정, 신규 게시글 0편, 원본 이미지 교체 0장.

## 범위
- `site/things-to-do/beppu-cruise-port-day-trip/index.html`
- `site/things-to-do/otaru-cruise-port-day-trip/index.html`
- `site/things-to-do/shimizu-cruise-port-day-trip/index.html`
- `site/things-to-do/hiroshima-cruise-port-day-trip/index.html`

각 기존 안내글에 공식 매표/구매 경로, 이용조건, 최종 귀선 3카드씩 총 12개 추가. 실제 발권 수단이 현장 판매이면 웹예약 가능하다고 거짓 표시하지 않는 원칙 적용. 라이선스·기존 WebP·HTML img src/alt/width/height·SEO title·description·canonical·기존 링크 및 sitemap 보존. 52px 이상 큰 CTA, 모바일 1열·태블릿 2열·PC 3열.

## 운영기관 공식 확인 사실

### 벳푸
- [벳푸지옥조합 공식 7지옥 공통권](https://www.beppu-jigoku.com/fee/index.html): 현장 각 지옥 매표소 구매, 성인 2,400엔/초중학생 1,200엔, 08–17시, 구매일 포함 다음 날까지 유효, 7곳 각 1회 입장. **공식 정보페이지 자체는 온라인 결제창이 아님.**
- [로손티켓 외부 판매처 교환권 L코드 84767](https://l-tike.com/order/?gLcode=84767): 지옥 매표창구에서 실입장권으로 교환해야 하는 상품. 운영기관 직영 웹결제와 다른 환불·교환약관을 비교·확인해야 함. 결제 성공/재고 실측하지 않음.
- [가메노이버스 실제 노선 확인](https://kamenoibus.com/scheduled_howto/) 및 크루즈 제4부두 등 외항 승객 게이트와 일반 터미널 구별.

### 오타루
- [실제 일반 고객용 데이크루즈 사전결제 페이지](https://book.otaru.cc/products/1ebc1dee-2e41-5a6e-b866-dd1e1df95281?lng=ja-JP) 직접 연결. 특별할인/초대권 고객용 현장결제 예약 링크와 구별함.
- [운영사 일반 예약 조건](https://otaru.cc/standardv2/): 60일 전부터 출항 1시간 전까지 웹 예약, 현장 출항 15분 전 매표 마감, 40분 운항, 발권소 중앙교(港町5-4) 15분 전 수속. 취소/변경은 구매 상품 약관 확인.
- [당일 운항/시간표](https://otaru.cc/timetable/)와 크루즈 제3부두·가쓰나이 부두로 별도 돌아가기 안내.
- **오래된 사실 오류 추가 수정:** 2009년 실제 오타루 운하 사진을 AI 생성 참고 이미지라고 잘못 명시한 figcaption과 OG alt를 실제 장소 사진 안내로 변경. 원본 사진 파일·CC BY-SA 출처·촬영정보는 보존.

### 시미즈
- [운영사 수상버스 가격/승선장/시간표](https://www.shimizu-cruise.co.jp/fare/): 히노데는 매표소, 에지리는 참치관 옆 매표기, 미호는 선내 구매·현금만. 수상버스 승선표와 별도의 관광 크루즈 웹 상품 구별.
- 기본 발표표에 미호 **16:35 출항→히노데 16:50 도착** 항차 기재. 해당 항차는 히노데에서 탑승 불가. 실제 기항일 운항·증편·날씨 변수로 절대적인 '보장된 막차'라고 단정하지 않음.
- [선착장 위치](https://www.shimizu-cruise.co.jp/access/). 히노데 등 일반 수상버스 선착장 ≠ 외항 크루즈 히노데 1/2호·오키쓰 게이트.

### 히로시마
- [JR 서일본 미야지마페리](https://jr-miyajimaferry.co.jp/access/): 미야지마구치 현장 매표/자동발권·교통IC 개찰구, 온라인 선박 좌석 구매로 오인 금지.
- [아쿠아넷 미야지마구치–미야지마 별도 운영사 예약페이지](https://www.aqua-net-h.co.jp/miyajimaguchi/reservation/): 웹예약 전날 20:30 마감, 예약 후 출항 15분 전까지 현장 승선권 구매 필요, 출항 5분 전 승선장 도착. 일부 왕복편은 귀항 출항 10분 전 집결, 예약=구매 완료가 아님.
- [하쓰카이치시 미야지마 방문세](https://www.city.hatsukaichi.hiroshima.jp/soshiki/9/108494.html) 1인 100엔(원칙)과 운임 포함 방식. 미야지마구치 도착 후 실제 크루즈 하선항(우지나/이쓰카이치 등)으로 육상 이동 추가.

## 최종 검증
- HTML 수정 커밋 [85fca323275b4b943e87a3b4fdfcc0dd0ba91991](https://github.com/mouk30/japan/commit/85fca323275b4b943e87a3b4fdfcc0dd0ba91991).
- GitHub Actions 최종 [40099030583](https://github.com/mouk30/japan/actions/runs/40099030583): 원본 SEO/라이선스·이미지 비교 및 `node build.js` PASS, 실제 공개 Chromium 검사 **390·768·945·1440px × 4페이지 = 16/16 PASS**, 스크린샷 16장·JSON 결과 artifact 두 개 저장.
- Vercel 배포 SUCCESS(HTML 변경 커밋 기준 확인).
- 원본 링크 전체 보존, 새로운 글/URL/사이트맵 증설 없음.

## 남은 범위/다음 품질 단계
공식 매표 규정·링크 및 페이지 출력은 검증했으나 개인 계정 결제·실제 좌석 구매 성공, 각 항차의 당일 결항/최종 귀선 승객 마감시각, 크루즈 전용 셔틀 유무 및 실측 GA4/GSC 클릭수는 검증되지 않음. 다음에는 계속 기존 글 중 **정보 페이지를 구매 화면처럼 표시하는 버튼**, **정기선과 크루즈 항만 혼동**, **실제 귀선 차량의 누락**을 우선 점검한다.
