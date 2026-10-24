# V161 — 기존 이즈제도 기항지 6편: 2026-10-24 도카이기선 공식 운항·예약·귀선 대조

> 보존 원칙: 기존 HTML 6편만 보강, 신규 게시글 0편, 기존 WebP 실사·촬영정보/라이선스·메타·canonical·URL·사이트맵 유지.

## 공식 확인된 변경

1. **2026년 10월 24일 태풍 30호 특별 예약 취소/변경:** 도카이기선 2026-10-25 도쿄 야간 출항편부터 2026-10-27 주간편까지 수수료 면제 대상. 인터넷 예매 고객이 온라인으로 직접 변경·취소할 수 있는 시한은 원칙적으로 출발 전날, 출발 당일은 고객센터 03-5472-9999(09:30~18:00) 문의. 여행사 예매는 그 회사 규정 확인. 무료 취소 공지가 전 노선 결항 확정이라는 의미는 아님.
   - https://www.tokaikisen.co.jp/news/836684/
2. **2026년 10월 9일~28일 대체선박 운항:** 도카이기선 일부 선박 사용정지로 くろしお丸, おがさわら丸, さるびあ丸 등을 포함한 대체선 편성(일부 귀착은 29일). 과거 기본 시간표·기항·승선항을 재사용하면 안 됨. 대체선 예약 승객은 개별 전화/SMS 변경 안내 대조.
   - https://www.tokaikisen.co.jp/news/826444/
   - https://www.tokaikisen.co.jp/news/833157/
3. **공식 예약·운항 입구:**
   - 실제 승선권 온라인 예약 운영사 시스템: https://www.tokaikisenyoyaku.com/app/web-front/precautions
   - 온라인 구매·절차 안내: https://www.tokaikisen.co.jp/boarding/reservation_flow/
   - 출항일 운항·실제 출입항 판단: https://www.tokaikisen.co.jp/schedule/
   - 현지 연락처: https://www.tokaikisen.co.jp/contact/
   - 사전 예약은 크루즈 항차별 승객 귀선 시각·대체선 좌석·현장 픽업을 보장하지 않음.

## 수정한 기존 기항지

| 기항지 | URL | 실전 귀선 보강 |
|---|---|---|
| 도쿄 | /things-to-do/tokyo-cruise-port-day-trip/ | 다케시바 이즈제도 여객선 승선과 국제크루즈터미널 구분. 도카이기선 수수료 면제 안내는 다른 대형 크루즈선 환불 규정이 아님 |
| 이즈오시마/오카타 | /things-to-do/okata-izu-oshima-cruise-port-day-trip/ | **오카타·모토마치** 당일 출항항이 변경 가능, 공식 운항조회+04992-2-5522로 귀선항 확인 |
| 니지마 | /things-to-do/niijima-cruise-port-day-trip/ | 10/9~28 대체선 편명과 **흑근(마에하마)·와카고** 출항 위치 점검. 환승/복귀 교통 분리 |
| 고즈시마 | /things-to-do/kozushima-cruise-port-day-trip/ | **마에하마·다코만(미우라항)** 출입항 변경 가능. 현지 문의 04992-8-1111. 시모다 출발 페리는 도카이기선의 온라인 예약 대상과 다름 |
| 미야케지마/미이케 | /things-to-do/miike-miyakejima-cruise-port-day-trip/ | **미이케·사비가하마(아코)·이케야** 3항 중 당일 출항항 04994-5-0221 확인. 셔틀 여부 미확정 |
| 하치조지마/가미나토 | /things-to-do/kaminato-hachijojima-cruise-port-day-trip/ | **소코도(가미나토)·야에네** 다른 출항항을 04996-2-1211로 재확인. 여객선 승선항과 대형 크루즈 귀선 게이트 분리 |

## 코드·QA 검증 범위
- 각 기존 게시글 첫머리에 **공식 변경 공지 → 실제 승선권/취소 경로 → 당일 출항항·복귀 교통** 3열 카드(모바일 1열·CTA 높이 52px) 추가.
- 원본 V160 최종 commit `30ebb5e65bd7c9d7aaffeab1dfaf60732821ed4d` 기준으로 보호 필드 완전 비교: `scripts/qa_v161_six_island_ferry_booking_return.py`; 워크플로 `.github/workflows/v161-six-island-official-qa.yml`.
- 생산 공개 HTTP는 6개 기존 상세페이지 + 6개 원본 WebP + 사이트맵 = 13개를 **독립적으로** 검사: `scripts/qa_v161_live_six_island_ports.py`; 워크플로 `.github/workflows/v161-live-six-ports.yml`. 실제 결과는 최신 실행 링크에서 확인할 것.
- GA4/GSC 노출·예약 버튼 실제 클릭·표 잔여석·환불 처리/셔틀 확정은 미측정.
- 운항기관의 날짜가 있는 공지는 시의성 높은 기록이므로 방문 날짜에 반드시 다시 확인해야 함. 실제 외항 크루즈의 도착·귀선 마감은 그 크루즈 선사 승객 안내가 우선.
