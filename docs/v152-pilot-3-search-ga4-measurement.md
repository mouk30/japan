# V152 — 시범 3편 검색·예약 의도 실측 준비 (2026-10-24)

## 적용 범위 — 신규 글 0편
| 시범 | 기존 URL | 식별자 |
|---|---|---|
| 나오시마 미술섬 | `/things-to-do/naoshima-art-ferry-return/` | `naoshima` |
| 데시마 예술섬 | `/things-to-do/teshima-art-ferry-return/` | `teshima` |
| 시코쿠 기항지별 미식 | `/things-to-do/takamatsu-cruise-udon-market-return/` | `shikoku_food` |

## 구분해서 측정할 4단계
1. **검색 노출·클릭:** Google Search Console에서 검색결과 > 검색유형 웹 > 정확한 페이지 URL별 7일·28일 노출, 클릭, CTR, 평균 게재순위와 주요 쿼리. 전체 도메인 평균과 혼합 금지.
2. **네이버 노출·클릭:** 네이버 서치어드바이저에서 같은 URL의 콘텐츠 노출·클릭 성과. 네이버의 업데이트 기준일은 대략 일주일 전의 검색자료이며 조회기간과 날짜 축이 Google과 다를 수 있음. 숫자를 단순 합산하거나 일별 지표를 동일 날짜로 비교하지 않음.
3. **GA4 시범 콘텐츠 진입:** `nf_pilot_guide_view` — 해당 페이지에서 방문자 **명시 동의 후** 보낸 이벤트. 전체 방문자·전체 검색 유입·예약 고객 수가 아님.
4. **GA4 의도 링크 클릭:** `nf_pilot_action_click` — 실제 클릭한 CTA에서만 보냄. 이벤트의 `pilot_id`, `pilot_action`로 식별. 미술관 예약페이지로 이동한 이벤트는 **예약 완료가 아니며** 선박 시간표 조회는 승선권 구매가 아님.

## GA4 이벤트 명세
| 이벤트 | 파라미터 `pilot_action` | 의미 |
|---|---|---|
| `nf_pilot_guide_view` | `page_view` | 동의한 사용자의 시범 가이드 표시 |
| `nf_pilot_action_click` | `museum_ticket` | 미술관 공식 날짜·시간 예약 페이지 이동 |
| `nf_pilot_action_click` | `museum_info` | 미술관 운영·예약 조건 읽기 |
| `nf_pilot_action_click` | `ferry_schedule` | 선사 운항·시간표 페이지 이동 |
| `nf_pilot_action_click` | `island_transport` | 현지 섬버스·교통 확인 |
| `nf_pilot_action_click` | `return_plan` | 귀선 확인표 선택 |
| `nf_pilot_action_click` | `port_return` | 기항지 하선·귀선 상세 이동 |
| `nf_pilot_action_click` | `booking_guide` | NIPPONFERRY 자체 예약 준비 가이드 이동 |
| `nf_pilot_action_click` | `official_food` | 가가와·도쿠시마·고치 공식 미식정보 |

이벤트 파라미터는 `pilot_id`, `pilot_action`, `page_area`, `destination_step`와 표준 `transport_type`만 사용. URL, 검색어, 쿠키값, 이름, 연락처, 결제정보·가격은 자체 이벤트 파라미터에 넣지 않음.

## 아직 필요한 연결 — 결측치를 0으로 쓰지 않음
- 실제 Vercel 빌드 환경변수 `GA4_MEASUREMENT_ID=G-...` 설정 여부 확인. 이 값이 없으면 GA4 스크립트를 **삽입하지 않으며** 이벤트는 아예 보내지 않음. 값은 **GA4 웹 데이터 스트림의 실제 측정 ID**로 설정하고 가짜 ID를 운영 환경에 넣지 않음.
- GA4 관리 > 데이터 표시 > 맞춤 정의 > 이벤트 범위의 맞춤 측정기준 `pilot_id`, `pilot_action`를 실제 속성 관리 권한으로 등록. 등록 후 보고서에 보이기까지 시간이 걸릴 수 있음. [공식 GA4 문서](https://support.google.com/analytics/answer/14239696?hl=en).
- 사용자 동의 후 GA4 Realtime / DebugView에서 `nf_pilot_guide_view`, `nf_pilot_action_click` 실제 수신 확인. 클릭만 테스트할 경우 예약·결제 확정 이벤트로 취급 금지.
- Google Search Console과 네이버 서치어드바이저 계정에서 각 정확한 URL의 성과를 확인. 본 저장소에 개인정보·OAuth 자격증명·API 토큰을 직접 저장하지 말 것.
- 연결 완료 시점 이전 GA4 이벤트를 새로 만들 수 없으며, 동의하지 않은 방문자의 이벤트도 수집하지 않음.

## 28일 성과 평가
**게시일 기준:** 나오시마·데시마 2026-10-23, 시코쿠 미식 2026-10-24. **잠정 28일 검토 기준:** 2026-11-21 전후. 검색엔진 데이터 지연과 측정 연결일을 고려해 각 수집기간을 개별 명시.

| 대상 | Google 노출 | Google 클릭 | CTR | 네이버 노출 | 네이버 클릭 | 동의 기반 GA4 가이드 이벤트 | 예약 링크 의도 클릭 | 실제 예약 완료 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 나오시마 | 미확인 | 미확인 | 미확인 | 미확인 | 미확인 | 측정 연결 필요 | 측정 연결 필요 | 확인 불가 |
| 데시마 | 미확인 | 미확인 | 미확인 | 미확인 | 미확인 | 측정 연결 필요 | 측정 연결 필요 | 확인 불가 |
| 시코쿠 미식 | 미확인 | 미확인 | 미확인 | 미확인 | 미확인 | 측정 연결 필요 | 측정 연결 필요 | 확인 불가 |

### 결론의 기준
- 데이터가 충분한 시범 중 검색 노출과 실제 진입, 방문 후 예약·운항·귀선 정보 확인 비율이 유의미한 주제만 **기존 콘텐츠 보강 대상**으로 확대.
- **예약의도 클릭률** = `nf_pilot_action_click` 중 `museum_ticket` 또는 `booking_guide`를 동의 기반 `nf_pilot_guide_view`로 나눈 참고 비율. 이벤트 수는 고유 방문자 수가 아니며, 링크/페이지가 다른 위치에서 반복 노출되고 한 사람이 여러 번 누를 수 있음. 실제 판매 전환율 아님.
- 검색 노출 데이터가 적거나 GA4 미연결이면 보류. 0건으로 단정하거나 페이지 증산 승인 불가.
- 선사·시설 운영변경, 사진/라이선스, 모바일 링크가 정확히 유지되는 것이 예약과 SEO에 우선.

Google 공식 [Search Console 실적 보고서](https://support.google.com/webmasters/answer/7576553/performance-report-search) · [GA4 맞춤 측정기준 등록](https://support.google.com/analytics/answer/14239696) · 네이버 [콘텐츠 노출·클릭 집계 범위 및 지연](https://searchadvisor.naver.com/guide/report-expose-ctr).
