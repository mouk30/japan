# V175 — 4개 기존 기항지 발권·공식 운영·마지막 귀선 수정 완료

검수 기준일: **2026년 10월 25일(한국시간)**.
대상은 미야코·이시노마키·도바·하치노헤 **기존 게시글 4편**, 신규 게시글 **0편**입니다.

## 실제 수정 범위

1. `site/things-to-do/miyako-cruise-port-day-trip/index.html`
2. `site/things-to-do/ishinomaki-cruise-port-day-trip/index.html`
3. `site/things-to-do/toba-cruise-port-day-trip/index.html`
4. `site/things-to-do/hachinohe-cruise-port-day-trip/index.html`

각 상세페이지 대표 이미지 직후에 시설별 실전정보 3개씩 **총 12개 카드**(직접 예약 또는 현장 매표·운영기간/약관·귀선 동선)를 추가. 기존의 '입장·예약 운영기관 안내 확인'이라는 잘못된 항만 정보 포털 CTA 4개를 해당 시설의 공식 구매 진입·현장 접수·휴관·행사 개최일 링크로 교체. 버튼 52px 이상, 모바일 1열·태블릿 2열·PC 3열.

## 공식 자료 기준 주요 변경

### 미야코
- [미야코 관광협회 청의 동굴 소형 사파선](https://kankou385.jp/spots/aonodoukutsu-sappasen-taiken/): 3~11월 약 20분, 1인 2,000엔, **예약 불필요, 마린하우스에서 현장 신청**. 온라인 결제 링크가 아님.
- [별도 관광선 미야코 우미네코마루 시간표/현장 매표소](https://www.jodo-yuransen.jp/timetable/): 데사키~조도가하마 만내 관광 1,800엔, 수상교통 600엔. 조도가하마→데사키 10월 기준 15:30→16:00가 막차 예정(10월 7번편 운휴). 실제 당일 운항·결항과 대형 크루즈 하선 선석은 별도.
- [데사키부두·조도가하마 승선장 위치](https://www.jodo-yuransen.jp/access/)로 관광선 도착 후 대형 크루즈 원래 부두로 복귀 차량 판단.

### 이시노마키
- [이시노모리 만화관 전관 휴관 공식 공지](https://www.mangattan.jp/manga/open/): **2026-10-19~2027-01-08** 전체 휴관; 1월 9일 이후 제한 운영, 3층 2027년 4월 초까지 제한. 휴관일 입장권 구매 금지.
- [공식 입장권 요금·환불 제한](https://www.mangattan.jp/manga/ticket/): 성인 1,300엔, 중고생 600엔, 초등생 400엔. 사전 판매처는 구매 후 환불·변경 불가 상품이 존재. 현재 휴관 중 입장 가능한 티켓처럼 연결하지 않음.
- [이시노마키 역→만화관 도보 12분 안내](https://www.mangattan.jp/manga/access/), 외부 만화로드 산책 대안, 항만 원래 승객 게이트·마지막 차량 별도 확인.

### 도바
- [도바 수족관 공식 입장 요금과 웹티켓 구매 진입](https://aquarium.co.jp/ryoukin/): 성인 2,800엔·초중학생 1,600엔·3세 이상 800엔, 웹티켓은 공식 홈→Webket 사이트로 이동; 실제 결제 완료 아님.
- [2026년 9월 30일 판매 종료 묶음 할인권](https://aquarium.co.jp/ryoukin/coupon.html)을 현재 예약상품으로 착각하지 않도록 별도 안내.
- [2026 대형 크루즈 도바 마린터미널 앞바다 정박 사례](https://www.tobanoyado.com/event.php): 해상 텐더 집결·마지막 배·관광 시설 위치를 구분. 출항시간 ≠ 텐더 승객 귀선 마감.

### 하치노헤
- [다테하나 시장 2026 공식 개최표](https://minatonichiyouasaichikai.com/533/): 3월 중순~12월 일요일 새벽~오전 8:30경, 임시 개최/휴시장 예외. 유료 온라인 입장권 상품이 아님.
- [이사바호 2026 순환버스](https://visithachinohe.com/stories/asaichi-junkan-bus/): 4/5~12/27 일요일, 시내↔시장 왕복 각 4편, 성인 150~200엔. 크루즈 외항 보안부두 무료 셔틀과 다름.
- [아오모리현 2026-10-20 하치노헤항 공식 입항 공지](https://www.pref.aomori.lg.jp/soshiki/kendo/ha-kokan/asuka.html): 2026-11-06 금요일 아스카Ⅲ의 하타로 4호부두 P안벽 접안 예정. 금요일 아침시장 개최를 잘못 안내하지 않음. 당일 실제 입항/승객 게이트는 재확인.

## 수정/QA 이력
- 기존 4편 콘텐츠 수정 커밋 [65853795721d6e5dcc83d7906d3de03211dbb35b](https://github.com/mouk30/japan/commit/65853795721d6e5dcc83d7906d3de03211dbb35b)
- 소스·브라우저 QA 도입 커밋 [1e2a3d9d83aca11f5d9e899aca1f1761f7aa4293](https://github.com/mouk30/japan/commit/1e2a3d9d83aca11f5d9e899aca1f1761f7aa4293)
- 최종 [GitHub Actions 실행 #40106321089](https://github.com/mouk30/japan/actions/runs/40106321089): **소스/빌드 성공 + 실제 사이트 16/16 화면 검사 PASS**.
- Chromium 공개 화면 **4페이지×390/768/945/1440px = 16장**. 정확한 기존 canonical/H1, 화면 폭 넘침 없음, 본문 새 3카드, 50px 이상 버튼, 공식 링크, 이미지를 로드해 표시함 확인.
- QA artifact `v175-public-four-sixteen-screens`: 16 스크린샷과 JSON, 3,279,945 bytes. `v175-original-four-source`: 원본 SEO·사진·링크 검증 JSON 523 bytes.
- Vercel 배포는 QA 커밋 `1e2a3d9d83aca11f5d9e899aca1f1761f7aa4293`에서 **success**로 확인.

## 원본 사진/미검증 경계
- **원본 사진 변경 0장**: 미야코·이시노마키·하치노헤의 기존 대표 이미지는 파일/캡션 그대로, AI 참고 이미지 표시 유지. 이 세 페이지의 실제 장소 사진 교체/원본 라이선스 검증은 별도 품질 작업 대상. 도바 실사 및 라이선스 링크 유지.
- 실제 웹 결제/티켓 발행, 방문일 기상결항, 현재 좌석, 외항 크루즈 셔틀·텐더 마지막 탑승시각·선사 승객 귀선 규정의 항차별 실측은 확인하지 못한 사항. 방문 시 해당 선사·운영사 공지를 우선.

## 다음 기존 페이지 품질 과제
추가 신규 글 없이 기존 기항지의 실제 예약처 링크와 귀선 교통을 차례대로 확인. 특히 **AI 참고 사진이 남은 기존 기항지**는 검증된 원본·권리 확보 후 변경하는 별도 단계가 필요.
