# V171 — 기존 미술섬·시코쿠 3편 공식 예약·휴관·귀선 보강 완료

확인일: 2026-10-24 (KST)

## 수정 범위
- 신규 글 0편. 기존 페이지 3편만 편집:
  1. `site/things-to-do/naoshima-art-ferry-return/index.html`
  2. `site/things-to-do/teshima-art-ferry-return/index.html`
  3. `site/things-to-do/takamatsu-cruise-udon-market-return/index.html`
- 사진 0장 교체. 기존 1200×900 WebP, alt, Wikimedia 저작자 및 CC 라이선스 출처, SEO title/meta/canonical, 사이트맵과 기존 링크 보존.

## 확실한 운영정보와 실제 조치
- 나오시마 지추미술관: 공식 보수 휴관 예정 **2027-01-12 ~ 2027-03-19** 공지를 첫 3단계 가이드 바로 앞에 표시. 출처 https://www.benesse-artsite.jp/news/20260525-3518.html . 지추 미술관만의 휴관이며 여객선·전체 미술섬 폐쇄라고 확대하지 않음.
- 공식 예매 전환: 기존 FAQ는 구매 후 취소를 불가로 표시하지만 최신 Eventos 공식 판매 화면은 **예약시간 30분 전까지 취소 가능**, 직접 날짜/시간 변경 불가(취소 후 재예약)를 표시. 오래된 FAQ 링크에는 안내 차이가 있음을 명시하고 현재 공식 예매 바로가기 https://benesse-artsite.eventos.tokyo/web/portal/797/event/8483/module/booth/239565/176695?language=eng 추가. 과거 FAQ URL은 관련성 때문에 보존하되 현행 조건이라고 단정하지 않음.
- 데시마미술관: **12월~2월 보통 화~목 휴관**(공휴일/대체휴관 예외), 2027년 지추와 다른 일정을 분명히 표기. 출처 https://www.benesse-artsite.jp/news/20260630-3558.html 와 공식 달력 https://benesse-artsite.jp/en/calendar/ . 날짜/시간권 30분 단위(성수기 15분), 매진·선박 귀항 별개로 재강조.
- 시코쿠 미식: 사누키 마르셰 2026-11-15 개최 예정 vs 11-22 연기 후보, 2027-01-17 예정 vs 01-24 연기 후보를 구분. 7·8·12월 휴장. 한국어 공식 일정 https://www.kensanpin.org/ko/marche/schedule/ . 연기일을 확정 개최로 안내하지 않음. 식당/크루즈 운영과 구분.

## 배포·실제 검증
- 실제 HTML 작업 커밋 https://github.com/mouk30/japan/commit/bd919c36246eb46fd10c87c3437a386a540270e0
- 소스 보호 / 사이트 빌드 / 공개 사이트 HTML 검사 **모두 SUCCESS** https://github.com/mouk30/japan/actions/runs/40097498886 
- 해당 HTML 변경 배포 Vercel SUCCESS. 단순 코드 생성 아닌 실제 운영 사이트 응답 확인.
- 공개 브라우저 390·768·945·1440px × 3편 = **12/12 PASS**, 스크린샷 12장과 원본 사진 치수/라이선스/공식 공지/CTA/가로넘침 검사 결과 https://github.com/mouk30/japan/actions/runs/40097807707 
- 사진 출처 접힘 영역 `details` 때문에 최초 화면 QA가 거짓 FAIL을 낸 오류는 검사기를 `innerText` → `textContent`로 고쳐 최종 12/12 PASS 확인. QA 수정 커밋 https://github.com/mouk30/japan/commit/4a033bc433856a252f3d16e83be30a7a8cc70368 . 이미지/게시글에 문제가 있었다는 의미는 아님.

## 범위의 한계
- 공식 발표와 페이지 출력, 원본 이미지·면허 및 기능적 링크 구성을 대조한 것. **실시간 티켓 재고, 결제 성공, 페리 당일 결항 여부, 예약 변경·환불 완료, 실제 크루즈의 최종 승객 탑승시각, GA4/GSC 수치는 검증하지 않음.**
- 장기 휴관 및 마르셰 일정은 현재 공식 공지에 근거한 미래 예정 상태. 이용 전 운영기관 공식 최신 발표로 재확인.
- 당일 귀선 기준은 개별 크루즈 선박/항차의 안내가 최우선이며 미술관 티켓이 선박 왕복을 보장하지 않음.

## 후속 우선순위 (V172 제안)
- 같은 V153 진입 구조에 속하는 기존 3개 안내 글과 타 기항지 페이지의 오래된 예매규정·실제 항구 명칭을 우선 재검증. 신규 게시글 발행보다 운영정확도/예약→현지이동→귀선 점검 계속.
