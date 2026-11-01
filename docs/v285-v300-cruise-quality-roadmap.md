# NIPPONFERRY V285–V300 quality-first work plan

Principles: **new articles 0**, retain canonical/sitemap/robots/CTA, never label AI art as a real photo, use the exact approved clean PanStar image, preserve source/rights documentation, no fake live availability.

| Version | Scope | Acceptance evidence |
|---|---|---|
| V285 | Existing seven cruise/booking hero backgrounds | Merged PR #93, production checked |
| V286 | Image inventory + stale V147/V156 booking QA | PR #94, CI + JSON inventory, no production before pass |
| V287 | Approved clean PanStar hero, whole ship, text and buttons in separate band | PR #95, binary upload and QA required |
| V288 | Main cruise/booking desktop hero visual QA | 1440px/1920px screenshots, no text overflow or ship crop |
| V289 | Mobile hero visual QA | 390px/430px/768px screenshots, full ship and readable buttons |
| V290 | Route identity and image relevance | route-by-route ship/operator and location match ledger |
| V291 | Replace legacy blurry/repeated image candidates | original source, license, pixel resolution and before/after |
| V292 | Booking route CTA checks | real official URL, no fabricated availability |
| V293 | Boarding terminals and check-in | verify terminal names and operator documents |
| V294 | Return trip and last transport | exact port, transport, check-in cutoffs with evidence |
| V295 | Cruise port cards | title/photo/place/landing URL alignment |
| V296 | Coastal ferry cards | correct ferry operator, route and booking landing |
| V297 | Image accessibility and speed | alt text, dimensions, lazy load and WebP as appropriate |
| V298 | SEO regression | canonicals, JSON-LD, robots, sitemap, internal links |
| V299 | Full responsive regression | existing 390/768/1440 QA plus targeted 1920 |
| V300 | Final audit and production verification | CI, preview, source proof, production URL checks |

## Current blockers
- V287 image is supplied in the conversation but **not yet present in GitHub** at `site/images/panstar-cruise-clean-2048.webp`. No deployment before the exact asset is committed.
- The user-supplied PanStar image is illustrative artwork, not verified operator photography. Do not call it a real official photo.
- V286 needs green QA and photo provenance validation before merge.
- A static regex inventory does **not** prove visual quality, geographic accuracy, license, or photo crop; use real viewport review for those.

## Scope policy
Keep versions as sequential, separately verifiable batches. Do not auto-merge failed CI, suppress failures to force deploy, or claim completion for versions only planned.
