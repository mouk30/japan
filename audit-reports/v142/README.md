# V142 — 공통 내비게이션 사용성·접근성 최종 완료

- 날짜: 2026-10-23
- 도메인: https://www.nipponferry.com/
- 적용 방식: 사이트 빌드시 공통 V301 헤더를 출력하는 방식. 기존 원문·SEO를 변경하지 않고 헤더 CSS/JS만 변경
- 대상: 공통 헤더 1,270개 HTML 빌드 결과 (전체 빌드 1,276개 페이지 중 6개는 별도 이동/예외 페이지)
- 신규 게시글·키즈관 확장: **0**
- 예약 메뉴 링크, 본문, 이미지, canonical, 기존 메타 제목/설명, 구조화 데이터 보존

## V142 개선 내용
1. 모바일 메뉴 열기 시 현재 카테고리(여행지·즐길거리·동행 가이드·여행 정보)에 해당하는 세부 링크를 자동 전개. 다른 카테고리는 임의로 펴지지 않음.
2. 하위 메뉴 버튼의 aria-expanded, aria-label, data-open을 동기화하고 하나만 열린 상태로 유지.
3. 메뉴가 열린 동안 Tab/Shift+Tab 키보드 포커스가 화면 뒤로 빠지지 않고 브랜드/예약/메뉴 항목 사이에서 순환. ESC로 닫기 및 열기 버튼 포커스 복귀. 페이지별 레거시 이벤트 충돌을 막기 위해 키보드 이벤트를 캡처 단계에서 처리.
4. 모바일 활성 카테고리의 남색 강조 및 열린 카테고리 시인성 개선, 높은 대비 설정 고려.
5. PC 드롭다운은 클릭으로 연 메뉴가 이웃 카테고리의 hover/mouseenter로 덮어써지는 실제 버그를 수정. 마우스 오버 탐색 자체는 유지. 데이터 open/aria-expanded/CSS display를 일치시킴.
6. 메뉴 위로 겹쳐 보이는 카카오 플로팅은 V141의 숨김 규칙 유지.

## 검수 결과 — 모두 성공
| 검수 | 범위 | 결과 |
|---|---|---|
| V142 로컬 빌드 Chromium | 6개 경로 × 320/390/768/1199/1200/1440px, 36화면 | PASS 36/36, errors 0 |
| V142 실제 운영 URL Chromium | 같은 36개 경로×폭 조합 | PASS 36/36, errors 0 |
| V301–V305 회귀검사 | 120개 화면 조합, 메뉴 링크, 기존 SEO/canonical | PASS |
| V141 큰 글씨/드롭다운 검수 | 20개 화면 조합 | PASS |
| Vercel 배포 | GitHub main 배포 상태 | SUCCESS |

## 증빙
- V142 공개 QA: https://github.com/mouk30/japan/actions/runs/39935455315
- V142 로컬 QA: https://github.com/mouk30/japan/actions/runs/39935400511
- 기존 공통 헤더 QA: https://github.com/mouk30/japan/actions/runs/39935400466
- V141 리뉴얼 회귀 QA: https://github.com/mouk30/japan/actions/runs/39935400378
- V142 실제 화면 캡처/JSON: https://github.com/mouk30/japan/actions/runs/39935455315/artifacts/12493746243

## 범위의 한계
Chromium 브라우저의 자동 회귀 검사와 캡처 기준이며, 실제 삼성 인터넷/아이폰 Safari의 모든 기기 조합 또는 터치 접근성 수동 QA까지 완료했다는 뜻은 아님.
