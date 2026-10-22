# V109 — 사진 출처·촬영 장소 검증 및 오사카 상세 이미지 개선

**작업일 2026-10-22 · NIPPONFERRY · 메인 홈 18개 카드는 8+4+6 구조 유지**

## 결과
- 메인에서 실사 또는 외부 원본 사진을 참조한 카드 **8/8개의 원본 출처·촬영자·이용 조건 기록을 대조**했다. 18개 중 나머지 10개는 연출 이미지로 그대로 분류하며 실사라고 주장하지 않는다.
- V107에서 출처가 확인되지 않았던 오사카 가이유칸 사진은 [Commons Kaiyūkan.jpg](https://commons.wikimedia.org/wiki/File:Kaiy%C5%ABkan.jpg)와 **시각적으로 일치하는 동일 장면**이다. Sakai Yayoi가 2026년 5월 7일 촬영한 사진이며 Commons 원본은 **CC0 1.0**. 기존 저장소 WebP는 유지하면서 source.json, 해시 SHA-256, 크레딧을 추가했다.
- 파일 동일 장면임은 사람이 구도를 비교해 확인한 내용이며, Commons JPEG가 WebP로 변환된 **정확한 작업 이력/원본 바이너리 대응 관계까지 증명했다는 뜻은 아니다**.
- 오사카 하루 코스 [상세페이지](https://www.nipponferry.com/things-to-do/osaka-one-day/)에서 출처 미기록 도톤보리 사진 3개 참조(OG 대표·상단 히어로·첫 관광 사진)를 [Commons 도톤보리 실사](https://commons.wikimedia.org/wiki/File:D%C5%8Dtonbori_at_night%2C_Osaka_%2819551420339%29.jpg)를 출처로 하는 **기존 V85 라이선스 검증 사진**으로 교체했다. Kristoffer Trolle · CC BY 2.0 · 2015년 촬영. 상세페이지에 크레딧과 라이선스 링크를 추가했다.

## 변경 파일 및 회귀 검증
- `site/index.html` — 오사카 가이유칸 CC0 출처 크레딧 보강. 기존 카드 이미지 및 버튼·레이아웃은 그대로 유지.
- `site/things-to-do/osaka-one-day/index.html` — 도톤보리 실사 이미지 출처 확보. 기존 title/description/canonical/Article·FAQ·Breadcrumb JSON-LD/본문 동선·내부 링크 보존.
- `site/images/venues/osaka-kaiyukan-aquarium.source.json` — 원본 출처, 사진 작가, 라이선스, 웹P 해시 및 증빙 범위 명시.
- `scripts/v105_home_photo_manifest.json` — 오사카 가이유칸 실사 출처 추가. 18개 카드의 src, SHA-1 고정값과 각 링크 유지.
- `scripts/v105_home_photo_quality.py` — 18개 중 실사 8개 전부 출처 기록이 있는지 검사하고 중복 크레딧/고아 크레딧을 차단.
- `tests/test_v105_home_photo_quality.py` — 사진 출처 누락 시 실패, 검증된 오사카 상세 사진 사용 및 SEO 보호 테스트 추가.
- `audit-reports/v109/photo-provenance-inventory.json` — 실사 8개/연출 10개, 원본과 라이선스, 한계 기록.

## 검증 한계와 다음 단계
- **8/8**은 홈에 사용한 8개 외부 출처 실사/참조 사진의 원본 링크와 라이선스가 기록된 상태이며 사이트의 모든 사진을 뜻하지 않는다.
- 10개 연출 이미지는 실제 지점 촬영 사진이 아니며 생성 경로/권리 귀속이 별도 검수 대상이다.
- 향후 검색 유입이 높은 상세페이지 10편씩 실물 사진의 출처 미기록 여부를 확인한다. 원본·라이선스 확인이 되지 않으면 사진을 교체하고, SEO와 URL은 보호한다.

## GitHub 커밋 및 CI 결과
- [V109 사진 출처 보강·상세 이미지 교체 커밋](https://github.com/mouk30/japan/commit/6228130821b33ca4a54f86cb7113d0b7b51cc14e)
- [V105 18개 이미지·출처·SHA-256 무결성 + 공개 홈페이지 PC/모바일 검증: 성공](https://github.com/mouk30/japan/actions/runs/39725984360)
- [V104 18개 썸네일 1440/390/360px 검증: 성공](https://github.com/mouk30/japan/actions/runs/39725984508)
- [V66 메인 SEO·반응형·링크 검증: 성공](https://github.com/mouk30/japan/actions/runs/39725984469)
- [V78 크루즈 메인 비주얼 PC·모바일: 성공](https://github.com/mouk30/japan/actions/runs/39725984448)
- [V85 파노라마 배너 PC·모바일: 성공](https://github.com/mouk30/japan/actions/runs/39725984455)
- [홈·에디토리얼 85편 링크/배포 점검: 성공](https://github.com/mouk30/japan/actions/runs/39725984382)

**검증 범위:** 자동화는 사진의 라이선스 기록·파일 무결성 및 표시·링크 회귀를 검사한다. 권리자의 법적 소유 증명이나 사이트 전체 모든 사진의 허락을 보증하지 않는다.
