# V132 — NIPPONFERRY 전역 품질관리 실행 보고서

**2026-10-22 · 신규 게시글 0 · 키즈관 게시 보류**

## 1. 소스 전수 검수
- 현재 GitHub site/ 아래 HTML 1,277편 전수 스캔: 로컬 이미지 src 누락 0, 내부 링크 누락 0, img alt 누락 0.
- 항만·크루즈 관련 194페이지에서 귀선 관련 표현은 모두 발견. 단어 존재는 항차별 막차·귀선 마감 검증을 의미하지 않음.
- 색인 대상 HTML 기초 SEO 누락 0. 초기 8개 감지 항목은 /route/ 및 /routes/의 의도적 /ferry/ 메타 리다이렉트와 noindex 도쿄 사진검수판에 해당.
- 원본 사진·장소·촬영자·권리 대조는 자동 스캔만으로 판정할 수 없으며 별도 육안 검수가 필요.

## 2. 발견해 수정한 오류
- 대표사진과 공유·검색 Article 이미지가 맞지 않았던 **83개 기존 상세페이지 / 메타데이터 101건** 수정.
- **OG:image 18건 + JSON-LD Article 이미지 83건** 수정. 기존 URL·title·description·canonical·H1 원형 유지.
- 동일 감사 반복 실행 결과 이미지 메타데이터 불일치 **0건**.
- [V132 자동 수정 및 재검사 성공](https://github.com/mouk30/japan/actions/runs/39800867867) · [수정 전 목록](./sitewide-inventory-before-photo-repair.json) · [83편 수정 결과](./image-metadata-repair.json)

## 3. 공식 예약 링크와 실제 예약 조건
- [예약 허브](https://www.nipponferry.com/booking/japan-cruise/), [페리 비교](https://www.nipponferry.com/ferry/), [부산-시모노세키 상세](https://www.nipponferry.com/guide/busan-shimonoseki-ferry/) 세 기존 페이지에 **관부훼리 온라인 예약의 시간·결제·취소·변경·현장 추가요금**을 공식 조건과 함께 명시.
- [선사 공식 예약 안내](https://kampuferry.co.jp/reserve/) 및 [선사 예약·취소 상세 조건](https://www.kampuferry.co.jp/yoyaku/jp/reservation.html). 사이트 안내 링크가 열린다고 좌석 예약·발권이 완료되는 것은 아님.
- [도쿄 스카이트리 입장권 안내](https://www.nipponferry.com/japan/tokyo/tokyo-skytree-tickets/)의 일반 공식 홈페이지 CTA를 [공식 다국어 티켓 구매 화면](https://global-official-ticket.tokyo-skytree.jp/ja/home)으로 교체.
- [기항지 입장권 안내](https://www.nipponferry.com/voucher/cruise-ports/)의 후쿠오카타워 홈페이지 구매 CTA를 해당 시설이 [공식 FAQ](https://www.fukuokatower.co.jp/faq/)에서 직접 소개하는 [Webket 입장권 구매 링크](https://webket.jp/pc/ticket/index?ac=5000&fc=00463&lang=0)로 교체.
- 2026년 10월 22일 기준 확인. 예약창 재고·현장 운영·실제 결제 성공은 별도 검증 대상.

## 4. 아직 수동 재검토할 대상
- 대표사진 출처 표시 후보: 기존 페이지의 레거시 사진 캡션이 단락에 있을 수도 있어 자동 누락으로 확정하지 않는다.
- 예약 CTA의 실제 판매창이 아닌 일반 설명 페이지 이동 사례: 단순 '예약 전 체크' 등은 오류가 아닐 수 있음. 검토 후보별로 의미를 구별해 고친다.
- 오래된 운영시각·요금·취소규정은 원문에 명확한 발효일과 여행일 조건이 있어야 수정.
- 기항지별 선박·날짜·실제 접안 게이트·승선 마감·복귀 차량의 마지막 운행 시각은 전수 확인 미완료. 임의 시간 입력 금지.
- 이시가키 버스·나가사키 공식 관광의 서버 접근 제한 링크는 V131에서 삭제·임의 대체하지 않았음.

## 검수 자료
- [전 사이트 페이지별 감사 결과](./sitewide-inventory.json)와 [자동 생성 건수표](./README.md)
- [최종 재생성 전수 검사 작업](https://github.com/mouk30/japan/actions/runs/39802461596)
- [83개 이미지 상세와 예약 3곳 PC·모바일 검수 작업](https://github.com/mouk30/japan/actions/runs/39801816061)

**품질관리 원칙:** 조사 결과가 후보인 경우에는 '오류 확정'으로 표시하지 않으며, 검색용 구조와 기항지의 실제 귀선 안전 정보는 증빙 없이 변경하지 않는다.
