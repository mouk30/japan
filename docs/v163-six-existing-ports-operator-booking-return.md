# NIPPONFERRY V163 — 공식 운항 변경·실예약·최종 귀선 (2026-10-24)

## 작업 범위
- 새 기항지/게시글 **0개**. 기존 상세 6편의 운영·예약·귀선 실전 카드만 추가.
- 기존 사진 WebP 6장, 실제 촬영지/ALT/권리표시, 기존 URL, 타이틀/H1/meta/canonical, Article JSON-LD, sitemap, 내부링크는 변경하지 않음.
- 각 기존 안내 상단에 **① 공식 공지 ② 실제 예매·취소 경로 ③ 마지막 귀선·출항항** 3장 카드 추가. 52px 버튼, 모바일 1열.
- 외항 크루즈의 터미널과 연안 정기 페리 터미널·귀선규칙은 다른 시설로 구분.

## 공식 확인 결과 및 수정 항목

| 수정된 기존 가이드 | 공식 사실 | 예약·복귀 행동 |
|---|---|---|
| `site/things-to-do/sado-ogi-cruise-port-day-trip/index.html` | 사도기선 10/24 08:58 주간 예보: 나오에쓰↔오기 10/26~28 ‘아마 괜찮으나 미정’; 출항 당일 1시간 전까지 결정 https://www.sadokisen.co.jp/forecast/ | 10월 오기→나오에쓰 정규표 10:35/17:25는 미확정. 실제 좌석 https://www.sadokisen.co.jp/reservation/seat-availability/?route=2 / 최종 운항 https://www.sadokisen.co.jp/reservation/service-status/?route=2 |
| `site/things-to-do/naoetsu-cruise-port-day-trip/index.html` | 동일 운항 전망. 2026년 10월 정규표 나오에쓰→오기 07:10/14:00, 오기→나오에쓰 10:35/17:25. https://www.sadokisen.co.jp/reservation/timetables/?route=2 | 실제 날짜별 좌석·기상 운항조회, 나오에쓰 대형 크루즈 부두와 사도기선 출항항 구분, 두 번째 육상 이동·마지막 승객 귀선 확보 |
| `site/things-to-do/yakushima-miyanoura-cruise-port-day-trip/index.html` | 오리타기선 10/24 공지: 페리 야쿠시마2 10/24·26 태풍 결항, 10/25 기존 정기 운휴 https://ferryyakusima2.com/news/15696 | 개인 여객 별도 예약 불필요, 차량·문의 099-226-0731 https://ferryyakusima2.com/about . 다른 회사 고속선/외항 크루즈에 자동 적용하지 않음 |
| `site/things-to-do/osaka-cruise-port-day-trip/index.html` | 산플라워 10/23 10:00 공지: 10/23·10/24 오사카↔시부시 양방향 결항, 10/24 기리시마/사쓰마. 오사카↔벳푸·고베↔오이타 정상 안내 https://www.ferry-sunflower.co.jp/news/article/3010231024.html | 10/23 10:00 이후 취소 수수료 면제 정책과 조건별 왕복 취소. 5자리 예약번호·3자리 액세스키로 실제 온라인 취소 https://booking.ferry-sunflower.co.jp/web/yoyaku/ . 오사카 제2터미널≠덴포잔 크루즈 승객게이트 |
| `site/things-to-do/nagasaki-cruise-port-day-trip/index.html` | 규슈상선 10/24 14:28 발표: 나가사키 14:00·15:45 제트포일 결항, 일부 카페리 나라오 기항 생략 https://kyusho.co.jp/status | 정식 예약 https://kyusho.co.jp/reserve ; 제트포일 온라인 출항 1시간 전까지 예약, 30분 전 발권/구매. 마쓰가에 외항 크루즈 터미널과 정기선 승선항 구별 |
| `site/things-to-do/aokata-cruise-port-day-trip/index.html` | 고토산업기선 공식 10/24 운항: 10/24 다이노우라 13:30/나가사키 16:00 결항, 오전 2편 운항. 10/25 전편 결항 https://www.goto-sangyo.co.jp/ | 다이노우라≠아오카타 크루즈 접안 부두. 공식 VELTRA 연동 일반 운임과 국경이도 할인 예약, 바우처 창구 교환 안내 https://www.goto-sangyo.co.jp/pickup/%E4%BA%88%E7%B4%84%E3%82%B5%E3%83%BC%E3%83%93%E3%82%B9%E3%80%8E%E3%83%99%E3%83%AB%E3%83%88%E3%83%A9%E3%80%8F%E3%81%A7%E4%B9%97%E8%88%B9%E4%BA%88%E7%B4%84%E3%81%8C%E5%8F%AF%E8%83%BD%E3%81%AB%E3%81%AA/ |

## QA
- Immutable V161+V162 baseline `04c7f107ad9ef0ab4e3ee24643357201dc6969c8`로 원본 보호 및 공식 링크 확인: `scripts/qa_v163_six_operator_return.py` + `.github/workflows/v163-six-operator-original-qa.yml`.
- 실제 공개 사이트 **6개 기존 HTML + 6개 원본 WebP + sitemap.xml = 13개 HTTP 항목** 검증: `scripts/qa_v163_live_six_ports.py` + `.github/workflows/v163-live-six-ports.yml`.
- 검수 결과는 링크된 실제 GitHub Actions 결론이 우선. 초기 커밋에서 QA가 실패한 경우 최종 커밋의 수정과 재검증 결과로 구분해서 보고.
- 예약 가능 시간/결항 공지와 실결제 좌석 확보는 다른 문제. 실시간 유료 승선권 잔여석, 웹 예약 결제 성공, 외항 크루즈 마지막 탑승, 셔틀, GA4/GSC 실측은 **검증되지 않음**.
- 검색 방문자가 당일 기상·결항·운항 여부를 결정할 때는 반드시 링크된 공식 **여행일 당일** 공지를 우선.
