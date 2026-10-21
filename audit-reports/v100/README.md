# NIPPONFERRY V100 — GA4 실측 예약 클릭 주간 운영 보고서

**적용일: 2026-10-22 · 기존 SEO URL/예약 링크 변경 없음 · 신규 검색용 게시글 0개**

## 최종 상태

- **V100 주간 GA4 실측 분석 실행기 구축 완료**. 기존 V98 Data API 집계, V99 항로·선사 무결성 검사, V95 한국어 대시보드, V96 전주 대비 검토 후보를 한 흐름으로 통합했다.
- **GA4 실제 계정 미연결**: V97에서 공개 사이트에 실제 Measurement ID가 없는 상태였고, 현재 연결된 GA4 속성의 읽기 권한·서비스 계정이 제공되지 않았다. 따라서 **실사용자 예약 버튼 클릭 수·상위 항로·예약률은 전부 미확인**이다.
- 데이터가 없을 때 생성되는 결과의 `actual_click_counts`는 **null**, 결제완료 `confirmed_bookings`도 **null**이다. "0건"을 허위 보고하거나 테스트 데이터를 실제 성과로 간주하지 않는다.
- 검수: [V100 주간 분석 CI](https://github.com/mouk30/japan/actions/workflows/v100-ga4-weekly-pulse-qa.yml). 가짜 GA4 자료는 **별도 오프라인 유닛테스트에만** 사용한다. GitHub Actions에 실제 GA4 비밀키나 실사용자 로그를 업로드하지 않는다.

## 현재 보장하는 분석 흐름

1. **로컬 GA4 읽기 권한 확인**: 숫자형 `GA4_PROPERTY_ID`와 안전한 별도 경로의 서비스계정 JSON이 있는지 검사한다. 별개로 Vercel Production `GA4_MEASUREMENT_ID`는 **측정 데이터 발생을 위한 웹 스트림 ID**이다.
2. **한국시간 기준 종료된 기간**만 이용: 실행일이 2026-10-22라면 **최근 7일 10/15–10/21**, **이전 7일 10/08–10/14**. 실행일 당일은 제외한다. 다른 날짜에는 자동으로 해당 실행일을 기준으로 계산한다.
3. [V98](../v98/README.md)의 GA4 Data API로 승인된 6개 웹사이트 이벤트만 집계하고, 기존 등록한 **5개 맞춤 측정기준 `route`, `page_area`, `placement`, `operator`, `destination_step`**를 확인한다. 누락된 매개변수, 권한/HTTP 오류, 응답이 일부만 전달된 경우는 **조회 실패**로 처리한다.
4. [V99](../v99/README.md)의 항로·선사·버튼 위치 분류 검사를 통과하지 못하면 **항로별 성과 순위를 생성하지 않고 검토 상태만 출력한다**.
5. 최근 기간만 수집됐으면 [V95](../v95/README.md)의 **최근 주간 정보**만 비공개로 만든다. 이전 기간에도 신뢰할 수 있는 데이터가 있을 때만 [V96](../v96/README.md) **동일 길이 기간 간 비교**를 수행한다.
6. 충분한 클릭 표본이 없는 경우에는 `insufficient_current_click_sample`로 구분하여 과잉 해석을 막는다. 각 페이지 조회 분모가 부족하면 V95/V96 기존 기준에 따라 순위를 유보한다.
7. 결과 저장은 **`private-analytics/v100/run-<실행시각>/`**의 매번 다른 폴더를 기본값으로 사용해 이전 데이터가 새 결과로 오인되는 일을 줄인다. 저장소의 `.gitignore`에 있는 내부 데이터만 사용한다. **`site/`나 Vercel에 실제 방문자 데이터·분석 보고서를 공개 배포하지 않는다.**

## 실제 GA4 연동이 완료된 뒤 실행

다음 설정을 계정 소유자가 한 번 해야 한다.

- GA4 웹 데이터 스트림 생성 → Vercel Production에 `GA4_MEASUREMENT_ID=G-...` 등록 → **재배포** → 실제 방문자의 동의/공식 예약 버튼 클릭이 GA4 Realtime에서 수신되는지 확인. [V97 가이드](../v97/README.md)
- GA4 관리자 → 이벤트 범위 맞춤 측정기준 5개 등록
- Google Cloud → **Google Analytics Data API** 활성화 → 서비스계정에 GA4 속성 **Viewer** 읽기 권한 부여
- 수치인 **GA4 Property ID**와 비공개 서비스계정 키 경로 준비. 서비스 계정 JSON, 비밀 토큰, 개인 데이터는 GitHub·대화 메시지·웹사이트 소스에 업로드하지 않음.

```bash
# 1. 별도 안전한 경로의 키와 GA4 Property ID가 실제로 설정된 경우에만
python -m pip install google-auth requests
export GA4_PROPERTY_ID="YOUR_NUMERIC_GA4_PROPERTY_ID"
export GOOGLE_APPLICATION_CREDENTIALS="/secure/private/ga4-readonly.service-account.json"

# 2. GA4 Data API에서 실제 데이터를 읽고 최근/이전 7일을 비교
python scripts/v100_ga4_weekly_pulse.py --days 7 --threshold 100 --strict

# 3. 특정 실행일을 기준으로 검사하려면 (한국시간 날짜 기준, 해당일은 제외)
python scripts/v100_ga4_weekly_pulse.py --as-of 2026-10-22 --days 7
```

**상태값 의미**:

| 출력 상태 | 의미 |
|---|---|
| `awaiting_account_connection` | GA4 속성/읽기 권한 정보가 없음, 클릭 수 미확인 |
| `source_unavailable` | 권한·API·일부 반환·비정상 응답; 숫자를 추정하지 않음 |
| `no_current_event_data` | 비교할 이벤트 기록이 없음, 수요가 0이란 뜻 아님 |
| `current_attribution_review` | 최근 주의 항로/선사 분류에 문제가 있어 랭킹 중단 |
| `current_only_no_baseline` | 최근 실제 데이터만 있고 이전 데이터가 없어 증감 표시 보류 |
| `prior_attribution_review` | 이전 기간 분류 품질이 낮아 기간 비교 보류 |
| `insufficient_current_click_sample` | 실제 데이터는 있으나 항로 클릭 표본이 적어 해석에 주의 |
| `qualified_weekly_review_ready` | 두 기간 집계가 조건 충족, V95·V96 내부 분석 확인 가능 |

## 최종 산출물은 오직 비공개

- `recent-actual.ga4.actual.csv`: 실제 현재 기간 **집계** 이벤트 CSV
- `recent-data-quality.json`: V99 실제 원천 데이터 품질표
- `recent-dashboard/dashboard.html`: V95 반응형 한국어 항로·페이지 활동량 비교
- `previous-actual.ga4.actual.csv`: 이전 기간 데이터가 있으면 생성
- `trend-review.json`: 양쪽 기간이 신뢰 가능할 때만 생성하는 V96 개선 후보
- `report.json`: 현재 실행의 상태. 데이터 없는 경우 `status.json`이며 실적은 모두 미확인

**운영 원칙:** GA4 "선사 예약 버튼 클릭"은 **실제 예약 결제/발권/매출이 아니다**. 동의하지 않은 이용자와 광고 차단 사용자의 클릭을 모두 측정할 수 없다. 같은 방문자가 여러 번 누르면 페이지 조회 100회당 클릭 수가 100 이상일 수 있으며, 실사용자 기준 전환율이라고 부르지 않는다. 결항 공지, 실제 운항, 최종 요금, 선사 예약 URL은 별도로 검증해야 한다. 개선 제안도 사람이 확인한 이후에만 사이트에 반영한다.

**다음 단계 V101 제안:** 실제 GA4 웹 스트림 연결 직후 1회 **Real-time 검수 → 7일 집계 → V100 보고서로 첫 항로별 클릭 현황**을 확인하는 운영 QA. 등록/권한이 없는 현재는 임의의 숫자/계정을 만들지 않고 기다리지 않는 것이 정확하다.
