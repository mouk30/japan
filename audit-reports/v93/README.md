# V93 — 실제 예약 버튼 클릭 GA4 측정 설정 및 검수

**2026-10-21 · NIPPONFERRY · GitHub `mouk30/japan` · 신규 SEO 기사 0편**

## 완료된 구현

- `site/nf-v93-booking-clicks.js`: 홈페이지/기존 기사/예약허브 등 **빌드 결과 전체 페이지에 적용 가능한 이벤트 수집 코드**. 공식 팬스타·고려훼리·관부훼리 링크만 분류하며 무관한 외부 사이트는 무시.
- `site/nf-v93-booking-clicks.css`: 사용자가 **수집 허용·거절·동의 변경**을 선택할 수 있는 안내. 거절 시 Google 스크립트가 로드되지 않음.
- `build.js`: Vercel의 `GA4_MEASUREMENT_ID` 빌드 환경변수가 유효한 `G-` ID일 때만 태그와 동의 UI를 삽입. 설정하지 않으면 **GA4 스크립트/데이터 수집을 삽입하지 않음**.
- 사용자 세부정보, 이름, 여권 번호, 출항 날짜, 좌석정보, 예약 URL 쿼리나 금액은 맞춤 이벤트 매개변수로 보내지 않음. 수집되는 구분값은 한정된 항로·버튼 위치·사이트 내 영역·선사·도착 화면 유형뿐.
- 전환율이라는 용어의 남용 방지: **공식 선사 이동 클릭은 예약 완료가 아니다.**

## 이벤트 규격

| GA4 이벤트 | 의미 | 필수 분류 예시 |
|---|---|---|
| `ferry_operator_click` | 방문자가 공식 선사 링크 클릭 | `route`, `placement`, `page_area`, `operator`, `destination_step` |
| `ferry_hub_view` | 동의한 방문자가 페리/예약 허브 페이지 확인 | `page_area=ferry_hub/booking_hub` |
| `ferry_route_view` | 동의한 방문자가 기존 4개 항로 가이드를 조회 | `route`, `page_area=route_guide` |
| `ferry_route_select` | 기존 항로 가이드로 내부 이동 클릭 | `route`, `placement` |
| `ferry_info_open` | 운영시간/요금 사실정보 영역 내부 클릭 | `route`, `placement` |
| `ferry_hub_open` | 예약 허브로 이동하는 사이트 내 링크 클릭 | `page_area` |

`destination_step`는 `booking_search`, `operator_search`, `route_info`, `booking_instructions` 등 **화면의 성격**이다. 직접 결제·발권 여부를 판정하지 않는다.

## 실제 데이터 수집을 시작하기 위해 필요한 1회 설정

**중요: GitHub 소스에는 실제 GA4 Measurement ID가 존재하지 않는다.** Vercel 프로젝트 계정의 환경변수 값을 읽거나 GA4 property를 생성한 것은 아니므로, 실제 누적 클릭 수가 수집되었다고 주장하지 않는다.

1. [Google Analytics](https://analytics.google.com/)에서 `www.nipponferry.com`의 **GA4 웹 데이터 스트림**을 만들거나 기존 스트림을 연다.
2. `G-XXXXXXXXXX` 형태의 **측정 ID(비밀 API 키 아님)**를 확인한다.
3. **Vercel 프로젝트 → Settings → Environment Variables**에서 이름 `GA4_MEASUREMENT_ID`, 값은 실제 측정 ID, 대상 **Production**으로 등록한다.
4. `main` 브랜치를 다시 배포한다. 사용자의 GA4 ID를 코드나 설명에 임의로 적지 않는다.
5. 사이트에서 방문자 동의 UI의 **통계 수집 허용**을 직접 선택한 다음 기존 [일본 페리 허브](https://www.nipponferry.com/ferry/)의 공식 선사 버튼을 눌러본다.
6. **GA4 실시간 보고서**에서 `ferry_operator_click` 이벤트가 나타나는지 확인한다. 이후 이벤트 탐색에서 `route`, `placement`, `page_area`, `operator`, `destination_step`을 이벤트 범위 **맞춤 측정기준(Custom definitions)**으로 등록해 항로별 숫자를 확인한다. 처리 지연/차단에 따라 보고시간 차이가 있다.

Vercel Hobby의 Web Analytics **맞춤 이벤트는 지원되지 않는다**. 이를 전제로 수집한다고 주장하거나 유료 플랜 활성화를 가정하지 않는다. GA4 구성/수집 동의 방식 사용.

## 실제 QA 기록

- **최종 V93 브라우저 검수 통과:** https://github.com/mouk30/japan/actions/runs/39593224842 — 97개 검사항목 통과, 오류 0건. 사용자가 거절·허용·철회하는 과정을 거쳐 공식 선사 클릭과 운항정보 클릭의 분리 확인.
- **배포 사이트 상태 확인:** 공개 홈·/ferry/·/booking/japan-cruise/ 3개에서 GA4 측정 ID 발견되지 않음. 현재 클릭 수 **미확인(null)**; Vercel에 유효한 실제 GA4 ID 입력 및 재배포 후 수집 가능.
- V93 synthetic browser tests: https://github.com/mouk30/japan/actions/workflows/v93-ga4-booking-click-qa.yml
- 테스트용 `G-TEST123456`을 **GitHub Actions의 일회성 컴파일에만** 주입해서 확인하며, 이 임의 값을 공개 사이트나 실제 GA4에 사용하지 않음.
- 방문자 동의 이전 Google 전송 **0회**, 수집 거부 후 방문·클릭 이벤트 **0회**, 동의 후 항로/버튼/허브 출처별 정확한 이벤트 생성 확인.
- 실제 공식 선사 새 탭 16건의 클릭을 Playwright로 검수, 동의 철회 후 새 이벤트 생성 중단 확인.
- 환경변수 없는 정적 빌드에서 `data-nf-ga4`/Google 태그가 전혀 삽입되지 않는 것 확인.
- `scripts/v93_public_ga4_readiness.py`는 **실제 공개 페이지의 연결 여부만 점검**하고 측정 ID 전체나 개인정보를 로그에 남기지 않음.

## 숫자의 의미와 한계

- 수집 허용한 방문자의 **공식 사이트 이동 클릭 수**를 집계한다. 수집 거절·광고차단 사용자는 포함되지 않아 전체 방문자 클릭을 정확히 나타내지 않을 수 있다.
- 공식 사이트로 이동한 수 = 해당 사이트에서 예약 또는 결제한 수가 아님.
- 허브 클릭수 / 허브 조회수는 **조회당 활동량**으로 표현하며 **실제 구매전환율이 아니다**. 한 사람이 여러 번 클릭하면 100%를 넘을 수 있음.
- V93 전 데이터는 GA4에서 소급 생성되지 않으므로, V92 이전/이후 성과를 정확히 비교한다는 주장 불가.
- 정식 개인정보 처리방침·쿠키 안내 적합성은 운영자가 데이터 처리 현황과 관련 법률에 맞게 별도 검수해야 한다.

다음 단계인 [V94](../v94/README.md)에는 실제 GA4 CSV 파일을 공급받아 항로별·버튼별·허브별 보고서를 산출하는 무조작 스크립트가 있다.
