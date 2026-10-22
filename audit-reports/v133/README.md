# V133 — 실사진 원본·촬영장소·라이선스 및 공식 운영정보 대조

**검증 기준일: 2026-10-23 · 기존 게시글 신규 생성 0 · 키즈관 게시 보류 · 기존 게시글 품질 보강만 실행**

## A. 이전 배치의 공개 사이트 오류 판정 수정
- V132 검수 [첫 실행](https://github.com/mouk30/japan/actions/runs/39801816061)은 **이미지 PC+모바일 166/166 성공**했으나, 예약안내 3페이지에 숫자 `13`을 강제하는 테스트가 한글 문구 `오후 1시`를 읽지 못해 실패한 **테스트의 가짜 오류**였음.
- 문자열 검수조건을 수정하여 [V132 재검증](https://github.com/mouk30/japan/actions/runs/39804159620)에서 사진 **166/166**, 공식 예약정보 **6/6**, 전체 **172/172 성공**, 오류 **0건**. [증빙 ZIP](https://github.com/mouk30/japan/actions/runs/39804159620/artifacts/12437285986).
- **V133에서 새로 고친 페이지 4곳의 공개 PC·모바일 표시까지 이미 검증했다는 의미는 아님.** 이번 새 수정은 기존 HTML 소스·canonical·출처를 별도 재검사함.

## B. 2026년 11월 슈리성 입장 조건 최신 원문 반영 (기존 2편)
- [오키나와 슈리성 즐길거리](https://www.nipponferry.com/things-to-do/okinawa-shuri-castle/)
- [나하 크루즈 슈리성 접근·귀선 가이드](https://www.nipponferry.com/things-to-do/naha-shuri-castle-cruise-sightseeing/)
- [시설 공식 현행 요금](https://oki-park.jp/shurijo/info/14)과 [시설 공식 정전 내부 관람 예약](https://oki-park.jp/shurijo/ticket_guide/) 원문 대조.
- 2026년 11월 21일까지 유료구역 개인 일반·고교생·초중학생 400/300/160엔. **11월 22일 종일과 23일 오전 휴원**.
- **11월 23일 정오** 복원 정전 내부 공개 시작. 그날부터 개인 일반·고교생·초중학생 **1000/760/370엔**으로 개정, 6세 미만 무료.
- **정전 내부 관람은 날짜·30분 단위 시간대 사전예약 필수**, 일반 유료구역 중 정전 내부 제외 부분은 해당 정전 내부 예약 불필요. 사전 예약 시각 및 공원 입장료는 크루즈 선사의 하선·귀선 허가와 별도.
- 복원 공사 2025년 사진은 해당 시점의 현장기록이지 2026년 완공 상태 사진이 아님. 기존 사진·출처 그대로 유지.

## C. 2024년 노토 지진 이후 나나오 현장 운영 정보 구분 (기존 1편)
- [나나오항 기항지](https://www.nipponferry.com/things-to-do/nanao-cruise-port-day-trip/)에 공식 관광 정보를 추가.
- [이시카와현 공식 관광청 시장 정보](https://www.hot-ishikawa.jp/spot/detail_1954.html): 노토 식제시장 통상 영업 09:00~17:00, 화요일 휴무(공휴일 예외), 입장 무료. **같은 공식 자료에 지진에 따른 운영시간 등 변경 가능** 명시되어 있어 특정 일자의 정상 영업을 보증하지 않음. [시장 공식 홈](https://www.shokusai.co.jp/)과 [와쿠라온천 관광협회](https://www.wakura.or.jp/)를 별도 확인 경로로 제시.
- 나나오항 대표 사진은 **2007년** 촬영자료라 2024년 이후 보수·복구 현황 또는 실제 크루즈 승객 게이트가 아님.
- 특정 항차의 최종 셔틀·귀선 마감, 지역 온천시설의 날짜별 영업 및 예약 가능성은 미확인.

## D. 실제 사진 원본·저작권과 본문 정합성 직접 비교 (3장)
| 기존 사진 사용 페이지 | 원본에서 직접 확인한 촬영 대상 | 저작자 · 촬영일 | 권리 조건 | 결과 |
|---|---|---|---|---|
| [슈리성 복원공사](https://www.nipponferry.com/things-to-do/okinawa-shuri-castle/) | [Wikimedia Commons 원본](https://commons.wikimedia.org/wiki/File:Shuri_Castle_Reconstruction.jpg): 슈리성 정전 복원 공사 중인 현장 | おにく · 2025-02-11 | CC0 1.0 | 2026년 완공장면이 아닌 과거 사진이라고 적혀 있어 설명 일치 |
| [나나오항](https://www.nipponferry.com/things-to-do/nanao-cruise-port-day-trip/) | [Commons 원본](https://commons.wikimedia.org/wiki/File:Nanao_port.JPG): 2007년 나나오항 | nanaoshimin · 2007-12-25 | Public domain (권리자 직접 기증) | 현행 항만시설·2024년 지진 후 사진 아님, 설명 일치 |
| [나가사키 글로버정원](https://www.nipponferry.com/things-to-do/nagasaki-cruise-port-day-trip/) | [Commons 원본](https://commons.wikimedia.org/wiki/File:Nagasaki-Glover-Garden-5384.jpg): **옛 링거 주택 (Ringer House)**. 글로버 저택 자체 아님 | Fg2 · 2007년 | Public domain (권리자 직접 기증) | 실제 사진 대상과 맞도록 대표사진 alt·캡션을 **옛 링거 주택**으로 정확히 수정 |

> 세 원본의 공개 설명·저자·촬영일·라이선스 표기를 독립 확인한 결과. 사이트 전체 사진 저작권 전수 인증이 아님.

## E. 과거 사진출처 확인 후보 289곳 중 핵심 22편 실제 표기 재검토
- V132 자동 스캐너가 `<figcaption>`이나 근접 크레디트 형식에 충분히 대응하지 못해, **사진 출처를 적절히 가진 크루즈·동행 가이드 22편도 표시누락 후보로 잡음**.
- 이 22편 각 HTML에서 **대표사진 가까이 Commons 원본 링크 + 촬영자 + 라이선스 표기 22/22 존재** 확인. 해당 표기 자체는 추가 교정 불필요.
- **22장 각각의 이미지 원본을 독립적으로 다운로드·시각 비교했다는 뜻은 아님**. 원본 저작자/라이선스까지 이번에 직접 다시 검증한 것은 위 3장.
- 잔여 **267곳은 '잘못된 이미지 267장'이 아니라 아직 문서·출처 표시 방법을 개별 대조하지 않은 기존 후보**임. 원본이 확인되지 않는 이미지는 성급히 CC 라이선스를 부여하거나 대체하지 않음.

## F. SEO·공개 QA·귀선 경계
- 기존 4개 페이지의 `canonical` 및 V133 공식·사진 검수문구 정적 검사 **4/4 정상**.
- 수정된 원문에서 기존 URL·제목·메타 설명·Article JSON-LD 유지; 새 게시글 0.
- 귀선 최종 시간은 **선박명·기항일·실제 접안 선석·승선 마감·교통 복귀시간** 없이 임의로 설정하지 않음.
- 기존 [V131 이시가키 버스](https://www.azumabus.co.jp/localbus/)와 [나가사키 관광 영문 안내](https://www.discover-nagasaki.com/en/transit/100790) 접근 제한은 여전히 기술적 미확인으로, 링크를 무작위로 삭제·치환하지 않음.
- [V133 사진 출처 서식 감사 스크립트](../../scripts/v133_photo_provenance_audit.py)와 [GitHub 검수 절차](https://github.com/mouk30/japan/actions/workflows/v133-photo-license-and-official-qa.yml). 자동검사 실행 성공 전에는 그 결과를 완료로 단정하지 않음.

**다음 보강:** 나머지 가이드 사진의 출처·실제 촬영 장소 일치 후보를 페이지별로 선정해 원본·저자·실제 피사체를 대조. 이후 예약 CTA 중 실제로 방문자에게 '즉시 구매'처럼 표현되지만 일반 홈페이지로 이동하는 링크만 출처를 확인해 수정.
