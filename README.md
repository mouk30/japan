# NIPPONFERRY — 일본크루즈·일본페리 여행 가이드

Website: https://www.nipponferry.com/

## V64 (2026-10-08): Shinrin-yoku evergreen education
- Published `/things-to-do/japan-forest-bathing-shinrin-yoku/` about origins, sensory practice, differences from hiking and regional experiences.
- Original educational story grounded in Japan Forestry Agency/JNTO; medical evidence responsibly cites systematic review and identifies very-low-certainty limitations.
- Canonical, Article and BreadcrumbList JSON-LD; visible answer summary, educational narrative and 4 reader FAQs.
- Linked from things-to-do and nature hubs; added sitemap URL; no internal version number visible to visitors.
- Long-term policy: keep stable educational explanation evergreen, verify volatile travel and scientific details as research evolves.

## V63 (2026-10-08): evergreen Japanese experiences editorial
- New article: `/things-to-do/japan-diving-first-time/` — scuba options, regional differences, safety, responsible sea activities, FAQs.
- Source: JNTO diving topic; original article based on general evergreen information, without invented current prices or operators.
- Linked from both `/things-to-do/` and `/things-to-do/nature/`; added canonical, Article/BreadcrumbList JSON-LD, source links and sitemap entry.
- **Permanent editorial standard:** one distinctive reader question per article; clear first answer; narrative depth; practical decision guide; regional differences; official sources; visible limitations; contextual internal links; no consumer-facing V## labels.
- Update volatile details separately from evergreen narrative. Review official references and visitor behavior periodically; do not add overlapping thin pages merely to increase URL count.

## V62 (2026-10-08): everyday Japan, four iconic shopping experiences
- Added `/things-to-do/japan-four-shopping-experiences/` featuring konbini, drugstores/pharmacies, Don Quijote and Pokemon Center.
- Balanced cultural background, direct-answer GEO summary, practical comparison, browsing ideas, shopping safety and FAQs.
- Linked from the main things-to-do hub and the existing konbini editorial, updated the sitemap.
- Distinguish medicine-purchasing rules, Korean import rules and Pokemon Center/Cafe services; verify hours and inventory on official sites.

## V61 (2026-10-08): reader-first GEO/SEO editorial pilot
- Updated existing `/things-to-do/why-travel-japan-by-sea/`; did not add thin or duplicate URLs.
- Added a visible answer-first summary, practical air/ferry/cruise comparison, three reader FAQs, and explicit freshness/availability limitations.
- Kept the original narrative writing, JNTO source links, Article/BreadcrumbList data and related content links.
- Editorial standard for future releases: engaging opening, plain-language answer, grounded factual explanation, actionable comparisons, trustworthy sources and contextual internal links.
- GEO is about eligible, verifiable answers; neither markup nor prose guarantees AI citations. Verify indexing, live deployment, search metrics and Bing Webmaster Tools AI Performance separately.

## V56–V60 (2026-10-08): Japan culture editorial quality
- V56: `/things-to-do/why-japanese-onsen-special/` — hot springs, sento, onsen towns, bathing culture.
- V57: `/things-to-do/japan-konbini-culture/` — Japanese convenience-store everyday culture.
- V58: `/things-to-do/japan-small-streets/` — yokocho alleys and local streets.
- V59: `/things-to-do/ryokan-vs-hotel/` — ryokan experiences versus hotel lodging.
- V60: `/things-to-do/why-travel-japan-by-sea/` — ferries, cruise distinctions, slow travel.
- Original explanatory articles with JNTO source links and relevant internal links.
- Connected from things-to-do hub; sitemap URLs registered.
- Editorial direction: focus on useful original writing; don't bulk-generate interchangeable pages.

## V51–V55 (2026-10-08): high-intent things-to-do SEO
- V51 `/things-to-do/family-with-kids/`: family, stroller and indoor experiences.
- V52 `/things-to-do/solo-cultural-day/`: solo cultural visits and small workshops.
- V53 `/things-to-do/japan-free-low-budget/`: free and low-cost experiences.
- V54 `/things-to-do/accessible-slow-travel/`: slower-paced travel with parents and accessibility checks.
- V55 `/things-to-do/experience-booking-checklist/`: cancellations, meeting points and bad-weather alternatives.
- All pages linked from `/things-to-do/`, with canonical, Article and BreadcrumbList JSON-LD. Sitemap updated.
- Editorial reference: Japan National Tourism Organization (JNTO) things-to-do sections; content is original and does not assert real-time availability.

## V45–V50 (2026-10-08): Japanese things-to-do high-intent search content
- The V44 Okinawa milestone remains intact.
- V45 `/things-to-do/onsen-first-time/`: first-time onsen etiquette, tattoo policy and day-use checks.
- V46 `/things-to-do/traditional-experience-booking/`: tea ceremony, kimono, craft workshops.
- V47 `/things-to-do/nature-outdoor-checklist/`: seasonal nature, difficulty and weather.
- V48 `/things-to-do/local-food-market-guide/`: local market foods and ordering tips.
- V49 `/things-to-do/shopping-city-night-guide/`: shopping, tax-free and evening logistics.
- V50 `/things-to-do/port-to-experience-planner/`: port-arrival itinerary and booking readiness.
- Linked all six from `/things-to-do/`; registered in the sitemap.
- Inspired by official JNTO category taxonomy (not copied); avoids unverifiable real-time fares and operating hours.

## V43–V44 (2026-10-08): Okinawa destination SEO
- V43: `/okinawa/miyakojima-hirara-port/`, `/okinawa/ishigaki-cruise-port/`.
- V44: `/okinawa/zamami-aka-ferry/`, `/okinawa/tokashiki-ferry/`.
- All four guides linked from `/okinawa/` and included in `site/sitemap.xml`.
- Distinguish Okinawa cruise ports, domestic island ferries and international connections. Check official schedules before booking.

## V42 (2026-10-08): Okinawa practical SEO expansion
- Previous V41 Okinawa hub and six guides preserved.
- Added `/okinawa/naha-half-day/`: Naha port-of-call half-day plan, berth check, Kokusai-dori, all-aboard deadline.
- Added `/okinawa/kerama-ferry-booking/`: Tomari departures, Zamami/Tokashiki booking and cancellation checklist.
- Linked both pages from `/okinawa/` and included in `site/sitemap.xml`.
- Sources linked to Okinawa's official cruise guidance and the local island authorities; no fabricated current fares, sailing times, or Korea–Okinawa direct ferry.

## Existing V41 strategy
- Main pillar: `/japan-cruise/` (cruise search intent).
- Transport reference: `/ferry/` (ferry routes and logistics).
- Regional hub: `/okinawa/` (Naha, Miyakojima, Ishigaki, Kerama).
- Combined activities hub: `/things-to-do/` (food, shopping, seasons/festivals).
- Existing homepage, design assets, and legacy URLs retained.

## Build and deployment
- Install Node.js and run `npm run build`.
- `build.js` copies `site/` to `dist/` and applies shared navigation adjustments.
- Vercel: build command `npm run build`, output directory `dist` (`vercel.json`).
- Change source under `site/`, not `dist/`.
- Check official vessel operators for schedules, berths, fares, cancellations, and booking availability.

## Original design notes (V12)
- Blue/white master template, deep-blue navigation, light-blue hero, red CTA, Pretendard typography.
- Preserved existing SEO pages and responsive navigation conventions.
