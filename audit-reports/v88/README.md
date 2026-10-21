# NIPPONFERRY V88 — Official source change watch & stale ferry fare audit

**Prepared 2026-10-21 KST; zero new public HTML articles.**

## Delivered

- Scheduled watch: [V88 GitHub Actions](https://github.com/mouk30/japan/actions/workflows/v88-official-ferry-watch.yml).
- GitHub cron `13 1,13 * * *` in UTC: approximately **10:13 and 22:13 KST** daily (GitHub may queue jobs later). Manual `workflow_dispatch` is available.
- Scanner [scripts/v88_official_watch.py](../../scripts/v88_official_watch.py) and dated reviewed values [scripts/v88_official_baseline.json](../../scripts/v88_official_baseline.json).
- Offline regression tests [test_v88_official_watch.py](../../tests/test_v88_official_watch.py).
- Every run archives `report.json` and `summary.md` for 90 days. **Unresolved relevant changes open/update a GitHub issue, not the website.**
- Existing [V18 official-source watch](https://github.com/mouk30/japan/actions/workflows/v18-official-source-watch.yml) remains intact and distinct.

## What gets checked

1. **PanStar:** official notice list for newly published fuel/sailing/cancellation notices; older operator surcharge and dated suspension source accessibility; changes to previously reviewed notice text across successful runs.
2. **Korea Ferry (New Camellia):** official ferry-notice board, including reservation periods and luggage restrictions; edited notice titles; quarterly TAX notice access and changes in the article body or referenced TAX graphic (image source/hash changes detected, monetary value within image is **not read by OCR**); automatic review ahead of 2026-12-31 quarter expiry.
3. **Kampu Ferry:** parse the specific **fuel-surcharge row** in the current official Korean tariff, separately identifying KRW 19,000 (Busan) and JPY 1,900 (Shimonoseki) instead of mixing basic fares, taxes or other charges.
4. **Existing site:** inspect all 12 V87 canonical guides for published baseline values, old July-as-current claims and document age; scan remaining `site/**/*.html` for high-confidence prior Osaka/Tsushima surcharge statements. Flag possible mismatches for review instead of rewriting files automatically.
5. **Freshness:** after 45 days from a review date, flag the 12 guide reviews for official reconfirmation. A future quarterly TAX notice is needed before the old period expires.

## First actual findings — corrected in-place

First [V88 run](https://github.com/mouk30/japan/actions/runs/39552432135) identified **18 additional pre-existing articles** still treating the old July 2026 fuel surcharge as current. These were corrected **without creating or removing an article**:
- **8 Osaka-related pages:** old KRW 29,000 → officially effective Sep 1 KRW 25,000, with Osaka→Busan JPY 2,500 and direct operator citation.
- **10 Tsushima-related pages:** old Hitakatsu KRW 16,000 / Izuhara KRW 27,000 → Sep 1 KRW 15,000 / KRW 25,000, with directional return fees and Oct 20–21 operator cancellation notice.
- These pages retain their existing route, URL, SEO and internal-link context. Avoid treating a dated operator notice as live inventory.

The first run also discovered Korea Ferry's notice #42 and #43 (posted Oct 12). Verified the actual source text and amended **three existing Fukuoka ferry/price/timetable guides**:
- [#42 holiday checked-baggage restrictions](https://koreaferry.kr/eng/bbs/board.php?bo_table=ferry_notice&wr_id=42): some temporary services Dec 29, 2026–Jan 3, 2027 run **without accepting checked baggage**; passengers must verify their specific direction and date.
- [#43 future April reservations](https://koreaferry.kr/eng/bbs/board.php?bo_table=ferry_notice&wr_id=43): reservation openings for Apr 10–30, 2027 are expected to be **temporarily held**, subject to unfinalized dry-dock plans, **not confirmed cancellations**.
- Both reviewed IDs are acknowledged in the monitor baseline; future higher IDs and changed existing notices will trigger new review.

## QA and evidence

- Re-run [V88 source watch: clean](https://github.com/mouk30/japan/actions/runs/39553069219) after corrections: **0 suspected legacy fare copies, 0 outstanding unreviewed new notices, 0 source failures**; official Kampu live fee parsed correctly.
- Initial issue [#23](https://github.com/mouk30/japan/issues/23) documents the pre/post discrepancies, editorial changes, and successful clean re-run; closed as completed.
- Existing [V87 responsive 24-check workflow](https://github.com/mouk30/japan/actions/workflows/v87-ferry-official-qa.yml) independently checks the 12 core guides.
- [PanStar Osaka surcharge change](https://www.panstarcruise.com/support/notice/294), [Tsushima change](https://www.panstarcruise.com/support/notice/292), [Kampu official fuel table](https://www.kampuferry.co.jp/lang_kor/fare/basic/), [Korea Ferry quarterly TAX](https://koreaferry.kr/eng/bbs/board.php?bo_table=ferry_notice&wr_id=39) are the dated reviewed sources.

## Safeguards and limitations

A notice-list match, HTTP/HTML change, parsing error or a suspected stale snippet is **not** proof that today's booked sailing has been cancelled or its final charge changed. All findings must be checked for direction, date of applicability, operator, taxes, and passenger-specific booking terms before any public update. Site HTML, inventory and booking systems are **never automatically edited**, and a scheduled Actions job is not an instant real-time notice. Image-only fare tables are compared using source references; new numerical amounts require human visual source confirmation. GitHub Issues notifications depend on repository notification settings.
