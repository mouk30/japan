# NIPPONFERRY V90 — Booking destination integrity, external navigation and mobile tap QA

**Release: 2026-10-21 KST. Zero new SEO articles.**
Four existing route guides plus existing `/ferry/` wide banners were refined; the existing booking hub, all 45 companion guides, article metadata, SEO titles, canonical tags and other pages remain.

## Final production QA

| Check | Verified |
|---|---|
| Official external booking and route-guide destinations | **7 / 7 unique URLs returned HTTP 200, correct final operator domain/path and relevant provider or booking content** |
| Misleading redirects, broken HTTP 404/410, wrong operator/route page | **0 actionable flags** |
| Production page + viewport combinations | **18 / 18 passed** |
| Real new-tab clicks on existing guide CTAs | **8 / 8 opened the correct official operator domain** |
| Screenshots and QA report | **30 production PNG captures plus `report.json`** |
| Existing new editorial articles | **0** |

Official URL monitor: https://github.com/mouk30/japan/actions/runs/39569665139

Real desktop/mobile Playwright: https://github.com/mouk30/japan/actions/runs/39569545019

V86 historical booking journey regression rechecked after synchronizing the verified target inventory:
https://github.com/mouk30/japan/actions/runs/39569396069

V85 panoramic ferry hub responsive regression (after route-specific provider link updates):
https://github.com/mouk30/japan/actions/runs/39568449394

### Actual problem found and corrected

**New Camellia / Busan–Fukuoka**: The official Korea Ferry homepage links to `https://www.koreaferry.co.kr/rs/idv/reservation`, which responded with HTTP 200 but its HTML yielded **no visible booking content** in automated inspection. Consequently the URL had initially been classified `unverified` rather than valid booking content.

An operator-owned Korean reservation page was independently verified to display booking stages and search inputs: 
`https://www.koreaferry.co.kr/rs/idv/reservation/calendar_index/1/2?country=2`

This is now used by the existing article's **top, middle and sidebar primary CTA buttons**. Verification confirms its `STEP.1 공실조회`, lowest fare calendar and departure-date/passenger search UI markers. Final network and real desktop/mobile popup checks identify the correct provider. Neither the calendar nor a sample displayed promotional fare constitutes guaranteed inventory or a quote.

Source operator website: https://www.koreaferry.kr/ (links to the booking service); verified actual Korean reservation page: https://www.koreaferry.co.kr/rs/idv/reservation/calendar_index/1/2?country=2

### Route-specific link destinations

| Existing article | Primary CTA destination and intent | Secondary path |
|---|---|---|
| `/guide/busan-osaka-ferry/` | `https://www.panstarcruise.com/` — **operator-home search**, choose Osaka/date | `https://www.panstarcruise.com/product/osaka/info` — Osaka-specific sailing and check-in guidance |
| `/guide/busan-fukuoka-ferry/` | `https://www.koreaferry.co.kr/rs/idv/reservation/calendar_index/1/2?country=2` — **Korean date/passenger booking search** | `https://www.koreaferry.kr/` — operator public notices/fallback |
| `/guide/busan-shimonoseki-ferry/` | `https://www.kampuferry.co.jp/lang_kor/reserve/` — **Korean instructions, not payment** | `https://www.kampuferry.co.jp/yoyaku/en/` — Japanese-side operator English online booking instructions |
| `/guide/busan-tsushima-ferry/` | `https://www.panstarcruise.com/` — **operator-home search**, choose Tsushima and destination port | `https://www.panstarcruise.com/product/daemado/info` — Tsushima Link port guidance |

On `/ferry/`, the existing four V84 wide banner secondary links now go **directly to matching routes or Korea Ferry's Korean official page** instead of generic operator homepages. The four internal guide CTAs and all destination photography/attributions remain.

### Mobile UX and click evidence

The `scripts/v90_booking_mobile_browser_qa.py` production-browser check tested:
- desktop 1440 × 900, mobile 390 × 844, small mobile 360 × 780;
- four route guides and both existing ferry/booking hubs (18 tested page/viewports);
- top, middle and sidebar primary/secondary CTA addresses and secure `target="_blank" rel="noopener noreferrer"`;
- tap target height at least 44px, viewport overflow, unchanged canonical and official fallback CTA;
- fixed Kakao floating bubble vs. reservation CTA collision geometry on both mobile sizes;
- real new-tab clicks on primary booking destinations, verifying **operator-domain destination** on desktop and phone (eight actual clicks, no forms submitted);
- **30 actual screenshots**. Added mobile right-hand safe zone for booking explanations to prevent the floating help bubble from obscuring text.

### Automatic monitoring

- Monitor: `.github/workflows/v90-booking-links-watch.yml`, scheduled **01:27 and 13:27 UTC daily** (approximately **10:27 and 22:27 KST**, subject to GitHub queue delays) and manual dispatch.
- Source registry: `scripts/v90_booking_link_targets.json`.
- Monitor code: `scripts/v90_booking_destination_health.py`.
- Offline tests: `tests/test_v90_booking_destination_health.py` (including HTTP-200 wrong-route, malicious-domain redirects, 404/410, provider identity, Korean calendar body, 403/429 uncertainty, and existing CTA safety).
- Report in each run: `audit-reports/v90/current/report.json` and `summary.md`, saved as GitHub Actions artifact for 90 days.

**Review issue is created for:** an existing onsite booking button pointing at the wrong provider URL, route-specific link changed to an unrelated path or homepage, unexpected redirected domain, genuine 404/410, or substantial HTTP 200 webpage content from the wrong operator/route.

**No broken-link claim for:** bot defense (403/429), temporary server outages, short JS-only blank responses or account-login gates. These are classified `unverified` in the report. A correct HTTP response or domain still does **not** prove a user can complete a purchase.

This monitor is strictly read-only: it never enters dates, changes cabins, makes reservations, alters prices, or automatically swaps publicly visible links. An operator site change must be checked before editorial deployment.

## Scope and future verification

Confirmed: **correct currently accessible provider pages and booking calendar intent; desktop/mobile popups opening the approved operator domains**.

Not established: login/payment success, any particular sailing's departure confirmation, seat inventory, discounts applying on a chosen date, final passenger fare, or guaranteed reachability from every customer network/device.
