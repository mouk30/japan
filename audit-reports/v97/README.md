# NIPPONFERRY — V97: GA4 Production 활성화 및 실제 배포 검증

**작성·배포: 2026-10-21 KST. 기존 정적 사이트 유지. 신규 HTML 게시글 0개.**

## 결과 및 현재 상태

- **실제 운영 사이트 GA4 상태:** 미연결. 공개 홈페이지, 페리 허브, 예약 허브, 후쿠오카 가이드 **총 4개 페이지 접속 후 GA4 태그 부재 확인**.
- **코드 준비:** GA4 실제 측정 ID가 Vercel Production에 설정된 새 배포본에서는 방문자 사전 동의 후에만 Google Analytics 측정 스크립트를 불러오도록 구성됨. Vercel 환경변수 변경만으로 기존 배포본이 업데이트되는 것은 아님.
- **V97 배포 검수:** [정상 통과한 GitHub Actions](https://github.com/mouk30/japan/actions/runs/39618805702). 가상 입력 테스트 7/7 통과, 실제 공개 사이트에서 `not_connected` 상태를 있는 그대로 기록. ID나 클릭 수를 생성하지 않음.
- **V93 동의 처리 수정 검수:** [GitHub Actions 100/100 통과](https://github.com/mouk30/japan/actions/runs/39618877671). 사전 거절 → 허용 → 거절 → 다시 허용 시 동의 상태가 재설정되는지 확인. 광고 저장/맞춤광고 동의는 모두 거부 상태로 유지. 선사 사이트는 모의 응답으로 격리해 이벤트 테스트에 외부 선사 사이트 접속 장애가 영향을 주지 않도록 했고, 외부 예약 URL의 실제 유효성은 **V90 별도 검사**로 유지함.

## 사용자 계정에서 한 번만 필요한 실제 연결

1. [Google Analytics](https://analytics.google.com/)에서 이 사이트용 웹 데이터 스트림을 생성하거나 기존 스트림을 열고, 실제 **측정 ID `G-XXXXXXXXXX`** 확인. Google 공식: [Measurement ID 설명](https://developers.google.com/analytics/devguides/collection/protocol/ga4/reference?client_type=gtag).
2. [Vercel Dashboard](https://vercel.com/dashboard)에서 **www.nipponferry.com이 연결된 정확한 프로젝트**를 선택하고 **Settings → Environment Variables**로 이동.
3. 다음 변수를 추가:
   - **Key:** `GA4_MEASUREMENT_ID`
   - **Value:** 발급받은 실제 `G-` 측정 ID
   - **Environment:** `Production` (필수). 사이트 배포가 Production에 연결돼 있는지 확인.
4. **Deployments → 최신 프로젝트 배포 → ⋯ → Redeploy** 또는 main에 새 커밋을 배포한다. **기존 배포에는 새로운 환경변수가 소급 적용되지 않는다**. (공식: https://vercel.com/docs/environment-variables)
5. [V97 Production 검사 워크플로](https://github.com/mouk30/japan/actions/workflows/v97-ga4-activation.yml)에서 **Run workflow → require_configured=true → Run** 선택. 이 경우 실제 태그가 4개 페이지에 설치되지 않았거나 JS/CSS가 깨졌으면 검사 실패로 표시한다.
6. 실제 사이트 방문 → 통계 수집 **허용** → 항로별 선사 예약 버튼 클릭 → [GA4](https://analytics.google.com/) **Reports → Realtime**에서 `ferry_operator_click` 이벤트 확인. 실시간 테스트에서 누르지 않은 클릭은 만들어 테스트하지 않는다. DebugView를 쓴다면 Tag Assistant 디버그 모드가 필요하고 수집 동의가 없으면 표시되지 않을 수 있다. (공식: https://support.google.com/analytics/answer/7201382)
7. GA4 **Admin → Custom definitions**에서 `route`, `page_area`, `placement`, `operator`, `destination_step`를 *이벤트 범위* 맞춤 측정기준으로 등록. 그 후 탐색(Explore)에서 항로별·버튼 위치별 실측치를 내보내면 V95·V96에 연결할 수 있다.

**아직 실제 Vercel 접근 권한/GA4 스트림 ID가 없어 이 환경변수 추가나 재배포를 대신 수행할 수 없었다.** Vercel 앱 계정 연결을 허용하면 직접 해당 프로젝트의 연결 상태를 확인하는 작업으로 이어갈 수 있다. 측정 ID를 코드에 하드코딩하거나 테스트용 `G-TEST123456`을 운영환경에 사용해서는 안 된다.

## V97 기술 작업

- `scripts/v97_ga4_activation_gate.py`: 공개 4개 페이지 HTTP 응답·canonical·GA4 태그 1회 삽입·태그 ID 형식·각 페이지 스트림 일치·동의 JS/CSS 상태 검사. 전체 측정 ID는 로그에 기록하지 않음.
- `tests/test_v97_ga4_activation_gate.py`: 연결 전, 정상 설치, 서로 다른 스트림 ID, 중복·손상 코드, 스크립트/CSS 오류를 다루는 정적 회귀 검사 7개.
- `.github/workflows/v97-ga4-activation.yml`: 매일 **한국시간 09:37경** 정적 상태 점검 및 수동 `require_configured` 검증. 수집 미연결 상태는 **운영 준비 대기**로 기록하지 즉시 사이트 장애로 오판하지 않음. 실제 활성화 후 선택한 `require_configured=true` 검사에서는 미연결이면 실패로 판단.
- `site/nf-v93-booking-clicks.js`: 이전에는 사용자가 통계를 허용한 뒤 거절하고 **동일 페이지에서 다시 허용**해도 Google에 전달되는 동의 상태가 복원되지 않을 수 있었음. 이를 개선하고 광고/개인화 관련 동의를 기본적으로 거부하도록 구현.
- `build.js`: 새로운 동의 스크립트 캐시 식별자 `?v=20261021-v97`을 사용하여 최신 코드를 배포하도록 함.
- `scripts/v93_ga4_click_browser_qa.py`: 방문자 동의 변경, 거절 시 이벤트 차단, 재허용 후 재수집, 정확한 항로·공식 버튼 이벤트를 합쳐 100건의 브라우저 확인. 실제 운영 GA4에 이벤트를 전송하지 않는 검증.

## 연결 후 비교할 수 있는 지표

- [V95 실제 측정 데이터 비교](../v95/README.md): 4개 항로 + 2개 허브 + 4개 항로 가이드별 **공식 선사 이동·예약 진입 클릭**.
- [V96 두 기간 비교](../v96/README.md): 이전·최근 같은 길이 기간의 클릭 활동량 변화와 검토 후보.
- GA4에 실제 클릭/조회 기록이 없는 동안 위 보고서의 수치는 **미확인(null)**이고, 완료 예약·발권·구매전환으로 표시하지 않음.

### 보안·검색엔진·운영 유의사항

- 이용자가 통계 수집을 거절하면 Google tag 로드를 시작하지 않음. 동의 재설정 가능. 광고 추적 동의는 코드에서 거부.
- 설정 검수 시 전체 GA4 측정 ID를 서버 출력·GitHub 로그에 노출하지 않음.
- `GA4_MEASUREMENT_ID`는 Vercel Production **빌드 환경변수**이며 GitHub 소스 코드에 추가하거나 실제 ID로 GitHub fixture를 대체하지 말 것.
- HTML 페이지 추가, SEO 제목·정규 URL·사이트맵 및 기존 예약 링크 변경 없음.
- V97가 `installed_ready_for_owner_realtime_test`라고 보고해도 **실제 GA4 수신은 계정 내 Realtime/DebugView에서 별도 확인**해야 함.
