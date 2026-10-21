# NIPPONFERRY V96 — GA4 실측 데이터 기반 저성과 페이지 검토 대기표

**기능 구현 및 회귀검수 완료. 신규 공개 게시글 0개. 실제 GA4 데이터가 없어 현재의 개선 후보 수는 미확인.**

V95가 항로·페이지별 실측 비교표를 만든 후, V96은 **이전 7일과 최근 7일** 등 같은 길이의 실제 GA4 CSV를 비교해 사람의 확인이 필요한 페이지 후보를 선별한다.

## 판단 조건

- 실제 동의 기반 `ferry_operator_click`을 `operator_search`, `booking_search`, `booking_instructions`의 **예약 진입·예약방법 정보 클릭**으로 정의.
- 두 기간의 길이가 같고, 해당 페이지의 **조회 기록이 양쪽 모두 최소 100회**(설정 가능)인 경우에만 조회 대비 클릭 활동량 변화를 계산.
- 조회 100회당 클릭 활동량이 **25% 이상 상대 감소**하고 **2클릭 이상 절대 감소**한 경우 `editorial_review_candidate`로 표시.
- 충분한 표본이나 비교 가능한 이벤트 분모가 없으면 **판정 보류**, 0회 이용이라고 가정하지 않음.
- 위 조건은 **검토 우선순위 휴리스틱**일 뿐 통계적 유의성이나 사이트 변경의 인과관계를 뜻하지 않는다.
- 수정 제안 전에 해당 항로의 최신 공식 운항·결항·예약 제한, 선사 URL, 노출 위치, 예약 버튼 문구를 각각 확인한다. **공개 HTML·예약 버튼·요금·SEO를 자동으로 변경하지 않는다.**

## 사용법

```bash
python scripts/v96_booking_change_review.py \
  --previous /path/to/ga4-previous-7-days.csv \
  --current /path/to/ga4-recent-7-days.csv \
  --previous-days 7 --current-days 7 --min-views 100 \
  --output audit-output/v96-editorial-review
```

실제 자료가 없으면 다음 명령은 **대기 상태만 기록**한다.

```bash
python scripts/v96_booking_change_review.py --output audit-output/v96-ready-no-data
```

결과 파일: `review_queue.json`, `review_queue.md`. 자료 미연결 시 `status.json`의 `review_candidate_count`는 `null`이다.

## 검사 및 품질 관리

- [V96 자동검수](https://github.com/mouk30/japan/actions/workflows/v96-booking-review-qa.yml)
- [V95 실제 CSV 비교](../v95/README.md)
- 앞뒤 기간 길이 다르면 입력 거부, 저표본 자동 하위순위 금지, 본문 자동수정 금지, 클릭과 발권을 명확히 구분.
- 회귀검사의 임의 숫자는 실사용자 실적으로 사용하지 않는다.

### 여전히 필요한 외부 설정

현재 프로젝트에 실제 GA4 Measurement ID 연결이 확인되지 않았다. **Vercel Production 환경변수 `GA4_MEASUREMENT_ID` 설정 및 재배포**, GA4 맞춤 측정기준 등록, 실제 CSV 탐색 내보내기가 필요하다. 한 번도 수집되지 않은 과거 이벤트는 재생성할 수 없다. 동일 기간 비교가 가능해져도 계절성·항차 변경·수집 동의율·유입 채널 차이를 함께 해석해야 한다.
