# NIPPONFERRY V87 — 4 Busan–Japan ferry routes: official schedule, surcharge and booking-condition audit

Audit date: **2026-10-21** (KST). Source of truth: official operator pages and dated notices, *not* third-party travel aggregators.

## Final QA

**PASS: 24/24 live production browser page/viewport checks; zero detected errors.**

- CI: https://github.com/mouk30/japan/actions/runs/39551210452
- CI artifact: `v87-official-ferry-routes-24-screenshots` (24 production screenshots + machine-readable `report.json`).
- Desktop **1440 × 900** and small-mobile **360 × 780** for each of 12 existing pages.
- Browser checked HTML/canonical identity, one V87 verification panel per page, four facts, warnings, at least three external official source links, relevant revised surcharge, no old July surcharge copy and no horizontal overflow.
- This tests publication and client presentation. It does **not** test live inventory, complete a purchase, or verify external booking availability on any future date.

## In-place edits; **no new editorial pages**

Four core route articles and eight existing price/schedule guides updated:

| Core route | Price guide | Schedule guide |
|---|---|---|
| `/guide/busan-osaka-ferry/` | `/guide/busan-osaka-ferry-price/` | `/guide/busan-osaka-timetable/` |
| `/guide/busan-fukuoka-ferry/` | `/guide/busan-fukuoka-ferry-price/` | `/guide/busan-fukuoka-timetable/` |
| `/guide/busan-shimonoseki-ferry/` | `/guide/busan-shimonoseki-ferry-price/` | `/guide/busan-shimonoseki-timetable/` |
| `/guide/busan-tsushima-ferry/` | `/guide/busan-tsushima-ferry-price/` | `/guide/busan-tsushima-timetable/` |

Existing URL paths, title tags, canonical tags, the booking journey from V86, and the 45 companion guides remain untouched. One *CSS resource*, one QA script and its workflow were added; no HTML article was created.

## Evidence-backed corrections

### 1) Osaka — PanStar Cruise
- **Correction**: previous text described **₩29,000** July surcharge as if current; the operator's Aug 31 notice changes this to **₩25,000 Busan→Osaka**, **¥2,500 Osaka→Busan**, applicable to sailings on or after **Sep 1, 2026**.
- The posted *basic* schedule gives **Busan Sunday 15:00**; **Tue/Thu 16:00**, with stated ticket issue and check-in windows (Sunday ticketing 13:00–14:15, Tue/Thu 14:00–15:00). Osaka→Busan Mon/Wed/Fri 17:00. Day-specific deviations override this guide.
- Operator confirmed a date-scoped Osaka departure exception on **Oct 14, 2026**, illustrating why no date-specific departure is guaranteed.
- Sources: https://www.panstarcruise.com/product/osaka/info ; https://www.panstarcruise.com/support/notice/294 ; https://www.panstarcruise.com/support/notice/305

### 2) Fukuoka — New Camellia / Korea Ferry
- Official **Oct–Dec 2026** TAX notice graphic gives Busan-departure **₩14,000 fuel surcharge** and **₩21,000 adult total departure TAX** (fuel surcharge + departure levy + terminal), exclusive of base passenger fare.
- The TAX is assessed at ticketing, not sailing date, paid in advance alongside the fare; posted upward/downward changes do not automatically generate later price adjustments.
- Fare revisions apply to reservations made on or after **Oct 1, 2026**. Former general return and student discounts ended Sep 30, 2026. Avoid relying on archived 2023 price/discount guide; time-limited online specials are separate.
- Travel-time **illustration only**: the operator's vehicle passage guide lists Busan 22:30→Hakata next day 07:30 and Hakata 12:30→Busan 18:30, but a vehicle-specific guide is *not* proof of any individual passenger departure; text prominently says to verify day-specific passenger schedules.
- Sources: https://koreaferry.kr/eng/bbs/board.php?bo_table=ferry_notice&wr_id=39 ; https://koreaferry.kr/eng/bbs/board.php?bo_table=ferry_notice&wr_id=40 ; https://koreaferry.kr/bbs/content.php?co_id=car

### 3) Shimonoseki — Kampu Ferry / Pukwan Ferry
- Standard timetable: **Busan 21:00 → Shimonoseki next morning 07:45**, **Shimonoseki 19:45 → Busan next morning 08:00**.
- Operator's Korean timetable provides Busan passenger check-in **14:30–17:30**, Shimonoseki **15:00–18:00**.
- Official Korean fare table **as viewed on Oct 21** lists Busan-departure fuel surcharge **₩19,000**, Shimonoseki-departure **¥1,900**. Effective date not stated alongside this dynamically served tariff; do not claim a future fixed price.
- Japanese-side online booking instructions say 2 months before travel starting 09:00 through previous-day 13:00, **but not assumed to govern Korean-side sales**. Shimonoseki departure fees/levies are marked cash-pay by the operator.
- Sources: https://www.kampuferry.co.jp/lang_kor/passenger_info/schedule/ ; https://www.kampuferry.co.jp/lang_kor/fare/basic/ ; https://www.kampuferry.co.jp/lang_kor/reserve/ ; https://www.kampuferry.co.jp/lang_kor/passenger_info/t_access/checkin.html

### 4) Tsushima — PanStar Tsushima Link
- **Correction**: obsolete July fuel surcharges **₩16,000 Hitakatsu/₩27,000 Izuhara** were replaced with **₩15,000/₩25,000** per official **Sep 1, 2026** effective-date notice. Return directions are respectively **¥1,500/¥2,500**.
- Official *base schedule*, subject to changes, shows Busan→Hitakatsu 08:40→09:50, Hitakatsu→Busan 17:10→18:20 and Monday Busan via Hitakatsu→Izuhara 08:40→11:20. All times local.
- **Urgent date-scoped notice**: **October 20–21, 2026 ALL Tsushima Link sailings cancelled** due to detailed vessel inspection and repair, per the notice dated Oct 19. **Do not infer** an assured resumption on Oct 22 or any other future date.
- Required reservation details include English name, DOB, passport number, contact info/address; sales window subject to change.
- Sources: https://www.panstarcruise.com/product/daemado/info ; https://www.panstarcruise.com/support/notice/292 ; https://www.panstarcruise.com/support/notice/307 ; https://www.panstarcruise.com/support/notice

## Trust / maintenance rules

- Clearly distinguish *base timetable* versus confirmed sailings, *base fare* versus fuel surcharge and TAX, and *Japan-side* versus *Korea-side* booking rules.
- Record applicable dates for all price change notices.
- Cite official operators with directly clickable source URLs.
- Do not assert confirmed departures, sold seat availability, guaranteed fares or refund conditions beyond an operator's current published terms.
- The next editorial check should repeat the official-site comparison rather than copying unverified historical travel numbers.
