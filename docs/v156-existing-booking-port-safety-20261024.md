# V156 — 실제 예약 가능 경로·운영 변경·귀선 안전 품질 보강

기준일 2026-10-24. **신규 글 0**. 기존 4개 페이지 수정:
- `/things-to-do/shimonoseki-cruise-port-day-trip/`
- `/things-to-do/sado-ogi-cruise-port-day-trip/`
- `/guide/busan-shimonoseki-ferry/`
- `/booking/japan-cruise/`

## 확인된 운영 문제와 조치

1. **시모노세키 국제크루즈 vs 부산행 페리:** 시모노세키시 2026-07-27 항만 자료는 크루즈 부두 3개(장주데지마/아루카포트/본항지구)를 명시합니다. [공식 크루즈 부두 3곳](https://www.shimonoseki-port.com/57635.html)과 [2026·2027 입항 예정표(2026-10-23 갱신)](https://www.shimonoseki-port.com/120177.html)를 분리. 관광객이 하선한 부두의 승객 게이트·선사 셔틀·장소를 확인하지 않은 상태에서 가라토시장 도보 코스를 확정하지 않습니다.
2. **관부훼리(부산⇄시모노세키) 인터넷 예약 중단:** [선사 2026-10-23 안전 점검 공지](https://www.kampuferry.co.jp/news/20261023systemmaintenance.html)에 따라 인터넷 예약 중지·재개일 미정. 같은 공지의 *영문 국제고객* 지침은 해외 고객의 예약 및 취소를 `support@kampuferry.co.jp` **이메일로만** 접수한다고 안내. 별도 일본어 국내고객 전화접수 지침과 혼동하지 않음. 메일 발송/온라인 화면 표시는 좌석 확보가 아니고, 공식 회신·결제 절차 확인 전 호텔/승차를 확정하지 않음. 국제고객 공식 공지의 통상 예약 신청 기간은 승선 두 달 전부터 전날까지(시모노세키 출발 왕복의 부산발 복귀편은 별도 세 달). [한국어 공식 국제선 승선터미널](https://www.kampuferry.co.jp/lang_kor/passenger_info/t_access/)과 [공식 수속](https://www.kampuferry.co.jp/lang_kor/passenger_info/t_access/checkin.html) 연결.
3. **사도섬 오기항 관광버스와 합승택시 구분:** [사도버스 정기 관광버스 중단](https://www.sado-bus.com/sightseeing/) 공지: 기사 부족으로 당분간 운행중단. 별도 [2026-07-18~11-30 관광 합승택시 공지](https://www.sado-bus.com/news/5492/)는 아이카와·사도금산 관광 대상의 **전날 15:30까지 완전 예약제**, 최대 9명, 만석 시 예약 불가. 오기항 출발 보장이나 크루즈 귀선 맞춤형 차량이 아님. [오기선 정기 버스 노선](https://www.sado-bus.com/route/ogi/)과 별도 검증하며, 왕복 귀선이 안 되면 가까운 항구 주변 관광으로 축소.

## 실제 적용 규칙
- 사진 주제/촬영연도/저작권/CC 출처 손대지 않음. 기존 URL, canonical, 메타, H1, 내부/외부 링크 및 사이트맵 모두 유지.
- 각 기존 페이지에 공식 운영자 확인 링크 3개 + 명확한 귀선 대안 링크 1개, 모바일 단일열에서도 보이는 48–52px 터치 CTA를 추가함.
- 오해할 수 있는 온라인 예약 버튼보다 외부 공식 공지와 `mailto:`를 먼저 제공하되, 예약·좌석·결제 확정으로 잘못 표기하지 않음.
- 보험적 안내가 아닌 실제 이용 순서: **해당 선석 확인 → 항차별 허용된 예약/이동수단 신청 → 확정 회신/전날 마감 → 실제 귀선 게이트 확인**.
- 기존 고정 요금·시간표를 추정한 새 숫자는 추가하지 않음.
- 소유자 인증이 필요한 **GA4/GSC/Naver Search Advisor 실측 수치 없음**. 계정 연결 이전에 클릭/전환 0건으로 기재하지 않음.

## QA
`scripts/qa_v156_existing_official_booking_return.py`: `origin/main`과 네 개 기존 페이지의 이미지/ALT/면책·사진 CC/SEO/H1/기존 링크 및 sitemap.xml 무결성을 비교, 각 공식 링크/운영 경고/귀선 동선을 검수. Build/이전 예약·사진·프라이버시 회귀 검사, Vercel Production 배포 후 실제 www.nipponferry.com HTTP 확인.
