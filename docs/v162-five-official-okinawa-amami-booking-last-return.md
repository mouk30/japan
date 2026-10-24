# NIPPONFERRY V162 — 공식 운영 변경·실예약 연결·마지막 귀선 기존 콘텐츠 보강

**공식 조회 기준일:** 2026-10-24. **신규 게시글 0개 / 기존 기항지 5편만 수정.**

## 변경된 기존 페이지 및 근거

| 기존 상세 URL | 공식 기관 2026-10-24 확인 사실 | 예약·마지막 귀선 핵심 |
|---|---|---|
| /things-to-do/hirara-miyakojima-cruise-port-day-trip/ | 오키나와현 10/22 20:00경 이라부·이케마대교 통제 → 10/24 10:36 폭풍경보 해제 → 도로점검 후 12:00경 통행 재개 **예정**. 미야코지마시는 구리마대교도 점검 후 12:00경 재개 예정 공지. https://www.pref.okinawa.jp/machizukuri/doboku/1013660/1022503/1030425.html ; https://www.city.miyakojima.lg.jp/ | 해제 예정 ≠ 확정 통과. 히라라항 일반 렌터카 픽업 제한/관광차량 허가 안내 유지: https://www.city.miyakojima.lg.jp/soshiki/shityo/kensetsu/kouwan/oshirase/2024-0222-0902-121.html |
| /things-to-do/motobu-cruise-port-day-trip/ | 이에촌 공식 10/24 06:15 모토부↔이에섬 4왕복 **전편 결항**. 10/25 전편/일부 결항 전망, 당일 06:30경 재결정. https://www.iejima.org/ | 도서 왕복 페리와 모토부 크루즈 귀선 게이트 구분. 날씨로 차량 승선 예약 무효시 재예약. 자동 발권기 Edy·WAON·교통계 전자머니 불가, 현금·신용카드. https://www.iejima.org/?pid=119 |
| /things-to-do/ishigaki-cruise-port-day-trip/ | 안에이관광과 야에야마관광페리 각각 10/24 전편 결항. 야에야마 측 10/25 미정, 안에이 측 10/25 하테루마 전편 및 기타 일부편 결항/미정. 야에야마 공식 https://yaeyama.co.jp/ ; 안에이 https://aneikankou.co.jp/condition | 이도여객선+육상 복귀가 확보되지 않으면 이도 당일 관광 중단. 이시가키공항 10/24 정오 건물 개방은 조건부 예정으로 실제 항공 운항과 구분. https://www.ishigaki-airport.co.jp/info/2026/10/30.html |
| /things-to-do/naha-cruise-port-day-trip/ | 구메지마 오션제트 10/24·10/25 나하부두↔가네구스쿠항 고속선 **결항**. 공식 https://ko-jet.com/news/ | 직접 공식 연동 예매 https://reserve.smart-theater.com/?projectId=kumejimaoceanjet-production 는 결항일 예매 권유 용도가 아님. 예약 변경·취소는 나하부두 영업소 098-943-6496에 문의. 정기선 나하부두와 대형 크루즈 귀선 게이트 구분. |
| /things-to-do/amami-naze-cruise-port-day-trip/ | 마릭스라인 10/23 가고시마 출발 퀸코랄플러스 **결항**, 따라서 10/24 나제 입·출항 예정도 결항: https://marixline.com/service/downstream20261023/ . 마루에이페리도 날짜·편명별 취소 공지: https://www.aline-ferry.com/ | 마릭스라인은 취소된 항차를 다른 날짜로 변경하려면 **새 예약 필요**. 연결된 정식 예매 서비스 https://ferry.smaku.app/ . 나제 본항/신항/나가하마 및 크루즈 승객 귀선 부두는 개별 항차 확인. |

## 실제 적용
- 위 기존 5편 `index.html`의 원본 사진·사진의 촬영 장소/시기 및 Wikimedia 라이선스 링크·alt·기존 메타·canonical·H1·기존 링크·사이트맵 모두 보존.
- 원본 크루즈 안내보다 먼저 **① 공식 변경/운항 ② 이용자 예약·취소 ③ 실제 귀선 차량·게이트** 카드 3개를 추가하고 모바일 52px 버튼/1열 카드를 적용.
- 시간 한정 임시 취소/해제 안내는 적용일과 출처를 기재하고, 타사 정기선이나 외항 크루즈 전체의 취소로 일반화하지 않음.
- 신규 글/이미지/키즈관 발행·메타 구조 개편 없음.

## 검수 및 제외
- GitHub Actions: `.github/workflows/v162-five-ports-operator-return.yml`, `scripts/qa_v162_official_five_booking_return.py` — V161 마무리 커밋 `04c7f107ad9ef0ab4e3ee24643357201dc6969c8` 기준 5편 원본 비교와 공식 링크·승선 정보·모바일·사이트맵 검사, `node build.js`.
- 실제 공개 HTTP: `.github/workflows/v162-public-five-ports.yml`, `scripts/qa_v162_public_five_ports.py` — 기존 상세 5개, 원본 WebP 5개, sitemap.xml 1개 = 11개 항목.
- 검증 완료 주장은 Actions 실행 결과와 공개 배포를 재확인한 후에만 가능. 임시 운영 변경/태풍 공지의 실시간 유효성은 출발일 다시 재확인해야 함.
- 실시간 유료 예약 잔여석, 표 결제 성공, 보험/환불 처리 완료, 귀선 셔틀 최종 출발시각, GA4 클릭, 구글/네이버 계정 노출 수치는 이 작업에서 검증하지 않음.
