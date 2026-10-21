# NIPPONFERRY V91 — Three-item booking preflight and one-click operator access

**Released:** 2026-10-21 KST. **No new public HTML pages or editorial articles.**

## Verified result

- **18 / 18 production browser page/viewport cases passed**, no errors.
- **16 / 16 actual one-click browser popup attempts reached the expected official operator domain** (4 routes × 2 existing hub pages × 2 click-tested viewport sizes).
- 18 real screenshots: 12 existing article preflight panels and 6 existing hub panels across desktop, mobile and small mobile.
- Exact run: https://github.com/mouk30/japan/actions/runs/39572500835
- Existing V86 official CTA regression: https://github.com/mouk30/japan/actions/runs/39572470188 (pass).
- Existing V85 ferry banner responsive regression: https://github.com/mouk30/japan/actions/runs/39572460694 (pass).

## Scope — zero new indexed articles

Updated in place:
- `site/guide/busan-osaka-ferry/index.html`
- `site/guide/busan-fukuoka-ferry/index.html`
- `site/guide/busan-shimonoseki-ferry/index.html`
- `site/guide/busan-tsushima-ferry/index.html`
- `site/ferry/index.html`
- `site/booking/japan-cruise/index.html`

Added shared scoped CSS `site/nf-v91-direct-booking.css`, QA script `scripts/v91_one_click_booking_qa.py`, and QA workflow `.github/workflows/v91-direct-booking-qa.yml`. Existing SEO titles, `canonical`, IDs, structured data, the 45 family/parent/couple guides, photography and prior V90 official booking targets are unchanged.

## Existing four route articles

Replaced generic “route/date/amount” step tiles with **three route-specific, short booking checks** directly before established official booking CTAs. Mid-article checklists were likewise contextualized.

| Route | Three succinct preflight checks |
|---|---|
| Osaka | Different local dates for overnight departure/arrival; cabin and check-in deadline; complete roundtrip fee including surcharge and cancellation |
| Fukuoka | Busan/Hakata sailing day and return; passenger count/cabin/passport spelling; fare/TAX/checked luggage/changes |
| Shimonoseki | Which country and port departing; differing Japanese and Korean booking/check-in processes; fees, cash and cancellation terms |
| Tsushima | Hitakatsu vs Izuhara destination; weather/cancellation news and return-port schedule; passport, total surcharge and baggage terms |

Avoid fixed prices or inventory claims in this decision-stage checklist. All four preserved the top, mid-article and sidebar V86 official booking links.

## One-click option from two already indexed hubs

Before V91, both `/ferry/` and `/booking/japan-cruise/` primarily sent users to the route article, requiring an additional click before reaching the operator.

V91 places **four prominent one-click external provider buttons above those original route-guide deep links**. Each hub gives a clear distinction between the direct provider choice and the existing route information.

| Route | One-click destination | Clearly labeled actual step |
|---|---|---|
| Osaka | https://www.panstarcruise.com/ | Operator homepage: select Osaka route and sailing date |
| Fukuoka | https://www.koreaferry.co.kr/rs/idv/reservation/calendar_index/1/2?country=2 | Operator Korean date/passenger booking inquiry |
| Shimonoseki | https://www.kampuferry.co.jp/lang_kor/reserve/ | Korean booking-method instructions, **not** completed checkout |
| Tsushima | https://www.panstarcruise.com/ | Operator homepage: choose Tsushima/arrival port and date |

For each of four route cards, a secondary internal detail link now points to the established V87 source-verified sailing/fee panel `#nf87-verified-operations`, while the original V86 route-guide group still points to `#nf86-official-entry`. These separate purposes prevent duplicate identical anchors, and existing V85/V86 QA remains valid.

The label “one click” means **one click from an existing NIPPONFERRY hub to the operator-owned site**, not “reservation completed in one click.”

## Browser test scope

Tested **1440×900 PC**, **390×844 mobile** and **360×780 small phone**. Test checks:
- Each core route page has exactly 3 usable short preflight bullet points.
- Existing three V86 booking sections' primary links preserved and canonical unchanged.
- Each of two hubs shows four route-specific direct official links and four correct source-information return links.
- Buttons at least 44px tall, not off-screen or covered by the floating Kakao chat control on narrow screens.
- No horizontal overflow.
- External targets are `target="_blank"`, `rel="noopener noreferrer"`.
- 16 real human-equivalent link clicks from the two hubs on desktop and regular mobile open tabs on approved operator domains; no reservation forms submitted.
- Existing internal route guide links remain intact.

## Maintenance policy and verification limits

The previously deployed V90 twice-daily official booking URL monitor continues watching operator destination and redirect changes. New V91 direct links intentionally reuse the same canonical V90 URL inventory; **there are no independent unmonitored booking destinations**. Verify the operator's actual sailing, passenger count, final amount, cancellation terms and payment validity at checkout. The browser QA does not prove dates are available, fare quotes are final, or purchases can be completed.
