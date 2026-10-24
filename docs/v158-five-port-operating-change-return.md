# V158 — 실제 접안 변경·예약 연결·마지막 귀선 수단 품질 개선

**2026-10-24 공식 운영처 검수 / 신규 게시글 0 / 기존 기항지 상세 5편만 수정 / WebP 실사·촬영·저작권·기존 URL·SEO 보존**

## 검증한 운영 변경과 선택지
| 기존 크루즈 기항지 | 확인한 문제 | 원문·수정 규칙 |
|---|---|---|
| 고치 | 2026-10-23 고치현 공식 공지는 **10/24 세븐시즈 익스플로러 선석 7-3→7-2 변경**. 다른 선박의 게이트와 동일하다고 가정하면 귀선 위험. 유료·비정기 셔틀을 기본 무료편이라 단정 불가 | [고치현 연도별 크루즈 선석·변경](https://www.pref.kochi.lg.jp/doc/kochi_cruise/), [프린세스 2026 선사별 예정 셔틀](https://www.princesscruises.jp/pdf/ports_shuttlebus.pdf) |
| 마쓰야마 | 마쓰야마시 2026 크루즈 입항 목록의 **외항 제1부두 2호안벽**, 2025-12 프린세스 예상 **해당 부두↔미쓰역 유료** 셔틀을 확정된 모든 선사 교통편처럼 소개 불가 | [마쓰야마시 공식 기항](https://www.city.matsuyama.ehime.jp/shisei/keikaku/kanko/cruisezyoho.html), [선사 셔틀 전망 PDF](https://www.princesscruises.jp/pdf/ports_shuttlebus.pdf), [도고온천 공식 운영](https://dogo.jp/) |
| 니가타 | 2026-10-25부터 니가타공항⇄사도기선 터미널 소형 미니셔틀 시간 변경. **사도기선→공항 오후 최종 15:30 출발(이전 16:15)**. 정원 **13명·현금만·만석 승차 불가**. 크루즈 게이트↔공항 교통과 혼동 금지 | [니가타공항 한국어 2026-10-25∼12-30](https://www.niigata-airport.gr.jp/access/liner/sado/?lang=ko), [사도기선 운항·예약](https://www.sadokisen.co.jp/) |
| 히로시마 | JR서일본 미야지마페리 **2026-10-24 다객(증편) → 일반 시간표로 당일 변경**. 이쓰카이치 크루즈 부두↔JR 미야지마구치 여객항↔미야지마섬 이동 모두 별도. 섬에서 돌아오는 페리만 확인하면 크루즈 귀선 보장 안 됨 | [JR서일본 미야지마 페리 2026-10-22 공지](https://jr-miyajimaferry.co.jp/), [일반 시간표](https://jr-miyajimaferry.co.jp/timetable/), [히로시마항 공식 이쓰카이치 접근](https://hiroshima-minato.jp/enaccessitsukaichi/) |
| 고베 | **제4돌제 포트터미널 4Q·4O** vs **중돌제 NAKA**. 각 접근 역과 보안 게이트가 다름. 일반 시설 개방시간과 승객 귀선 마감, 승용차 비예약 주차/관광버스 예약 구분 필요 | [고베시 입항별 터미널](https://www.city.kobe.lg.jp/a14075/kanko/leisure/harbor/passenger/schedule/index.html), [시설·접근·차량 규정](https://www.city.kobe.lg.jp/a14075/kanko/leisure/harbor/passenger/terminal/index.html) |

## 페이지에 추가한 실제 사용자 행동 순서
1. **실제 선박·접안 선석**을 공식 입항 공지에서 찾고 선내 하선 지침을 우선.
2. **공식 시설·선사·현지 교통 예약/시간표**로 이동하되 예약·매진·무료 여부 등 미확인 상태를 구분.
3. **관광지→복귀 교통→실제 선사 승객 게이트**를 역산하며 차량 미확정 시 장거리 일정을 포기.

- 3단 카드(모바일 단일열), 48–52px 클릭 CTA, 공식 원문 직링크 3개 및 기존 본문 앵커.
- 기존 여행기사 5개, canonical/SEO 제목·메타·원본 실사 WebP/ALT/크기/사진 라이선스·사이트맵을 전부 유지.
- **일별 실제 좌석·마지막 셔틀·승객 게이트 확정 시각 및 실제 예약결제 여부는 확인하지 않음.** 공식 공지가 변경되면 새 날의 자료가 우선.
- GA4 Production ID, GSC/Naver Search Console 사유 데이터 실측이 연결되지 않아 클릭·예약 수치를 계산하지 않음.

## QA
`scripts/qa_v158_five_port_operator_changes.py`: 기존 `origin/main`을 기준으로 위 모든 안내, 3+1 새 링크, 원본 전체 링크·사진·출처·canonical·H1·메타·사이트맵 무결성 검사. Build, 기존 예약·귀선/실사 QA 후 실제 공개 사이트 HTTP 검증.
