# V132 — NIPPONFERRY 전체 페이지 1차 정적 품질 전수 조사

**1277개 HTML 페이지 소스 조사 · 신규 게시글 0개 · 운항·예약 실시간 확약 없음**

| 분류 | 건수 | 자동 판정 범위 |
|---|---:|---|
| missing_image_local_references | 0 | HTML img src와 로컬 파일 존재 |
| unresolved_internal_links | 0 | HTML a href와 내부 경로 존재 |
| seo_fields_or_nonself_canonical | 8 | meta description/canonical/H1 기초 구조 |
| cover_social_or_article_image_conflicts | 101 | 상세사진과 OG·Article 이미지 문자열 비교 |
| likely_stale_ai_label | 0 | 실사 교체 후 AI 문구 잔존 추정 |
| hero_photo_source_visibility_review | 289 | 대표사진 뒤 표기 여부만 판별(진위 검증 아님) |
| cruise_port_pages | 194 |  |
| cruise_return_language_missing | 0 | 기항지 페이지 귀선·재승선 문구 단어 검색 |
| booking_cta_destination_review | 44 | 예약 CTA가 일반 홈·콘텐츠로 이동 |
| old_operational_date_context_review | 28 | 과거 날짜 인접 운영정보 수동검토 후보 |
| missing_alt | 0 | HTML 이미지 대체텍스트 누락 |

## 반드시 구별할 한계
- 스크립트가 식별한 후보는 **오류가 확정되었다는 뜻이 아닙니다**. 본문 표·FAQ·상품이 유효한지는 공식 원자료 별도 대조 필요.
- 로컬 이미지의 존재는 실제 일본 지역을 올바르게 촬영했는지, 저작권 표시가 합법적인지를 증명하지 않습니다.
- 업체 홈페이지를 향한 예약 버튼이 실제 결제까지 연결되는지의 여부는 페이지 탐색과 날짜/인원 입력 단계로 별도 확인해야 합니다.
- **귀선 시각은 선박명·날짜·접안 선석·재승선 마감이 확인된 항차에 대해서만** 쓸 수 있습니다.

## 원본 상세 목록
[JSON에서 페이지별·링크별 문제 후보 확인](./sitewide-inventory.json)
