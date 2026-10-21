# NIPPONFERRY V98 — Google Analytics 실제 항로별 클릭 데이터 수집·비교

**작업 반영일: 2026-10-22. 신규 검색용 게시글 0편. 기존 SEO·예약 URL 변경 없음.**

## 현재 실측 현황과 완료 범위

- 실제 GA4 계정 데이터 API에 접근할 **GA4 속성 ID와 서비스계정 읽기 권한이 제공되지 않았음**. 공개 사이트의 최근 검수(V97)에서도 측정 ID 미연결로 확인됨.
- 따라서 **오사카/후쿠오카/시모노세키/대마도 예약 클릭 수와 순위는 현재 미확인**이며, 결제·발권 건수는 처음부터 별도 지표임.
- V98 구현 완료: **Google Analytics Data API v1beta 실제 집계 조회 → GA4 이벤트 측정기준·권한 검사 → 모든 페이지 수집 → 로컬 비공개 CSV → V95 한국어 항로별 클릭 비교 대시보드**.
- 가짜 요청용 샘플 숫자는 검수 전용 단위 테스트에서만 사용하고 실측 보고서로 저장하거나 사이트에 노출하지 않음.

## 기존 분석기와 달라진 점

| 구분 | V95/V96 | V98 |
|---|---|---|
| 데이터 입력 | GA4 탐색 CSV 수동 전달 | **GA4 Data API 직접 읽기**(서비스 계정 필요) |
| GA4 맞춤 측정기준 | CSV 열 누락 검사 | **속성 metadata에서 맞춤 측정기준 등록 여부 먼저 검증** |
| 실제 집계 정확성 | 제공 CSV에 의존 | **전 행 페이지네이션·행 수 일치 확인·thresholding/기타 행 손실 감지** |
| 결과 | 수동 비교 보고서 | **비공개 CSV 및 V95 HTML 비교 보고서를 1회 명령으로 생성** |
| 자격증명 | 필요 없음 | 로컬/비공개 서비스계정 파일. **GitHub에 업로드하거나 공개하지 않음** |

API는 공식 [Google Analytics Data API v1beta runReport](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)를 사용한다. 계정 권한 없이 마법처럼 기존 GA4 수치를 읽는 도구가 아니다.

## 실제 데이터 연결: 한 번만 해야 하는 설정

1. 실제 [Google Analytics](https://analytics.google.com/)의 **GA4 웹 스트림 측정 ID `G-...`**를 만들고 **Vercel Production의 `GA4_MEASUREMENT_ID`**를 설정하여 재배포한다. 최초부터 태그가 운영 사이트에 삽입돼 있지 않았다면 과거 이벤트는 소급 조회할 수 없다. [V97 절차](../v97/README.md)
2. GA4 관리(관리자) → **맞춤 측정기준/맞춤 정의**에서 아래 *이벤트 범위* 항목 5개가 등록됐는지 확인한다. (이름/이벤트 매개변수 명: `route`, `page_area`, `placement`, `operator`, `destination_step`). Google 공식: [Event-scoped custom dimensions](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema).
3. Google Cloud에서 **Analytics Data API**를 사용하도록 설정하고, 보고서를 읽기 위한 서비스 계정을 발급한다. 그 서비스 계정의 이메일에 **GA4 속성 Viewer(읽기)** 권한을 부여한다. API 공식 가이드: [Quickstart](https://developers.google.com/analytics/devguides/reporting/data/v1/quickstart).
4. GA4 → 관리 → 속성 설정에서 **숫자로 된 Property ID** 확인. `G-...` 형태의 **Measurement ID와 숫자 Property ID는 별개**다.
5. 서비스 계정 JSON 키는 **로컬 보안 디렉터리**에 두고 저장소·Issue·공개 채팅에 올리지 않는다. `.gitignore`에 CSV/비공개 보고서/서비스 계정 파일 패턴을 추가했다.

```bash
# 로컬 개발환경: 별도 보안 경로 사용 (예시 경로만 기입)
python -m pip install google-auth requests

export GA4_PROPERTY_ID="YOUR_NUMERIC_PROPERTY_ID"
export GOOGLE_APPLICATION_CREDENTIALS="/private/secure/path/ga4-readonly.service-account.json"

python scripts/v98_ga4_data_api.py \
  --start 7daysAgo --end yesterday \
  --output private-analytics/v98/actual-ferry-events.ga4.actual.csv \
  --strict
```

연결되어 있고 실제 집계 이벤트가 있으면 **실제 CSV + `private-analytics/v98/v98-real-dashboard/dashboard.html`**을 생성한다. 사이트에 공개 자동 업로드하지 않으며, 매출·완료 예약으로 표기하지 않는다. 
연결되지 않았다면 `not_connected`, API 권한 오류는 `ga4_api_verification_failed`, 조회기간에 이벤트가 없으면 `no_matching_ga4_events_in_period`로 구분한다. 모두 **클릭 0건이나 예약 0건으로 단정하지 않는다.**

### 조회 이벤트 이름과 범위

- `ferry_operator_click`: 공식 선사 링크 클릭
- `ferry_hub_view`, `ferry_route_view`: 분모용 동의 기반 페이지 열람
- `ferry_info_open`, `ferry_route_select`, `ferry_hub_open`: 사실정보 및 내부 이동
- 항로/위치/선사/도착 화면은 `route`, `placement`, `operator`, `page_area`, `destination_step` 속성으로 구분.
- 온라인 예약 화면 진입·공식 홈페이지 검색·예약방법 안내는 **예약 완료가 아닌 단계별 이동**. 동의 거부 사용자는 제외.

## 실제 파일 검수 및 증명

- 구현: `scripts/v98_ga4_data_api.py`
- 자동 회귀: `tests/test_v98_ga4_data_api.py`
- 자동 검수: [V98 CI](https://github.com/mouk30/japan/actions/workflows/v98-real-ga4-api-qa.yml)
- 테스트 항목: 서비스 계정/속성 ID 부재, GA4 등록 측정기준 누락, 다른 이벤트 혼입, 완전한 페이지네이션, 부분 반환 실패, privacy threshold 감지, 개인정보/토큰 배제.
- CI는 **실제 방문자 데이터 접근을 시도하지 않고** 모의 GA4 응답과 연결 불가 시 상태 구분을 테스트한다. 실제 숫자가 나오려면 위 인증 작업이 선행돼야 한다.

## 다음 V99

[V99 데이터 신뢰성 검사](../v99/README.md)는 실제 V98 CSV에 잘못된 항로-선사 분류나 맞춤 측정기준 누락이 있는지 확인한 뒤 비교에 사용하도록 설계했다.
