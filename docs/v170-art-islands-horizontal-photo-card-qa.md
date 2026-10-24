# V170 — 3개 미술섬·미식 카드 가로형 4:3 사진 표시 수정

확인일: 2026-10-24 (KST)

## 사용자 제보
스크린샷에 등장한 `페리로 떠나는 일본 미술섬·시코쿠 실전 여행`의 세 카드 사진이 폭에 비해 지나치게 길게 늘어져 보임. 나오시마 미술섬·데시마 예술섬·시코쿠 기항지 미식의 사진이 세로로 긴 막대처럼 보여 여행 사진의 인지성이 크게 떨어짐.

## 원인과 실제 조치
- 같은 카드 섹션이 **두 기존 페이지**에 중복 포함되어 있어 둘 모두 수정:
  - `site/things-to-do/index.html`
  - `site/things-to-do/cruise-ports/index.html`
- V146에서 원본을 검증하고 **이미 1200×900 WebP로 만들어 둔 실제 장소 사진 3장**을 확인:
  1. `/images/editorial/v146-naoshima-miyanoura-ferry-terminal-2025.webp` — 나오시마 미야노우라 여객터미널, Bea Phi, 2025년, CC BY-SA 4.0.
  2. `/images/editorial/v146-teshima-art-museum-exterior-2013.webp` — 데시마 미술관 건물 외관, Kentaro Ohno, 2013년, CC BY 2.0.
  3. `/images/culture-verified/japan-kagawa-udon-pilgrimage.webp` — 가가와 다카마쓰 사누키 우동, sekido, CC BY 2.0.
- 실제 WebP가 원래부터 가로 4:3이므로 가짜 새 이미지나 AI 창작/해상도 확대 없이, **늘어나는 프런트엔드 표시 규칙을 수정**하는 것이 정확한 해결이었음.
- 세 이미지 요소를 `.nf-v170-wide-media` 4:3 고정 비율 래퍼로 감싸고, 이미지 표시를 래퍼 높이 내 `object-fit:cover`, `position:absolute`로 고정. 주변 CSS 규칙이 이미지 높이를 늘려도 최종 이미지 슬롯을 4:3으로 유지하도록 `#nf-v153-pilot-hub`에 국한한 높은 우선순위 스타일 적용.
- 카드 전체를 flex column으로 정리해 설명·원본 저작권/라이선스 표기·예약/귀선 CTA 유지. CTA 높이 52px.
- **원본 이미지 파일을 교체한 작업은 아님**. 이미 사용 중인 인증된 사진을 잘리지 않는 가로형 카드 슬롯에 보이도록 사진 표현을 바꿈. 추가 장면이 필요하다면 새 실사·저작권을 별도 검증해야 함.

## QA 및 배포
- 원본 SEO, 제목, URL, canonical, 저작자·저작물 원본·라이선스, 기존 3개 가이드 링크, 모든 img.src·alt, 사이트맵 보존.
- 소스 코드·빌드 검수 PASS: https://github.com/mouk30/japan/actions/runs/40095072846.
- 공개 운영 사이트에서 실제 화면 8/8 PASS: https://github.com/mouk30/japan/actions/runs/40095142011.
  - 각 페이지 × 390/768/945/1440px.
  - 세 이미지 모두 실제 원본 1200×900 WebP 로드·각 카드 사진 4:3 비율 유지·가로 이미지로 렌더링·중복 사진 없음·원본·라이선스·실제 가이드 CTA 유지·50px 이상 버튼·가로 넘침 없음.
  - 스크린샷 8장 및 측정 JSON은 해당 GitHub Actions artifact에 업로드됨.
- 사이트 변경 2개 커밋 `6979de84528338ab72e86c551cc328e61f1b1f27`, `c72de438a836898fedcd8595fe658bf89379081e` Vercel 배포 SUCCESS.
- 신규 글 0편, 신규 사진 0장, 기존 콘텐츠/SEO 경로 보존.

## 다음 보강 범위 주의
V170은 사용자 제보의 **길쭉한 세 카드 사진 표시 문제**를 해결한 단계. 이 3장보다 미술관/미술작품 중심의 더 멋진 *다른* 사진이 필요하다면 원본 장소·원촬영자·권리·촬영일 확인된 새로운 가로 실사를 별도 발굴해야 한다. 현재 확인되지 않은 미술관 사진이나 저작권 불명 사진으로 대체하지 않음.
