# NIPPONFERRY V99 — GA4 항로별 클릭 데이터 신뢰성 검수

**반영일: 2026-10-22 · 신규 게시글 0편 · 기존 SEO·예약 링크 유지**

## 이 단계의 목적

[V98 실제 GA4 API 데이터 조회](../v98/README.md)에서 나온 클릭 정보가 **올바른 항로와 선사로 분류됐는지** 확인한다. 클릭이 많다는 사실만으로 구매 전환이나 예약 성공이라고 주장하지 않는다.

대상 항로와 기대 선사는 다음과 같다.

| 클릭 항로 | 기대 선사 | 중요 구분 |
|---|---|---|
| 오사카 | PanStar (`panstar`) | 공식 홈페이지 내 항로·날짜 검색 |
| 후쿠오카 | Korea Ferry (`koreaferry`) | 한국어 출항일·인원 검색 |
| 시모노세키 | Kampu Ferry (`kampuferry`) | 예약 방법 안내, 온라인 결제 완료 아님 |
| 대마도 | PanStar (`panstar`) | 쓰시마링크·도착항 확인 |

다음과 같은 데이터를 **수정 없이 검토 대상으로 표시한다**.

- `route=tsushima`인데 `operator=koreaferry` 등 실제 항로와 선사가 불일치
- GA4 `route`, `page_area`, `placement`, `operator`, `destination_step`가 `(not set)` 또는 누락
- 후쿠오카 핵심 예약 버튼이 `operator_home`으로 잘못 분류되는 경우
- 관부훼리 예약 **방법 안내**를 예약 결제 `booking_search`로 잘못 분류하는 경우
- 분석할 외부 클릭 표본이 20회보다 작으면 `small_sample_unreliable`
- 외부 클릭 이벤트 자체가 없으면 `no_verifiable_outbound_click_data` — **0건 관심·매출로 추론하지 않음**

## 실제 데이터 검수 방법

먼저 V98에서 본인이 소유한 GA4 실제 CSV를 비공개 디렉터리에 생성한 다음 아래 명령을 사용한다.

```bash
python scripts/v99_ga4_attribution_qa.py \
  --input private-analytics/v98/actual-ferry-events.ga4.actual.csv \
  --output private-analytics/v99
```

출력: `private-analytics/v99/report.json`, `report.md`. 사용자별 원시 개인정보는 수집하지 않고 집계 이벤트만 처리한다.

**GA4 연결 전 대기 확인 명령**

```bash
python scripts/v99_ga4_attribution_qa.py \
  --output private-analytics/v99
```

이때 `operator_clicks`와 `problem_events`는 반드시 `null`(미확인)이어야 한다.

## 자동 검수 증거

- 분석 프로그램: `scripts/v99_ga4_attribution_qa.py`
- 모의 분류 테스트: `tests/test_v99_ga4_attribution_qa.py`
- [GitHub V99 자동 검수](https://github.com/mouk30/japan/actions/workflows/v99-ga4-attribution-qa.yml)
- 시뮬레이션 검사는 실방문자 수치를 생성하지 않는다.

## 성과 개선에 적용할 조건

1. 실제 데이터에서 항로·선사 정보가 일치하고 측정누락이 없는지 확인.
2. V95/V98 항로별 클릭 비교에서 페이지 조회 분모를 확보하고 저표본 페이지 제외.
3. V96 두 기간 비교 결과에서 변화가 확인되면 결항/운임 변동, 예약 링크 리디렉션(V90), 카드 가독성·클릭 동선을 **사람이 재검수**한다.
4. **확인되지 않은 숫자만으로 공개 페이지 요금·SEO·예약 URL을 자동으로 변경하지 않는다.**
