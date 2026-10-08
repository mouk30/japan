# NIPPONFERRY — 일본크루즈·일본페리 여행 가이드

Website: https://www.nipponferry.com/

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
