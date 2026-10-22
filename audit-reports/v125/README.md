# V125 | 기항지 AI 대표 이미지 10편 실사진 교체 — 완료 확인 기록

**날짜: 2026-10-22. 키즈관은 보류. 신규 게시글 0편. 기존 기항지 10편의 대표 사진 개선.**

## 확인된 결과

- Wikimedia Commons의 **서로 다른 10개 실사 원본**을 다운로드한 후 WebP로 변환. 10장 다운로드/변환/검증 중 하나라도 실패하면 배포하지 않는 all-or-none 방식.
- 원래 AI 대표 이미지 10건은 새로운 실사진 10건으로 교체, OG 이미지는 새 WebP로 연결.
- 기존 **title · description · canonical · H1 · JSON-LD** 10편 원문 일치 검수 통과. 본문·URL 증산/제거 없음.
- 관광지·항만 실제 장소 설명, 저작자, 촬영일, 라이선스 원문, WebP 변환 및 공개 범위 고지 표시.
- GitHub Actions에서 **PC 1440px 10편 + 모바일 390px 10편 = 20/20 성공**, 오류 0건, 공개 이미지 실제 로딩/출처 표시/원래 SEO/가로 넘침 확인.

## 사진 원본·촬영일·사용 권리

| 지역 | 사진 속 실제 위치 | 촬영일 | 출처·저작자·라이선스 |
|---|---|---|---|
| 가나가와·요코하마 | 다이코쿠부두에서 바라본 요코하마 도심 풍경 | 2023-04-02 | [Syced · CC0 1.0](https://commons.wikimedia.org/wiki/File:Yokohama%20seen%20from%20Daikoku%20Pier.jpg) |
| 가고시마·아마미오시마 | 아마미 나제항 본항·신항·나가하마 지구의 실제 모습 | 2012-01-20 | [Vanquish0 · CC BY-SA 3.0](https://commons.wikimedia.org/wiki/File:Naze%20port2.JPG) |
| 후쿠이·사카이 | 후쿠이 도진보 해안의 실제 주상절리 바위 | 2008-11-01 | [663highland · CC BY-SA 3.0](https://commons.wikimedia.org/wiki/File:Japan%20Tojinbo04s4592.jpg) |
| 시즈오카·이토 | 이토 조가사키 해안의 실제 절벽 풍경 | 2019-04-04 | [Zairon · CC BY-SA 4.0](https://commons.wikimedia.org/wiki/File:Ito%20Jogasaki-K%C3%BCste%2042.jpg) |
| 도쿄도·하치조지마 | 하치조지마의 실제 태평양 해안 경관 (가미나토 부두 사진은 아님) | 2012-07-10 | [Matryokeshi · CC BY-SA 3.0](https://commons.wikimedia.org/wiki/File:Hachijojima.JPG) |
| 미야자키·아오시마 | 미야자키시 아오시마 신사의 촬영 당시 모습 | 2008-06-01 | [JKT-c · CC BY 3.0](https://commons.wikimedia.org/wiki/File:Aoshima%20Shrine.jpg) |
| 에히메·니이하마 | 니이하마 마인트피아 벳시 본관의 실제 건물 (크루즈 부두 아님) | 2017-04-15 | [Dokudami · CC BY-SA 4.0](https://commons.wikimedia.org/wiki/File:Maintopia01a.jpg) |
| 도쿄도·오가사와라 지치지마 | 2000년 당시 지치지마 후타미항에 입항하는 오가사와라호 | 2000-08 | [Si-take. · CC BY-SA 3.0](https://commons.wikimedia.org/wiki/File:Port%20of%20Futami%2C%20Chichijima%2C%20Ogasawara.jpg) |
| 나가사키·이키섬 | 2023년 촬영한 이키섬 고노우라항 실제 항만 경관 | 2023-01-02 | [Tsuyoshi chiba · CC BY-SA 4.0](https://commons.wikimedia.org/wiki/File:Gonoura%20port.jpg) |
| 에히메·이마바리 | 이마바리성과 도도 다카토라 동상 실제 사진 | 2025-07-11 | [Fred Cherrygarden · CC BY-SA 4.0](https://commons.wikimedia.org/wiki/File:Imabari%20Castle.jpg) |

> 주의: 하치조지마 해안, 도진보, 마인트피아 벳시, 아오시마 신사, 조가사키, 이마바리성은 각각 실제 관광명소 사진이며 **해당 항만의 현재 접안부두나 승객 게이트를 보여주는 것이 아님**. 2000년 당시 오가사와라 후타미항 사진 등 오래된 촬영본도 촬영 시점만 기록하며 오늘 운영 모습이라고 보증하지 않음.

## 실제 작업 검증 링크

- [원본 10건 + 원본 SEO 고정선](./seo-and-ai-candidate-baselines.json)
- [10장 Commons 사진 출처/촬영일/라이선스 선정표](./photo-plan.json)
- [실제 다운로드 기록 + 사진/최종 WebP SHA256 + 파일 크기](./import-result.json)
- [GitHub Actions: 실제 변환·배포 성공](https://github.com/mouk30/japan/actions/runs/39771465603)
- [GitHub Actions: 원본 검수 + 공개 PC·모바일 20회 통과](https://github.com/mouk30/japan/actions/runs/39771690364)
- [실제 Chromium 화면 캡처 20장 ZIP + JSON 결과](https://github.com/mouk30/japan/actions/runs/39771690364/artifacts/12422841668)
- [실제로 적용한 WebP 10장 + 원본·저작권 기록 ZIP](https://github.com/mouk30/japan/actions/runs/39772142531/artifacts/12423201194) — 추가 실행도 PC·모바일 20회 통과

## 잔여 품질 과제

- [AI 대표 이미지 잔여 36편](./remaining-36-ai-heroes.json): 이전 46편에서 현재 10편 감축.
- 기존 도쿄 사진 원본 육안 검토 약 20건은 이번 대체 10건과 다른 독립 QA 항목.
- 출처/운영 정보 링크의 URL 응답 확인이 항차별 실시간 예약·운임·운영시간을 보증하는 것은 아님.
- **키즈관 자료 확보 전까지 신규 키즈 콘텐츠 작업을 시작하지 않음.**
