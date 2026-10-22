# V106 — 홋카이도 인기 여행지 썸네일을 낭만적인 설경·온천 이미지로 교체

**2026-10-22 · https://www.nipponferry.com/ · 기존 인기 여행지 8개 카드 수·크기·본문·연결 URL/SEO 구조 유지**

## 사용자 요청 및 적용

- 대상 카드: **HAKODATE · HOKKAIDO / 홋카이도**, 기존 가이드 링크 `/japan/hokkaido/`.
- 원본 사진: `/images/editorial/hakodate-goryokaku-fort.webp`(고료카쿠 성곽 연출), 겨울 낭만과 온천을 충분히 보여주지 못함.
- 변경: `/images/editorial/hakodate-snow-onsen-romantic-v106.webp`(900×600px, 76,512 bytes, 단독 WebP 1장).
- 장면: **노천온천의 따뜻한 수증기와 등불, 눈 덮인 나무·일본식 료칸 건물, 항구도시의 겨울 노을**을 함께 보여주는 풍경.
- alt: `하코다테 항구 야경을 배경으로 눈 덮인 노천온천에 수증기가 피어오르는 낭만적인 홋카이도 겨울 설경을 표현한 연출 이미지`.
- **실제 특정 온천 시설·숙소 촬영이나 그 숙소에서 보이는 전망이 아니다.** OpenAI 이미지 생성 도구로 제작한 **여행 분위기 연출 이미지**이며 카드의 기존 연출 표시를 유지한다.
- 홋카이도 실제 온천 정보는 공식 일본 관광안내의 **하코다테 유노카와 온천**과 구분한다. 실제 여행 시 [하코다테 공식 관광](https://www.hakodate.travel/en/more-about-hakodate/yunokawa/) 및 [홋카이도 공식 관광](https://www.visit-hokkaido.jp/en/spa/spot/detail_10615.html)에서 운영 정보를 확인한다.

## 파일 및 보호장치

- 신규 WebP: `site/images/editorial/hakodate-snow-onsen-romantic-v106.webp`.
- 생성/출처·변환·비실사 정보: `site/images/editorial/hakodate-snow-onsen-romantic-v106.source.json`.
- 기존 홈페이지 `site/index.html`에서 **홋카이도 카드 1개만 변경**, 나머지 17개 썸네일과 기존 링크 유지.
- `scripts/v105_home_photo_manifest.json` V106 신규 파일 SHA-1(Git blob) 고정.
- `scripts/v105_home_photo_quality.py` 18개 기존 이미지 품질 검사에 **생성 이미지 출처·SHA-256·'실제 숙소' 오인 방지** 추가.
- `scripts/v104_home_thumbnail_browser_qa.py` 새 이미지 주소로 수정하여 **PC 1440px / 모바일 390px / 소형 360px**에서 전체 이미지 표시를 다시 검수.

## 검증

- 이미지 형식: **WebP**, 원본 PNG 1536×1024에서 **900×600으로 축소**, 고품질 압축·76,512바이트.
- 생성 이미지 SHA-256: `7d5ae2a9567714deaebc9b78b7c8e70e490f70956095984da68220b55030a691`.
- 브라우저 검수: https://github.com/mouk30/japan/actions/runs/39700034177 (V104 업데이트 전체 18장 통과).
- 이미지 출처·변조 방지: [V105 실사이트·이미지 무결성 통합검수 최종 성공](https://github.com/mouk30/japan/actions/runs/39700167791). **14개 단위검사 통과, 소스 이미지 18/18 정상, 오류 0건; PC·모바일 배포본 검사 통과.**

**주의:** 이미지의 항구와 온천 배치는 예술적으로 합성된 이미지 구성이다. 특정 관광시설 사진 또는 실제 촬영 당시의 설경을 증명하지 않는다. 이미지 하나로 운영시간/요금/예약 가능을 단정하지 않는다.
