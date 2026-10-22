# V131 — 핵심 크루즈 기항지 5편 운영정보·귀선·공식 예약조건 심화 검수

**검토일 2026-10-22 · 기존 상세페이지 수정 5편 · 신규 게시글 0 · 키즈관 게시 0**

## 검수 규칙
- 선박 이름·기항 날짜·승선 마감·지정 선석이 없는 경우 **항차별 마지막 셔틀·버스 시간은 산출하거나 확정하지 않음**.
- '공식 항만·기항 예약시스템'과 승객용 유료 크루즈 예약·관광시설 전자티켓은 다른 것.
- 공식 링크의 200 접속만으로 입장권·항공/선박 좌석·귀선 셔틀·취소·환불 가능 조건 확정하지 않음.
- 기존 `title`, `meta description`, `canonical`, `H1`, 기존 JSON-LD 콘텐츠 보호. 별도 V131 4단계 공식자료 안내만 기존 글에 추가.
- 기존 오래된 'AI 생성 사진' 문구(실제 사진 전환 뒤 남아 있던 나하·하카타 2편)를 실제 촬영 장소 설명으로 바로잡음.

## 기항지별 판정표

| 기항지 | 접안 위치·현장 동선 | 셔틀 / 대중교통 | 마지막 귀선 차량 | 예약조건·입장규정 |
|---|---|---|---|---|
| [나하](https://www.nipponferry.com/things-to-do/naha-cruise-terminal-kokusai-dori/) | 항만관리조합이 도마리 8호와 신항 12호 구분 | 신항 12호 외부 항만도로는 차량 동선 사용 유의, 특정 셔틀 운행 불확정 | **선박/날짜별 미확인** | [나하항 기항 예정정보](https://nahaport.jp/users/kyakusen/)는 여객 관광·선박 티켓 예약 아님 |
| [이시가키](https://www.nipponferry.com/things-to-do/ishigaki-cruise-kabira-bay-bus-taxi/) | 신항 크루즈 안벽은 유그레나 리토터미널과 구별 | 무료 셔틀은 일부 선박, 유료도 비정기·택시 대기 보장 안 함. 도심 9·11번 가비라공원앞 경유 | **귀환 방향 시간표·항차별 미확인** | NACRU 기항 예약 정보는 승객 입장·크루즈 티켓 예매 아님 |
| [하카타](https://www.nipponferry.com/things-to-do/hakata-port-hakata-station-access/) | 국제터미널 14-1 vs 중앙부두 크루즈센터 24-25 | 하카타역 88번/BRT→국제터미널, 크루즈센터 도보 약 500m | **요일별 버스·선사 귀선 마감 미확인** | 중앙부두 제한구역 여권·승선권 확인. 관광버스 진입 신청은 사업자 절차 |
| [나가사키](https://www.nipponferry.com/things-to-do/nagasaki-matsugae-glover-garden-cruise-access/) | 마쓰가에 7-16 vs 데지마 부두 구분 | 마쓰가에→오우라카이간도리 전차 정류장 도보 약 3분, 셔틀 별도 미확인 | **전차 귀환·항차별 마감 미확인** | 글로버정원 [2026년 공식 요금·개원시간](https://glover-garden.jp/guide/): 일반 1,300엔, 초·중·고 650엔. 실제 입장시간·웹티켓 조건 별도 검증 |
| [요코하마](https://www.nipponferry.com/things-to-do/yokohama-red-brick-warehouse/) | 오산바시·다이코쿠·신코 3개 터미널 | 오산바시/신코는 역에서 도보, 다이코쿠는 차량 이동 전제 | **다이코쿠 특히 예약 차량·선사 귀선편 필요, 시간 미확인** | 터미널 소개는 여객 예약화면 아님. 관광 체험 예약은 해당 운영사 별도 확인 |

## 접속이 불확실했던 원본 2개: 삭제·임의 대체하지 않음
1. [아즈마버스 공식 9·11번 노선 페이지](https://www.azumabus.co.jp/localbus/) — 공공 검색 결과에서 운영사의 노선 정보 확인. 이전 GitHub 서버에서 `URLError`, 다른 직접 검색 접근에서 `502` 가능: **실제 링크 삭제/404로 단정할 수 없음**. 기존 링크 그대로 유지, [운영사 공식 홈](https://www.azumabus.co.jp/) 병기. 실제 가비라→시내 마지막 편은 여행 날짜의 **반대 방향 시간표** 확인.
2. [나가사키 공식 관광 영문 마쓰가에 터미널 페이지](https://www.discover-nagasaki.com/en/transit/100790) — 이전 GitHub 체크 시 `503`이었지만 동일 관광공식 사이트 영문/한국어의 터미널 정보가 공공 검색 결과에 존재. 기존 영문 그대로 유지하고 [공식 한국어 페이지](https://www.discover-nagasaki.com/ko/transit/100790) 추가. 교통은 독립된 [마쓰가에 공식 터미널 접근 안내](https://nagasaki-p.com/access/)도 병기.

## 추가로 대조한 공식 자료
- [나하항 크루즈 부두·선석](https://nahaport.jp/users/kyakusen/), [제2크루즈 부두 안전·교통 FAQ](https://nahaport.jp/sp/faq/cat%3A%E9%82%A3%E8%A6%87%E3%82%AF%E3%83%AB%E3%83%BC%E3%82%BA%E3%82%BF%E3%83%BC%E3%83%9F%E3%83%8A%E3%83%AB%E3%81%AB%E3%81%A4%E3%81%84%E3%81%A6/)
- [이시가키시 크루즈선 입항·셔틀·현장 픽업 안내](https://www.city.ishigaki.okinawa.jp/soshiki/kowan/kuruzusenn/370.html)
- [하카타 크루즈센터 공식 안내](https://hakataport.com/center/) 및 [접근교통](https://hakataport.com/access/)
- [나가사키 마쓰가에 선석·데지마 정보](https://nagasaki-p.com/cruise/) 및 [마쓰가에 접근 안내](https://nagasaki-p.com/access/)
- [나가사키 글로버정원 2026 공식 이용안내](https://glover-garden.jp/guide/)
- [요코하마시 3개 크루즈 터미널 공식 안내](https://www.city.yokohama.lg.jp/lang/overseas/port/cruise/terminal_info.html)

## 게시/소스 검수 증빙
- [V131 기존 5편 개별 HTML 정적 감사 및 PC/모바일 공개 브라우저 검사](https://github.com/mouk30/japan/actions/runs/39793584724)
- [V131 기항지별 공식·미확정 항목 기계판독 상태표](./official-operating-status.json)
- [V131 QA 실행 스크립트](../../scripts/v131_five_ports_official_qa.py)
- [키즈관은 기획만 보관, 미게시](../kids-hub-concept-2026-10-22.md)

**추가 작업은 선박명·기항일·선석·승선 마감 확인 후에만** 실제 마지막 귀선차량/셔틀 시각 확정 또는 상품 예약 가능성 검증으로 들어가야 함.
