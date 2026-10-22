# V114 — 기존 크루즈 기항지 10편 AI 대표 사진 → 실제 촬영 WebP 전면 교체

**2026-10-22 · NIPPONFERRY · 신규 게시글 0편 · 기존 상세페이지 10편 개선**

## 변경 결과

- 기존 10개 기항지에서 확인된 **AI 연출 대표 사진 10개**를 각각 해당 지역의 **실제 촬영 관광명소 사진 10개**로 교체했다.
- 10개 새 원본을 Wikimedia Commons의 사진별 촬영자·촬영 시점·표시 라이선스와 연결했고, 각각 독립 WebP를 생성해 `site/images/venues/nf-v114-<slug>-real.webp`에 배포했다.
- **대표 본문 사진 10곳 및 OG 대표 이미지 10곳**을 동일한 새 WebP로 맞췄다. 기존 HTML `title`, meta description, canonical, H1, JSON-LD, 방문·교통·귀선 본문은 보존했다.
- AI 설명 대신 **해당 장소명, 촬영 날짜, 촬영자, 원본 주소, 라이선스, WebP 축소·형식 변환 고지**를 사진 바로 아래에 보여준다.
- 사진을 **2026년 현재 크루즈 접안 선석, 승객 게이트, 셔틀 운영 및 시설 개방상태**를 증명하는 자료로 오해하지 않도록 모든 alt·캡션에서 구분했다.
- 기존 AI 이미지 로딩 실패 시 무관한 일반 페리 사진으로 전환되는 `onerror`도 새 이미지 태그에서는 제거했다.

## 10개 지역 적용 내역

| 기항지 | 실제 촬영 사진의 대상 | 촬영 시점 | 촬영자·원본·라이선스 |
|---|---|---|---|
| 아바시리 | 박물관 아바시리 감옥의 실제 시설·건물 | 2022-08-09 | [Nesnad · CC BY 4.0](https://commons.wikimedia.org/wiki/File:Abashiri%20Prison%20Museum%20-%202022%20Aug%209%20various%2014%2002%2036%20248000.jpeg) |
| 왓카나이 | 왓카나이항 북방파제 돔의 아치 구조 외관 | 2008-08-13 | [Captain76 · Public domain](https://commons.wikimedia.org/wiki/File:%E9%98%B2%E6%B3%A2%E5%A0%A4%E3%83%89%E3%83%BC%E3%83%A0-01.JPG) |
| 야쿠시마·미야노우라 | 야쿠시마 시라타니 운스이쿄 삼림·이끼 계곡 | 2009-11-22 | [KimonBerlin · CC BY-SA 2.0](https://commons.wikimedia.org/wiki/File:Shiratani%20Unsuikyo%20(4196806304).jpg) |
| 오키나와·모토부 | 오키나와 츄라우미 수족관의 고래상어 수조 | 2018-07-07 | [Mokkie · CC BY-SA 3.0](https://commons.wikimedia.org/wiki/File:Whale%20shark%20at%20Churauma%20Aquarium%2C%20Okinawa.jpg) |
| 히메지 | 히메지성 천수각 외관 | 2020-12-29 | [Drivephotographer · CC0 1.0](https://commons.wikimedia.org/wiki/File:Himeji%20castle.jpg) |
| 도쿠시마·고마쓰시마 | 도쿠시마시 료고쿠바시 인근 아와오도리 축제 | 2010-08-12 | [Kounosu · CC BY-SA 3.0](https://commons.wikimedia.org/wiki/File:Awa-odori%20in%20Tokushima%20City.jpg) |
| 가라쓰 | 가라쓰성 천수각의 과거 외관 | 2005-08-20 | [MC MasterChef · CC BY-SA 2.0](https://commons.wikimedia.org/wiki/File:Karatsu%20Castle.jpg) |
| 이바라키·히타치나카 | 국영 히타치 해변공원 미하라시 언덕의 네모필라 | 2021-04-23 | [Miyuki Meinaka · CC BY-SA 4.0](https://commons.wikimedia.org/wiki/File:Nemophila%20and%20a%20Tree%20in%20Hitachi%20Seaside%20Park.jpg) |
| 와카야마·시모쓰 | 와카야마성 대천수의 과거 외관 | 2007-12-27 | [kouko0515 · CC BY-SA 3.0](https://commons.wikimedia.org/wiki/File:Wakayama%20Castle.jpg) |
| 사도섬·오기 | 사도 오기항 인근 타라이부네 통배 체험 풍경 | 2014-05-29 | [rhodnite · CC BY 2.0](https://commons.wikimedia.org/wiki/File:Taraibune%20in%20Sado%20Ogi.jpg) |

## 파일·작업 근거

- [사진 10장의 선택·원본 파일명·촬영일·저작자·사용조건](./photo-plan.json)
- [사진 변경 전 원본 SEO 전수 보존](./seo-baselines.json)
- [실제 내려받은 원본 해시, 각 WebP SHA-256·픽셀·출처, 교체 10건 성공 결과](./import-result.json)
- `scripts/v114_replace_ai_heroes.py`: 다운로드된 모든 사진을 변환·확인한 경우에만 열 페이지를 함께 바꾸는 구조로, 중간 실패 시 부분 게시를 차단했다.
- [GitHub 사진 생성·본문 변경·배포 작업](https://github.com/mouk30/japan/actions/runs/39744555239) — 10장과 10개 페이지 반영 **성공**.
- `scripts/v114_photo_quality_audit.py` 및 `tests/test_v114_photo_quality_audit.py`: 10장 SHA-256, 실제 WebP 크기·구조, 출처/저자/라이선스, AI 태그 제거, OG·canonical, 원래 SEO 및 JSON-LD 일치 검증.
- `scripts/v114_photo_live_qa.py`: 공개 사이트 실제 Chromium 브라우저에서 **PC 1440px, 모바일 390px × 10페이지 = 20회** 사진 로딩·픽셀 크기·크레딧·OG·canonical·가로 넘침 검증.
- [GitHub V114 전체 사진·SEO·모바일 최종 검수](https://github.com/mouk30/japan/actions/runs/39744943087) — **소스 10/10 통과, 실제 공개 브라우저 20/20 통과, 오류 0건**.
- 브라우저 캡처 및 검수 JSON: 최종 Actions의 `v114-ten-real-images-desktop-mobile-evidence` 아티팩트에 수록.

## 명확히 구분해야 하는 사항

- 저작권은 원본 Commons 파일 페이지에 표시된 공개 라이선스를 기준으로 연결했다. CC BY·CC BY-SA 사진은 저작자 표시, 원본 링크, 라이선스 링크, 변환 사실을 본문에 노출했으며, 공유동일조건 등 추가 재사용 의무는 원본 라이선스를 따른다.
- 사진들은 **해당 관광명소를 특정 촬영 날짜에 보여주는 기록**일 뿐, 현행 영업·유지보수·승선 예약·접안 장소의 공식 운영자료는 아니다.
- 일본 기항지 145편 전부나 기존 글에 남아 있는 **다른 본문 AI 이미지까지 전수 검수한 뜻은 아니다.** 이번에는 대표 사진과 OG 이미지에 집중했다.
- GA4 실측 트래픽 권한이 없으므로 실제 방문 순위가 아니라 **기존 AI 대표 이미지가 남은 페이지와 지역별 여행 가치**를 우선해 10곳을 선정했다.

## 검수 결과

- [이미지 10개·저작자·라이선스·원본 SEO 무결성 검사: 성공](https://github.com/mouk30/japan/actions/runs/39744943087)
- [PC 1440px / 모바일 390px 실제 공개 페이지 20/20: 성공](https://github.com/mouk30/japan/actions/runs/39744943087)
- 검사 원문: `{"passed": true, "checked": 20, "expected": 20, "errors": []}`.
