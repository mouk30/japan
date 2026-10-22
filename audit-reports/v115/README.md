# V115 — 기존 AI 대표 이미지 10편 실사진 교체 및 공개 검수 결과

**2026-10-22 · 기존 게시글 10편 개선 · 신규 게시글 0편**

## 결과
- 실제 Wikimedia Commons의 서로 다른 촬영 원본 10장 → 개별 WebP 10장으로 변환 후 `site/images/venues/nf-v115-<slug>-real.webp` 반영
- 크루즈 상세페이지 10편 대표 사진과 OG 이미지 교체 및 출처·촬영 날짜·저작자·사용 허락 라이선스 표시
- 기존 페이지 10편의 title, meta description, canonical, H1, JSON-LD 문자열을 기존 기준선과 정확히 비교해 보존
- 사진 실제 촬영 관광지와 현재 크루즈 접안부두, 승객 게이트, 셔틀, 공연일정 구분. 과거 사진은 촬영일 공개
- 이미지 포맷·픽셀 크기·바이트·SHA256, 라이선스 링크, OG·canonical, AI 대표 이미지 제거 검수
- 공개 사이트 **1440px PC 10건 + 390px 모바일 10건 = 20/20 성공, 오류 0건**. Chromium 이미지 정상 로딩·출처 문구·원래 SEO와 가로 넘침 검사

## 10개 기항지별 원본

| 기항지 | 실제 사진의 장소 | 촬영일 | 저작자·원본·라이선스 |
|---|---|---|---|
| 아오카타 | 가시라가시마 천주당 실제 건물 | 2016-07-05 | [ふうけ · CC BY-SA 4.0](https://commons.wikimedia.org/wiki/File:KashiragashimaChurch160705.jpg) |
| 후쿠야마 | 후쿠야마성 천수의 촬영 당시 외관 | 2025-04-03 | [Editor0206 · CC0 1.0](https://commons.wikimedia.org/wiki/File:Fukuyama%20Castle%202025-04.jpg) |
| 가마고리 | 다케시마섬과 다케시마 다리 | 2017-01-21 | [Alpsdake · CC BY-SA 4.0](https://commons.wikimedia.org/wiki/File:Take%20Island%20and%20Bridge.jpg) |
| 하기 | 하기성 유적의 성벽 | 2010-09-22 | [Kuru man · CC BY 2.0](https://commons.wikimedia.org/wiki/File:Hagi%20Castle%20-Wall.jpg) |
| 한난 | 한난항 인근 관광지 기시와다성 | 2012-05-12 | [663highland · CC BY 2.5](https://commons.wikimedia.org/wiki/File:Kishiwada%20Castle%20Kishiwada%20Osaka%20pref%20Japan04s3.jpg) |
| 히다카 | 히다카가와 도조지 본당 | 2008-12-30 | [663highland · CC BY 2.5](https://commons.wikimedia.org/wiki/File:Dojoji%20Gobo%20Wakayama15s3200.jpg) |
| 하마다 | 시마네 해양관 아쿠아스의 실제 시로이루카 공연 수조 (촬영 당시) | 2020-03-07 | [Totti · CC BY-SA 4.0](https://commons.wikimedia.org/wiki/File:Shimane_Aquarium_AQUAS_beluga_pool.jpg) |
| 히라도·가와치 | 히라도항에서 바라본 히라도성 | 2010-05-15 | [STA3816 · CC BY-SA 3.0](https://commons.wikimedia.org/wiki/File:HiradoCastle.jpg) |
| 호소시마 | 휴가 우마가세 해안 절벽 | 2013-10-06 | [Yobito KAYANUMA · CC BY-SA 3.0](https://commons.wikimedia.org/wiki/File:%E9%A6%AC%E3%83%B6%E8%83%8C%20-%20panoramio%20(1).jpg) |
| 기사라즈 | 기사라즈항 나카노시마 대교 | 2015-08-14 | [Kentagon · CC BY-SA 4.0](https://commons.wikimedia.org/wiki/File:Nakanoshima-Bridge%20Kisarazu%20150814.jpg) |

## 검증 자료

- [원본 사진 선택·출처·저작자·권리조건](./photo-plan.json)
- [수정 전 10개 상세페이지 SEO 기준선](./seo-and-ai-candidate-baselines.json)
- [사진·WebP SHA-256, 크기, 실제 다운로드 URL, 교체 후 상태](./import-result.json)
- [기존 10편 교체 본문과 WebP 실물 GitHub 커밋](https://github.com/mouk30/japan/commit/28eeda9c3d05cf13393031781e6c5cec0a47a436)
- [모든 사진을 함께 변환하고 부분 적용을 막은 GitHub Actions](https://github.com/mouk30/japan/actions/runs/39753885493) — 통과
- [10장 로컬 사진·SEO QA 및 20회 공개 PC/모바일 Chrome QA](https://github.com/mouk30/japan/actions/runs/39753975746) — **20/20 통과, 오류 0건**
- [PC·모바일 스크린샷/검수 JSON 증빙 아티팩트](https://github.com/mouk30/japan/actions/runs/39753975746/artifacts/12413614971) — 20장 화면 캡처 및 report.json, 보존기간은 Actions 설정 참고

## 작업 범위 한계
- 이번 검수는 **대표 이미지 10개와 OG, 실물 사진 출처 및 검색 메타태그 보존**에 집중했다. 본문 중간의 모든 AI 이미지와 일본 전 지역 145개 기항지를 전수 검수한 것으로 간주하지 않는다.
- 촬영지의 실제 사진이라는 사실이 현재 접안 위치·방문일 영업·크루즈 입항 상황을 보증하지 않는다. 오래된 사진은 특히 촬영 당시 상태로만 해석한다.
- 자동화된 화면 스크린샷과 픽셀 정상 로딩 검수는 성공했으나, 모든 원본 사진에 대한 현장 촬영자 직접 확인이나 현지답사는 수행하지 않았다.
- **일본 키즈여행(V116)은 별도의 독립 콘텐츠 작업**이며 V115 이후에 관리한다. V115에서는 키즈 상세 글을 증산하지 않았다.

최종 공개 QA 출력: `{"passed": true, "checked": 20, "expected": 20, "errors": []}`.
