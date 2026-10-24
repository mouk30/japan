# NIPPONFERRY V159 — 기존 기항지 실제 운영 변경·예약·귀선 보강 (2026-10-24)

## 이번 작업의 완료 범위
- 기존 크루즈 기항지 상세 **5편 수정**, 신규 페이지 **0편**, 사이트맵 변경 **없음**.
- 기존 사진·alt·크기·Wikimedia 출처·CC 표시·기존 링크·H1·meta description·canonical을 보존.
- 각 상세의 첫머리에 **선석/승객 게이트 → 공식 운영기관 입장·예약 → 복귀 교통** 3단 실전 카드 추가.
- 미확인 날짜별 예약 잔여석, 실제 선사 셔틀, 크루즈 승객 최종 귀선시각을 확정 문구로 표시하지 않음.

## 운영정보 원문과 적용 범위

| 수정한 기존 URL | 확인된 운영 공지·공식 예약 | 반드시 구분해야 할 귀선 위험 |
|---|---|---|
| /things-to-do/shimizu-cruise-port-day-trip/ | 시미즈항 관리국 2026년 10–12월 입항·오키쓰 일반 견학 제한 https://www.portofshimizu.com/overview/%E5%AE%A2%E8%88%B9-%E5%B8%86%E8%88%B9/ ; 쓰카마 수상버스 운영사 2026-11-01 운임 예정: 성인 1,000엔/아동 500엔 https://www.shimizu-cruise.co.jp/news/detail/934 ; 운행·시간표 https://www.shimizu-cruise.co.jp/fare/ | 관광 수상버스≠크루즈 선사 셔틀, 히노데/오키쓰 선석과 실제 승객 게이트 구별 |
| /things-to-do/osaka-cruise-port-day-trip/ | 오사카시 부두별 SOLAS 출입·투어 차량 사전 신청 https://www.city.osaka.lg.jp/port/page/0000442982.html ; 덴포잔 시설·도보 https://www.city.osaka.lg.jp/port/page/0000002874.html ; 가이유칸 날짜별 공식 e티켓 https://www.kaiyukan.com/info/ticket/kaiyukan/ | 덴포잔과 중앙돌제·서쪽 부두가 다름, 투어 차량 보안 출입 조건과 승객 귀선 마감 별도 |
| /things-to-do/sasebo-cruise-port-day-trip/ | 사세보시 국제터미널 두 곳 주소 https://www.city.sasebo.lg.jp/kouwan/koukanri/terminal-info.html ; 2026-10-05 갱신 크루즈 안내 https://www.city.sasebo.lg.jp/kouwan/cruise/cruise.html ; 하우스텐보스 한국어 공식 입장권 https://english.huistenbosch.co.jp/ticket/?lang=ko | 우라가시라(하리오키타마치 342-2)와 요코우 테라스(히즈쿠시초 1-42) 장거리 역주행 방지 |
| /things-to-do/sakaiminato-cruise-port-day-trip/ | 2026-10-21 게시 10/26 스펙트럼 오브 더 시즈 공지 https://www.sakai-tottori.jp/archives/3375 ; 항만 접근 https://www.sakai-tottori.jp/ ; 미즈키 시게루 기념관 09:30–17:00, 최종 입장 16:30, 공식 온라인 티켓 경로 https://mizuki.sakaiminato.net/ | JR 사카이미나토역≠크루즈 터미널. 박물관에서 역까지만 돌아오면 선박까지 미도착 |
| /things-to-do/otaru-cruise-port-day-trip/ | 오타루시 제3부두·가쓰나이 부두 접근 구분 https://www.city.otaru.lg.jp/docs/2020112000666/ ; 공식 운하 유람선 예약 https://otaru.cc/standardv2/ ; 운항·취소 https://otaru.cc/timetable/ | 운하 관광유람선과 대형 크루즈는 별개. 제3부두=JR오타루역 도보 약 15분, 가쓰나이=JR오타루칫코역 도보 약 20분 |

## 검수 결과
- GitHub Actions의 V159 원본 비교·SEO·사진·링크·CTA 자동 검사: **성공** (2026-10-24).
- 5편의 원본·개정 파일 직접 비교: **55/55 세부 검사 통과**.
- 공개 실사이트 검증은 별도 워크플로 `v159-public-port-qa.yml`에서 5개 페이지·WebP 5개·사이트맵 1개 = **11개 HTTP 항목**을 검사.
- 크롤러 접근 불가 또는 Vercel 반영 지연으로 공개 HTTP 검사가 실패하면 **완료 주장 금지**. 원문과 새 섹션의 일치·사진 로딩까지 통과한 뒤 공개 검증을 별도로 보고.
- GSC·네이버 검색성과·GA4 실측과 실제 상품 잔여석·결제 성공은 검수 대상에서 제외(권한/실시간 데이터 없음).

## 운영 정책
- 이 단계에서 새 글 발행, 기존 URL 변경, AI 이미지 증산, 메타·canonical 변경 금지.
- 다음 버전 역시 **변경이 실제로 확인된 기항지부터** 정정. 시간표·셔틀·예약이 불확실하면 여행일 운영기관 페이지와 안전한 대체 동선만 제공.
