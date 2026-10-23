# V145 — 일본 바다 여행: 항구에서 관광·예약·귀선까지

**기준일:** 2026-10-23 · **도메인:** https://www.nipponferry.com/ · **저장소:** `mouk30/japan`

## 실제 반영 범위

기존 `/things-to-do/` 상세글 **10편**을 새 글 증산 없이 보강했다. 각 글마다 5개 항목(항구·하선 판단 → 섬/도심 이동 → 관광지 선택 → 시설 예약·이용조건 → 안전 복귀)으로 구성된 한국어 안내, 공식 원문 링크, 실제 존재하는 기존 관련글 링크, 과거 대표사진의 검증 범위 안내를 추가했다.

| 지역 | 기존 페이지 | 본문 보강 방향 |
|---|---|---|
| 세토내해 | [쇼도시마 페리](https://www.nipponferry.com/things-to-do/shodoshima-ferry-island-access/) | 다카마쓰↔도노쇼, 일반·고속선 구별, 엔젤로드 간조, 본토 복귀 |
| 세토내해 | [다카마쓰 크루즈](https://www.nipponferry.com/things-to-do/takamatsu-cruise-port-day-trip/) | 실제 접안 선석 확인, 시내 관광과 별도 섬 페리 일정 구분 |
| 세토내해 | [도모노우라 옛 항구](https://www.nipponferry.com/things-to-do/tomonoura-setouchi-port/) | 역사 관광항과 크루즈 접안항 구별, 후쿠야마 버스·역 복귀 |
| 아마미 | [나제항 크루즈](https://www.nipponferry.com/things-to-do/amami-naze-cruise-port-day-trip/) | 실제 나제 선석, 맹그로브와 시내 일정 구분 |
| 아마미 | [오시마쓰무기](https://www.nipponferry.com/things-to-do/japan-amami-oshima-tsumugi/) | 공방 사전문의, 염색·직조 체험, 항구 왕복 |
| 고토열도 | [후쿠에항](https://www.nipponferry.com/things-to-do/goto-fukue-cruise-port-day-trip/) | 후쿠에섬 별도 관광, 외곽 명소 이동·귀선 |
| 고토열도 | [아오카타항](https://www.nipponferry.com/things-to-do/aokata-cruise-port-day-trip/) | 나카도리섬과 후쿠에섬 구분, 가시라가시마 성당 사전 연락 |
| 시코쿠 | [마쓰야마항](https://www.nipponferry.com/things-to-do/matsuyama-cruise-port-day-trip/) | 도고온천/마쓰야마성 선택, 대중교통·입장조건 |
| 시코쿠 | [가가와 사누키 우동](https://www.nipponferry.com/things-to-do/japan-kagawa-udon-pilgrimage/) | 식당 주문법·휴무·항구와 연결하는 동선 |
| 시코쿠 | [도쿠시마·고마쓰시마](https://www.nipponferry.com/things-to-do/tokushima-komatsushima-cruise-port-day-trip/) | 도심 회관·비잔 전망·나루토 해양관광 구분, 항구 귀선 |

## 근거와 사진의 처리

- 공식 자료는 각 상세글의 `공식 원문` 영역에 링크. JNTO·실제 페리 운항사·지방정부/관광 안내를 우선했다.
- 아오카타 페이지의 출처를 후쿠에섬 일반 소개에서 [일본 국토교통성 아오카타 크루즈 항만 자료](https://www.mlit.go.jp/kankocho/cruise/detail/061/index.html) 및 [신카미고토 관광협회 가시라가시마 성당 방문 안내](https://shinkamigoto.nagasaki-tabinet.com/junrei/10239)로 바로잡았다. 성당 내부 방문 **사전 연락 필요**를 본문에 반영했다.
- JNTO 글·사진을 그대로 복제하지 않고 50개 단계별 실전 본문을 작성했다. 실시간 요금, 임의 출항시각, 미확정 배편, 쇼핑·시설 예약 재고를 생성하지 않았다.
- **원래 대표사진 전부 유지. 새 사진 교체 0장.** 사진은 장소·촬영연도·권리 미확인 상태에서 실사로 오인시키지 않는다. 특히 도모노우라의 기존 AI 참고 이미지는 현재 실사로 대체했다고 표현하지 않는다.

## 자동 QA 결과

- [V145 10개 기존 페이지 수정·전체 빌드·SEO 보존·30개 화면 조합 QA 성공](https://github.com/mouk30/japan/actions/runs/39952125282)
- [아오카타항 선석·성당 사전 연락 조건 공식 출처 수정 및 전체 빌드 성공](https://github.com/mouk30/japan/actions/runs/39952805341)
- [최종 공개 사이트 브라우저 QA](https://github.com/mouk30/japan/actions/runs/39952935426): **10개 기존 페이지 × 320·390·1440px = 30/30, 오류 0**. 포트 동선 5카드·공식 링크·관련 내부 링크·하선 안전 안내·가로 넘침·SEO·모바일 글자 크기를 검사했다.
- [최종 공개 사이트 대표 화면 캡처 8장 및 JSON 검사 기록](https://github.com/mouk30/japan/actions/runs/39952935426/artifacts/12501606192)
- URL/SEO title/description/canonical, 기존 OG·사진·구조화 데이터, 예약 링크와 기존 전체 공통 메뉴 유지. **신규 글 0, 키즈관 0**.

## 반드시 별도 확인할 것

현재 입항선의 선석·승객 게이트, 셔틀 운영, 마지막 복귀 수단, 특정 관광시설의 영업시간·입장권·취소조건 및 실시간 잔여좌석은 항차/이용 날짜별 공식 원문이 우선한다. **공개 QA는 글·인터페이스 정확성 검증이지 2026년 모든 실제 운항시간을 현장 검증했다는 의미가 아니다.**

## 다음 품질 우선순위 (미실시)

1. 도모노우라 AI 참고 이미지 실사로 바꿀 때는 원본 장소·촬영자·허가를 확인한 사진만 사용.
2. 향후 나제·후쿠에·아오카타 항만에서 정확한 항차별 승객 출입구·셔틀/복귀 안내 보강.
3. 신규 나오시마·데시마 페이지 추가는 공식 페리/미술관 이용조건과 검색 성과를 확인한 뒤 별도 결정.
