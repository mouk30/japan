# V108 — 추천 테마 여행 6개 이미지 품질·출처 및 지역 사진 보강

**2026-10-22** · https://www.nipponferry.com/ · 기존 카드 개수 (인기 여행지 8 / 지역별 즐길거리 4 / 추천 테마 6), SEO canonical/JSON-LD, 각 카드 링크·제목, CSS, 카드 크기 유지.

## 테마 6개 카드: 점검 및 적용

| 테마 | 최종 이미지 | 조치 | 정확성 조건 |
| --- | --- | --- | --- |
| 식도락 여행 | `/images/culture-verified/ramen-japanese-noodle-evolution.webp` | 기존 출처 미확인 라멘 이미지 → 실제 돈코츠 라멘 사진 (Syced, CC0) | 도쿄 촬영, 후쿠오카 특정 식당을 주장하지 않음 |
| 쇼핑 가이드 | `/images/culture-verified/shotengai-japanese-shopping-arcades.webp` | 오키나와 거리 연출 → 돈키호테 간판이 보이는 삿포로 쇼핑거리 실사 (Mugu-shisai, CC BY-SA 3.0) | 2008년 사진, 현재 점포 영업/재고 근거 아님 |
| 4계절·축제 | `/images/editorial/okinawa-eisa-dance-festival.webp` | 유지: 여름축제 안내와 사진 주제 일치 | 실제 에이사 행사 기록이 아닌 연출 표시 유지 |
| 커플 여행 | `/images/couple.jpg` | 교토 건축 중심 → 기존 사이트의 기모노 커플·전통거리 연출 이미지 | 교토 실제 촬영이라고 주장하지 않음; 연출 표시 유지. 원본 제작 증빙 추가 확인 필요 |
| 포토 스팟 | `/images/editorial/ishigaki-kabira-bay.webp` | 유지: 가비라만 풍경이 포토 스팟 목적에 적합 | 연출 이미지를 실사로 둔갑시키지 않음 |
| 현지 생활정보 | `/images/culture-verified/konbini-japanese-convenience-store-life.webp` | 자판기 이미지 → 일본 편의점 내부 실사 (Yuya Tamai, CC BY 2.0) | 2009년 자료 사진; 현행 상품·가격 안내 아님 |

## 지역별 사진 출처 V107 후속보강

- 시모노세키 가라토시장: [Wikimedia 원본](https://commons.wikimedia.org/wiki/File:Karato_Fish_Market,_Shimonoseki_-_Jun_24,_2023.jpg), bryan..., CC BY-SA 2.0, 2023년 촬영; 이전 `docs/v62-regional-real-photo-sources.json` 기록과 교차 확인.
- 대마도 이즈하라항: [Wikimedia 원본](https://commons.wikimedia.org/wiki/File:Izuhara_port,_terminal.jpg), Saigen Jiro, CC0, 2017년 촬영; 이전 V62 파일 출처와 교차 확인.
- **오사카 가이유칸 건물**: 기존 V107 사진 원본의 촬영자·이용 라이선스를 현재 자료만으로 확정하지 못함. 권리가 확인되기 전까지 출처 인증 완료로 표시하지 않음. 실제 시설 외관과 별개로 **추가 권리 검수 필요**.
- 홈페이지의 사진 사용 안내에 위 2개 지역 사진과 V108 신규 3개 실사 사진의 저자·원본·라이선스 링크를 명시함.

## 코드·검수

- `site/index.html`: 대표 이미지 4개 교체, alt 텍스트 수정, 실사/연출 표시 정합성 확보 및 사진 크레딧 추가.
- `scripts/v105_home_photo_manifest.json`: 18개 대표 썸네일별 src/alt/원본 Git blob SHA-1/종류 검수 고정, 실사 출처 5건 추가.
- `scripts/v104_home_thumbnail_browser_qa.py`: 1440/390/360px 이미지·연출 표시·alt·사진 출처·가로 스크롤 검사를 V108 상태로 변경.
- `tests/test_v105_home_photo_quality.py`: V108 6개 이미지 위치·주제·출처, 연출 표시 유지 검사 추가.
- `audit-reports/v108/thumbnail-source-inventory.json`: 6개 테마·3개 지역 사진의 검증 수준, 출처와 미확인 사항 기록.

**제한:** 이미지 주제·공개 Commons 원본·라이선스 표기를 확인했더라도 현재 여행 운영정보 또는 외부 저작권 분쟁의 부재를 보증하지 않습니다. WebP 재생성은 하지 않았고, 기존 저장소의 WebP 및 사이트 JPG 한 장을 재사용했습니다. 커플·에이사·가비라만 이미지는 생성/연출된 관광 분위기 이미지로 문구를 유지했습니다. 기존 18개 카드와 URL은 유지합니다.

## GitHub 적용 및 자동 검사 결과

- [V108 콘텐츠·출처 커밋](https://github.com/mouk30/japan/commit/d8530916e1cd5beffdb848b186547c158c701301)
- [V108 실제 사진의 alt 검증 조건 수정](https://github.com/mouk30/japan/commit/f48fc72a1e9d0c995a35a66d64f065fbc6caf53c): 실제 사진에 대한 설명과 연출 이미지를 구분.
- [V104 PC 1440px / 모바일 390px / 소형 360px 공개 사이트 썸네일 QA 성공](https://github.com/mouk30/japan/actions/runs/39721518395)
- [V105 썸네일 18개 소스 검증·라이선스 출처·공개 홈페이지 브라우저 QA 성공](https://github.com/mouk30/japan/actions/runs/39721518357)
- [V66 기존 메인페이지 SEO 및 반응형 링크 검사 성공](https://github.com/mouk30/japan/actions/runs/39721275361)
- [공개 홈페이지 및 85개 에디토리얼 페이지 검사 성공](https://github.com/mouk30/japan/actions/runs/39721275551)
- 추가 관찰: V108 첫 시도 당시 V78 비주얼 워크플로는 PC에서 예전 배경 이미지/스타일을 읽어 실패했다. V108 대표 이미지 변경과는 별도 영역이며 재검사를 요청하였다. 성공 검증 전에는 V78까지 통과했다고 보고하지 않는다.
