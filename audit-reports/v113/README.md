# V113 — 10개 기존 크루즈 기항지 AI 대표 이미지의 실제 장소 WebP 교체

**2026-10-22 · NIPPONFERRY · 기존 상세페이지 10편 · 신규 게시글 0편**

## 결과

- **AI 연출 이미지 10장 → Wikimedia Commons 실제 관광지 원본 사진 10장**, 각각 다른 지역의 개별 WebP로 변환해 GitHub `site/images/venues/nf-v113-*-real.webp`에 저장했다.
- **대표 본문 사진 10개 + OG 대표 이미지 10개**를 함께 교체. 기존 URL, SEO 제목, 검색 설명, H1, canonical, JSON-LD 원문과 이동·귀선 관광정보는 보존했다.
- 원본 사진의 **실제 촬영 장소, 촬영 날짜, 저작자, 출처 URL, 라이선스, WebP 리사이즈·형식 변환**을 공개 본문 이미지 바로 아래에 표시했다.
- 촬영 당시 사진을 현재 항차의 접안 부두·승객 게이트·셔틀·시설 영업 상태라고 주장하지 않는다. 특히 마쓰시마는 센다이항에서 이동하는 **관광지**이며 항구 자체가 아니다.
- **시라오이 시각 검수 추가 수정:** 최초 가져온 우포포이 실내 화로 장면이 관광지 대표 이미지로 적합하지 않아, [전통 아이누 가옥(치세) 외관 실사](https://commons.wikimedia.org/wiki/File:Shiraoi-upopoy_14.jpg) (Higa4, CC0 1.0, 2020년)로 교체했다. 수정 기록: [visual-corrections.json](./visual-corrections.json).
- 10편의 한국어 `alt`와 사진 크레딧 문구를 다시 다듬었고, 실사 로딩 실패 시 일반 페리 이미지로 슬쩍 변경하는 `onerror` 속성은 새 카드에 넣지 않았다.

## 수정 페이지·촬영 시점·저작자

| 기항지 | 새 실제 장소 사진 | 촬영 | 사진 원본 및 이용 조건 |
|---|---|---|---|
| 시라오이 | 우포포이 아이누 전통가옥 외관 | 2020-11-15 | [Higa4 · CC0 1.0](https://commons.wikimedia.org/wiki/File:Shiraoi-upopoy%2014.jpg) |
| 센다이 | 미야기현 마쓰시마만의 섬들, 센다이항에서 이동하는 관광 명소 | 2008-04-15 | [KimonBerlin · CC BY-SA 2.0](https://commons.wikimedia.org/wiki/File:The%20islands%20of%20Matsushima%20from%20Saigyo%20Modoshi%20No%20Matsu%20park%20(2456102064).jpg) |
| 니가타 | 니가타 시내 반다이교와 강변 | 2025-06-12 | [Mateuser · CC0 1.0](https://commons.wikimedia.org/wiki/File:Bandai%20Bridge%2020250612%20184846.jpg) |
| 구시로 | 구시로 습원 호소오카 전망대에서 본 자연 경관 | 2008-09-05 | [欅 (Keyaki) · CC BY-SA 3.0](https://commons.wikimedia.org/wiki/File:Kushiroshitsugen.jpg) |
| 무로란 | 무로란 지구곶의 하얀 등대 | 2009-09-11 | [Soica2001 · Public domain](https://commons.wikimedia.org/wiki/File:Muroran%20Cape%20Chikyuu%20lighthouse.jpg) |
| 도마코마이 | 도마코마이 우토나이호 습지·호수 | 2013-06-15 | [Prosperosity · CC BY-SA 3.0](https://commons.wikimedia.org/wiki/File:Utonai-ko.jpg) |
| 후시키·도야마 | 다카오카 대불의 2004년 모습 | 2004-09-20 | [Carlj7 · CC BY-SA 3.0](https://commons.wikimedia.org/wiki/File:TakaokaDaibutsu.jpg) |
| 돗토리 | 돗토리 사구 황금빛 모래 언덕 | 2021-06-21 | [Drivephotographer · CC0 1.0](https://commons.wikimedia.org/wiki/File:Tottori%20Sand%20Dunes.jpg) |
| 사카타 | 사카타 산쿄소코 창고와 느티나무길 | 2013-08-15 | [掬茶 · CC BY-SA 3.0](https://commons.wikimedia.org/wiki/File:Sankyo%20Warehouse%20in%20Sakata%2C%20Yamagata%2C%2015%20August%202013%2C%2001.jpg) |
| 아타미 | 아타미 선비치의 해안 풍경 | 2024-03-14 | [m-louis .® · CC BY-SA 2.0](https://commons.wikimedia.org/wiki/File:View%20of%20Atami%20Sun%20Beach%20from%20northeast%20-%20Mar%2014%2C%202024.jpg) |

> **유의:** 2004년 다카오카 대불, 2008년 구시로 습원·마쓰시마, 2009년 무로란 등은 **역사적 실제 장소 사진**이지 2026년 현재 시설 상태를 보증하는 사진이 아니다. CC BY-SA 등 공유동일조건 라이선스는 2차 이용 시에도 원본 라이선스 조건을 지켜야 한다.

## GitHub 원본·SEO·배포 관련 증빙

- [V113 이미지 원본 10건·촬영자·CC 라이선스 연결 기록](./photo-import-plan.json) — 최초 선택 목록이며 시라오이 1건은 시각검수 단계에서 수정했다.
- [변환 성공 결과 및 실제 적용된 10개 WebP SHA-256·픽셀 크기](./import-result.json) — 최종 시라오이 수정 원본까지 반영.
- [시라오이 1건 외관 교체와 10개 한국어 문구 수정 내역](./visual-corrections.json).
- [편집 이전 10편 SEO 원문 및 JSON-LD 기록](./seo-baselines.json) — 사진 교체 후 글자 단위 비교.
- `scripts/v113_replace_ai_heroes.py` — Wikimedia 출처 사진 다운로드, Pillow WebP 변환, 10장 전부 준비된 경우에만 파일/문서 작성.
- `scripts/v113_visual_photo_polish.py` — 시라오이 대표 사진 정확성 수정, 10편 한국어 `alt`·출처 안내 보강.
- `scripts/v113_photo_quality_audit.py` — 실제 WebP SHA-256·크기·원본 라이선스·OG·SEO 변경 여부 자동 검사.
- `scripts/v113_photo_live_qa.py` — PC 1440px/모바일 390px 실제 공개 페이지 20회 이미지 표시·저작권·OG·canonical·가로 스크롤 점검.
- [V113 사진 가져오기 Actions 성공](https://github.com/mouk30/japan/actions/runs/39737901676).
- [시라오이 외관 이미지 및 사진 설명 보정 Actions 성공](https://github.com/mouk30/japan/actions/runs/39738438296).
- [V113 최종 이미지·SEO·모바일 검수](https://github.com/mouk30/japan/actions/runs/39738896338).

## 검수 범위와 한계

- 이 10편의 대표 이미지와 OG만 바꿨다. 다른 본문 사진·본문 사실·예약 가능 여부와 전체 145편 이미지를 전수 검사한 것은 아니다.
- 인용한 라이선스 정보는 Wikimedia Commons의 해당 파일 페이지에 근거하며, 인물 초상권 또는 상업시설의 상표권까지 보증하지 않는다.
- 사이트 WebP는 원본 사진의 리사이즈 변환이다. 원본 이미지의 촬영 연도와 현재 관광시설 영업시간 및 선석은 별개로 안내한다.
- 실제 GitHub 검색 실적/GA4 측정 없이 기존 AI 기항지 글 가운데 10편을 선택했다.

## 최종 공개 사이트 검사 결과

**GitHub Actions의 최종 PC/모바일 실행 결과를 기준으로 기록한다.**
