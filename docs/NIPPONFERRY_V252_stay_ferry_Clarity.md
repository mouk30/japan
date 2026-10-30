# NIPPONFERRY V252 — 숙박 28개 기존 페이지 페리 예약 안내·모바일 CTA 정비

**검수일:** 2026-10-30 · **범위:** `site/stay/index.html` 및 `site/stay/*/index.html` 기존 28개 페이지.

## 실제 문제
기존 숙박 가이드 끝의 페리 외부 링크는 `https://willer-travel.com/ko/ferry/`였지만 버튼 문구 `예약 가능한 항로 확인`에는 **숙소와 별개인 일본 국내 페리 예약**이라는 설명이 없었습니다. WILLER가 운영하는 해당 페이지는 일본 국내 페리의 목적지·항로 검색을 안내합니다. 숙박 가격·객실 예약을 보장하는 링크가 아닙니다.

## 변경

- 기존 외부 URL 보존, **버튼 표기를** `일본 국내 페리 항로·요금 조회 ↗`로 변경.
- CTA 아래에 숙소·객실 예약과 **별개의 페리 상품**이며 출발일·요금·운항·승선 조건은 판매처에서 최종 확인해야 한다는 문구 추가.
- 외부 이동임을 드러내는 aria-label과 `noopener noreferrer` 강화.
- 터치 영역 최소 44px, 모바일 640px 이하 버튼을 세로 정렬. 기존 4:3 카드·다른 사진·기존 예약 경로 유지.
- 28개 페이지의 기존 title/description/canonical/robots/sitemap 및 로컬 링크·이미지 참조를 자동 회귀검사로 확인.
- **신규 글 0건**, 실제 예약·가격·객실 재고 확인 주장 0건. KidsStay 실운영/원본/시범 사이트 연결 금지 유지.

## 검증 명령

`node scripts/check-v252-stay-ferry-clarity.mjs` (28개 페이지 누락·SEO 변형·링크 오류 방지)

GitHub Actions: `.github/workflows/v252-stay-ferry-clarity.yml`

**한계:** 저장소 정적 회귀 QA는 외부 예약처에 해당 날짜의 페리 좌석이 실제 있는지 또는 공개 사이트 화면이 배포됐는지를 검증하지 않습니다. 공개 URL/모바일 실제 화면 검증은 별도 단계로 남깁니다.
