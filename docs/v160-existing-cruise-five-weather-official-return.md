# NIPPONFERRY V160 — 공식 운항 변경·예약 경로·마지막 귀선 보강

**검수 기준일 2026-10-24 · 기존 기항지 상세 5편 수정 · 신규 게시글 0편 · 기존 사진/WebP, SEO, URL 보존**

## 실제 운영 변경을 기준으로 수정한 페이지

| 기존 페이지 | 공식 확인 내용 | 직접 이동할 공식 출처 | 여행자 행동 |
|---|---|---|---|
| 이시가키 /things-to-do/ishigaki-cruise-port-day-trip/ | 2026-10-24 11:18 안에이관광: 태풍 30호로 전 노선·전편 결항. 10/25 하테루마 전편 결항, 기타 선편 12:30 이시가키 출항까지 결항, 13:00 이후 미정 | https://aneikankou.co.jp/condition (운항), https://aneikankou.co.jp/ (온라인 승선권) | 오늘 이도관광 중단. 다음날 운항 재개를 추정하지 말고 왕복 운항 상태 확인. 대형 크루즈 선박 귀선과 이도여객선 터미널 구분 |
| 모토부 /things-to-do/motobu-cruise-port-day-trip/ | 2026-10-20 미쓰이 오션 후지: 10/25 모토부 07:00–18:00 기항 포함 **특정 상품 취소** | https://www.mitsuioceancruises.com/news/20261020.html ; https://www.mitsuioceancruises.com/contact/ | 취소 상품으로 관광권·송영차량 구매 금지, 예약 여행사 통해 대체·환불 확인. 다른 선사의 모토부 운항을 취소로 단정하지 않음 |
| 나하 /things-to-do/naha-cruise-port-day-trip/ | 기존 10/23 나하 출항 16:00 예정 미쓰이 상품 취소, 새 10/23 하카타 발착 상품 편성 | https://www.mitsuioceancruises.com/news/20261020.html ; https://www.mitsuioceancruises.com/ | 나하 승선 수속이 가능한지 기존 예약처에서 확인. 변경 자동 승인·잔여 좌석을 추정하지 않음 |
| 사세보 /things-to-do/sasebo-cruise-port-day-trip/ | 미쓰이 10/24 사세보 08:00 입항·18:00 출항으로 **대체 상품 편성** | https://www.mitsuioceancruises.com/news/20261020.html ; https://www.city.sasebo.lg.jp/kouwan/koukanri/terminal-info.html | 실제 선석·귀선 게이트를 우라가시라/요코우 중 선내 공지로 재확인. 18:00은 승객 최종 귀선 마감이 아님 |
| 하카타 /things-to-do/hakata-cruise-port-day-trip/ | 미쓰이 변경 상품 10/23 17:00 하카타 출항, 10/28 09:00 귀항 예정 | https://www.mitsuioceancruises.com/news/20261020.html ; https://hakataport.com/Access/ | 국제여객터미널과 크루즈센터 구분, 예약 및 실제 수속지 안내 확인. 미쓰이 특정 항차 외 다른 선박에 일괄 적용하지 않음 |

## 적용된 UX/SEO 정책
- 5편 모두 첫머리 **01 공식 운항·접안 → 02 실제 운영기관 예약/문의 → 03 최종 귀선 교통** 카드 3개를 배치.
- 대상 페이지 원본 제목, H1, canonical, OG/SEO 메타, 본문 링크, 원본 WebP, 촬영연도/alt/CC 사진 출처를 유지.
- 기항 취소 안내에 명시적인 선사·항차·날짜를 붙이고 그 기간 이외에는 일반화하지 않음.
- 운항 당일 수정 가능성이 있으므로 실시간 상황은 반드시 원문을 우선 확인하도록 알림.
- 2026-10-24 시점 사실을 설명하는 것으로 향후 예약 잔여석, 선사 탑승 마감, 실제 결제 성공, GA4·GSC 노출 수치를 보증하지 않음.
- XML 사이트맵/URL을 새로 발행하거나 수정하지 않음.

## QA
- `scripts/qa_v160_five_weather_booking_return.py` + `.github/workflows/v160-verified-weather-booking-return.yml`: immutable V159 원본 SHA 기준으로 5개 가이드 수정·사진·출처·SEO·sitemap 보존, 공식 링크, 불확실성 구분 검사.
- `scripts/qa_v160_live_five_ports.py` + `.github/workflows/v160-live-five-port-qa.yml`: 공개 사이트 5페이지, 실사 WebP 5개, 사이트맵 = 총 11 HTTP 검사. 성공 여부는 실제 Actions 실행 결과를 우선.
