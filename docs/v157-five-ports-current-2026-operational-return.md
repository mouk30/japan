# V157 — 핵심 일본 크루즈 기항지 5곳: 최신 운휴·입장·선석·귀선

공식자료 대조일: 2026-10-24. **기존 게시글 5편 수정 / 신규 게시글 0편 / 사진 교체 0장 / 기존 URL 유지**.

## 실제 운영 변동 우선 조치
| 기존 상세페이지 | 놓치기 쉬운 실제 변경·조건 | 공식 운영 주체 |
|---|---|---|
| 아오모리 | 신추오부두/오키다테부두를 구분. 2026년 기항 예정은 확정된 게이트 아님. 네부타 와랏세의 **9~4월 9:00~18:00 / 최종 입장 17:30** 및 8/9~8/10·12/31~1/1 휴관. 아오모리역 동·서 승강장 별도 | [아오모리현 입항 예정](https://www.pref.aomori.lg.jp/soshiki/kendo/kowan/2023-aomori-cruise.html), [와랏세 이용 시간](https://www.nebuta.jp/warasse/shisetsu/business-day.html), [시 교통 승강장](https://www.city.aomori.aomori.jp/koutsu/noriba_location-system_jikokuhyou/1002332.html) |
| 하코다테 | **2026년 10/20~11/8 로프웨이 운휴**, 같은 기간 버스 **2계통도 운휴**. 1계통 등산버스는 별개로 운행하나 당일 시간표 확인해야 함. 시가 안내하는 접안 3곳(와카마쓰·미나토초·니시) 중 와카마쓰만 JR역 가까움 | [로프웨이 공지](https://334.co.jp/news/2026/0406-22668/), [하코다테버스 1/2 운행구분](https://hakobus.co.jp/info/2639/), [하코다테시 부두](https://www.city.hakodate.hokkaido.jp/docs/2014031100439/) |
| 가고시마 | 마린포트/가고시마 본항 북부두/사쿠라지마 일반 페리터미널은 서로 다른 구역. 마린포트 외곽 교통 접근시간 별도. **사쿠라지마 페리는 2025년 10월부터 24시간 운항 종료, 04:00~23:30 운영**. 항차별 셔틀 무료·유료 여부와 택시 대기 불확실 | [현 관광 마린포트 공식교통](https://www.kagoshima-kankou.com/cruise/marineport/top), [사쿠라지마 시영 페리 운영](https://www.city.kagoshima.lg.jp/sakurajima-ferry/howtouse/hajimete.html), [크루즈→페리 코스](https://www.kagoshima-kankou.com/course/53184) |
| 벳푸 | 2026년 9/30 갱신 현 크루즈 입항예정에 **제4부두** 명기, 정기 여객항과 구분. 지옥 7곳 공통관람권 운영사 기준 대인 **2,400엔**, 소·중학생 **1,200엔**, **08:00~17:00**. 시내 일반버스와 별도 예약 정기 관광버스를 구분하며 귀선 마지막차 실제 확인 | [오이타현 기항예정](https://pref.oita.jp/site/beppu17003/2026cruising.html), [7개 지옥 운영/발권](https://beppu-jigoku.com/fee/index.html), [가메노이 공식버스](https://kamenoibus.com/scheduled_howto/) |
| 가나자와 | 가나자와항 크루즈터미널 이용 시설 **09:00~21:00**는 선사 승객 귀선 마감이 아님. JR가나자와역까지 공식 일반 안내 약 **5km/차량 15분**. 역↔터미널 일반 노선버스 운행은 무료 항차별 셔틀과 다른 교통으로 구분 | [터미널 공식 접근/노선버스](https://www.kanazawa-cruise.jp/access/), [터미널 공식 공지](https://www.kanazawa-cruise.jp/) |

## 사용자 관점에서 본 개선
- 상단에 **실제 하선 부두 → 별도 현지 교통·예약조건 → 되돌아올 승객 출입 게이트** 세 칸을 큰 사진 아래에 배치.
- 공식 운휴/휴관/운임과 날짜별 티켓 잔여석을 구분. **구매·예약 가능성 자체는 실제 판매처에서 최종 확인**.
- 귀선차 미확정 또는 기상 변동 시 계획을 줄일 명확한 대안 제시.
- 기존 5개 H1/canonical/메타/사진 WebP/ALT/CC/전체 내부·외부 링크/사이트맵 보존. V157은 새 기사 증산 아님.
- 출발일 실제 승객 게이트·마지막 셔틀 운행, 로프웨이 현재 예약 재고, GSC/GA4 클릭 데이터는 직접 접근·확인하지 않았음.

## 기술 검증
`scripts/qa_v157_five_port_operating_facts.py`: 원본 `origin/main` 대조로 각기 기존 사진·ALT·크기, 기존 모든 링크와 CC 라이선스, 단일 H1, canonical, 메타, 정합성, 새로운 공식 3링크/승선 귀선표, 기존 상세/사이트맵 보존 검사.
