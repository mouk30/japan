# V124 — 지역별 하루 즐길거리 3개 카드 실사진 프리미엄 리뉴얼

- 시행일: 2026-10-22
- 공개 위치: `https://www.nipponferry.com/`, 홈페이지 ‘지역별 하루 즐길거리’ 카드
- 대상: **오사카 / 시모노세키 / 대마도 정확히 3개**
- 기존 글·링크·페이지 SEO title, description, canonical, H1, JSON-LD 변경 없음
- 실사진 3장의 명확한 장소·촬영연도·저작자·라이선스 출처를 카드 아래 표시
- 기존 오사카/가라토시장/대마도 터미널 사진은 삭제하지 않고 다른 페이지와의 참조 유지
- 원본 사진은 화면비 조정 및 색보정 후 1200×800 WebP로 변환, 원본 권리조건 유지
- **중요**: 앞서 ChatGPT에서 생성한 아름다운 3장 콘셉트 연출 이미지는 별도의 디자인 시안이며, 실제 사이트에 업로드한 이 3장은 Commons 사용조건 검증된 실제 현장 사진임. 이미지 연출과 실사를 혼동해서는 안 됨.

| 카드 | 변경 후 촬영 장소·내용 | 촬영시점 | 저작자 | 라이선스 |
|---|---|---|---|---|
| 오사카 | 덴포잔 대관람차 황혼 풍경 | 2011-11-01 | [TimBray](https://commons.wikimedia.org/wiki/File:Tempozan_Ferris_Wheel_in_Osaka_at_Dusk.jpg) | CC BY-SA 4.0 |
| 시모노세키 | 가라토시장 인근 간몬해협의 황혼 풍경 | 2016-12-06 | [そらみみ](https://commons.wikimedia.org/wiki/File:View_of_Kammon_Strait_and_Mojiko_Retro_Area_near_Karato_Market_at_dusk.jpg) | CC BY-SA 4.0 |
| 대마도 | 이즈하라항을 육지 쪽에서 본 항구 풍경 | 2017-08-12 | [Saigen Jiro](https://commons.wikimedia.org/wiki/File:Izuhara,_Tsushima-2.jpg) | CC0 1.0 |

## 품질 기준

- 원본 파일·촬영시점·저자·Commons 라이선스 확인: [사진 계획](./photo-plan.json)
- WebP 원본 체크섬 및 교체 내역: [사진 적용 결과](./import-result.json)
- 실제 교체 자동화: [GitHub Actions](https://github.com/mouk30/japan/actions/runs/39768619393)
- 1440px PC 및 390px 모바일에서 3개 카드 이미지 열기·실제 해상도·출처 링크·SEO·가로 넘침 점검: [공개 사이트 QA](https://github.com/mouk30/japan/actions/runs/39769323534)
- **공개 사이트 PC 1440px × 3장 + 모바일 390px × 3장 = 6/6건, 오류 0건.** [검수 화면 이미지 2장과 JSON 보고서](https://github.com/mouk30/japan/actions/runs/39769323534/artifacts/12421621735).
- *사이트에 실사진이 게시되었다는 사실이 해당 촬영연도의 풍경이 현재까지 동일하거나 항차·시설 운영정보가 최신임을 보장하지는 않습니다.*
