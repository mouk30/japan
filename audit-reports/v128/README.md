# V128 — 기존 크루즈 기항지 AI 대표 사진 10편을 실제 촬영 사진으로 교체

**작업일 2026-10-22 · 신규 글 0 · 키즈관 신규 게시 0**

## 완료 범위
- V127 후 남은 명시적 AI 대표 이미지 16편 중 우선순위 10편을 지역과 장소가 입증되는 Wikimedia Commons 원본 실사진 10장으로 변경하고 개별 WebP 제작.
- 10편 기존 URL, title, meta description, canonical, H1, 본문 및 FAQ·BreadcrumbList 구조화 정보 유지.
- 대표 이미지, 대체텍스트, 출처 figcaption, OG 및 Twitter 이미지의 사진 URL 변경. **Article JSON-LD의 image 주소만 실제 WebP URL로 동기화**, 다른 JSON-LD 키·값과 기존 SEO 보존.
- 각 WebP 원본 파일 출처·저자·촬영일 또는 촬영 월·크레디트·사용 라이선스 및 포맷변환 고지를 게시글 아래 명시.
- 사진과 접안부두의 관계를 설명. 관광지·철도역·오래된 항공사진이 현재 승객 하선 게이트나 당일 크루즈 접안 상태의 증거로 오인되지 않게 함.
- **10편 GitHub 이미지 변환·파일 유효성·SEO 원본 및 속성 검사 통과, 이미지 구조/출처/동기화 정적 90개 항목 통과.**
- 잔여 명시적 AI 대표 이미지: **6편**. [남은 6편 확인](./remaining-6-ai-heroes.json)

## 사진별 원본·촬영 시점·권리조건
| 기존 게시글 | Wikimedia Commons 실제 사진 원본 | 촬영일 | 촬영자 | 권리 | 사진 내용/현재 항만 상태 한계 |
|---|---|---|---|---|---|
| [가가와·사카이데](https://www.nipponferry.com/things-to-do/sakaide-cruise-port-day-trip/) | [실사 원본](https://commons.wikimedia.org/wiki/File:Seto-Ohashi_Bridge.jpg) | 2007-03-05 | Hideyuki KAMON | [CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/) | 사카이데에서 촬영한 세토대교 항공 경관. 사카이데항 크루즈 접안 선석 사진은 아님 |
| [시즈오카·시모다](https://www.nipponferry.com/things-to-do/shimoda-cruise-port-day-trip/) | [실사 원본](https://commons.wikimedia.org/wiki/File:Shimoda_Port_Shimodau_Shizuoka_pref_Japan01s.jpg) | 2013-05-12 | 663highland | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) | 2013년 항공 촬영한 시모다항 실제 전경. 현재 여객 게이트나 크루즈 선석 확정 사진은 아님 |
| [와카야마·신구](https://www.nipponferry.com/things-to-do/shingu-cruise-port-day-trip/) | [실사 원본](https://commons.wikimedia.org/wiki/File:Shingu_Kumano_Hayatama-taisha_Shin-mon_2.jpg) | 2023-10-19 | Zairon | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 와카야마현 신구시에 있는 구마노 하야타마 신사의 신문 실제 촬영. 후쿠오카현 신구와는 다른 장소이며 신구항 접안시설 사진은 아님 |
| [고치·스쿠모](https://www.nipponferry.com/things-to-do/sukumo-cruise-port-day-trip/) | [실사 원본](https://commons.wikimedia.org/wiki/File:Port_of_Sukumo_-_%E5%AE%BF%E6%AF%9B%E6%B8%AF_-_panoramio_(4).jpg) | 2016-05-04 | z tanuki | [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/) | 2016년 고치현 스쿠모항 실제 촬영 사진. 현재 크루즈 선박 접안 게이트나 셔틀 현황을 보증하지 않음 |
| [시즈오카·다고노우라](https://www.nipponferry.com/things-to-do/tagonoura-cruise-port-day-trip/) | [실사 원본](https://commons.wikimedia.org/wiki/File:Port_of_Tagonoura.jpg) | 2016-12-17 | Alpsdake | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | 2016년 아시타카산에서 내려다본 다고노우라항과 해안 실제 전경. 당일 크루즈 접안 상황과는 별도 |
| [미에·도바](https://www.nipponferry.com/things-to-do/toba-cruise-port-day-trip/) | [실사 원본](https://commons.wikimedia.org/wiki/File:Toba_Port_01.jpg) | 2006-11-22 | Hideyuki KAMON | [CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/) | 2006년 항공 촬영한 도바항 실제 전경. 현행 부두와 셔틀 동선을 확인하는 사진은 아님 |
| [아이치·도코나메](https://www.nipponferry.com/things-to-do/tokoname-cruise-port-day-trip/) | [실사 원본](https://commons.wikimedia.org/wiki/File:Tokoname_landscape_ac_(1).jpg) | 2020-09 | Asturio Cantabrio | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | 도코나메에서 촬영한 도자기·타일 문화 풍경. 도코나메항 승객 접안부두 사진이 아님 |
| [야마구치·도쿠야마](https://www.nipponferry.com/things-to-do/tokuyama-kudamatsu-cruise-port-day-trip/) | [실사 원본](https://commons.wikimedia.org/wiki/File:View_of_Tokuyama_Port.jpg) | 2018-05-01 | そらみみ | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | 2018년 촬영한 도쿠야마항 실제 전경. 크루즈 운항 및 접안 선석은 항차별 확인 필요 |
| [아오모리·아지가사와](https://www.nipponferry.com/things-to-do/tsugaru-ajigasawa-cruise-port-day-trip/) | [실사 원본](https://commons.wikimedia.org/wiki/File:Ajigasawa_Station_20190908a.jpg) | 2019-09-08 | 掬茶 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | 2019년 촬영한 아지가사와역 실제 경관. 쓰가루·아지가사와 연안 크루즈 접안부두 사진은 아니며 기차역과 하선 위치를 혼동하지 말 것 |
| [후쿠이·쓰루가](https://www.nipponferry.com/things-to-do/tsuruga-cruise-port-day-trip/) | [실사 원본](https://commons.wikimedia.org/wiki/File:Port_of_Tsuruga.jpg) | 2016-11-02 | Alpsdake | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | 2016년 데즈쓰산에서 바라본 쓰루가항 실제 전경. 현재 크루즈 하선 선석 및 출입 게이트는 항차별 확인 필요 |

## 자동 검수/다운로드
- [V128 이미지 변환·배포 성공 GitHub Actions](https://github.com/mouk30/japan/actions/runs/39777070249)
- [V128 WebP 사진 및 기존 게시글 교체 커밋](https://github.com/mouk30/japan/commit/9c276f0feebf4a6f90e387f6206f4f55548b8707)
- [V128 전용 공개 PC·모바일 브라우저 검수 작업](https://github.com/mouk30/japan/actions/runs/39778061146) — 별도 진행 상태를 확인해 최종 판정
- [V128 사진 원본 출처와 권리 내역](./photo-plan.json)
- [V128 수정 전 페이지 SEO 원본](./seo-and-ai-candidate-baselines.json)
- [원본 JPEG 및 변환 WebP SHA256·픽셀 기록](./import-result.json)

## 다음 단계
- V129: [우베, 우노, 우와지마, 야쓰시로, 야와타하마, 욧카이치](./remaining-6-ai-heroes.json) 마지막 6편 실사진 교체.
- [NIPPONFERRY KIDS](../kids-hub-concept-2026-10-22.md): 자료를 받기 전까지 컨셉만 보관, 실제 메뉴 및 사이트 콘텐츠 게시 금지.
