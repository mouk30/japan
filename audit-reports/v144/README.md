# V144 — 기존 51편 세부설명·비주얼 품질보강 최종 현황

기준: 2026-10-23 · Repository: mouk30/japan · 공개 URL: https://www.nipponferry.com/

## 실행 결과 — 신규 글 생성 없이 기존 내용만 보완

| 검수·수정 항목 | 결과 | 근거 |
|---|---:|---|
| 계절·축제·겨울여행 관련 기존 원문 | 24편 보강 | `scripts/v144_season_specifics.json` |
| 교통·관광열차·테마파크·생활정보 기존 원문 | 27편 보강 | `scripts/v144_practical_specifics.json` |
| 제목과 일치하는 주제별 정보형 비주얼 | 51개 적용 | `site/nf-v144-topic-depth.css` |
| 위 51편 사진 원본 검토 대상 분리 | 51개 구 사진 경로 기록 | `editorial-image-provenance-report.json` |
| 실제 장소·촬영자·CC 라이선스 검증 사진 추가 | 3장 WebP·캡션·과거 촬영연도 | `verified_documentary_photo_additions` |
| 전체 기존 페이지 HTML 검사 | 원본 1,277개 / 배포 1,276개 | V143/144 source/build |
| 공식 참조/SEO·관련링크·예약 경로 | 원본 URL, title, meta description, canonical, 원래 예약 링크 유지 | V144 build QA |
| 신규 게시글·키즈관 | 0건 | V144 report |

### 내용
- 같은 계절 일반문구 대신 각 페이지 주제에 맞는 **3개 실제 확인 순서**로 기존 첫 상세본문을 교체.
- 일반 교통·기기 안내가 재사용된 실용 정보 27편도 교통수단별·시설별 조건과 귀가/환승·예약/취소 핵심 정보로 구분.
- `NEXT QUESTION` 일반 추천글 연결 253개는 V143 공유 빌드 규칙으로 기존 관련글에 연결되며 V144 전체 빌드 회귀 검사를 통과.
- 각 페이지에서 촬영 원본·장소·라이선스가 없는 공통 커버를 특정 장소의 사진인 것처럼 쓰지 않기 위해 **페이지별 주제에 맞는 정보형 비주얼**로 우선 교체. 원본 대표이미지 파일은 삭제하지 않음.
- 새로운 실제 촬영 사진 3장은 비주얼 위에 **별도 추가**했으며 정보형 안내도 유지. 설명·출처·촬영일·CC 라이선스·변경사항을 사진 아래 기록.

### 실제 촬영 사진 3장 (Wikimedia Commons 개별 원문 확인)
1. **아사히카와 눈축제** · 2007-02-11 · 京浜にけ · CC BY-SA 3.0 · [Commons 원문](https://commons.wikimedia.org/wiki/File:Asahikawa_Winter_Festival_Snow_Statue_1.jpg)
2. **오타루 눈빛거리** · 2014-02-14 · t-konno · CC BY-SA 3.0 · [Commons 원문](https://commons.wikimedia.org/wiki/File:%E5%B0%8F%E6%A8%BD%E9%9B%AA%E3%81%82%E3%81%8B%E3%82%8A%E3%81%AE%E8%B7%AF%EF%BC%88Otaru_Snow_Light_Path_Festival%EF%BC%89_-_panoramio.jpg)
3. **교토 단고 쿠로마츠 관광열차** · 2019-03-21 · おのののの · CC BY-SA 4.0 · [Commons 원문](https://commons.wikimedia.org/wiki/File:%E4%BA%AC%E9%83%BD%E4%B8%B9%E5%BE%8C%E9%89%84%E9%81%93%E8%A6%B3%E5%85%89%E5%88%97%E8%BB%8A%E3%80%8C%E3%81%82%E3%81%8B%E3%81%BE%E3%81%A4%E3%80%8D%E3%80%8C%E3%81%8F%E3%82%8D%E3%81%BE%E3%81%A4%E3%80%8D.jpg)

사진은 과거 기록이며 2027년 행사 풍경/현재 차량 운행 편성을 보여주는 사진이라고 기재하지 않았다. 원본은 각각 WebP 크기 변환 및 전환된 파생물임.

### 완료된 실제 브라우저 및 CI
- [V144 원본 51편 수정·배포 빌드·SEO 검사 성공](https://github.com/mouk30/japan/actions/runs/39943746809)
- [V144 공개 사이트 69개 화면 조합, 오류 0건](https://github.com/mouk30/japan/actions/runs/39943950394): 51편 모바일 390px + 주요 6개 경로 320·768·1440px. **이 검수는 추가 3장 실사 삽입 직전 버전**을 검사한 것이며, 새 세 실사까지 함께 검사했다고 해석하지 않음.
- [세 실사 이미지 다운로드/원본 출처·권리표시/SEO 검증 빌드 성공](https://github.com/mouk30/japan/actions/runs/39944569483)
- **추가 3장에 대한 공개 모바일·PC 최종 브라우저 검수:** [별도 작업](https://github.com/mouk30/japan/actions/runs/39944755499) 진행 상태는 링크에서 확인; 완료 결과를 확인하기 전에는 통과라고 표기하지 않음.

### 남은 공통사진 정확성 검토 대상 (원본 1,276개 HTML 재검사)
- `/images/ferry.jpg`: **40편**
- `/images/couple.jpg`: **27편**
- `/images/city.jpg`: **26편**
- `/images/tsushima.jpg`: **16편**
- `/images/local.jpg`: **15편**
- `/images/fukuoka.jpg`: **13편**

원본 목록은 [remaining-photo-provenance-queue.json](./remaining-photo-provenance-queue.json). 위 숫자는 반복 사용·원본 검토 후보이지 137개 촬영 장소 오류 확정이라는 뜻이 아님. 사진·실제 장소·저작자·라이선스를 1건씩 확인한 다음에만 교체. 2027 축제 일정과 현재 운행 시간은 과거 사진으로 증명하지 않는다.

### 원칙
신규 글 0건. 도메인·SEO·canonical·예약 경로 보존. 연령대별로 읽기 쉬운 글씨와 본문-비주얼 연결 강화. 원본 권리 미확인 사진의 무단 대체 금지. 향후 우선 대상은 노선별 공통 `ferry.jpg` 40건, 실제 관광지 장소가 명확한 공통 `city.jpg` 26건, 그리고 동행·커플 카드 `couple.jpg` 27건의 개별 실사 원본 확인.
