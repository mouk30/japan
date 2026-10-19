# NIPPONFERRY · 상업 롱테일 3편 실측 운영 기준 (2026-10-19)

## 실험 대상 — 페이지 추가 금지, 세 주제만 관측
1. /japan-cruise/busan-hakata-ferry-reservation/
2. /japan-cruise/bukan-ferry-shimonoseki-price/
3. /japan-cruise/panstar-miracle-osaka-cabin-types/

## 측정 구분
- **검색 유입**: Google Search Console, 네이버 서치어드바이저에서 URL별 노출, 클릭, CTR, 평균 순위(가능한 범위).
- **사이트 방문**: GA4에서 랜딩 페이지별 organic sessions. GA4 설치·동의 설정 완료 전에는 측정된 것으로 간주하지 않는다.
- **실제 행동**: `nf_travel_link_click` 이벤트를 GA4 또는 GTM에서 수집하도록 구성한 경우에만 외부 사이트 이동 클릭 집계.
- **예약 성과**: 별도 제휴/운항사 전환 데이터 또는 결제 확인이 없으면 **확인 불가**. 예약 화면 열기를 실제 예약 전환으로 보고하지 않는다.

## 이벤트 계약 (site/nf-longtail-clicks.js)
| 필드 | 의미 |
| --- | --- |
| event | nf_travel_link_click |
| experiment | longtail_ferry_trial |
| page_path | 위 세 경로 중 하나 |
| link_type | operator_booking_start / operator_official_info / internal_booking_guide |
| destination_host | 링크 목적지 도메인 (개인정보 없음) |
| destination_path | 링크 목적지 경로 (쿼리 문자열 제외) |

**주의**: 이 스크립트는 데이터 수집 서버가 아니다. 기존 GA4 gtag가 설치되면 이벤트를 보내고, GTM이 설치되면 dataLayer에 이벤트를 전달한다. GA4/GTM 미설치 또는 GTM 트리거 미구성 상태에서는 **보고서에 클릭수가 쌓이지 않는다**. 도메인·GA4 측정 ID를 확인하지 않은 채 추측값을 삽입하지 않는다.

## 출시 전 체크
- 각 페이지 SEO canonical, description, 유효 JSON-LD, 내부 링크, 모바일 390·태블릿 768·PC 1440 화면 및 외부 링크 클릭 이벤트: `scripts/qa_longtail_3.cjs` 검사.
- 세 URL 공개 도메인 HTTP 200 및 robots/noindex, sitemap 반영 확인.
- 각 운항사의 운항 여부, 실제 객실·운임·유류할증료, 예약 경로 확인(외부 페이지의 날짜별 예약 가능 여부는 별도).
- Google Search Console 및 네이버 서치어드바이저에 URL 제출·색인 확인. 색인 신청은 노출 또는 순위를 보장하지 않음.
- GA4 또는 GTM 연결 확인, 동일 클릭의 중복 전송 여부 테스트, 맞춤 측정기준 `page_path`, `link_type` 설정. 실측 수집 시작일 기록.

## 성과 기록
| 주간 기준일 | 검색엔진 | 랜딩 URL | 노출 | 클릭 | CTR | organic sessions | 공식 사이트 클릭 | 예약 시작 클릭 | 확인된 예약 건수 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 미측정 | Google/Naver | 세 URL 각각 | 미측정 | 미측정 | 미측정 | 미측정 | 미측정 | 미측정 | 미측정 |

## 확대·중단 기준
- 공개 후 **28일 이상** 데이터가 누적되면 3개 주제별 검색 노출·클릭·공식 링크 클릭의 움직임을 비교한다.
- 의미 있는 검색 수요나 사업적 행동이 포착된 주제만 추가 페이지 후보 조사.
- 성과가 없다면 색인·검색 의도·공식 정보 정확성·검색 경쟁을 먼저 점검하고 자동 증산하지 않는다.
- 저품질 중복 페이지, 체험하지 않은 후기, 확인되지 않은 요금·실시간 잔여석은 생성하지 않는다.
