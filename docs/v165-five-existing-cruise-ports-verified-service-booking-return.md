# NIPPONFERRY V165 — 기항지 기존 5편 최신 운항/실예약/귀선 정보 (2026-10-24)

## 변경 정책
- 신규 기항지·게시글 **0개**, 기존 `site/things-to-do/.../index.html` 5편 수정.
- 원본 이미지 5장·사진촬영지·ALT·Wikimedia/CC·메타/제목/H1/canonical·기존 링크·URL·sitemap 보존.
- 새 카드 3개: (1) 운영기관 시각이 표시된 실제 운항·접안 공지 (2) 사업자별 실예약/매표·취소 경로 (3) 섬 왕복과 외항 크루즈 승객 최종 귀선 구분.
- 모바일 1열, 52px 이상 명확한 CTA. 정기선 결항과 국제 크루즈 자체 취소는 별도로 표시.

## 운영기관에서 확인한 실제 사실

| 기존 페이지 | 2026-10-24 확인 운영 사실 | 예약 및 돌아올 항구 주의 |
|---|---|---|
| `/things-to-do/goto-fukue-cruise-port-day-trip/` | 고토여객선 **10/24 15:20 갱신**: OCEAN 나루 06:35→후쿠에 07:20 첫편 운항, 대부분 결항이나 **후쿠에 17:15→나루 18:00 최종편은 정상 운항으로 변경 확정**. TAIYO 10/24 전편 결항, 10/25·26은 OCEAN/TAIYO 모두 전편 결항. https://goto-ryokyakusen.com/ | 최초 10/23 16:30 공지에서 막편 '미정'이었던 정보는 10/24 15:20의 운영사 최신 정정이 우선. 실제 왕복 정기선 확보 전 외딴섬 관광 금지. 다른 회사 규슈상선 온라인 승선권 https://kyusho.co.jp/reserve 는 고토여객선 TAIYO 예약페이지가 아님. 고토여객선 후쿠에 영업소 0959-72-8151 |
| `/things-to-do/aokata-cruise-port-day-trip/` | 고토여객선 TAIYO 10/25~11/23 **일·월 휴항 연장**, 10/25·26, 11/1·2·15·16·22·23 적용. **11/8·9은 도크 대체선(프로바5·오션라이너8)으로 별도 시간 운항**. 원문 https://goto-ryokyakusen.com/10%E6%9C%8825%E6%97%A5%E4%BB%A5%E9%99%8D%E3%81%AE%E9%AB%98%E9%80%9F%E8%88%B9taiyo%E3%81%AE%E9%81%8B%E8%88%AA%E3%81%AB%E3%81%A4%E3%81%8D%E3%81%BE%E3%81%97%E3%81%A6/ | 노모상선 다이코 하카타–아오카타–후쿠에 항로는 별도 https://www.nomo.co.jp/taiko/news/status.html . 고토여객선 TAIYO ≠ 고토산업기선 다이노우라 정기선 ≠ 아오카타 크루즈 접안 선석 |
| `/things-to-do/sasebo-cruise-port-day-trip/` | 규슈상선 2026-10-24 14:28 공지에서 **10/25 사세보 12:05·15:50 고속선 결항 예정**. 다른 고속선/카페리와 구분 https://kyusho.co.jp/status | 정식 예약·구입 https://kyusho.co.jp/reserve . 고속선 온라인 예약 2개월 전~출항 1시간 전, 출항 30분 전까지 발권/결제. 규슈상선 무료 셔틀 https://kyusho.co.jp/shuttle 은 **나가사키–나라오 제트포일 연계 승객 전용**, 사세보 국제크루즈 무료 셔틀이 아님. 사세보 우라가시라/요코우 실제 승객 게이트를 선내 공지로 확인 |
| `/things-to-do/hakata-cruise-port-day-trip/` | 후쿠오카시 **10/21 갱신 선석 예약**: 10/24 LUMINARA 08:30~21:00 중앙부두 **5호**, 11/3 LUMINARA 09:00~21:00 하코자키 **5호**, 11/3 아스카Ⅱ 07:30~17:00 중앙 **5호**. https://www.city.fukuoka.lg.jp/kowan/k-kikaku/hakata-port/cruise1.html | 도시의 **선석 예약 예정표**는 당일 실제 접안·승객 게이트 또는 탑승 마감이 아님. 날짜가 다르면 부두가 바뀌어 택시 픽업과 마지막 차량 동선 달라짐. 하카타 크루즈센터 https://hakataport.com/Access/ 로 일반 접근 확인하되 하코자키로 귀선하는 승객에게 동일한 위치를 안내하지 않음 |
| `/things-to-do/yakushima-miyanoura-cruise-port-day-trip/` | 가쇼카이운 페리 하이비스커스 **2026-10-05~11-15 (42일) 도크 운휴** https://www.yakushimaferry.com/2026/08/24/post-163/ . 부겐빌레아 대체선의 날짜별 일정·10/23 결항은 운영사 운항현황 https://www.yakushimaferry.com/flight_status/ | 부겐빌레아가 매일 운항하거나 표가 확보됐다는 뜻이 아님. 다른 회사 오리타기선의 '페리 야쿠시마2' 10/24·26 결항 및 10/25 정기 운휴와 분리. 야쿠시마 크루즈 접안정보 https://www.mlit.go.jp/kankocho/cruise/detail/072/index.html 확인 |

## 검수
- `scripts/qa_v165_five_original_port_bookings.py` / `.github/workflows/v165-five-verified-ports.yml`: pre-V165 HEAD `316790832f238929e628b25fff90ca28e37f1c8b`와 5개 원본의 이미지·라이선스·기존 앵커/메타/canonical/H1/사이트맵 일치 비교, 3개 실제 공식 CTA 및 위험고지 확인, `node build.js` 실행.
- `scripts/qa_v165_public_five_ports.py` / `.github/workflows/v165-public-five-ports.yml`: **공개 사이트**의 상세페이지 5개·원본 WebP 5장·사이트맵 = **11개 HTTP 항목** 점검.
- Vercel이 성공했다고 해도 그 시점의 다른 후속 커밋 배포는 별개일 수 있음. 최신 공개 HTTP 검수 완료 상태를 우선 확인해 결과를 보고할 것.
- **미검증**: 유료 승선권 실재고, 결제 성공·취소 환불 입금, 승객별 선사 최종 귀선시간, 크루즈 선사 셔틀 배차, GA4/GSC 검색 및 예약 전환. 실운항/잔여석은 여행 당일 사업자 원문 재조회 필요.
