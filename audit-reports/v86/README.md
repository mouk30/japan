# NIPPONFERRY V86 — Official booking journey quality release
Date: 2026-10-21 (KST)

**Outcome: PASS — 18/18 real production browser page/viewports, 0 failures.**
Final Github Actions: https://github.com/mouk30/japan/actions/runs/39549347187
Screenshot/report archive: workflow artifact `v86-official-booking-pc-mobile` (30 PNG screenshots and report.json)

## Scope
No new editorial articles, route articles, or destination pages. Existing page metadata, article sections and 45 companion guides retained.

Modified six existing pages:
- `site/guide/busan-osaka-ferry/index.html`
- `site/guide/busan-fukuoka-ferry/index.html`
- `site/guide/busan-shimonoseki-ferry/index.html`
- `site/guide/busan-tsushima-ferry/index.html`
- `site/ferry/index.html`
- `site/booking/japan-cruise/index.html`

Added scoped CSS `site/nf-v86-booking-journey.css`, a real-production Playwright QA script, its workflow, and this QA report; **no new HTML pages**.

## Problem detected and corrected
Four Busan international route guides previously sent primary booking links to `willer-travel.com/ko/ferry/`, a list of **Japan domestic ferry products**, not a direct way to check the selected Busan-to-Japan international crossing. The ferry hub and booking hub also had potentially misleading generic buttons to the same source.

V86 replaced those generic CTA paths **within these six pages** with route-specific links to each operator. Each established guide now has three convenient booking-info entry points (above the first section, mid-article, and sidebar) with a primary operator button, a secondary official route/how-to link, a three-step preparation path, and disclosure about no availability guarantee.

## Operator links verified through official websites
| Existing article | Primary | Secondary | Trust condition |
|---|---|---|---|
| Osaka | https://www.panstarcruise.com/ | https://www.panstarcruise.com/product/osaka/info | Official PanStar search and Osaka route information |
| Fukuoka | https://www.koreaferry.co.kr/rs/idv/reservation | https://www.koreaferry.kr/ | The latter website links directly to the former as its own online-reservation service |
| Shimonoseki | https://www.kampuferry.co.jp/lang_kor/reserve/ | https://www.kampuferry.co.jp/yoyaku/en/ | Korean booking-method information and English online booking instructions by the official operator; check eligibility and actual booking conditions |
| Tsushima | https://www.panstarcruise.com/ | https://www.panstarcruise.com/product/daemado/info | PanStar's Tsushima Link page explains Hitakatsu vs Izuhara and weather-related changes |

**No** claim is made about live fare, bookable inventory, confirmed operation, specific sailing availability or purchase completion. All official links are marked as external and open with `rel="noopener noreferrer"`. NIPPONFERRY is an editorial travel information service, not the operator.

## Verified browser conditions
Three viewport sizes for all six target pages:
- PC: 1440 × 900
- Mobile: 390 × 844
- Small mobile: 360 × 780

Checked:
- Each existing guide has top, mid, sidebar panels, 3 correct CTA pairs, readable warning and its canonical.
- Exact route-operator primary and secondary URLs match in the DOM; browser links open a new tab safely.
- No outdated Japan-domestic booking destination remains in these six source pages.
- Footer article `#ferry` anchor and return route hub link preserved.
- Four existing panoramic route banners remain.
- Both existing hubs have the four correct deep links to `/#nf86-official-entry` sections.
- Booking-choice buttons are accessible within viewport, sufficient size, and no horizontal scrolling.
- Browser screenshots inspected manually. The persistent Kakao bubble initially obscured the fourth mobile route button. **Fix: mobile booking hub reserves 76px right-side space for floating Kakao UI.** The QA was strengthened with geometry-based float-to-link collision testing; final run passed.

## Future validation boundary
The browser QA checks exact rendered link targets, layout and same-site destination pages. It does **not** submit a booking, prove the external reservation process can be completed, guarantee availability for any date, or audit every unrelated page across the website.
