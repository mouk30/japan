# NIPPONFERRY V102 — 관부훼리 예약 링크 접속 거부 복구 및 재발 방지

**작업일: 2026-10-22. 기존 URL·canonical·SEO 구조 유지. 신규 콘텐츠 0편.**

## 실제 문제와 근거

사용자가 **`https://www.kampuferry.co.jp/lang_kor/reserve/`** 버튼을 누르면 연결 거부가 발생한다고 신고. 독립 웹 검증에서도 해당 원본 주소를 502로 불러올 수 없었다. 기존 V90의 단순 200/도메인 기반 자동 검수로는 이러한 **실제 방문자 접속 문제**를 충분히 예방할 수 없었음.

2026-10-22 검증한 선사·공공기관 경로:
- 공식 선사 **일본어 예약방법 안내**: https://kampuferry.co.jp/reserve/ — 실제 예약 방법, 온라인/전화, 수속·요금 안내 페이지. 한국어가 아닌 일본어임을 버튼에 명시.
- 공식 선사 **영어 예약 조건**: https://kampuferry.co.jp/yoyaku/en/reservation.html — 예약·결제·변경/취소 안내. 바로 구매를 완료하는 화면은 아님.
- 공식 선사 **일본어 운임·할인 메뉴**: https://kampuferry.co.jp/fare/
- 공식 **부산항만공사 운항정보**: https://www.busanpa.com/bpt/index.bpa?menuCd=DOM_000000401003000000
- 공식 **부산항만공사 출국 수속**: https://www.busanpa.com/bpt/index.bpa?menuCd=DOM_000000401007001000
- 한국 부관훼리 **부산 예약 전화 051-464-2700**: https://www.busanpa.com/index.bpa?menuCd=DOM_000000401005000000

공식 홈페이지에는 언어선택이 있어도 일부 `www.` 호스트·한국어 하위 주소는 특정 환경에서 실패할 수 있다. 따라서 **검증된 일본어/영어 주소로 교체하고 원래 링크가 한국어라고 표시하지 않음**. 브라우저·고객 네트워크에 따라 접속이 달라질 가능성은 남는다.

## 실제 수정 파일

- `site/guide/busan-shimonoseki-ferry/index.html`: 상단/하단 외부 예약 CTA, 영어 예약조건 보조 CTA, 공식 운임/운항/수속 출처, 부산 예약 문의 보충 설명.
- `site/guide/busan-shimonoseki-ferry-price/index.html`: 공식 예약·운임·운항·수속 근거 URL 교체.
- `site/guide/busan-shimonoseki-timetable/index.html`: 공식 예약·운임·운항·수속 근거 URL 교체.
- `site/ferry/index.html`: 와이드 항로 카드 및 선사 바로가기 주소·일본어 안내 표기 수정.
- `site/booking/japan-cruise/index.html`: 선사 바로가기 및 경로 언어 표기.
- `scripts/v90_booking_link_targets.json`: 4항로 공식 목적지 인벤토리에서 시모노세키 새 공식 주소 동기화, 일본어 문서 본문 선사 식별문 지원.
- `tests/test_v90_booking_destination_health.py`: 옛 차단 링크 재등장 금지, 실제 일본어 공식 예약 안내 문서 판정 회귀.
- `scripts/v102_kampu_reservation_recovery.py`: 오래된 링크 재등장 차단 및 공개 Vercel 5개 페이지에서 실제 새 주소 노출 여부 검사.
- `tests/test_v102_kampu_reservation_recovery.py`: 연결오류·미배포·정상배포 상태와 링크 재발 여부를 구분하는 6개 단위검사.
- `.github/workflows/v102-kampu-reservation-recovery.yml`: 정기 검사, 소스·실제 공개 버전 확인, 검수 근거 아티팩트 저장. Vercel 배포 후 수동 `require_deployed=true`로 불일치 시 실패 처리 가능.

## 최종 품질 결과: 배포 동기화 확인

- **V102 실제 공개 사이트 검수**: https://github.com/mouk30/japan/actions/runs/39694183943
- **정적 회귀검사 6/6 통과.** GitHub 원본의 차단 링크 0건.
- **실제 공개 페이지 5/5 변경 반영**: `/ferry/`, `/booking/japan-cruise/`, `/guide/busan-shimonoseki-ferry/`, `/guide/busan-shimonoseki-ferry-price/`, `/guide/busan-shimonoseki-timetable/`.
- 실제 검사 아티팩트 `v102-kampu-booking-recovery-and-live-state/report.json`: `production.status = production_updated`, `source_issues = []`, 5개 모두 `corrected_link_visible`.
- 기존 V90 공식 목적지 정합성/조회 모니터링의 회귀검사: https://github.com/mouk30/japan/actions/runs/39693719422 **success**.

**범위 한계**: NIPPONFERRY 공개 HTML에 **교체한 공식 URL이 들어갔는지** 실제 응답에서 확인함. 모든 방문자 브라우저에서 선사 사이트 접속·예약 가능한 항차·로그인/결제 성공이 보장됐다는 뜻은 아니다. 브라우저 자동화 CI에서 때때로 발생하는 Playwright CDN 인증서 오류는 선사 예약 사이트 오류가 아니므로 구분해야 한다. 기존 HTML canonical·운임 숫자 자체와 전체 항로 SEO를 바꾸지 않았다.

## 운영 재발 방지

앞으로 관부훼리 예약주소가 다시 접속 차단을 일으키면 **고객 보고 → 원문 접속 확인 → 검증된 대체 경로·한국 측 예약 문의 안내 → 저장소 교체 → 실제 Vercel 5개 페이지 검수** 순서로 처리. 오작동 중이던 옛 주소를 그대로 되살리지 않는다.
