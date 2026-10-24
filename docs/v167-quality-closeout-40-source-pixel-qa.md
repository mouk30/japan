# NIPPONFERRY V167 — Image quality closeout and production QA
**Final verification: 2026-10-24 (KST). Existing URLs maintained. No new articles.**

## Scope and observed defects
- User-supplied screenshots: blurred PanStar Miracle image; Sapporo Snow Festival and Otaru winter cards incorrectly shared unrelated Kyoto-style red autumn photo.
- V167 initial fixes: PanStar official ship photo and noncropped fit on Osaka and Busan/Osaka guide; 3 independently subject-matched Hokkaido real photos (Sapporo Snow Festival, Otaru winter canal, Noboribetsu real CC0 onsen with source attribution); 19 wrong-city Fukuoka directory links and sweet/dessert thumbnail corrected.
- Exact original document title, meta description, canonical, H1, page URLs, main link structure preserved (initial 4-page content QA).
- Site-wide static scan: **1,268 local HTML img references, 0 missing files; 40 small-dimension asset candidates**. This is not a count of SVGs. A dimension threshold alone cannot certify blur, wrong city, or image licensing.

## 40 candidates individually classified
GitHub Actions **40090650541** and `audit-output/v167/v167-low-resolution-40-priorities.json`:
- P0 entry-page: 1 (Fukuoka Tower portrait source 637×850).
- P1 category/theme listing: 11 (including Hakodate Goryokaku, Kobe Meriken, Shamisen and Tatami).
- P2 topic/detail: 25 (many authentic narrow Tokyo Commons originals).
- P3 appropriate UI icons: 3 (Kakao 512×512 and favicons 32×32 / 180×180).
- All 40 are *candidates*, not necessarily wrong photographs. Do not generate or upscale original pixels to meet a nominal width threshold.

## Real browser pixel-scale finding and repairs
The first individual-browser audit **40090824505** visited 86 page/viewport combinations (390 and 1440 px, up to three use pages per asset) and found **22 out of 40** candidate source assets significantly *upscaled* in at least one actual page:
- **20 Tokyo original Commons topic images:** CSS article hero forced portrait/narrow 500–600px to cover an 812px landscape region (examples 1.35–1.60×). Fixed centrally in `site/tokyo-guide.css`: target only the 20 verified small-photo image source paths, `object-fit:scale-down`, preserve complete scene and natural pixel size; other original high-resolution Tokyo photos are not affected.
- **Fukuoka Tower** in `site/things-to-do/hakata-cruise-parents-guide/index.html`: 637×850 source wrongly declared 1200×675 in markup and enlarged 1.43×. Corrected intrinsic dimensions and replaced forced-cover display by a contained native-pixel foreground and muted scenic background.
- **Tatami interior** in `site/things-to-do/tatami-floor-japanese-living/index.html`: 616×459 source enlarged **2.34×**; replaced forced-cover with native-pixel scale-down foreground plus muted ambiance.
- Earlier V167 additional high-priority portrait fixes: Hakodate Goryokaku Tower, Kobe Meriken Park and cultural Shamisen. Existing authentic portrait photo pixels are displayed in a contained, uncropped, non-upscaled foreground with soft decorative scene backdrop; files/source credits unchanged.
- **11 Tokyo original-photo alt texts** formerly falsely described food, shops and attractions as "related station photographs"; corrected only alt to identify source-file-subject, untouched real photo, Wikimedia attribution, titles, canonical and descriptions. GitHub Actions **40090293855** source comparison passed.

The post-repair browser rerun **40091116606** measured the same **86 page/viewport observations**:
- **0 source photo assets significantly enlarged**.
- **38 assets measured with no significant upscaling** in sampled pages.
- **2 unmeasured image-tag UI icon files** (favicons/touch icon) are not large photographic thumbnails.
- Threshold >1.10. The CSS `scale-down` rule is capped at 100% natural pixel size by the measurement script. Source-photo metadata is not artificially inflated.
- Browser measurement is sampled, not a proof about every possible HTML/CSS placement or every device pixel ratio.

## Mobile/tablet/desktop public acceptance
- First run 40085341444 canceled when an unbounded 19-card directory region stalled; the first 6 Hokkaido/Osaka screens had passed, no claim of 12 then.
- Fixed lazy image decode deadline, scroll/capture timeout and bounded viewport screenshot. **12/12 pass** https://github.com/mouk30/japan/actions/runs/40089782142.
- Added 3 real portrait-origin pages (Hakodate, Kobe, Shamisen) across 390/768/1440 screen widths, checking `object-fit:contain`, source-content scale and no horizontal overflow. **21/21 pass** https://github.com/mouk30/japan/actions/runs/40090586438.
- Original SEO/photo-source attribution/site build acceptance for corrected native-resolution images: https://github.com/mouk30/japan/actions/runs/40091196083 (**success**).
- Original primary V167 overall image audit and priority-source checks: https://github.com/mouk30/japan/actions/runs/40090650541 (**success**).
- Re-run of post-repair all-40 real-image pixel scaling QA: https://github.com/mouk30/japan/actions/runs/40091116606 (**success**, 0 problematic sampled scale-ups).

## Scope limitation before subsequent content work
- This completes the specifically agreed **V167 1st-pass photo/media/wording/QA scope** on the identified homepage and representative pages and audited undersized candidates.
- Does **not** mean that the exact location, year, author, ownership/license, or every image-caption pairing across all 1,000+ HTML pages has been individually visually inspected.
- Avoid automatic replacement of portrait photos merely because their natural width is below 640 px. A local high-res original with verified place, photographer and rights should be obtained before replacing any remaining photo that users actually observe as soft.
- User's next workstream is content QUALITY, not new post count; subsequent content tasks should preserve URLs and links, only update officially verified data, authentic photos, and real reservations/return-to-ship routes.
