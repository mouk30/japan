# NIPPONFERRY V89 — Booking-trust verification date and official source integrity

**Completed: 2026-10-21 KST. No new publicly indexed content articles.**

## Release status

- **PASS, 24/24 real production browser layouts**, official link checks and time-aging behavior on 12 existing ferry guides.
- Main QA: https://github.com/mouk30/japan/actions/runs/39554506996
- QA artifact: `v89-ferry-review-date-24-screens` (24 visual captures and `report.json`).
- **PASS, source monitor regression workflow**, including image byte integrity check: https://github.com/mouk30/japan/actions/runs/39554730791
- Source integrity artifact: `v88-official-notice-and-stale-fare-report`.
- Monitoring latest report status: `clean`, no unreviewed notices, no tracked stale-price matches, no missing sources; Kampu surcharge row confirmed at 19,000 KRW and 1,900 JPY. Korea Ferry quarterly TAX image was reachable and SHA-256 was recorded.

## Public trust label (12 in-place pages)

The existing V87 official-reference panel now displays a clearly attributed and **immutable** editorial cross-check date (2026-10-21), plus a direct route-appropriate operator website link. The displayed date never updates merely because someone visits the page or the automated watcher runs.

| Route | Direct provider destination | Existing page group |
|---|---|---|
| Osaka | [PanStar notices](https://www.panstarcruise.com/support/notice) | guide, fare, timetable |
| Fukuoka | [Korea Ferry official notices](https://koreaferry.kr/eng/bbs/board.php?bo_table=ferry_notice) | guide, fare, timetable |
| Shimonoseki | [Kampu official fare](https://www.kampuferry.co.jp/lang_kor/fare/basic/) | guide, fare, timetable |
| Tsushima | [PanStar notices](https://www.panstarcruise.com/support/notice) | guide, fare, timetable |

Behavior:
- Last verification less than 21 days: prominently disclose that the date is an editorial review date and **not proof of live bookability**.
- From 21 days: display a warning to re-check the current sailing/fare before booking.
- From 45 days: display **re-verification required** status, rather than automatically pretending old values are current.
- Accessible high-contrast call to action, at least 48 px tap target (54 px in narrow mobile), `noopener noreferrer` for external destinations.

Only the twelve existing HTML files, plus `site/nf-v89-verified-date.css` and `site/nf-v89-verified-date.js`, were deployed; pre-existing canonical URLs, titles, V86 booking paths, and family/parent/couple 45 guides remain.

## Automated regression QA

`scripts/v89_date_ribbon_browser_qa.py` checks in a real browser:
- 1440×900 desktop and 360×780 phone, each for 12 production pages (24 combinations).
- One cross-check label and exactly one source link per verified panel.
- The original four V87 factual fields and original canonical link remain.
- Official route URLs and safe external tab behavior.
- Horizontal overflow and button dimensions.
- Synthetic browser clock: 2026-10-22 → ordinary caution, 2026-11-12 → `review`, 2026-12-10 → `overdue`. Synthetic time does not edit the real review date.

## V88 official notice watcher hardened

V88 already monitors new notices, reported tariffs and older published fee copy at **approximately 10:13 and 22:13 KST**, subject to GitHub Actions queueing. V89 improved the underlying monitor without creating a second scheduler:

1. **Source image bytes**: for the official Fukuoka quarterly TAX notice, download up to three images directly from the provider's trusted website (maximum four megabytes per image, bounded timeouts), compute SHA-256 and compare with the *previous successful source report*. A changed binary at the **same image URL** now creates a manual review request.
2. **Security and false positives**: refuse arbitrary external image domains and redirects, distinguish failed source retrieval from an actual updated fee. A source outage is never equated with a fare increase or cancellation.
3. **Additional headline categories**: monitor luggage intake limitations, reservation acceptance, safety, delays, temporary runs and maintenance, not just surcharge/fare/cancellation keywords.
4. **Fixture test**: verifies different bytes at a constant official image URL are detectable; external third-party images are skipped.

Final V88-run evidence: `status: clean`; `review_items: 0`; `new_official_notices: 0`. Quarterly TAX image read successfully at the exact official provider URL, with SHA-256 stored in the run artifact. This is **change detection**, *not* automatic image text recognition or final fare confirmation.

## Editorial maintenance rule

Before changing any public price or marking a departure confirmed, a human must verify the operator announcement, sailing applicability date, departure direction, individual baggage/cabin conditions, and updated fees/taxes. Do not automatically revise 2026-10-21 verification dates without human source recheck. No scheduled watcher can guarantee instantaneous detection or seat availability.
