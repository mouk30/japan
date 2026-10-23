# V143 — 세부섹션 품질 보강 및 이미지-본문 매칭 감사

2026-10-23 · https://www.nipponferry.com/

## 첨부 영상에서 실제 확인한 문제
- 삿포로 눈축제 2027 안내와 일부 파생글이 여행 계획에 필요한 교통·회장별 목적·이동·방한 정보를 충분히 제공하지 않고 같은 계절 일반문구를 반복했다.
- 일본 eSIM과 데이터 가이드가 여러 주제에 동일한 일반 안내를 배치하고 일부는 실물 이미지가 아닌 도시 대표사진까지 사용했다.
- 기존의 영문 NEXT QUESTION/KEEP EXPLORING/OPEN THE MAP 연결은 해당 게시글과 직접적인 관련성이 낮았다.

## 실제 수정한 기존 페이지 15편
- 삿포로 눈축제: 메인 2027 일정, 가족, 커플, 2박3일, 3박4일, 옷차림, 숙소 위치, 사진, 먹거리 — **9편**
- 통신·데이터: eSIM/유심/포켓 와이파이 비교, 몇 GB, eSIM 최초 설치, iPhone, Galaxy, 연결 장애 — **6편**
- 한 페이지 내 상세 정보 카드 4~5개, 이용 주의·판단 기준·공식 정보 링크·같은 주제의 다음 안내 적용.
- 행사 공식 안내: https://www.snowfes.com/ ; 2027년 2월 4~11일, 3개 회장 공식 확인 (확인일 2026-10-23).
- eSIM 통신 기본정보: https://faq.japan-travel.jnto.go.jp/en/plan/wifi-and-connectivity/
- 운영시간·개별 요금·체험 가능 여부는 확인되지 않은 경우 추정하여 기재하지 않음.

## 사진과 도식
- 기존 공통 `/images/hokkaido.jpg`를 눈축제 9편에서 행사장 실제 촬영 실사로 교체. 출처: [2014년 삿포로 눈축제 t-konno 촬영본](https://commons.wikimedia.org/wiki/File:%E7%AC%AC65%E5%9B%9E%E3%81%95%E3%81%A3%E3%81%BD%E3%82%8D%E9%9B%AA%E3%81%BE%E3%81%A4%E3%82%8A%EF%BC%88SAPPORO_SNOW_FESTIVAL_65th%EF%BC%89_-_panoramio_(1).jpg) · 2014-02-05 · CC BY-SA 3.0. WebP 변환·크기 변경, 촬영자·원본·라이선스·연도 표기.
- 사진을 **2027년 현장 사진으로 표시하지 않음**. 동일한 검증 사진을 임시로 9편에 사용하므로 후속으로 각 글에 맞는 사진을 확보하면 개별 교체할 수 있다.
- eSIM 계열 6편은 `esim.jpg`·`city.jpg`를 주제에 맞춘 QR·SIM·Wi-Fi·데이터 사용량 정보 도식으로 대체. **실사라는 주장을 하지 않음**.
- 사진을 검증하지 않고 특정 기항지·호텔·셔틀 운영 사진으로 오인 표시하는 변경은 수행하지 않음.

## 공통 다음단계 링크 253곳
- `build.js`의 공유 변환기 `scripts/v143_contextual_related.cjs`가 실제 관련 게시글에 있던 링크만 사용하여 253개 원본의 NEXT QUESTION 등 공통 연결을 **한국어 다음 단계 카드**로 변경.
- 허구 URL 생성 없음. 빌드에서 대상 경로가 실제로 존재하는지 확인; 원본 title·meta description·canonical 완전 동일 여부 검사.
- 전체 빌드 1,276HTML 기준 253/253 변환 · 영문 공통 연결 잔존 0 · 오류 0건.
- 2026-10-23 GitHub Actions: https://github.com/mouk30/japan/actions/runs/39939270580

## 전체 사이트 감사
- 원본 **1,277개 HTML** 정적 검사. 배포 산출물은 기존 빌드 규칙상 1,276개.
- 추가 검사 대상: `/images/ferry.jpg` 40편, `/images/city.jpg` 35편, `/images/couple.jpg` 29편, `/images/hokkaido.jpg` 20편 등.
- 다른 시즌 일반문구 24개, 실전 일반문구 27개 계속 확인 필요.
- **중요:** 위 숫자는 반복 또는 원본 미확인 후보 수, 잘못된 촬영지·저작권 위반 확정 수가 아님.
- 전체 원본자료: [sitewide-content-and-image-audit.json](./sitewide-content-and-image-audit.json)

## 검수 범위
- 보강 원본 15편 소스의 SEO title·description·canonical 유지, 기존 내부링크 유효성 검사, 원본 사진 파일 SHA-256 확인, 전체 빌드와 공통 헤더 정상 확인 완료.
- 공개 브라우저 390px·1440px 상세 검수는 별도 workflow [V143 production QA](https://github.com/mouk30/japan/actions/workflows/v143-public-depth-qa.yml)에서 관리. **통과 결과 전까지 모두 성공이라 기재하지 않음.**
- 기존 URL·예약 링크·본문 외 구조 유지, 신규 글/키즈관/GA4 변경 0.

## 다음 우선순위
1. 영상처럼 제목 대비 설명이 부족한 계절·생활 콘텐츠 24편+27편을 개별 주제로 선별해 보강.
2. 공통 `ferry.jpg`·`city.jpg`·`couple.jpg` 사용 페이지에서 **사진-시설-본문-촬영 장소 및 라이선스** 1편씩 원문 대조.
3. 신규 게시글 증산보다 실제 방문자에게 유용한 세부시설·가는 법·현장 운영 조건·예약/귀선 정보 우선.
