# V172 — 구레·후쿠야마·사카이데·마이즈루 4개 기존 기항지 보강 완료

최종 확인: 2026-10-24 (KST)
**기존 페이지 4편 수정 · 신규 게시글 0편 · 원본 사진 0장 교체 · 기존 SEO·URL·사이트맵 보존**

## 수정 대상

1. /things-to-do/kure-cruise-port-day-trip/
2. /things-to-do/fukuyama-cruise-port-day-trip/
3. /things-to-do/sakaide-cruise-port-day-trip/
4. /things-to-do/maizuru-cruise-port-day-trip/

각 기존 상세페이지의 사진 아래 원문 앞에 **공식 운영/예약 · 실제 승선장/이동 · 안전 귀선**을 설명하는 카드 3개씩, 총 12개 카드를 삽입. 390px 모바일 1열·태블릿 2열·PC 3열. CTA min-height 52px. 원본 사진, 촬영시점, 저작자·라이선스, 모든 기존 링크·H1·title·description·canonical·site/sitemap.xml 보존.

## 공식 정보와 실제 적용

### 구레
- 운영사 [Bunker Supply](https://bunker-supply.com/service/sightseeing_cruise/) 구레만 함선 관광선: 사전 WEB 예약은 출항 2일 전까지; 당일 전화 예약 불가, 현장 잔여석은 운영기관 문의. 운영사 안내의 현장 결제 문구와 연결된 외부 예약 화면의 '온라인 결제 전용' 분류가 다른 점을 고려해 결제 완료/방식을 보장하는 문구를 게시하지 않음.
- **구레 중앙잔교 터미널 1F, 다카라마치 4-44**는 해당 관광선의 매표/승선 장소이지 대형 크루즈 접안 선석으로 자동 적용되지 않음. https://kure-trip.jp/spots/469
- 야마토뮤지엄 2026-04-23 재개관, 통상 09~18시 / 최종 입장 17:30 / 화요일 휴관(예외). https://yamato-museum.com/%E6%9D%A5%E9%A4%A8%E6%A1%88%E5%86%85/%E3%81%94%E5%88%A9%E7%94%A8%E3%81%AB%E3%81%A4%E3%81%84%E3%81%A6/

### 후쿠야마
- [후쿠야마시 2026-10-16 시영 도선 최신 안내](https://www.city.fukuyama.hiroshima.jp/soshiki/kanko/91534.html): 도모노우라–센스이지마 약 5분, 안내 성인 왕복 240엔·어린이 120엔, 운항 확인 084-982-2115. 외항 크루즈 터미널과 동일하지 않음.
- 센스이지마의 2026-02-12 고시키이와 방면 일부 산책로 개방과 고우라→다노우라 계속 통제 구분 https://www.city.fukuyama.hiroshima.jp/site/miryoku2023/287776.html .
- 도선 귀항 후 크루즈선 원래 하선 부두까지 육상 차량/셔틀 이동이 추가됨을 명시.

### 사카이데
- 2024-12-17 미쓰이 오션 후지 **하야시다 A호 안벽 기항**은 사카이데시가 공개한 과거 항차 사실만으로 기재. 2026 선박의 접안·승객 게이트로 추정 금지. https://www.city.sakaide.lg.jp/soshiki/kouwanka/cruise.html
- 세토대교 기념공원과 기념관 무료, 기념관 통상 09~17시 마지막 입장 16:30, 월요일 휴관(공휴일 예외), 민간 세토대교 타워는 유료. https://www.city.sakaide.lg.jp/soshiki/sangyoukankou/kinenkouen.html
- JR 사카이데역 출발 이동시간을 항만 선석에서 출발하는 시간과 구분.

### 마이즈루
- [마이즈루시 2026 크루즈 입항 예정](https://www.city.maizuru.kyoto.jp/kankou/0000014705.html) 상 서항 제2부두(舞鶴西港第2ふ頭)와 [신일본해페리 동항 마에지마부두(浜2025-1)](https://www.snf.jp/guide/embark/maizuru/) 분리. 모든 항차가 일률적으로 서항 제2부두에 기항한다는 단정 금지.
- 시 발표 2026 무료 명소 루프버스는 10월 **18일·25일**만 운행하며 동마이즈루역 출발 관광노선(고로전망대 등). 10월 24일이나 서항 크루즈 하선 선석에서 항상 운영되는 셔틀이 아님. https://www.city.maizuru.kyoto.jp/kankou/0000015405.html
- 정기페리의 터미널 도착 권고 60분 전(성수기 90분), 30분 미도착 취소 취급이라는 조건은 별도 정기선 예약자용으로 안내. **외항 크루즈 귀선 마감과 다름.**

## 실제 배포와 검사

- 콘텐츠 커밋: https://github.com/mouk30/japan/commit/6da1fad6c316489aedc4aaaeab699d77a47f467e
- 회귀 검사 수정 최종 커밋: https://github.com/mouk30/japan/commit/ead0221cd0414622d467a62be9547825430c6f22
- GitHub Actions 최종 https://github.com/mouk30/japan/actions/runs/40098428938 : **SOURCE/BULD PASS 및 PUBLIC BROWSER 16/16 PASS**.
- 4페이지 × 390·768·945·1440px 실제 Chromium 검사: HTTP 200, H1 1개, 원본 canonical, 실제 WebP 디코드/최소 픽셀, 원본 라이선스 링크, 3개 공식 연결, CTA >=50px, 가로 넘침 없음. 스크린샷 16장과 JSON은 위 Actions 두 번째 artifact에 저장.
- Vercel commit `ead0221cd0414622d467a62be9547825430c6f22` 배포 **success**.
- 첫 회귀 검사 0/4 오류는 신규 style id를 기존 ID 집합 비교에서 제외하지 않아 발생한 **검사기 오탐**. 소스 QA 수정 후 PASS. 초기의 브라우저 소스 스크립트 구문오류 역시 실제 배포 수정 전 자동 검사기만 고쳤고 최종 재실행 성공.

## 미검증 범위
- 실제 관광선 온라인 결제/좌석 발권 성공, 정기페리 실시간 좌석·현장 재고, 실제 크루즈 선석 배정/승객 귀선 게이트/마지막 셔틀/최종 승선 마감, GA4/GSC 측정자료는 확인하지 못함.
- 2026 예정 운항일·기관 휴관과 운임은 변경될 수 있음. 방문일에는 공식기관 안내와 선사의 항차별 최종 공지가 우선.

## 후속 V173 추천
기존 글 중 공식 관광예약 버튼이 정보 포털로만 연결되는 경우, 실제 시설 입장권 조건·정기선 항차별 유효성을 우선 재검증. 신규 글 증산 금지 원칙 유지.
