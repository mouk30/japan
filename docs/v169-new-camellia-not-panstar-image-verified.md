# NIPPONFERRY V169 — New Camellia vs PanStar image mismatch confirmed and fixed

**2026-10-24 21:15 KST. New articles: 0. Existing pages fixed: 2.**

## User-reported real production failure
The Fukuoka ferry card clearly says **"부산 → 후쿠오카, 페리부터 이해하기"** and **"뉴카멜리아로 하카타항 국제터미널까지"**, but its large photo displayed the blue-white **PanStar Cruise** vessel. The user reported the same incorrect image after V167 because this particular Fukuoka section was not included in V167's original four-section tests.

### Root cause
- `site/japan/fukuoka/index.html` used generic `/images/ferry.jpg` in the **New Camellia** card. That file depicts PanStar and is the wrong ship, not a mere low-resolution defect.
- `site/busan-fukuoka-cruise/index.html` also reused the same wrong PanStar file twice: as CSS hero background and in the ship image tag.
- The repository already owned a correctly attributed, licensed, high-resolution New Camellia photo stored as `site/images/venues/nf-v134-new-camellia-busan-2026-real.webp`, previously used by the correct `site/guide/busan-fukuoka-ferry/index.html`.

## Actual fixes committed
1. `site/japan/fukuoka/index.html`:
   - Swapped incorrect PanStar image for **actual New Camellia** WebP.
   - Descriptive subject-matched alt, 1400×934 source, `object-fit:contain` to avoid cropping or scale.
   - Correct photo credit **immediately beneath the corresponding New Camellia content**, not the next Fukuoka transport section.
2. `site/busan-fukuoka-cruise/index.html`:
   - Replaced both original `/images/ferry.jpg` references: hero CSS and main content photo.
   - Subject-specific 1400×934 WebP, noncropped cover, original author/CC license citation near the actual photo.
3. Photo provenance preserved:
   - Real New Camellia in Busan harbor 2026-07-01.
   - Photo author **Midnight cadet**.
   - Wikimedia Commons original https://commons.wikimedia.org/wiki/File:%E9%87%9C%E5%B1%B1%E6%B8%AF%E3%83%8B%E3%83%A5%E3%83%BC%E3%81%8B%E3%82%81%E3%82%8A%E3%81%82.jpg
   - License: https://creativecommons.org/licenses/by/4.0/ CC BY 4.0.
   - The original was previously resized / encoded to WebP. This image is of the ship and is not evidence of a specific trip's sailing, ship gate or ticket stock.

## Verification and release
- GitHub repository: `mouk30/japan`; commits include `293563188592ef4fd58832f5a4757c122ddc86da` (correct credit placement) and `2c50650295f44b8f73a92042d41a6fa54c50d9ee` (route image/hero).
- **Source, protected canonical/title/meta, correct image, credits, full site build**: PASS https://github.com/mouk30/japan/actions/runs/40093040069 .
- **Actual public browser verification**: PASS **390, 768, 1440px × 2 pages = 6 screen combinations**, no wrong image in either page, expected image `naturalWidth>=1200`, `object-fit:contain`, correct author/licensing, no major horizontal overflow, verified Fukuoka ferry content; original WebP response was HTTP 200 and valid WebP (**117,746 bytes**). Total **7/7 PASS**: https://github.com/mouk30/japan/actions/runs/40093114469 .
- The six screenshots plus JSON audit are stored in the GitHub Actions artifact of the public verification run.
- Verified Vercel deployments succeeded on changed-page commits; this was not just a branch diff.
- **Do not confuse** successfully loading the licensed ship photo with verifying actual sailing dates, ticket payment or the ferry operator's current boarding time.

## Regression prevention
New CI workflows:
- `.github/workflows/v169-camellia-source-qa.yml`
- `.github/workflows/v169-live-ship-photo-qa.yml`

The former rejects renewed links to generic `/images/ferry.jpg` within the two New Camellia pages. The latter checks the actual public image by file identity, size, licensing and human-visible browser image, not merely whether a photo URL returns HTTP 200.

**Outcome:** The precise mismatch shown by the user has been fixed and verified in production. Next content-quality work should never reuse a ferry photograph to illustrate a different named ship even if visually similar; title, actual vessel, source license and visible image must match.
