# V94 — 실제 GA4 데이터로 예약 버튼 이용률 보고서 산출

**완료한 것:** 보고서 집계기 + 회귀검사 + CSV 입력 형식. **실제 데이터가 연결되지 않았으므로 클릭 수는 아직 미확인**이며, 숫자를 만들어 채우지 않는다.

## 실행 순서

1. 먼저 [V93 GA4 연결 설정](../v93/README.md)대로 `GA4_MEASUREMENT_ID`를 Vercel **Production** 환경변수에 저장하고 재배포한다. 홈페이지에서 통계 수집을 허용하고 공식 선사 버튼 클릭을 테스트한다.
2. GA4 → **탐색(Explore)** 에서 이벤트 이름, 이벤트 수와 이벤트 범위 맞춤 측정기준 **route, page_area, placement, operator, destination_step**을 선택한다. 다음 이벤트가 포함되도록 필터한다.
   - `ferry_operator_click` (선사 이동)
   - `ferry_hub_view` (허브 페이지 조회, 수집 동의한 경우)
   - `ferry_route_view` (항로 가이드 조회, 수집 동의한 경우)
   - `ferry_info_open` (사실정보 링크)
   - `ferry_route_select`, `ferry_hub_open` (사이트 내부 이동)
3. 데이터를 **CSV**로 내보낸다. 실제 파일을 `--input` 옵션으로 전달하면 항로별 합계, PC/모바일이 아닌 **버튼 위치별**, 각 공식 이동 링크 유형별 클릭 수를 산출한다. PC/모바일 구분은 현재 이벤트 규격에 없으므로 보고서에 근거 없는 분류를 추가하지 않는다.

```bash
python scripts/v94_booking_click_report.py --input /path/to/actual-ga4-export.csv --output audit-output/v94-actual
```

출력: `audit-output/v94-actual/report.json`, `report.md`.

실제 데이터 없이 실행하면 `status.json`의 `operator_clicks_total: null`을 기록한다. **자료가 없는 것을 0회로 표현하지 않는다.**

```bash
python scripts/v94_booking_click_report.py --output audit-output/v94-unconfigured
```

## 보고서 지표

| 지표 | 계산 | 해석 |
|---|---|---|
| 항로별 선사 이동 클릭 | `ferry_operator_click`의 `route`별 이벤트 수 합계 | 예약 완료가 아닌 **공식 사이트 이동 시도** |
| 버튼 위치별 이동 | `page_area` + `placement`별 이벤트 합계 | `ferry_hub`, `booking_hub`, `route_guide` 구분 |
| 허브 100회 조회당 선사 이동 클릭 | 같은 허브의 `ferry_operator_click ÷ ferry_hub_view × 100` | **조회당 활동량**, 전환율이 아니며 100 이상 가능 |
| 항로 가이드 100회 조회당 선사 이동 클릭 | 항로 가이드 클릭 수 ÷ `ferry_route_view` × 100 | 고유 사용자별 전환율 아님 |
| 운항정보 추가 확인 | `ferry_info_open` 수 | 정보 조회 클릭, 구매와 별개 |

분모 이벤트가 수집되지 않은 기간에는 `null`로 표시한다. 동의한 방문자와 실제 GA4에서 수집된 데이터 기준이므로 전체 방문자와 차이가 있다. **정책상 방문자 개인식별정보·예약내역·카드정보는 GA4 맞춤 이벤트로 수집하지 않는다.**

## QA 및 배포

- 집계기: [`scripts/v94_booking_click_report.py`](../../scripts/v94_booking_click_report.py)
- 회귀검사: [`tests/test_v94_booking_click_report.py`](../../tests/test_v94_booking_click_report.py)
- GitHub Actions: [V94 GA4 real-export report integrity](https://github.com/mouk30/japan/actions/workflows/v94-ga4-click-report-qa.yml)
- 검사 범위: 실제 데이터 파일이 없을 때 임의 숫자 생성 금지, 가상 테스트 CSV의 항로 합산·조회당 클릭 계산, 누락된 필수 열/이상한 이벤트수 거부.
- 실제 GA4 내역은 업로드/연결받지 않았으며, **검사에 사용된 숫자는 모두 테스트용 가상 데이터다.**

## 운영 주의점

- V92 이전 수치는 그 시점에 GA4 측정이 활성화되지 않았다면 소급할 수 없다.
- GA4에서 Enhanced Measurement 자동 `click` 이벤트와 V93 `ferry_operator_click`을 합산하면 중복될 수 있다. 실제 보고서에서는 **V93 전용 이벤트명만 사용**한다.
- 출항 가능 좌석, 결제/발권 완료는 외부 선사 사이트 안에서 처리되므로 본 사이트 클릭 이벤트로 확인할 수 없다.
- GA4 추적 허용을 하지 않았거나 차단기를 쓰는 사용자 행동은 보고서에 포함되지 않는다.
