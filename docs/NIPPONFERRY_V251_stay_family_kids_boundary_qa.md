# NIPPONFERRY V251 — 숙박·가족 숙소·키즈관 정합성 QA

**검수일:** 2026-10-30 · **범위:** `mouk30/japan` 저장소의 기존 공개 콘텐츠 3개 페이지만 대상으로 하는 정적 회귀검사.

## 실제 검수 결과

| 기존 페이지 | 제목·canonical·robots | 로컬 링크·이미지 원본 존재 | KidsStay 시범 예약 연결 |
|---|---|---|---|
| `/stay/` | 정상 | 누락 0 | 없음 |
| `/stay/family/` | 정상 | 누락 0 | 없음 |
| `/kids/` | 정상 | 누락 0 | 없음 |

- 세 페이지의 **기존 내부 상대 링크·이미지·스타일 파일을 저장소 트리와 대조**했고 누락을 발견하지 않았습니다. 쿼리 문자열을 제외한 파일 위치를 검사합니다.
- 검색용 제목, 설명, canonical, 색인 허용과 sitemap 등재 여부를 확인했습니다.
- KidsStay 시범 `kidsstay-v5.vercel.app` / 원본 `kids-stay.com`으로의 미검증 직접 연결은 없습니다.
- **한계:** 저장소 정적 파일 검수이므로 공개 URL의 HTTP 응답, 실시간 예약, 저작권 또는 사진의 실제 장소 일치까지 검증했다는 뜻은 아닙니다.
- **운영 원칙:** NIPPONFERRY를 KidsStay 외부 프로젝트와 혼합하거나 예약 기능을 선공개하지 않습니다. 신규 글 0건.
- 이번 작업으로 원본 HTML·이미지·예약 URL을 **수정하지 않습니다.** QA 문서·검증 스크립트·GitHub Actions만 추가합니다.

## 검증 실행

`node scripts/check-v251-stay-kids-boundary.mjs`

자동화: `.github/workflows/v251-stay-kids-boundary.yml`

사이트가 빌드되거나 공통 헤더·메뉴가 바뀐 후에도 이 검증을 반복할 수 있습니다.
