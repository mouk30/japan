# NIPPONFERRY V95 — 항로별 예약 클릭·페이지별 선사 이동 비교

**2026-10-21, 개인용 분석 도구 구축. 신규 공개 기사 0개.**
**GA4 공개 사이트 측정 ID는 확인된 마지막 검사에서 미설정. 현재 실사용자 예약 클릭 수·성과 순위는 미확인이다.**

## 실제 데이터가 들어오면 비교할 것

- 오사카·후쿠오카·시모노세키·대마도 **4개 항로**의 공식 선사 클릭 수
- 단순 노선 안내 열람(`route_info`, `operator_home`)과 **예약·날짜검색/예약방법 진입**(`operator_search`, `booking_search`, `booking_instructions`)을 별도로 분류
- **6개 페이지**: 페리 허브 `/ferry/`, 예약 허브 `/booking/japan-cruise/`, 오사카·후쿠오카·시모노세키·대마도 대표 항로 가이드
- 페이지별 실제 GA4 `ferry_hub_view` / `ferry_route_view` 대비 버튼 클릭, **페이지 조회 100회당 클릭 활동량**. 동일 사용자가 반복 클릭할 수 있으므로 결제 전환율이 아님.
- 관부훼리 버튼은 **예약방법 안내**로 이동한다는 해석을 명시. 공식 선사 이동만으로 실제 예약 완료·잔여 좌석을 주장하지 않음.
- 조회 100회 미만 페이지(`--min-views`로 조정 가능)는 **표본 부족**, 조회 이벤트 분모가 없으면 **미확인**으로 표시하고 순위를 매기지 않음.
- 공식 이동 클릭은 있지만 `destination_step` 등의 예약 이벤트 분류가 CSV에 없으면, **실제 예약 진입 클릭 0건이 아니라 측정자료 불충분**이라고 표시.

## 사용법

Vercel에 유효한 실제 GA4 측정 ID `GA4_MEASUREMENT_ID`를 연결하고 Production을 재배포해야 방문자 동의 이후부터 수집된다. 기존 수치는 소급하지 않는다. [V93 연결 가이드](../v93/README.md).

GA4 **탐색(Explore)** 화면에서 `Event name`, `Event count`, `route`, `page_area`, `placement`, `operator`, `destination_step`을 포함해 **실제 GA4 CSV**를 내보낸다. 맞춤 측정기준 `route`, `page_area` 등은 GA4 이벤트 범위로 먼저 등록한다.

```bash
# 아직 GA4를 연결하지 않았을 때 — 미확인 상태만 출력
python scripts/v95_booking_comparison.py --output audit-output/v95-private-comparison

# 연결 이후 실제 방문자 데이터가 생긴 경우
python scripts/v95_booking_comparison.py \
  --input /path/to/GA4-Explore-actual.csv \
  --period "2026년 11월 첫째 주" \
  --min-views 100 \
  --output audit-output/v95-actual
```

**출력 파일:** `dashboard.html` (고급 반응형 한국어 개인용 비교 대시보드), `report.json` (근거 이벤트별 비교), `report.md` (요약). 연결 전에는 `status.json`만 기록한다.

**주의:** `dashboard.html`은 `site/`에 배포하지 않고 사적인 검토 자료로만 사용한다. 페이지 자체에 `noindex,nofollow`를 포함한다. CSV·리포트에 개인정보를 넣지 않으며 GitHub의 공개 커밋에 사용자별 데이터 파일을 업로드하지 않는다.

## 실제 검수 범위와 한계

- [V95 Actions](https://github.com/mouk30/japan/actions/workflows/v95-booking-comparison-qa.yml): 실제 GA4 CSV 없이 비공개 미연결 상태가 제대로 생성되는지 확인.
- 가상 CSV fixture에서 4항로·6화면 비교, 안내 클릭과 예약 검색 진입 구분, 낮은 표본·분모 없는 페이지 순위 제외, HTML 특수문자 안전 처리, 반복 클릭으로 100 초과 가능한 활동량 확인.
- 검증에 사용한 fixture 숫자는 **실사용자 데이터가 아니므로 결과로 게시하지 않는다**.
- V95 분석 결과만 보고 현장 운항일, 결항, 실제 예약 좌석, 매출 상승을 주장하지 않으며 공개 페이지 코드를 자동 수정하지 않는다.

## V96 연결

GA4 수집이 일정 기간 쌓이고 **길이가 같은 실제 CSV 두 기간**이 확보되면, [V96 편집 검토 대기표](../v96/README.md)에서 활동량 변화 후보만 추려 공식 예약 동선·운영 공지와 대조한다.
