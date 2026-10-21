# NIPPONFERRY V85 — Panoramic ferry route banner quality audit

Date: 2026-10-21 (KST). Scope: existing `/` and `/ferry/` only. **No new editorial articles.**

## Result

**PASS — 10/10 browser viewports; 0 QA errors and 0 warnings.**

- Production browser URL: https://www.nipponferry.com/
- Route gallery: https://www.nipponferry.com/ferry/#recommended-ferry-routes
- Latest production Playwright run: https://github.com/mouk30/japan/actions/runs/39547491143
- Artifact (run's Artifacts section): `v85-sea-routes-pc-mobile` (10 screenshots + `report.json`)
- Viewports: 1440×900, 1024×768, 768×1024, 390×844, 360×780, each checked on both homepage and ferry hub.

## What was actually measured

- Both destination sections appear on real production pages.
- Four route banners and four correct existing article URLs were present.
- All four image elements loaded (nonzero naturalWidth); production stylesheet reachable.
- Existing internal target URLs responded with non-error HTTP status.
- No horizontal document overflow, credit/button visual overlap, missing banner, too-small CTA, or off-viewport button.
- Final horizontal credit↔CTA separation on desktop/laptop/tablet and mobile was positive across all four routes.
- Mobile image credit font increased **11px → 13px**; additional banner height, bottom spacing, and room for fixed floating Kakao button on the homepage.

## Actual issues found and fixed

1. Osaka route and homepage imagery previously lacked attributable provenance (and homepage depiction did not accurately communicate Osaka Dotonbori).
   - Replaced only V84 banner image references with `/images/venues/nf-v85-osaka-dotonbori-licensed.webp`.
   - Verified source: [Kristoffer Trolle, Dōtonbori at night, Osaka](https://commons.wikimedia.org/wiki/File:D%C5%8Dtonbori_at_night%2C_Osaka_%2819551420339%29.jpg), photo dated 2015-06-30, **CC BY 2.0**; WebP resizing indicated.
   - Cryptographic original/output digests and license URL: [source manifest](../../site/images/venues/nf-v85-osaka-dotonbori-licensed.source.json).
   - Existing old sitewide image `osaka-dotonbori.webp` was not globally altered.
2. Full-width desktop/laptop/tablet credit captions were found to overlap the action links when the stronger button-overlap test was enabled. This was corrected by reserving bottom space inside the panoramic banner.
3. Increased mobile credit font to 13px and card minimum height to 585px. Reserved mobile home-caption right padding so floating chat UI does not obscure attribution.

## Four source citations

| Existing route guide | V85 banner image subject | Source / license |
|---|---|---|
| `/guide/busan-osaka-ferry/` | Osaka Dotonbori, 2015 | [Original](https://commons.wikimedia.org/wiki/File:D%C5%8Dtonbori_at_night%2C_Osaka_%2819551420339%29.jpg) · [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/) |
| `/guide/busan-fukuoka-ferry/` | Fukuoka Ohori Park, 2026 | [Original](https://commons.wikimedia.org/wiki/File:%C5%8Chori_Park_The_view_NNE_from_Ukimid%C5%8D_%C5%8Chorik%C5%8Den_Ch%C5%AB%C5%8D-ku_Fukuoka_20260609_154008.jpg) · [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| `/guide/busan-shimonoseki-ferry/` | Shimonoseki Karato Market, 2023 | [Original](https://commons.wikimedia.org/wiki/File:Karato_Fish_Market,_Shimonoseki_-_Jun_24,_2023.jpg) · [CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/) |
| `/guide/busan-tsushima-ferry/` | Tsushima Izuhara terminal, 2017 | [Original](https://commons.wikimedia.org/wiki/File:Izuhara_port,_terminal.jpg) · [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) |

Photos show *locations*, not confirmed sailing vessels or departures. Existing route destinations and the 45 companion-guide articles remain untouched. Live prices, departure confirmations, bookable inventory, and vessel schedules are not claimed. The browser audit verifies linked destinations and rendered layouts, **not** whether a transport booking can be completed, nor the byte-for-byte fidelity of the three previously existing image files against their Wikimedia originals.
