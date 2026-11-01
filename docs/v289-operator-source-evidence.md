# V289 operator notice evidence ledger (2026-11-02 KST)

Scope: existing booking/Osaka, Tsushima, Shimonoseki pages only. No new articles.

| Existing page | Operator primary source | Verified fact | Site treatment |
|---|---|---|---|
| /booking/osaka/ | https://www.panstarcruise.com/support/notice/273 (2026-05-06) | Sunday Busan–Osaka PanStar Miracle departure changed to 15:00 effective 2026-05-17; operator asks passengers to arrive at Busan 3F counter by 13:30 | Link to official notice, remind to verify by date |
| /booking/osaka/ | https://www.panstarcruise.com/support/notice/310 (2026-10-23) | Fuel surcharge changed for sailings from 2026-11-01 | Link to source; do not hard-code fares in evergreen text |
| /booking/osaka/ | https://www.panstarcruise.com/product/osaka/info | Boarding/check-in and return schedules differ by sailing day | Link to official table |
| /booking/tsushima/ | https://www.panstarcruise.com/support/notice/309 (2026-10-23) | Fuel surcharge change effective 2026-11-01 | Link to source |
| /booking/tsushima/ | https://www.panstarcruise.com/support/notice/285 (2026-07-14) | Historical example of Izuhara to Hitakatsu port change due to weather | General caution and current operator notice link; do NOT present past change as current |
| /booking/shimonoseki/ | https://www.kampuferry.co.jp/news/20261027systemmaintenance.html (2026-10-27) | Internet reservation system resumed | Link to source |
| /booking/shimonoseki/ | https://www.kampuferry.co.jp/news/newyear_schedule.html (2026-09-01) | Both directions suspended 2026-12-30 through 2027-01-03 | Link to source; advise return itinerary check |

## Accuracy constraints
- PanStar Osaka official **route illustration row** currently shows Sunday Busan–Osaka time 15:30, while its **boarding/check-in table** and dated 2026-05-06 notice show 15:00. Do not silently reconcile or reproduce the conflicting route-illustration time. Prefer the explicit dated change notice and reconfirm directly with operator for a booked sailing.
- Do not imply a static official page confirms seat availability or booking completion.
- The approved PanStar hero image is an illustration, not verified real vessel photography. It is especially **not** the actual vessel image for the Fukuoka (New Camellia) or Shimonoseki (Kampu/Pukwan) route pages; label it and source route-specific photography before claiming identity.
- Confirm live operator notices, boarding terminal and last return transport again for each departure date.
- GitHub PR #95 must not merge or deploy without the exact approved image file at `site/images/panstar-cruise-clean-2048.webp` passing SHA-256.
