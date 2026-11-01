# V290 — Existing Busan departure booking CTA integrity (2026-11-02 KST)

## Finding and correction
Four existing route-specific booking pages had **three primary/footer CTAs each** pointing to the same generic Japanese domestic-ferry marketplace: https://willer-travel.com/ko/ferry/ . That marketplace explicitly presents Japanese **domestic** ferry routes; it is not evidence that Busan–Japan international tickets are sold there. Do not label it a route-specific Busan booking destination.

Only these **12 existing CTA links** were changed. Canonicals, article URLs, existing headings, internal guide links and the approved-artwork reference were retained.

| Existing page | Operator | New operator destination | CTA wording |
|---|---|---|---|
| /booking/fukuoka/ | Korea Ferry (New Camellia) | https://www.koreaferry.kr/ | 고려훼리 공식 예약 안내 |
| /booking/osaka/ | PanStar (Osaka) | https://www.panstarcruise.com/ | 팬스타 공식 날짜·항로 검색 |
| /booking/shimonoseki/ | Kampu Ferry / Pukwan | https://www.kampuferry.co.jp/reserve/ | 관부훼리 공식 예약방법 확인 |
| /booking/tsushima/ | PanStar Tsushima Link | https://www.panstarcruise.com/ | 팬스타 대마도 공식 날짜 검색 |

## Sources checked on 2026-11-02
- WILLER marketplace: https://willer-travel.com/ko/ferry/ — describes domestic Japanese ferry reservations.
- Korea Ferry: https://koreaferry.kr/ — operator site, New Camellia Busan–Fukuoka and reservation navigation.
- PanStar: https://panstarcruise.com/ — operator home has origin/destination/date search; Osaka: https://www.panstarcruise.com/product/osaka/info ; Tsushima: https://www.panstarcruise.com/product/daemado/info .
- Kampu: https://www.kampuferry.co.jp/reserve/ — official booking method, internet reservation and conditions.

## Safety and limitations
- Operator homepages and method pages are **not** a claim of a specific sailing being bookable, nor a completed booking.
- Keep Japanese domestic ferry marketplace links in *relevant domestic-ferry articles* if their routes have been verified; do not silently repurpose international CTAs.
- PanStar hero is an illustration, not verified route-specific vessel photography. **V287/V288 remain blocked** until the user-approved exact image is committed at `site/images/panstar-cruise-clean-2048.webp` and both SHA/decode and visual checks pass.
- No new pages. No PR merge or production deployment.
